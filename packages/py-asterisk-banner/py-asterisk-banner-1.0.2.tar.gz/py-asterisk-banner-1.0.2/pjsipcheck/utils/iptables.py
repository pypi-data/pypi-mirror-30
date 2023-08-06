from pjsipcheck import settings

import logging
import os


class IPTables(object):
    def __init__(self):
        self.logger = logging.getLogger(settings.LOGGER_NAME)

    def block(self, ipaddress):
        self.unblock(ipaddress)

        self.logger.info('IPTables - Bloqueando IP --> %s' % ipaddress)
        os.system("iptables -I INPUT -s %s -j DROP" % ipaddress)
        return True

    def unblock(self, ipaddress):
        self.logger.info('IPTables - Desbloqueando IP --> %s' % ipaddress)
        os.system("iptables -D INPUT -s %s -j DROP" % ipaddress)
        return True
