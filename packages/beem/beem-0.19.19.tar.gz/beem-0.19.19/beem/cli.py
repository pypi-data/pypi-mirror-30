# This Python file uses the following encoding: utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from builtins import bytes, int, str
from beem.instance import set_shared_steem_instance, shared_steem_instance
from beem.amount import Amount
from beem.account import Account
from beem.steem import Steem
from beem.comment import Comment
from beem.storage import configStorage
from beem.version import version as __version__
from datetime import datetime, timedelta
import pytz
from beembase import operations
from beemgraphenebase.account import PrivateKey, PublicKey
import json
from prettytable import PrettyTable
import math
import random
import logging
import click
click.disable_unicode_literals_warning = True
log = logging.getLogger(__name__)


availableConfigurationKeys = [
    "default_account",
    "default_vote_weight",
    "nodes",
]


@click.group(chain=True)
@click.option(
    '--node', '-n', default="", help="URL for public Steem API")
@click.option(
    '--offline', is_flag=True, default=False, help="Prevent connecting to network")
@click.option(
    '--nobroadcast', '-d', is_flag=True, default=False, help="Do not broadcast")
@click.option(
    '--unsigned', is_flag=True, default=False, help="Nothing will be signed")
@click.option(
    '--blocking', is_flag=True, default=False,
    help="Wait for broadcasted transactions to be included in a block and return full transaction")
@click.option(
    '--bundle', is_flag=True, default=False,
    help="Do not broadcast transactions right away, but allow to bundle operations ")
@click.option(
    '--expiration', '-e', default=30,
    help='Delay in seconds until transactions are supposed to expire(defaults to 60)')
@click.option(
    '--debug', is_flag=True, default=False, help='Enables Debug output')
@click.version_option(version=__version__)
def cli(node, offline, nobroadcast, unsigned, blocking, bundle, expiration, debug):
    stm = Steem(
        node=node,
        nobroadcast=nobroadcast,
        unsigned=unsigned,
        blocking=blocking,
        bundle=bundle,
        expiration=expiration,
        debug=debug
    )
    set_shared_steem_instance(stm)
    pass


@cli.command()
@click.option(
    '--account', '-a', multiple=False, help="Set default account")
@click.option(
    '--weight', '-w', multiple=False, help="Set your default vote weight")
@click.option(
    '--node', '-n', multiple=True, help="Set nodes")
def set(account, weight, node):
    """ Set configuration
    """
    stm = shared_steem_instance()
    if account:
        stm.set_default_account(account)
    if weight:
        configStorage["default_vote_weight"] = weight
    if len(node) > 0:
        nodes = []
        for n in node:
            nodes.append(n)
        configStorage["node"] = nodes


@cli.command()
def config():
    """ Shows local configuration
    """
    stm = shared_steem_instance()
    t = PrettyTable(["Key", "Value"])
    t.align = "l"
    for key in stm.config:
        # hide internal config data
        if key in availableConfigurationKeys:
            t.add_row([key, stm.config[key]])
    for node in stm.config.nodes:
        t.add_row(["node", node])
    t.add_row(["data_dir", stm.config.data_dir])
    print(t)


@cli.command()
@click.option('--password', prompt=True, hide_input=True,
              confirmation_prompt=True)
@click.option(
    '--wipe', is_flag=True, default=False,
    help="Delete old wallet. All wallet data are deleted!")
def createwallet(password, purge):
    """ Create new wallet with password
    """
    stm = shared_steem_instance()
    if purge and click.confirm('Do you want to continue to wipe your Wallet?'):
        stm.wallet.wipe(True)
    stm.wallet.create(password)
    set_shared_steem_instance(stm)


@cli.command()
def walletinfo():
    """ Show info about wallet
    """
    stm = shared_steem_instance()
    t = PrettyTable(["Key", "Value"])
    t.align = "l"
    t.add_row(["created", stm.wallet.created()])
    t.add_row(["locked", stm.wallet.locked()])
    # t.add_row(["getAccounts", str(stm.wallet.getAccounts())])
    # t.add_row(["getPublicKeys", str(stm.wallet.getPublicKeys())])
    print(t)


