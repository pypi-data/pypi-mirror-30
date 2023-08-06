from apscheduler.schedulers.background import BlockingScheduler
import docker
import status
import utils
from uuid import getnode as get_mac
import api


class Watch:
    def __init__(self, time):
        self.time = time
        self.key = None
        self.api = api.Api(None, "http://eubchain.local")

    def upload_machine_information(self):
        client = docker.from_env()
        current_status = status.Status.IDLE.value
        if len(client.containers()) > 0:
            current_status = status.Status.RUNNING.value
        data = utils.get_device_info()
        data['status_info'] = {
            'key': self.key,
            'status': current_status
        }
        data['mac'] = get_mac()
        response = self.api.upload_machine_and_get_task(data)
        print(data, response)

    def watch(self):
        scheduler = BlockingScheduler()
        scheduler.add_job(self.upload_machine_information, 'interval', seconds=self.time)
        scheduler.start()
