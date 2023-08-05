from click.testing import CliRunner

from clusterone import ClusteroneClient
from clusterone.config import Config
from clusterone.clusterone_cli import cli

from clusterone.commands.matrix import cmd


def test_opening(mocker):
    """
    Call to click utility for browser controll
    """

    mocker.patch.object(ClusteroneClient, '__init__', autospec=True, return_value=None)
    mocker.patch.object(Config, 'save', autospec=True, return_value=None)
    cmd.MATRIX_URL = "https://dummy/matrix"

    cmd.launch = mocker.Mock()

    CliRunner().invoke(cli, ['matrix'],)

    cmd.launch.assert_called_with("https://dummy/matrix")
