from api import Api
from azure.storage.file import FileService
import logging
import os
from netifaces import interfaces, ifaddresses, AF_INET
import socket
from json import load
from urllib2 import urlopen
from gpuinfo.nvidia import get_gpus
import click


def init_environment():
    os.system('curl https://public-packages.oss-cn-beijing.aliyuncs.com/install_nvidia_docker.sh|sh -')


def init_file_server_by_key(key):
    config = Api(key=key).get_config_by_key().get('data')

    file_service = FileService(account_name=config.get('account_name'),
                               account_key=config.get('account_key'),
                               endpoint_suffix=config.get('endpoint_suffix'))

    logging.basicConfig(format='%(asctime)s %(name)-20s %(levelname)-5s %(message)s', level=logging.INFO)
    logger = logging.getLogger('azure.storage')
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s %(name)-20s %(levelname)-5s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    return file_service


def get_folder_name_from_path(path):
    return os.path.basename(path)


def listdir(path, list_name):
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        if os.path.isdir(file_path):
            listdir(file_path, list_name)
        else:
            list_name.append(file_path)


def ip4_addresses():
    ip_list = []
    for interface in interfaces():
        for link in ifaddresses(interface).get(AF_INET, ()):
            ip_list.append(link['addr'])
    return ip_list


def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


def get_public_ip():
    return load(urlopen('http://jsonip.com'))['ip']


def is_empty(key):
    return key == '' or key is None


def get_device_info():
    gpus = []
    try:
        for gpu in get_gpus():
            gpus.append({
                "Name": gpu.get('name'),
                "Memory": gpu.get('total_memory')
            })
    except:
        click.echo("get gpu information error ")
    return {
        "hostname": socket.gethostname(),
        "ip_address": get_host_ip(),
        "gpu": gpus,
        "public_ip": get_public_ip()
    }
