import configparser
import os

class config:
    def __init__(self, filename):
        self.cfg = configparser.ConfigParser()
        if filename.endswith('.ini'):
            self.filename = filename
        else:
            self.filename = filename + '.ini'
        self.configs = {}
        self.sectionslist = []

    def addconfig(self, config, section, config_name):
        typeof = 'str'
        if type(config) == int:
            typeof = 'int'
        elif type(config) == float:
            typeof = 'float'
        elif type(config) == bool:
            typeof = 'bool'
        
        if section not in self.sectionslist:
            self.sectionslist.append(section)
        self.configs[config_name] = {'config':config, 'section':section, 'typeof':typeof}
        
    def getconfig(self):
        if os.path.exists(self.filename):
            self.cfg.read(self.filename)
            for config in self.configs:
                if self.configs[config]['section'] not in self.cfg:
                    self.cfg[self.configs[config]['section']] = self.configs[config]['section']
                    with open(self.filename, 'w+') as configfile:
                        self.cfg.write(configfile)
                if config not in self.cfg[self.configs[config]['section']]:
                    self.cfg[self.configs[config]['section']][config] = str(self.configs[config]['config'])
                    with open(self.filename, 'w+') as configfile:
                        self.cfg.write(configfile)
                if self.configs[config]['typeof'] == 'int':
                    self.configs[config]['config'] = int(self.cfg[self.configs[config]['section']][config])
                if self.configs[config]['typeof'] == 'str':
                    self.configs[config]['config'] = self.cfg[self.configs[config]['section']][config]
                if self.configs[config]['typeof'] == 'bool' or self.configs[config]['typeof'] == 'boolean':
                    self.configs[config]['config'] = self.cfg[self.configs[config]['section']][config]
                    if self.configs[config]['config'].lower() == 'true':
                        self.configs[config]['config'] = True
                    elif self.configs[config]['config'].lower() == 'false':
                        self.configs[config]['config'] = False
                    else:
                        self.configs[config]['config'] = None
                        raise 'Couldn\'t check value true or false\\value isn\'t true or false.'
        else:
            for section in self.sectionslist:
                self.cfg[section] = {}
            for config in self.configs:
                self.cfg[self.configs[config]['section']][config] = str(self.configs[config]['config'])
            with open(self.filename, 'w+') as configfile:
                self.cfg.write(configfile)
    def returnresult(self, singledict=False):
        result = {}
        if not singledict:
            for config in self.configs:
                if self.configs[config]['section'] not in result:
                    result[self.configs[config]['section']] = {}
                result[self.configs[config]['section']][config] = self.configs[config]['config']
        else:
            for config in self.configs:
                result[config] = self.configs[config]['config']

        return result
    def returneverything(self):
        return self.cfg.__dict__['_sections']
