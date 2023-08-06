import requests
import json


class Api:
    def __init__(self, key, base_url='http://www.baidu.com'):
        self.key = key
        self.base_url = base_url

    def get_url(self, url):
        return "%s/%s" % (self.base_url, url)

    def upload_machine_and_get_task(self, data={}):
        return requests.post(self.get_url('project/machine/%s' % (data.get('mac'))), data=json.dumps(data),
                             headers={'Content-Type': 'application/json'}).json()

    def get_config_by_key(self):
        key = self.key
        return {
            "from": {"account_name": "eubtestdownload",
                     "account_key": "OKCVxAo5INdYAa5JmiVA2m1dk6dYStG4JI2lDku8rFqMKTj4qKUq0CrcsFfzDIoGoGEGUsRbQxDxG94IQYNnBw==",
                     "endpoint_suffix": "core.chinacloudapi.cn"},
            "to": {"account_name": "eubtestdownload",
                   "account_key": "OKCVxAo5INdYAa5JmiVA2m1dk6dYStG4JI2lDku8rFqMKTj4qKUq0CrcsFfzDIoGoGEGUsRbQxDxG94IQYNnBw==",
                   "endpoint_suffix": "core.chinacloudapi.cn"}
        }
