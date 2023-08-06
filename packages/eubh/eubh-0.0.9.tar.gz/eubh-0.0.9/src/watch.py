from apscheduler.schedulers.background import BlockingScheduler
import docker
import status
import utils
from uuid import getnode as get_mac
import api
import get
import os
import put
from click import echo
from thread import start_new_thread


def clean_file():
    echo('remove /root/code and /root/result')
    os.popen('rm -rf /root/code result')
    echo('remove files successful.')


def create_directories():
    os.makedirs('/root/code')
    os.makedirs('/root/result')


def cat_logs_in_background(container):
    container_id = container.id
    for line in container.logs(stream=True):
        with open('/root/result/%s.log' % container_id, 'a') as f:
            f.writelines(line)
            f.close()


class Watch:
    def __init__(self, time):
        self.time = time
        self.key = None
        self.api = api.Api()
        self.docker_client = docker.from_env()

    def clean_docker(self):
        client = self.docker_client
        for container in client.containers.list():
            container.stop()

    def run_cmd_and_upload_result(self, pivot):
        cmd = pivot.get('cmd')
        if not utils.is_empty(cmd):
            cmd_result_out_put = os.popen(cmd)
            cmd_result_out_put_string = cmd_result_out_put.read()
            self.api.project_machine_update_cmd({"id": pivot.get('id'), "result": cmd_result_out_put_string})
            cmd_result_out_put.close()

    def upload_machine_information(self):
        client = self.docker_client
        current_status = status.Status.IDLE.value

        client_containers_count = len(client.containers.list())
        if client_containers_count == 0:
            if not utils.is_empty(self.key):
                current_status = status.Status.COMPLETE.value
                put.Put(self.key, 'result').put('/root/result', True)
        else:
            current_status = status.Status.IDLE.value

        if client_containers_count > 0:
            current_status = status.Status.RUNNING.value

        data = utils.get_device_info()
        data['status_info'] = {
            'key': self.key,
            'status': current_status
        }
        data['mac'] = "machine_%s" % get_mac()
        response = self.api.upload_machine_and_get_task(data)

        print(data, response)

        if type(response) is not list:
            option = response.get('option')
            project = response.get('project')
            pivot = response.get('pivot')

            key = None
            if project is not None:
                key = project.get('key')

            if not utils.is_empty(key):
                if option == 'init':
                    clean_file()
                    create_directories()
                    get.Get(key).get('/root')
                    self.key = key
                    self.run_cmd_and_upload_result(pivot)
                    for container in client.containers.list():
                        try:
                            start_new_thread(cat_logs_in_background(container))
                        except:
                            echo('The container(%s) has been closed' % container.id)

                elif option == 'cmd':
                    self.run_cmd_and_upload_result(pivot)

            if option == 'clean':
                self.clean_docker()
                clean_file()
                self.key = ''

    def watch(self):
        scheduler = BlockingScheduler()
        scheduler.add_job(self.upload_machine_information, 'interval', seconds=self.time, max_instances=5)
        try:
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            scheduler.shutdown()
