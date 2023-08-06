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

    _scan_directory(deploy, ".", ".")
    return deploy


def _scan_directory(obj, dir, subdir):
    for file in os.listdir(dir):
        if os.path.isdir(file):
            _scan_directory(obj, file, file)

        _, ex = os.path.splitext(file)
        for key in data_extension:
            for ext in data_extension[key]:
                if ext == ex:
                    obj.data[key].append(subdir + '\\' + file)
                    print("Adding file: " + subdir + '\\' + file)
                else:
                    print("Ignoring file: " + subdir + "\\" + file)

        # logger.info("Found file: " + subdir + '\\' + file)


class Deploy:
    def __init__(self):
        self.data = {}

    def to_string(self):
        return json.dumps(self.data, indent=4)
