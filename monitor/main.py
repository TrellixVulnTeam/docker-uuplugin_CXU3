import hashlib
import os
import sys
import tarfile
from io import BytesIO
from subprocess import call

import requests

PLUGIN_API = "https://router.uu.163.com/api/plugin"
BASE_PATH = "/uuplugin"
PROGRAM_PATH = os.path.join(BASE_PATH, "uuplugin")
VERSION_PATH = os.path.join(BASE_PATH, "version")


def is_up_to_date(remote_hash: bytes):
    if not os.path.exists(VERSION_PATH):
        return False
    with open(VERSION_PATH, "r") as fp:
        return remote_hash == bytes.fromhex(fp.read())


def set_local_version(remote_hash: bytes):
    with open(VERSION_PATH, "w") as fp:
        fp.write(remote_hash.hex())


def config_network():
    pass


def install_plugin(machine: str):
    metadata = requests.get(PLUGIN_API, params={"type": "openwrt-" + machine}).json()
    remote_hash = bytes.fromhex(metadata["md5"])
    if is_up_to_date(remote_hash):
        return
    compressed = requests.get(metadata["url"]).content
    downloaded_hash = hashlib.md5(compressed).digest()
    if remote_hash != downloaded_hash:
        raise Exception("Install failed")
    with tarfile.open(fileobj=BytesIO(compressed), mode="r:gz") as fp:
        def is_within_directory(directory, target):
            
            abs_directory = os.path.abspath(directory)
            abs_target = os.path.abspath(target)
        
            prefix = os.path.commonprefix([abs_directory, abs_target])
            
            return prefix == abs_directory
        
        def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
        
            for member in tar.getmembers():
                member_path = os.path.join(path, member.name)
                if not is_within_directory(path, member_path):
                    raise Exception("Attempted Path Traversal in Tar File")
        
            tar.extractall(path, members, numeric_owner=numeric_owner) 
            
        
        safe_extract(fp, BASE_PATH)
    set_local_version(remote_hash)


def monitor_plugin():
    while True:
        return_code = call(
            [PROGRAM_PATH], cwd=BASE_PATH, stdout=sys.stdout, stderr=sys.stderr
        )
        if return_code > 0:
            print("Exit Code:", return_code, file=sys.stderr)


def main():
    print("config network")
    config_network()
    print("install plugin")
    install_plugin(os.uname().machine)
    print("monitor plugin")
    monitor_plugin()


if __name__ == "__main__":
    main()
