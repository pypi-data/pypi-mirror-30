#
# A library to manage ARCFIRE experiments
#
#    Copyright (C) 2017 Nextworks S.r.l.
#    Copyright (C) 2017 imec
#
#    Sander Vrijders   <sander.vrijders@ugent.be>
#    Dimitri Staessens <dimitri.staessens@ugent.be>
#    Vincenzo Maffione <v.maffione@nextworks.it>
#    Marco Capitani    <m.capitani@nextworks.it>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., http://www.fsf.org/about/contact/.
#
import enum
import os

import rumba.log as log
import rumba.model as model

# Fix input reordering
try:
    import builtins  # Only in Python 3

    def input(prompt=''):
        log.flush_log()
        return builtins.input(prompt)
except ImportError:  # We are in Python 2
    import __builtin__

    def input(prompt=''):
        log.flush_log()
        return __builtin__.raw_input(prompt)

logger = log.get_logger(__name__)


class SwapOutStrategy(enum.Enum):
    """
    What action to perform on swap-out.
    """
    NO = 0
    AUTO = 1
    PAUSE = 2
    PROMPT = 3


class SyslogsStrategy(enum.Enum):
    """
    What prototype and system logs to retrieve.
    """
    NO = 0
    DEFAULT = 1
    DMESG = 2
    CUSTOM = 3


# Utility names for importing in the scripts
NO_SWAPOUT = SwapOutStrategy.NO
AUTO_SWAPOUT = SwapOutStrategy.AUTO
PAUSE_SWAPOUT = SwapOutStrategy.PAUSE
PROMPT_SWAPOUT = SwapOutStrategy.PROMPT

NO_SYSLOGS = SyslogsStrategy.NO
DEFAULT_SYSLOGS = SyslogsStrategy.DEFAULT
DMESG_SYSLOGS = SyslogsStrategy.DMESG
CUSTOM_SYSLOGS = SyslogsStrategy.CUSTOM


class ExperimentManager(object):
    """
    Helper class for running a Rumba experiment.
    """
    def __init__(self,
                 experiment,
                 swap_out_strategy=AUTO_SWAPOUT,
                 syslogs_strategy=NO_SYSLOGS,
                 syslogs=None):
        """
        :param experiment: The experiment name.
        :type experiment: `rumba.model.Experiment`
        :param swap_out_strategy: What action to perform on swap-out.
        :param syslogs_strategy: What system and prototype logs to retrieve
                                before swap-out.
        :param syslogs: The location of the syslogs in case of custom syslogs.
        :type syslogs: `str`

        .. note:: Options for swap_out_strategy are

                  - NO_SWAPOUT == 0,
                  - AUTO_SWAPOUT == 1,
                  - PAUSE_SWAPOUT == 2,
                  - PROMPT_SWAPOUT == 3.

        .. note:: Options for syslog_strategy are

                  - NO_SYSLOGS == 0,
                  - DEFAULT_SYSLOGS == 1,
                  - DMESG_SYSLOGS == 2,
                  - CUSTOM_SYSLOGS == 3.
        """
        assert isinstance(experiment, model.Experiment), \
            'An experiment instance is required.'
        self.experiment = experiment
        self.swap_out_strategy = swap_out_strategy
        self.syslogs_strategy = syslogs_strategy
        self.syslogs = [syslogs] if isinstance(syslogs, str) else syslogs
        self.use_sudo = self.experiment.testbed.username != 'root'

    def __enter__(self):
        pass

    def fetch_dmesg_syslog(self, node, node_dir):
        node.execute_command('dmesg > /tmp/dmesg')
        node.fetch_file('/tmp/dmesg', node_dir)

    def fetch_syslog(self, node, node_dir):
        node.fetch_files(self.syslogs,
                         node_dir, self.use_sudo)

    def fetch_prototype_logs(self, node, node_dir):
        node.fetch_files(self.experiment.prototype_logs,
                         node_dir, self.use_sudo)

    def fetch_syslogs(self):
        local_dir = self.experiment.log_dir

        # Define and set up fetching function
        if self.syslogs_strategy == DMESG_SYSLOGS:
            fetching_function = self.fetch_dmesg_syslog
        elif self.syslogs_strategy == DEFAULT_SYSLOGS:
            self.syslogs = self.experiment.testbed.system_logs
            fetching_function = self.fetch_syslog
        elif self.syslogs_strategy == CUSTOM_SYSLOGS:
            assert self.syslogs is not None, \
                'Custom syslog strategy requires specifying a path'
            fetching_function = self.fetch_syslog
        else:
            raise ValueError('Unknown syslogs strategy %s'
                             % self.syslogs_strategy)

        for node in self.experiment.nodes:
            node_dir = os.path.join(local_dir, node.name)
            if not os.path.isdir(node_dir):
                os.mkdir(node_dir)
            try:
                fetching_function(node, node_dir)
                self.fetch_prototype_logs(node, node_dir)
            except Exception as e:
                logger.warning(
                    'Could not fetch prototype logs of node %s. %s%s',
                    node.name,
                    type(e).__name__,
                    (": " + str(e)) if str(e) != "" else ""
                )

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            # Pause to let the user play
            if self.swap_out_strategy == PAUSE_SWAPOUT:
                input('Press ENTER to start swap out.')
                do_swap_out = True
            elif self.swap_out_strategy == PROMPT_SWAPOUT:
                do_swap_out = None
                while do_swap_out is None:
                    ans = input('Swap out experiment? (y/n): ')
                    if ans == 'y':
                        do_swap_out = True
                    elif ans == 'n':
                        do_swap_out = False
                    else:
                        print("Only 'y' or 'n' please.")
            elif self.swap_out_strategy == AUTO_SWAPOUT:
                do_swap_out = True
            elif self.swap_out_strategy == NO_SWAPOUT:
                do_swap_out = False
            else:
                logger.warning('Unknown swap-out strategy %s. Swapping out.',
                               self.swap_out_strategy)
                do_swap_out = True

            # Fetch syslogs (if requested)
            if self.syslogs_strategy != NO_SYSLOGS:
                try:
                    self.fetch_syslogs()
                except Exception as e:
                    logger.warning(
                        'There has been a problem fetching syslogs. %s%s',
                        type(e).__name__,
                        ": " + str(e) if str(e) != "" else ""
                    )

            # Swap out
            if do_swap_out:
                self.experiment.swap_out()
            if exc_val is not None:
                logger.error('Something went wrong. '
                             'Got %s: %s',
                             type(exc_val).__name__, str(exc_val))
                logger.debug('Exception details:', exc_info=exc_val)
        finally:
            log.flush_and_kill_logging()
            # Make sure to print all logs before execution terminates,
            # Specifically the last two error logs above.
        return True
        # Suppress the exception we logged: no traceback, unless logged.
