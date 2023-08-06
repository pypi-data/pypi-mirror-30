import click

from fogstone.app import create_app


@click.group()
def cli(): pass


@cli.command(name="run", help="Run server")
def run():
    create_app().run()
