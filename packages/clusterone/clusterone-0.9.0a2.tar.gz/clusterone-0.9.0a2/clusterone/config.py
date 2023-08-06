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
        # TODO: Context manager?
        try:
            self.update(json.loads(self.config.read()))
            # logger.info('Config file loaded.')

        # When failing to parse the file we'd like this not to fail
        # User will login then and rewrite the config
        except (ValueError, py.error.ENOENT) as exception:
            pass

    def save(self):
        #TODO: Is this necessary?
        self.config.ensure()
        with self.config.open('w', encoding='utf-8') as dumpfile:
            try:
                dumpfile.write(json.dumps(self))
            except TypeError:
                # Python 2 compliance - .write() required unicode
                dumpfile.write(json.dumps(self).decode('utf-8'))

    def delete(self):
        try:
            self.config.remove()
        except py.error.ENOENT:
            # no file -> deletion done
            pass

