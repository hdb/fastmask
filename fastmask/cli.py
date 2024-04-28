from fastmask.masked_email import MaskedMailClient
from fastmask.utils import (
    PrettyTable, 
    error_msg, 
    success_msg,
    to_date
)

import click
from datetime import datetime, timezone, timedelta
import os
import re
import pandas as pd

skip_dotenv=os.getenv('SKIP_PYTHONDOTENV', 'False').lower() in ('true', '1', 't')
if not skip_dotenv:
    from dotenv import load_dotenv
    load_dotenv()

EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'


@click.group()
@click.option(
    "--username",
    default=lambda: os.environ.get("FM_USERNAME", ""),
    show_default="FM_USERNAME"
)
@click.option(
    "--token",
    default=lambda: os.environ.get("FM_ME_TOKEN", ""),
    show_default="FM_ME_TOKEN",
)
@click.pass_context
def cli(context, username: str, token: str):
    """Manage Fastmail masked email from the command line"""
    
    context.obj = MaskedMailClient(username=username,token=token)

@cli.command(name='list')
@click.option('--limit', default=None, type=int, help='Limit number of results')
@click.option("--active", 'state', flag_value='active', help="Show only active addresses.")
@click.option("--blocked", 'state', flag_value='blocked', help="Show only blocked addresses.")
@click.option("--unused", 'state', flag_value='unused', help="Show only active + unused addresses.")
@click.option("--used", 'state', flag_value='used', help="Show only used addresses.")
@click.option("--deleted", 'state', flag_value='deleted', help="Show only deleted addresses.")
@click.option('--sort', type=click.Choice(
    ['email', 'createdAt', 'description', 'lastMessageAt', 'forDomain', 'url']
    , case_sensitive=False), help='Field to sort by')
@click.option('--desc/--asc', default=False, help='Sort order')
@click.option('--recent', default=None, type=int, help='Only show items from the past X days')
@click.option('-o', '--out', default=None, type=str, help='Output to csv')
@click.pass_obj
def list_cmd(client: MaskedMailClient, limit: int | None, state: str | None, recent: int | None, sort: str | None, desc: bool, out: str | None):
    """List masked emails associated with account"""
    
    state_map = {
        'active': (lambda x: x['state'] == 'enabled'),
        'blocked': (lambda x: x['state'] == 'disabled'),
        'deleted': (lambda x: x['state'] == 'deleted'),
        'unused': (lambda x: x['lastMessageAt'] is None and x['state'] == 'enabled'),
        'used': (lambda x: x['lastMessageAt'] is not None),
        None: (lambda x: x)
    }

    if recent is not None:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        recent_filter = (lambda x: (now - to_date(x['createdAt'])) < timedelta(days=recent))
    else:
        recent_filter = (lambda x: x)

    filters = (lambda x: state_map[state](x) and recent_filter(x))

    results = client.get(filters=filters, limit=limit, sort_by=sort, sort_order='desc' if desc else 'asc')
    if out is not None:
        pd.DataFrame(results).to_csv(out, index=False)
    else:
        PrettyTable(results, title=f'Masked Emails {client.account_id}').out()

@cli.command()
@click.argument('query', default='')
@click.option('--blank', is_flag=True)
@click.option('--field', '-f', 'fields', multiple=True, default=['email', 'description'])
@click.option('--limit', default=None, type=int, help='Limit number of results')
@click.option('-o', '--out', default=None, type=str, help='Output to csv')
@click.pass_obj
def search(client: MaskedMailClient, query: str, limit: int, fields: list[str], blank: bool, out: str | None):
    """Search for masked emails"""
    
    if blank:
        results = client.get(filters=(lambda x: x['description'] == ''), limit=limit)
    elif len(query)==0:
        error_msg('No query provided. Did you mean to use \'fastmask search --blank\'?')
    else:
        results = client.search(query=query, fields=fields)

    if out is not None:
        pd.DataFrame(results).to_csv(out, index=False)
    else:
        PrettyTable(results, title=f'Search results for "{query if query is not None else ""}"').out()

@cli.command()
@click.argument('description', default='')
@click.option('--url', type=str)
@click.option('--domain', default='', type=str)
@click.option('--pending', is_flag=True, default=False)
@click.pass_obj
def new(client: MaskedMailClient, description: str, url: str, domain: str, pending: bool):
    """Create a new masked email"""
    
    response = client.new(
        description=description,
        url=url,
        domain=domain,
        state='enabled' if not pending else 'pending'
    )

    try:
        result = [v for k,v in response[1]["created"].items()][0]
        desc_str = f'for "{description}" ' if len(description)>0 else ''
        msg = f'Successfully added email {result["email"]} {desc_str}(id: {result["id"]})'
        success_msg(msg)

    except Exception as e:
        error_msg(e)

@click.pass_obj
def update(client: MaskedMailClient, id_: str, changes: dict):
    """Update a masked email. Called by edit, activate, block, delete"""
    
    def get_masked_email_id(id_):
        if id_.startswith('masked-') and id_[7:].isnumeric():
            result = client.get(ids=[id_])
        elif id_.isnumeric():
            result = client.get(ids=[f'masked-{id_}'])
        elif re.match(EMAIL_PATTERN, id_):
            result = client.get(filters=(lambda x: x['email'] == id_))
        else:
            result = client.get(filters=(lambda x: x['description'].lower() == id_))

        if len(result)>0:
            return result[0]['id']
        else:
            error_msg(f'Unable to find Masked Email "{id_}"')

    masked_email_id = get_masked_email_id(id_)

    changes = {k:v for k,v in changes.items() if v is not None}

    if len(changes)<1:
        error_msg('Specify fields to update')

    response = client.update(masked_id=masked_email_id, changes=changes)

    return response

@cli.command()
@click.argument('id_', required=True)
@click.option('--description', type=str)
@click.option('--url', type=str)
@click.option('--domain', type=str)
@click.pass_obj
def edit(client: MaskedMailClient, id_: str, description: str, url: str | None, domain: str | None):
    """Edit information associated with a masked email"""
    
    changes = {
        'description': description,
        'url': url,
        'forDomain': domain,
    }

    response = update(id_=id_, changes=changes)

    try:
        msg = f'Successfully edited email {[k for k,v in response[1]["updated"].items()][0]}'
        success_msg(msg)

    except Exception as e:
        error_msg(e)

@cli.command()
@click.argument('id_', required=True)
@click.pass_obj
def activate(client: MaskedMailClient, id_: str):
    """Set state of masked email to Active"""

    response = update(id_=id_, changes={'state': 'enabled'})
    try:
        msg = f'Successfully activated email {[k for k,v in response[1]["updated"].items()][0]}'
        success_msg(msg)

    except Exception as e:
        error_msg(e)

@cli.command()
@click.argument('id_', required=True)
@click.pass_obj
def block(client: MaskedMailClient, id_: str):
    """Set state of masked email to Blocked"""

    response = update(id_=id_, changes={'state': 'disabled'})

    try:
        msg = f'Successfully blocked email {[k for k,v in response[1]["updated"].items()][0]}'
        success_msg(msg)

    except Exception as e:
        error_msg(e)

@cli.command()
@click.argument('id_', required=True)
@click.pass_obj
def delete(client: MaskedMailClient, id_: str):
    """Delete masked email"""

    response = update(id_=id_, changes={'state': 'deleted'})

    try:
        msg = f'Successfully deleted email {[k for k,v in response[1]["updated"].items()][0]}'
        success_msg(msg)

    except Exception as e:
        error_msg(e)
