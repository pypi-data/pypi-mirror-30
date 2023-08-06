# -*- coding: utf-8 -*-

import click

from clusterone import config


@click.command()
@click.pass_obj
@click.argument('key', type=str)
@click.argument('value', type=str)
def command(context, key, value):
    """
    Configure the CLI. Config is persistent.

    Available values:
    - Endpoint - the URL to Clusterone service
    """

    setattr(config, key, value)
