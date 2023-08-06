import configparser


class Config:

    def __init__(self, conf_file):
        self.config = configparser.ConfigParser()
        self.config.read(conf_file)

    def get_asterisk(self, key=None):
        try:
            if key is not None:
                return self.config['ASTERISK'][key]
            else:
                return self.config['ASTERISK']

        except KeyError:
            return None

    def get_database(self, key=None):
        try:
            if key is not None:
                return self.config['DATABASE'][key]
            else:
                return self.config['DATABASE']

        except KeyError:
            return None

    def get_white_list(self):
        try:
            return self.config['WHITE_LIST']['ip_addresses'].split('|')

        except KeyError:
            return None

    def get_email(self, key=None):
        try:
            if key is not None:
                if key == 'enable':
                    if self.config['EMAIL']['enable'] == 'yes':
                        return True
                    elif self.config['EMAIL']['enable'] == 'no':
                        return False
                    else:
                        return False

                else:
                    return self.config['EMAIL'][key]
            else:
                return self.config['EMAIL']

        except KeyError:
            return None

    def get_log(self, key=None):
        try:
            if key is not None:
                return self.config['LOG'][key]
            else:
                return self.config['LOG']

        except KeyError:
            return None
