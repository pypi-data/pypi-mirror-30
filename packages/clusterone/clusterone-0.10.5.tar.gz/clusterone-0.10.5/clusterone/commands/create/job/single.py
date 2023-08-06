import click

from clusterone import client
from clusterone.utilities import Choice
from .base_cmd import job_base_options, base


@job_base_options
@click.option(
    '--instance-type',
    type=Choice(client.instance_types_slugs),
    default="t2.small",
    help="Type of single instance to run.")
def command(context, custom_arguments, **kwargs):
    """
    Creates a single-node job.
    """

    client = context.client
    job_sessionuration = base(context, kwargs, module_arguments=custom_arguments)

    job_sessionuration['parameters']['mode'] = "single"
    job_sessionuration['parameters']['workers'] = \
    {
        'slug': kwargs['instance_type'],
        'replicas': 1
    }

    client.create_job(
        job_sessionuration['meta']['name'],
        description=job_sessionuration['meta']['description'],
        parameters=job_sessionuration['parameters'],
        )
