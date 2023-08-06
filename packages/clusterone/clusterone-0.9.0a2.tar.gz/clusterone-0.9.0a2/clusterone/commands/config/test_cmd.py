from click.testing import CliRunner

from clusterone import ClusteroneClient
from clusterone.config import Config as Session
from clusterone._config import Config
from clusterone.clusterone_cli import cli
from clusterone.commands.config import cmd


def test_passing(mocker):

    mocker.patch.object(ClusteroneClient, '__init__', autospec=True, return_value=None)
    mocker.patch.object(Session, 'save', autospec=True, return_value=None)
    mocker.patch.object(Config, '__init__', autospec=True, return_value=None)

    Config.set = mocker.Mock()

    CliRunner().invoke(cli, [
        'config',
        '--endpoint', 'whatever',
    ])

    Config.set.assert_called_with('endpoint', 'whatever')
