import click

from recodex.api import ApiClient
from recodex.config import UserContext
from recodex.decorators import pass_user_context, pass_api_client


@click.group()
def cli():
    """
    Tools for user manipulation
    """


@cli.command()
@click.argument("search_string")
@pass_user_context
@pass_api_client
def search(api: ApiClient, context: UserContext, search_string):
    """
    Search for a user
    """

    instance_id = api.get_user(context.user_id)["privateData"]["instanceId"]

    for user in api.search_users(instance_id, search_string):
        click.echo("{} {}".format(user["fullName"], user["id"]))
