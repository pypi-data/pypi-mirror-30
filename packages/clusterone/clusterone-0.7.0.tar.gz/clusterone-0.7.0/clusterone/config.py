import py
import click
import json

import os
HOME_DIR = os.getcwd()

#TODO: Redo this to sesion / sth else
#TODO: Maybe as a context manager
class Config(dict):
    def __init__(self, *args, **kwargs):
        self.config = py.path.local(
            click.get_app_dir('clusterone')).join('config.json')

        self.home = HOME_DIR

        # retry behaviour, used when aquiring tport remote repo
        self.retry_count = 60 # times
        self.retry_interval = 1 # seconds

        # events watch behaviour, used when dispalying events
        self.events_refresh_rate = 1 # seconds

        super(Config, self).__init__(*args, **kwargs)


    def load(self):
        """load the JSON config file from disk"""
        try:
            self.update(json.loads(self.config.read()))
            # logger.info('Config file loaded.')
        except py.error.ENOENT:
            # logger.error('Cannot Load Config File')
            pass

    def save(self):
        #TODO: Is this necessary?
        self.config.ensure()
        with self.config.open('w', encoding='utf-8') as dumpfile:
            dumpfile.write(json.dumps(self))

    def delete(self):
        try:
            self.config.remove()
        except py.error.ENOENT:
            # no file -> deletion done
            pass

