from pydeployer import __version__
from pydeployer import security
from pydeployer import client
from pydeployer import deploy
from pydeployer import user

import logging
import argparse
import json
import sys
import os

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description='A very small python project deployer'
    )
    parser.add_argument(
        'root', help='root folder of the Python project'
    )
    parser.add_argument(
        '-r', '--remove',
        help='remove the pydeployer data file'
    )
    parser.add_argument(
        '-v', '--version', action='version',
        version='%(prog)s ' + __version__,
    )
    args = parser.parse_args()

    if not args.root:
        args.print_help()
        sys.exit(1)

    try:
        deploy_project(args.root)
    except KeyboardInterrupt:
        print("Program aborted by user")
        sys.exit(1)


def deploy_project(root):
    user_fn = os.path.join(root, 'user.dat')
    user_fh, user_obj = read_data_file(user_fn)

    deploy_fn = os.path.join(root, 'deploy.json')
    deploy_fh, deploy_obj = read_project_file(deploy_fn)

    ftp_client = client.Client(
        user_obj.data['ip'],
        user_obj.data['name'],
        user_obj.data['pwd']
    )
    ftp_client.deploy(deploy_obj)

    user_fh.close()
    deploy_fh.close()


def read_data_file(fn):
    try:
        fh = open(fn, 'r')
        data = security.read_file(fh)
        user_obj = user.parse_user_file(data)

        return fh, user_obj

    except FileNotFoundError:
        logger.warning("User data file not found. Creating one.")
        return create_data_file(fn)


def create_data_file(fn):
    fh = open(fn, 'w')
    user_obj = user.create_user()
    fh.write(user_obj.to_string())

    return fh, user_obj


def read_project_file(fn):
    try:
        fh = open(fn, 'r')
        return fh, json.load(fh)

    except FileNotFoundError:
        logger.warning("Deploy file not found. Creating one.")
        return create_project_file(fn)


def create_project_file(fn):
    fh = open(fn, 'w')
    deploy_obj = deploy.create_deploy()
    fh.write(deploy_obj.to_string())
    return fh, deploy_obj.data


if __name__ == '__main__':
    main()