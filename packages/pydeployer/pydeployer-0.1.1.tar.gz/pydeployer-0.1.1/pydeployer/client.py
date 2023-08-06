from ftplib import FTP

import logging
import json
import os

logger = logging.getLogger(__name__)


class Client:
    def __init__(self, ip, name, pwd):
        self.ip = ip
        self.name = name
        self.ftp = FTP(ip)
        self.ftp.login(name, pwd)

    def deploy(self, info):
        root_dir = self.ftp.pwd()

        print("Deploying project ...")
        print("Remote machine:\t", self.ip)
        print("User name:\t", self.name)

        for key in info:
            for file in info[key]:
                folder = root_dir + "/" + os.path.dirname(file)
                current_dir = self.ftp.pwd()
                change_dir = os.path.relpath(folder, current_dir)

                if change_dir != ".":
                    print("-> Changing working directory to", os.path.dirname(file))
                    self.change_dir(change_dir)

                fn = os.path.basename(file)
                self.ftp.storbinary("STOR " + fn, open(file, "rb"), 1024)
                print("[" + "OK" + "]\t", file)

        self.ftp.close()

        print("... project deployed!")

    def change_dir(self, dir):
        path = os.path.normpath(dir)
        dir_list = path.split(os.sep)

        for sub_dir in dir_list:
            if sub_dir != '..':
                if not self.dir_exists(sub_dir):
                    self.ftp.mkd(sub_dir)
            self.ftp.cwd(sub_dir)

    def move_up(self):
        self.ftp.cwd("../")

    def dir_exists(self, dir):
        file_list = []
        self.ftp.retrlines('LIST', file_list.append)
        for f in file_list:
            if f.split()[-1] == dir and f.upper().startswith('D'):
                return True
        return False
