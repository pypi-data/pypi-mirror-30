import logging
import json
import os

logger = logging.getLogger(__name__)
data_extension = {
    'source': ['.py'],
}


def create_deploy():
    deploy = Deploy()
    for key in data_extension:
        deploy.data[key] = []

    _scan_directory(deploy, ".")
    return deploy


def _scan_directory(obj, dir):
    for file in os.listdir(dir):
        if os.path.isdir(dir + "\\" + file):
            _scan_directory(obj, os.path.join(dir, file))

        _, ex = os.path.splitext(file)
        for key in data_extension:
            for ext in data_extension[key]:
                if ext == ex:
                    obj.data[key].append(dir + '\\' + file)
                    print("Adding file: " + dir + '\\' + file)
                else:
                    print("Ignoring file: " + dir + "\\" + file)

        # logger.info("Found file: " + subdir + '\\' + file)


class Deploy:
    def __init__(self):
        self.data = {}

    def to_string(self):
        return json.dumps(self.data, indent=4)
