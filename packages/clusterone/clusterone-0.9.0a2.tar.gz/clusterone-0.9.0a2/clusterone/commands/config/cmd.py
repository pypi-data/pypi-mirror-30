# -*- coding: utf-8 -*-

import click

from clusterone._config import Config


@click.command()
@click.pass_obj
@click.option(
    '--endpoint',
    required=True,
    help="The endpoint for the CLI to use",
    #type=
    #TODO: Look for http URL type
    #TODO: Validate if this return schema
    )
def command(context, *args, **kwargs):
    """
    Allows to configure the CLI
    """

    #TODO: append all avaible values with explanation?
    #TODO: Add better syntax support - see Jira ticket

    config = Config()

    key = "endpoint"
    value = kwargs['endpoint']

    config.set(key, value)
