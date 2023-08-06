from clusterone import ClusteroneClient

#TODO: OMG REFACTOR THIS!!!!
from clusterone.config import Config
config = Config()
config.load()

CLIENT_INSTANCE = ClusteroneClient(token=config.get('token'), username=config.get('username'))
