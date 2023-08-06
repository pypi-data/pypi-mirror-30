import utils
from azure.storage.file.models import FileProperties, DirectoryProperties
import os
import click

class Get:
    def __init__(self, key, directory='code'):
        self.key = key
        self.directory = directory
        self.origin_path = None

    def recursive_get_file(self, file_service, directory):
        directories = file_service.list_directories_and_files(self.key, directory)
        for file_directory in directories:
            file_or_directory = "%s/%s/%s" % (self.origin_path, directory, file_directory.name)
            if isinstance(file_directory.properties, FileProperties):
                file_service.get_file_to_path(self.key, directory, file_directory.name,
                                              file_or_directory)
                click.echo("created file %s success ." % file_or_directory)
            elif isinstance(file_directory.properties, DirectoryProperties):
                if not os.path.exists(file_or_directory):
                    os.mkdir(file_or_directory)
                    click.echo("created directory %s success ." % file_or_directory)
                self.recursive_get_file(file_service, os.path.join(directory, file_directory.name))

    def get(self, to_path):
        self.origin_path = to_path
        code_path = "%s/%s" % (to_path, self.directory)
        if not os.path.exists(code_path):
            os.makedirs(code_path)
        file_service = utils.init_file_server_by_key(self.key)
        self.recursive_get_file(file_service, self.directory)
