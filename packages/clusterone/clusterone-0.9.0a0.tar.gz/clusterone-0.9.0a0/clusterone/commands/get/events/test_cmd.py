from collections import OrderedDict

from click.testing import CliRunner
from pytest import raises

from clusterone import ClusteroneClient
from clusterone.config import Config
from clusterone.clusterone_cli import cli
from clusterone.commands.get.events import cmd
from clusterone.client_exceptions import SoftInternalServiceError


import pytest

ORIGINAL_OUTPUT_EVENTS = cmd.output_events
ORIGINAL_EXTRACT_DATA = cmd.extract_data_from_events

def test_one_output(mocker):
    mocker.patch.object(ClusteroneClient, '__init__', autospec=True, return_value=None)
    cmd.time = mocker.Mock()
    cmd.output_events = mocker.Mock()

    CliRunner().invoke(cli, ['get', 'events', '--once'])

    assert cmd.output_events.call_count == 1


def test_forever_output(mocker):

    cmd.clear = mocker.Mock()
    cmd.output_events = mocker.Mock()

    # StopIteration is a hack used to test an infinite while loop
    # It it handled internally by the loop and breaks out of it
    cmd.sleep = mocker.Mock(side_effect=StopIteration)

    CliRunner().invoke(cli, ['get', 'events'])

    cmd.output_events.assert_called_with(mocker.ANY, before_printing=cmd.clear)
    assert cmd.sleep.called


def test_output_events(mocker):
    mocker.patch.object(ClusteroneClient, '__init__', autospec=True, return_value=None)
    ClusteroneClient.get_events = mocker.Mock(return_value="retval_from_get_events")
    cmd.extract_data_from_events = mocker.Mock(return_value="retval_from_extract_data")
    cmd.make_table = mocker.Mock(return_value="Example table string")
    cmd.echo = mocker.Mock()

    test_action = mocker.Mock()

    # resetting a mock like a n00b :c
    cmd.output_events = ORIGINAL_OUTPUT_EVENTS

    cmd.output_events(ClusteroneClient(), before_printing=test_action)

    assert ClusteroneClient.get_events.called
    cmd.extract_data_from_events.assert_called_with("retval_from_get_events")
    cmd.make_table.assert_called_with("retval_from_extract_data", header=cmd.HEADER)
    cmd.echo.assert_called_with("Example table string")
    assert test_action.called

def test_extracting_data(mocker):
    cmd.extract_data_from_events = ORIGINAL_EXTRACT_DATA

    assert cmd.extract_data_from_events([
    OrderedDict([
        ('id', 458091),
        ('repository', '0748b269-94f9-48ee-bc84-542c3801acea'),
        ('job', 'd4ad4c61-87b5-4389-855b-02895fa1d369'),
        ('job_run', 'af3da7db-94bf-41b9-acaa-64f175bcae2c'),
        ('job_name', 'muddy-fog-901'),
        ('repository_name', 'clusterone-test-mnist'),
        ('event_level', 40),
        ('event_level_display', 'Error'),
        ('event_type', 'TERMINATE_ERROR'),
        ('event_type_display', 'Terminate the job on error'),
        ('event_content', 'Job terminated due to code error'),
        ('created_at', '2018-03-14T15:36:33.218301Z'),
        ('created_by', None),
        ]),
    OrderedDict([
        ('id', 458090),
        ('repository', '0748b269-94f9-48ee-bc84-542c3801acea'),
        ('job', 'd4ad4c61-87b5-4389-855b-02895fa1d369'),
        ('job_run', 'af3da7db-94bf-41b9-acaa-64f175bcae2c'),
        ('job_name', 'muddy-fog-901'),
        ('repository_name', 'clusterone-test-mnist'),
        ('event_level', 25),
        ('event_level_display', 'Success'),
        ('event_type', 'DELETE_JOB'),
        ('event_type_display', 'Delete Job Command'),
        ('event_content',
         'Job d4ad4c61-87b5-4389-855b-02895fa1d369 Deleted Successfully'
         ),
        ('created_at', '2018-03-14T15:36:32.394262Z'),
        ('created_by', None),
        ]),
    ]) == [
    ['2018-03-14T15:36:33', 'muddy-fog-901', 'af3da7db-94bf-41b9-acaa-64f175bcae2c', 'Error',
     'Terminate the job on error'],
    ['2018-03-14T15:36:32', 'muddy-fog-901', 'af3da7db-94bf-41b9-acaa-64f175bcae2c', 'Success',
     'Delete Job Command'],
    ]

def test_empty_event_list_error(mocker):
    mocker.patch.object(ClusteroneClient, '__init__', autospec=True, return_value=None)
    ClusteroneClient.get_events = mocker.Mock(return_value=[])

    with raises(SoftInternalServiceError):
        cmd.output_events(ClusteroneClient())
