# -*- coding: utf-8 -*-

import click
from click import launch
from clusterone.clusterone_client import MATRIX_URL


@click.command()
@click.pass_obj
def command(context):
    """
    Open Matrix in your browser
    """

    #TODO: What if operating in headless mode? What does happens then?
    launch(MATRIX_URL)
