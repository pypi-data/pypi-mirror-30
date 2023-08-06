import json
import sys

import click
from requests_toolbelt.multipart.encoder import (
    MultipartEncoder,
)
from terminaltables import AsciiTable

from ..utils import make_request
from .utils import create_tar_from_folder


@click.group()
def blueprint():
    """Blueprints cli."""
    pass


@blueprint.command('create', short_help='create a new blueprint.')
@click.option('--base', '-b', help="Base image", default=None)
@click.option('--description', '-d', help="Description", default=None)
@click.option('--name', '-n', help="Name for the new blueprint", default=None)
@click.option('--tag', '-t', help="Tag", default=None)
@click.option('--cargo', '-c', help="Name of the cargo,", default=None)
def create(base, description, name, tag, cargo):
    """Create a new probe."""
    if base is None:
        click.echo("A base blueprint is needed.")
        sys.exit(1)

    if description is None:
        click.echo("You need to specify a description.")
        sys.exit(1)

    if name is None:
        click.echo("You need to specify a name for your blueprint.")
        sys.exit(1)

    if tag is None:
        click.echo("You need to specify a tag (name:tag) for your blueprint.")
        sys.exit(1)

    data = {
        "description": description,
        "base_image": base,
        "name": name,
        "tag": tag
    }

    if cargo:
        data['cargo'] = cargo
        uri = '/api/spawner/blueprints/create_from_cargo'
        response = make_request(uri, method='POST', data=data)

    else:
        with create_tar_from_folder() as fp:
            m = MultipartEncoder(
                fields={
                    'json': ('json', json.dumps(data), "application/json"),
                    'file': ('blueprint.tar.gz', fp, "application/gzip")
                }
            )

            response = make_request('/api/spawner/blueprints/create_from_folder',
                                    files=m, method='POST', headers={'Content-Type': m.content_type})

    click.echo(response.json()['message'])


@blueprint.command()
def list():
    """List your probes."""
    response = make_request('/api/spawner/blueprints', method='GET')
    blueprints = response.json()['blueprints']

    data = []
    data.append([
        "",
        "UUID",
        "Blueprint",
        "Description",
        "Public",
    ])
    for index, blueprint in enumerate(blueprints):
        image = "{}/{}:{}".format(blueprint['repository'],
                                  blueprint['name'], blueprint['tag'])
        data.append([
            index,
            blueprint['uuid'],
            image,
            blueprint['description'],
            blueprint['public']]
        )
    table = AsciiTable(data)
    table.inner_row_border = True
    click.echo(table.table)


@blueprint.command()
@click.argument('name')
def remove(name):
    """Remove a blueprint."""
    data = {
        "reference": name,
    }
    uri = '/api/spawner/blueprints'
    response = make_request(uri, method='DELETE', data=data)

    click.echo(response.json()['message'])