@cli.command()
@click.option('--password', prompt=True, hide_input=True,
              confirmation_prompt=False)
@click.option('--key')
def addkey(password, key):
    """ Add key to wallet
    """
    stm = shared_steem_instance()
    if not stm.wallet.locked():
        return
    stm.wallet.unlock(password)
    if stm.wallet.locked():
        print("Could not be unlocked!")
    else:
        print("Unlocked!")
        stm.wallet.addPrivateKey(key)
    set_shared_steem_instance(stm)


@cli.command()
def listkeys():
    """ Show stored keys
    """
    stm = shared_steem_instance()
    t = PrettyTable(["Available Key", "Account", "Type"])
    t.align = "l"
    for key in stm.wallet.getPublicKeys():
        if key[0:2] != stm.prefix:
            continue
        account = stm.wallet.getAccount(key)
        if account["name"] is None:
            accountName = ""
            keyType = "Memo"
        else:
            accountName = account["name"]
            keyType = account["type"]
        # keyType = stm.wallet.getKeyType(account, key)
        t.add_row([key, accountName, keyType])
    print(t)


@cli.command()
def listaccounts():
    """Show stored accounts"""
    stm = shared_steem_instance()
    t = PrettyTable(["Name", "Type", "Available Key"])
    t.align = "l"
    for account in stm.wallet.getAccounts():
        t.add_row([
            account["name"] or "n/a", account["type"] or "n/a",
            account["pubkey"]
        ])
    print(t)


@cli.command()
@click.argument('post', nargs=1)
@click.option('--account', '-a')
@click.option('--weight', '-w', default=100.0, help='Vote weight (from 0.1 to 100.0)')
def upvote(post, account, weight):
    """Upvote a post/comment"""
    if not weight:
        weight = configStorage["default_vote_weight"]
    if not account:
        account = configStorage["default_account"]
    post = Comment(post)
    post.upvote(weight, voter=account)


@cli.command()
@click.option('--password', prompt=True, hide_input=True,
              confirmation_prompt=True)
def changewalletpassphrase(password):
    """ Change wallet password
    """
    stm = shared_steem_instance()
    stm.wallet.changePassphrase(password)


@cli.command()
@click.option(
    '--account', '-a', multiple=True)
def balance(account):
    """ Shows balance
    """
    stm = shared_steem_instance()
    if len(account) == 0:
        if "default_account" in stm.config:
            account = [stm.config["default_account"]]
    for name in account:
        a = Account(name, steem_instance=stm)
        print("\n@%s" % a.name)
        t = PrettyTable(["Account", "STEEM", "SBD", "VESTS"])
        t.align = "r"
        t.add_row([
            'Available',
            str(a.balances['available'][0]),
            str(a.balances['available'][1]),
            str(a.balances['available'][2]),
        ])
        t.add_row([
            'Rewards',
            str(a.balances['rewards'][0]),
            str(a.balances['rewards'][1]),
            str(a.balances['rewards'][2]),
        ])
        t.add_row([
            'Savings',
            str(a.balances['savings'][0]),
            str(a.balances['savings'][1]),
            'N/A',
        ])
        t.add_row([
            'TOTAL',
            str(a.balances['total'][0]),
            str(a.balances['total'][1]),
            str(a.balances['total'][2]),
        ])
        print(t)


@cli.command()
@click.argument('objects', nargs=-1)
def info(objects):
    """ Show info
    """
    stm = shared_steem_instance()
    if not objects:
        t = PrettyTable(["Key", "Value"])
        t.align = "l"
        info = stm.get_dynamic_global_properties()
        median_price = stm.get_current_median_history()
        steem_per_mvest = stm.get_steem_per_mvest()
        price = (Amount(median_price["base"]).amount / Amount(
            median_price["quote"]).amount)
        for key in info:
            t.add_row([key, info[key]])
        t.add_row(["steem per mvest", steem_per_mvest])
        t.add_row(["internal price", price])
        print(t.get_string(sortby="Key"))
    for o in objects:
        a = Account(o, steem_instance=stm)
        a.print_info()
        print("\n")


if __name__ == "__main__":
    cli()
