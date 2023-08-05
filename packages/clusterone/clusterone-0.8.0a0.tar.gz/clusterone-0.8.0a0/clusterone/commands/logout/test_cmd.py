from click.testing import CliRunner

from clusterone import ClusteroneClient
from clusterone.config import Config
from clusterone.clusterone_cli import cli

from clusterone.commands.logout import cmd


def test_local_session_deletion(mocker):
    """
    No credentials are left on user's machine
    """

    mocker.patch.object(ClusteroneClient, '__init__', autospec=True, return_value=None)
    mocker.patch.object(Config, 'delete', autospec=True, return_value=None)

    cmd.is_latest_version = mocker.Mock(return_value=False)

    CliRunner().invoke(cli, ['logout'])

    assert Config.delete.called
