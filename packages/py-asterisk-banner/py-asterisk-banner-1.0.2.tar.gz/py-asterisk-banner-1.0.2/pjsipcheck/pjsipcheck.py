from pjsipcheck.utils.iptables import IPTables
from pjsipcheck.utils.sendmail import SendMail
from pjsipcheck.utils.tools import Tools
from pjsipcheck.utils.attacks import Attacks
from pjsipcheck.utils.db import DB
from pjsipcheck import settings

import sys
import time
import logging


class PJSIPCheck:
    db = DB()
    tools = Tools()
    iptables = IPTables()
    attacks = Attacks()

    def __init__(self):
        self.log = logging.getLogger(settings.LOGGER_NAME)

        self.white_list = settings.CONFIG.get_white_list()
        self.max_attempts = int(settings.CONFIG.get_asterisk('maxAttempts'))

        if settings.CONFIG.get_email('enable'):
            self.mail = SendMail()
        else:
            self.mail = None

        if self.db.init_db() is False:
            sys.exit(-1)

    @staticmethod
    def get_asterisk_log():
        return open(settings.CONFIG.get_asterisk('logFile'), 'r')

    def main(self):
        with self.get_asterisk_log() as asterisk_log:

            while True:
                where = asterisk_log.tell()
                line = asterisk_log.readline()

                if not line:
                    time.sleep(1)
                    asterisk_log.seek(where)

                elif self.attacks.is_sip(line) or self.attacks.is_pjsip(line):

                    ip_address = self.tools.get_ip_address(line)
                    tries = self.db.insert_ip(ip_address)

                    if ip_address in self.white_list:
                        self.log.info("Ignorando IP %s" % ip_address)

                    elif tries >= self.max_attempts:
                        if self.db.block_ip(ip_address):
                            self.iptables.block(ip_address)

                        if self.mail is not None:
                            self.mail.send(ip_address, line)

                    else:
                        continue

                else:
                    continue
