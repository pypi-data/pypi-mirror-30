from configparser import ConfigParser


class CaseConfigParser(ConfigParser):

    def optionxform(self, optionstr):
        return optionstr
