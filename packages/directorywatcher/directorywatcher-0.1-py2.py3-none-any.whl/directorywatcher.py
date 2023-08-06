# -*- coding: utf-8 -*-
"""
Created on Thu Mar 12 2015

@author: Josh Burnett

"""

import os, re, random
from multitimer import MultiTimer

"""
Barebones cross-platform library to poll directories for added & removed files
"""


#%%
class DirectoryWatcher:
    """
    Monitors a directory for added and removed files, optionally matching file names against a pattern.
    Runs specified functions when files matching the pattern are added or removed.
    """

    on_added = None
    on_removed = None
    active = False

    def __init__(self, path, interval=5):
        self.directory = path
        self.interval = interval
        self.actions_on_added = {}
        self.actions_on_removed = {}
        self.timer = MultiTimer(interval=interval, ontimeout=self._mainloop)
        self.before = set()


    def register_action_on_added(self, action, pattern=None, **kwargs):
        """
        Add a function to 'actions_on_added,' the list of functions to run when a file has been added.
        """
        if pattern is not None:
            pattern_re = re.compile(pattern)
        else:
            pattern_re = None

        actionid = hash(random.random())
        if pattern_re not in self.actions_on_added:
            self.actions_on_added[pattern_re] = {}
        self.actions_on_added[pattern_re][actionid] = (action, kwargs)
        return actionid


    def deregister_action_on_added(self, actionid, pattern=None):
        """
        Remove a function from 'actions_on_added,' the list of functions to run when a file has been added.
        """
        if pattern is not None:
            pattern_re = re.compile(pattern)
        else:
            pattern_re = None
        del self.actions_on_added[pattern_re][actionid]
        if not self.actions_on_added[pattern_re].values():
            del self.actions_on_added[pattern_re]


    def register_action_on_removed(self, action, pattern=None, **kwargs):
        """
        Add a function to 'actions_on_removed,' the list of functions to run when a file has been removed.
        """
        if pattern is not None:
            pattern_re = re.compile(pattern)
        else:
            pattern_re = None

        actionid = hash(random.random())
        if pattern not in self.actions_on_removed:
            self.actions_on_removed[pattern_re] = {}
        self.actions_on_removed[pattern_re][actionid] = (action, kwargs)
        return actionid


    def deregister_action_on_removed(self, actionid, pattern=None):
        """
        Remove a function from 'actions_on_removed,' the list of functions to run when a file has been removed.
        """
        if pattern is not None:
            pattern_re = re.compile(pattern)
        else:
            pattern_re = None
        del self.actions_on_removed[pattern_re][actionid]
        if not self.actions_on_removed[pattern_re].values():
            del self.actions_on_removed[pattern_re]


    def start(self, startempty=False):
        if startempty:
            self.before = set()
        else:
            # Initialize the file list outside of the loop
            self.before = set(os.listdir(self.directory))

        self.active = True
        self.timer.start()


    def _mainloop(self):
        if self.active:
            # print 'checking for new files:\t{fdir}'.format(fdir=self.directory)
            self.after = set(os.listdir(self.directory))

            # Compares lists and passes file/folder names, filtering based on file name pattern if specified
            if self.actions_on_removed:
                removed = list(self.before - self.after)
                for fname in removed:
                    # First, run through all actions defined for pattern=None (always run)
                    if None in self.actions_on_removed:
                        for action, kwargs in self.actions_on_removed[None].values():
                            action(filepath=os.path.join(self.directory, fname), **kwargs)
                    # Then go through each pattern and run actions if filename matches pattern
                    other_patterns = [pattern for pattern in self.actions_on_removed.keys() if pattern is not None]
                    for pattern in other_patterns:
                        if pattern.match(fname):
                            for action, kwargs in self.actions_on_removed[pattern].values():
                                action(filepath=os.path.join(self.directory, fname), **kwargs)

            if self.actions_on_added:
                added = list(self.after - self.before)
                for fname in added:
                    # First, run through all actions defined for pattern=None (always run)
                    if None in self.actions_on_added:
                        for action, kwargs in self.actions_on_added[None].values():
                            action(filepath=os.path.join(self.directory, fname), **kwargs)
                    # Then go through each pattern and run actions if filename matches pattern
                    other_patterns = [pattern for pattern in self.actions_on_added.keys() if pattern is not None]
                    for pattern in other_patterns:
                        if pattern.match(fname):
                            for action, kwargs in self.actions_on_added[pattern].values():
                                action(filepath=os.path.join(self.directory, fname), **kwargs)

            self.before = self.after

        else:
            self.timer.stop()


    def stop(self, *args, **kwargs):
        self.active = False
        self.timer.stop()


    def summary(self):
        out = ['Monitoring:\t{fdir}'.format(fdir=self.directory)]
        for regex in self.actions_on_added.keys():
            out.append('  %s' % regex.pattern)
            for action in self.actions_on_added[regex].values():
                out.append('    -> %s' % action[0].func_name)
        return '\n'.join(out)

#%%