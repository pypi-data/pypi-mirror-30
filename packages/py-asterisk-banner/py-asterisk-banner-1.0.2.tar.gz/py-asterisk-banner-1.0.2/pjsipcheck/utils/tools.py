from pjsipcheck import settings

import logging
import re


class Tools:
    def __init__(self):
        self.log = logging.getLogger(settings.LOGGER_NAME)

    @staticmethod
    def get_ip_address(line):
        numips = len(re.findall(r'[0-9]+(?:\.[0-9]+){3}', line))

        if numips > 0:
            if numips == 2:
                ipaddress = re.findall(r'[0-9]+(?:\.[0-9]+){3}', line)[numips - 1]
            else:
                ipaddress = re.findall(r'[0-9]+(?:\.[0-9]+){3}', line)[numips - 2]

            return ipaddress
        else:
            return None
