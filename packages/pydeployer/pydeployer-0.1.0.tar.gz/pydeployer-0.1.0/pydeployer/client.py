from ftplib import FTP

import logging
import json
import os

logger = logging.getLogger(__name__)


class Client:
    def __init__(self, ip, name, pwd):
        self.ftp = FTP(ip)
        self.ftp.login(name, pwd)

    def deploy(self, info):
        for key in info:
            for file in info[key]:
                print("Deploying: " + file)
                fn = os.path.basename(file)
                self.ftp.storbinary("STOR " + fn, open(file, "rb"), 1024)
        self.ftp.close()
        print("Project deployed to server")
