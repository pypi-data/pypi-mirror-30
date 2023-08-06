import sys

import click
from terminaltables import AsciiTable

from ..utils import make_request


@click.group()
def probe():
    """Probes cli."""
    pass


@probe.command('create', short_help='create a new probe.')
@click.option('--description', '-d', help="Description", default=None)
@click.option('--blueprint', '-b', help="Blueprint to use", default=None)
@click.option('--machine', '-m', help="Machine type", default=None)
@click.option('--gpu', help="Add gpu", is_flag=True)
def create(description, blueprint, machine, gpu):
    """Create a new probe."""
    if description is None:
        click.echo("A description is needed.")
        sys.exit(1)

    if blueprint is None:
        click.echo("You need to select a blueprint.")
        sys.exit(1)

    if machine is None:
        click.echo("You need to select a machine type.")
        sys.exit(1)

    data = {
        "description": description,
        "blueprint": blueprint,
        "gpu": gpu,
        "machine_type": machine,
    }
    response = make_request('/api/spawner/probes', method='POST', data=data)

    click.echo(response.json()['message'])


@probe.command()
def list():
    """List your probes."""
    response = make_request('/api/spawner/probes', method='GET')
    probes = response.json()['probes']
    data = []
    data.append(["", "Name", "Url", "Token", "Blueprint",
                 "Status", "Machine/GPU"])
    for index, probe in enumerate(probes):

        gpu = "Y" if probe['specs']['gpu'] else "N"
        data.append([
            index,
            probe['name'],
            probe['url'],
            probe['token'],
            f"{probe['specs']['repository']}/{probe['specs']['blueprint']}",
            probe['status'],
            f"{probe['specs']['machine_type']}/{gpu}",
        ])
    table = AsciiTable(data)
    table.inner_row_border = True
    click.echo(table.table)


@probe.command()
@click.argument('name')
def remove(name):
    """Remove a probe."""
    uri = '/api/spawner/probes/{}'.format(name)
    response = make_request(uri, method='DELETE')
    click.echo(response.json()['message'])


@probe.command()
@click.argument('name')
def logs(name):
    """Get logs of a probe."""
    uri = '/api/spawner/probes/logs/{}'.format(name)
    response = make_request(uri, method='GET')
    logs = response.json()['logs']

    for log in logs:
        click.echo(log)
