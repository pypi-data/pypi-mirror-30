#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

from builtins import object
import os
import sys
import platform
import configobj
from configobj import ConfigObj
import validate

join = os.path.join


class Preferences(object):
    """Users can alter preferences from the dialog box in the application,
    by editing their user preferences file (which is what the dialog box does)
    or, within a script, preferences can be controlled like this::

        import psychopy
        psychopy.prefs.general['audioLib'] = ['pyo','pygame']
        print(prefs)
        # prints the location of the user prefs file and all the current vals

    Use the instance of `prefs`, as above, rather than the `Preferences` class
    directly if you want to affect the script that's running.
    """

    def __init__(self):
        super(Preferences, self).__init__()
        self.userPrefsCfg = None  # the config object for the preferences
        self.prefsSpec = None  # specifications for the above
        # the config object for the app data (users don't need to see)
        self.appDataCfg = None

        self.general = None
        self.coder = None
        self.builder = None
        self.connections = None
        self.paths = {}  # this will remain a dictionary
        self.keys = {}  # does not remain a dictionary

        self.getPaths()
        self.loadAll()
        # setting locale is now handled in psychopy.localization.init
        # as called upon import by the app

        if self.userPrefsCfg['app']['resetPrefs']:
            self.resetPrefs()

    def __str__(self):
        """pretty printing the current preferences"""
        strOut = "psychopy.prefs <%s>:\n" % (
            join(self.paths['userPrefsDir'], 'userPrefs.cfg'))
        for sectionName in ['general', 'coder', 'builder', 'connections']:
            section = getattr(self, sectionName)
            for key, val in list(section.items()):
                strOut += "  prefs.%s['%s'] = %s\n" % (
                    sectionName, key, repr(val))
        return strOut

    def resetPrefs(self):
        """removes userPrefs.cfg, does not touch appData.cfg
        """
        userCfg = join(self.paths['userPrefsDir'], 'userPrefs.cfg')
        try:
            os.unlink(userCfg)
        except Exception:
            msg = "Could not remove prefs file '%s'; (try doing it manually?)"
            print(msg % userCfg)
        self.loadAll()  # reloads, now getting all from .spec

    def getPaths(self):
        # on mac __file__ might be a local path, so make it the full path
        thisFileAbsPath = os.path.abspath(__file__)
        prefSpecDir = os.path.split(thisFileAbsPath)[0]
        dirPsychoPy = os.path.split(prefSpecDir)[0]

        # path to Resources (icons etc)
        dirApp = join(dirPsychoPy, 'app')
        if os.path.isdir(join(dirApp, 'Resources')):
            dirResources = join(dirApp, 'Resources')
        else:
            dirResources = dirApp

        self.paths['psychopy'] = dirPsychoPy
        self.paths['appDir'] = dirApp
        self.paths['appFile'] = join(dirApp, 'PsychoPy.py')
        self.paths['demos'] = join(dirPsychoPy, 'demos')
        self.paths['resources'] = dirResources
        self.paths['tests'] = join(dirPsychoPy, 'tests')

        if sys.platform == 'win32':
            self.paths['prefsSpecFile'] = join(prefSpecDir, 'Windows.spec')
            self.paths['userPrefsDir'] = join(os.environ['APPDATA'],
                                              'psychopy2')
        else:
            self.paths['prefsSpecFile'] = join(prefSpecDir,
                                               platform.system() + '.spec')
            self.paths['userPrefsDir'] = join(os.environ['HOME'],
                                              '.psychopy2')

        # avoid silent fail-to-launch-app if bad permissions:
        if os.path.exists(self.paths['userPrefsDir']):
            try:
                if not os.access(self.paths['userPrefsDir'],
                                 os.W_OK | os.R_OK):
                    raise OSError
                tmp = os.path.join(self.paths['userPrefsDir'], '.tmp')
                with open(tmp, 'w') as fileh:
                    fileh.write('')
                open(tmp).read()
                os.remove(tmp)
            except Exception:  # OSError, WindowsError, ...?
                msg = 'PsychoPy2 error: need read-write permissions for `%s`'
                sys.exit(msg % self.paths['userPrefsDir'])

    def loadAll(self):
        """Load the user prefs and the application data
        """
        self._validator = validate.Validator()

        # note: self.paths['userPrefsDir'] gets set in loadSitePrefs()
        self.paths['appDataFile'] = join(
            self.paths['userPrefsDir'], 'appData.cfg')
        self.paths['userPrefsFile'] = join(
            self.paths['userPrefsDir'], 'userPrefs.cfg')

        # If PsychoPy is tucked away by Py2exe in library.zip, the preferences
        # file cannot be found. This hack is an attempt to fix this.
        libzip = "\\library.zip\\psychopy\\preferences\\"
        if libzip in self.paths["prefsSpecFile"]:
            self.paths["prefsSpecFile"] = self.paths["prefsSpecFile"].replace(
                libzip, "\\resources\\")

        self.userPrefsCfg = self.loadUserPrefs()
        self.appDataCfg = self.loadAppData()
        self.validate()

        # simplify namespace
        self.general = self.userPrefsCfg['general']
        self.app = self.userPrefsCfg['app']
        self.coder = self.userPrefsCfg['coder']
        self.builder = self.userPrefsCfg['builder']
        self.connections = self.userPrefsCfg['connections']
        self.keys = self.userPrefsCfg['keyBindings']
        self.appData = self.appDataCfg

        # keybindings:
        self.keys = self.userPrefsCfg['keyBindings']

    def loadUserPrefs(self):
        """load user prefs, if any; don't save to a file because doing so
        will break easy_install. Saving to files within the psychopy/ is
        fine, eg for key-bindings, but outside it (where user prefs will
        live) is not allowed by easy_install (security risk)
        """
        self.prefsSpec = ConfigObj(self.paths['prefsSpecFile'],
                                   encoding='UTF8', list_values=False)

        # check/create path for user prefs
        if not os.path.isdir(self.paths['userPrefsDir']):
            try:
                os.makedirs(self.paths['userPrefsDir'])
            except Exception:
                msg = ("Preferences.py failed to create folder %s. Settings"
                       " will be read-only")
                print(msg % self.paths['userPrefsDir'])
        # then get the configuration file
        cfg = ConfigObj(self.paths['userPrefsFile'],
                        encoding='UTF8', configspec=self.prefsSpec)
        # cfg.validate(self._validator, copy=False)  # merge then validate
        # don't cfg.write(), see explanation above
        return cfg

    def saveUserPrefs(self):
        """Validate and save the various setting to the appropriate files
        (or discard, in some cases)
        """
        self.validate()
        if not os.path.isdir(self.paths['userPrefsDir']):
            os.makedirs(self.paths['userPrefsDir'])
        self.userPrefsCfg.write()

    def loadAppData(self):
        # fetch appData too against a config spec
        appDataSpec = ConfigObj(join(self.paths['appDir'], 'appData.spec'),
                                encoding='UTF8', list_values=False)
        cfg = ConfigObj(self.paths['appDataFile'],
                        encoding='UTF8', configspec=appDataSpec)
        resultOfValidate = cfg.validate(self._validator,
                                        copy=True,
                                        preserve_errors=True)
        self.restoreBadPrefs(cfg, resultOfValidate)
        # force favComponent level values to be integers
        if 'favComponents' in cfg['builder']:
            for key in cfg['builder']['favComponents']:
                _compKey = cfg['builder']['favComponents'][key]
                cfg['builder']['favComponents'][key] = int(_compKey)
        return cfg

    def saveAppData(self):
        """Save the various setting to the appropriate files
        (or discard, in some cases)
        """
        # copy means all settings get saved:
        self.appDataCfg.validate(self._validator, copy=True)
        if not os.path.isdir(self.paths['userPrefsDir']):
            os.makedirs(self.paths['userPrefsDir'])
        self.appDataCfg.write()

    def validate(self):
        """Validate (user) preferences and reset invalid settings to defaults
        """
        result = self.userPrefsCfg.validate(self._validator, copy=True)
        self.restoreBadPrefs(self.userPrefsCfg, result)

    def restoreBadPrefs(self, cfg, result):
        """result = result of validate
        """
        if result == True:
            return
        vtor = validate.Validator()
        for sectionList, key, _ in configobj.flatten_errors(cfg, result):
            if key is not None:
                _secList = ', '.join(sectionList)
                val = cfg.configspec[_secList][key]
                cfg[_secList][key] = vtor.get_default_value(val)
            else:
                msg = "Section [%s] was missing in file '%s'"
                print(msg % (', '.join(sectionList), cfg.filename))

prefs = Preferences()
