# -*- coding: utf-8 -*-

import click

from clusterone import config


@click.command()
@click.pass_obj
@click.argument('key', type=str)
@click.argument('value', type=str)
def command(context, key, value):
    """
    Configure the CLI. Config is persistant between CLI invocations.

    The contents are stored in justrc.json file.

    Avaible values:
    - Endpoint - the URL to Clusterone
    """

    setattr(config, key, value)
