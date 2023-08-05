# This Python file uses the following encoding: utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from builtins import bytes, int, str
import pytz
import json
from datetime import datetime, timedelta
import math
import random
import logging
from beem.instance import shared_steem_instance
from .exceptions import AccountDoesNotExistsException
from .blockchainobject import BlockchainObject
from .blockchain import Blockchain
from .utils import formatTimeString, formatTimedelta, remove_from_dict
from beem.amount import Amount
from beembase import operations
from beemgraphenebase.account import PrivateKey, PublicKey
from beemgraphenebase.py23 import bytes_types, integer_types, string_types, text_type
log = logging.getLogger(__name__)


class Account(BlockchainObject):
    """ This class allows to easily access Account data

        :param str account_name: Name of the account
        :param beem.steem.Steem steem_instance: Steem
               instance
        :param bool lazy: Use lazy loading
        :param bool full: Obtain all account data including orders, positions,
               etc.
        :returns: Account data
        :rtype: dictionary
        :raises beem.exceptions.AccountDoesNotExistsException: if account
                does not exist

        Instances of this class are dictionaries that come with additional
        methods (see below) that allow dealing with an account and it's
        corresponding functions.

        .. code-block:: python

            from beem.account import Account
            account = Account("test")
            print(account)
            print(account.balances)

        .. note:: This class comes with its own caching function to reduce the
                  load on the API server. Instances of this class can be
                  refreshed with ``Account.refresh()``.

    """

    type_id = 2

    def __init__(
        self,
        account,
        full=True,
        lazy=False,
        steem_instance=None
    ):
        """Initilize an account

        :param str account: Name of the account
        :param beem.steem.Steem steem_instance: Steem
               instance
        :param bool lazy: Use lazy loading
        :param bool full: Obtain all account data including orders, positions,
               etc.
        """
        self.full = full
        super(Account, self).__init__(
            account,
            lazy=lazy,
            full=full,
            id_item="name",
            steem_instance=steem_instance
        )

    def refresh(self):
        """ Refresh/Obtain an account's data from the API server
        """
        if self.steem.rpc.get_use_appbase():
                account = self.steem.rpc.find_accounts({'accounts': [self.identifier]}, api="database")
        else:
            if self.full:
                account = self.steem.rpc.get_accounts(
                    [self.identifier])
            else:
                account = self.steem.rpc.lookup_account_names(
                    [self.identifier])
        if self.steem.rpc.get_use_appbase():
            account = account["accounts"]
        if not account:
            raise AccountDoesNotExistsException(self.identifier)
        else:
            account = account[0]
        if not account:
            raise AccountDoesNotExistsException(self.identifier)
        self.identifier = account["name"]
        # Parse Amounts
        amounts = [
            "balance",
            "savings_balance",
            "sbd_balance",
            "savings_sbd_balance",
            "reward_sbd_balance",
            "reward_steem_balance",
            "reward_vesting_balance",
            "reward_vesting_steem",
            "vesting_shares",
            "delegated_vesting_shares",
            "received_vesting_shares"
        ]
        for p in amounts:
            if p in account and isinstance(account.get(p), (string_types, list)):
                account[p] = Amount(account[p], steem_instance=self.steem)
        self.steem.refresh_data()

        super(Account, self).__init__(account, id_item="name", steem_instance=self.steem)

    def getSimilarAccountNames(self, limit=5):
        """ Returns limit similar accounts with name as array
        """
        if self.steem.rpc.get_use_appbase():
            account = self.steem.rpc.list_accounts({'start': self.name, 'limit': limit}, api="database")
            if account:
                return account["accounts"]
        else:
            return self.steem.rpc.lookup_accounts(self.name, limit)

    @property
    def name(self):
        """ Returns the account name
        """
        return self["name"]

    @property
    def profile(self):
        """ Returns the account profile
        """
        return json.loads(self["json_metadata"])["profile"]

    @property
    def rep(self):
        """ Returns the account reputation
        """
        return self.get_reputation()

    @property
    def sp(self):
        return self.get_steem_power()

    @property
    def vp(self):
        return self.get_voting_power()

    def print_info(self, force_refresh=False, return_str=False):
        """ Prints import information about the account
        """
        if force_refresh:
            self.refresh()
            self.steem.refresh_data(True)
        ret = self.name + " (%.2f) " % (self.rep)
        ret += "%.2f %%, full in %s" % (self.get_voting_power(), self.get_recharge_time_str())
        ret += " VP = %.2f $\n" % (self.get_voting_value_SBD())
        ret += "%.2f SP, " % (self.get_steem_power())
        ret += "%.3f, %.3f" % (self.balances["available"][0], self.balances["available"][1])
        bandwidth = self.get_bandwidth()
        if bandwidth["allocated"] > 0:
            ret += "\n"
            ret += "Remaining Bandwidth: %.2f %%" % (100 - bandwidth["used"] / bandwidth["allocated"] * 100)
            ret += " (%.0f kb of %.0f mb)" % (bandwidth["used"] / 1024, bandwidth["allocated"] / 1024 / 1024)
        if return_str:
            return ret
        print(ret)

    def get_reputation(self):
        """ Returns the account reputation
        """
        if self.steem.rpc.get_use_appbase():
            rep = self.steem.rpc.get_account_reputations({'account_lower_bound': self["name"], 'limit': 1}, api="follow")['reputations']
            if len(rep) > 0:
                rep = int(rep[0]['reputation'])
        else:
            rep = int(self['reputation'])
        if rep == 0:
            return 25.
        score = max([math.log10(abs(rep)) - 9, 0])
        if rep < 0:
            score *= -1
        score = (score * 9.) + 25.
        return score

    def get_voting_power(self, with_regeneration=True):
        """ Returns the account voting power
        """
        if with_regeneration:
            utc = pytz.timezone('UTC')
            diff_in_seconds = (utc.localize(datetime.utcnow()) - formatTimeString(self["last_vote_time"])).total_seconds()
            regenerated_vp = diff_in_seconds * 10000 / 86400 / 5 / 100
        else:
            regenerated_vp = 0
        total_vp = (self["voting_power"] / 100 + regenerated_vp)
        if total_vp > 100:
            return 100
        if total_vp < 0:
            return 0
        return total_vp

    def get_steem_power(self, onlyOwnSP=False):
        """ Returns the account steem power
        """
        vests = (self["vesting_shares"])
        if not onlyOwnSP and "delegated_vesting_shares" in self and "received_vesting_shares" in self:
            vests = vests - (self["delegated_vesting_shares"]) + (self["received_vesting_shares"])
        return self.steem.vests_to_sp(vests)

    def get_voting_value_SBD(self, voting_weight=100, voting_power=None, steem_power=None):
        """ Returns the account voting value in SBD
        """
        if voting_power is None:
            voting_power = self.get_voting_power()
        if steem_power is None:
            sp = self.get_steem_power()
        else:
            sp = steem_power

        VoteValue = self.steem.sp_to_sbd(sp, voting_power=voting_power * 100, vote_pct=voting_weight * 100)
        return VoteValue

    def get_recharge_time_str(self, voting_power_goal=100):
        """ Returns the account recharge time
        """
        remainingTime = self.get_recharge_timedelta(voting_power_goal=voting_power_goal)
        return formatTimedelta(remainingTime)

    def get_recharge_timedelta(self, voting_power_goal=100):
        """ Returns the account voting power recharge time as timedelta object
        """
        missing_vp = voting_power_goal - self.get_voting_power()
        if missing_vp < 0:
            return 0
        recharge_seconds = missing_vp * 100 * 5 * 86400 / 10000
        return timedelta(seconds=recharge_seconds)

    def get_recharge_time(self, voting_power_goal=100):
        """ Returns the account voting power recharge time in minutes
        """
        utc = pytz.timezone('UTC')
        return utc.localize(datetime.utcnow()) + self.get_recharge_timedelta(voting_power_goal)

    def get_feed(self, entryId=0, limit=100, raw_data=False, account=None):
        if account is None:
            account = self["name"]
        self.steem.register_apis(["follow"])
        if raw_data and self.steem.rpc.get_use_appbase():
            return [
                c for c in self.steem.rpc.get_feed({'account': account, 'start_entry_id': entryId, 'limit': limit}, api='follow')["feed"]
            ]
        elif raw_data and not self.steem.rpc.get_use_appbase():
            return [
                c for c in self.steem.rpc.get_feed(account, entryId, limit, api='follow')
            ]
        elif not raw_data and self.steem.rpc.get_use_appbase():
            from .comment import Comment
            return [
                Comment(c['comment'], steem_instance=self.steem) for c in self.steem.rpc.get_feed({'account': account, 'start_entry_id': entryId, 'limit': limit}, api='follow')["feed"]
            ]
        else:
            from .comment import Comment
            return [
                Comment(c['comment'], steem_instance=self.steem) for c in self.steem.rpc.get_feed(account, entryId, limit, api='follow')
            ]

    def get_blog_entries(self, entryId=0, limit=100, raw_data=False, account=None):
        if account is None:
            account = self["name"]
        self.steem.register_apis(["follow"])
        if raw_data and self.steem.rpc.get_use_appbase():
            return [
                c for c in self.steem.rpc.get_blog_entries({'account': account, 'start_entry_id': entryId, 'limit': limit}, api='follow')["blog"]
            ]
        elif raw_data and not self.steem.rpc.get_use_appbase():
            return [
                c for c in self.steem.rpc.get_blog_entries(account, entryId, limit, api='follow')
            ]
        elif not raw_data and self.steem.rpc.get_use_appbase():
            from .comment import Comment
            return [
                Comment(c, steem_instance=self.steem) for c in self.steem.rpc.get_blog_entries({'account': account, 'start_entry_id': entryId, 'limit': limit}, api='follow')["blog"]
            ]
        else:
            from .comment import Comment
            return [
                Comment(c, steem_instance=self.steem) for c in self.steem.rpc.get_blog_entries(account, entryId, limit, api='follow')
            ]

    def get_blog(self, entryId=0, limit=100, raw_data=False, account=None):
        if account is None:
            account = self["name"]
        self.steem.register_apis(["follow"])
        if raw_data and self.steem.rpc.get_use_appbase():
            return [
                c for c in self.steem.rpc.get_blog({'account': account, 'start_entry_id': entryId, 'limit': limit}, api='follow')["blog"]
            ]
        elif raw_data and not self.steem.rpc.get_use_appbase():
            return [
                c for c in self.steem.rpc.get_blog(account, entryId, limit, api='follow')
            ]
        elif not raw_data and self.steem.rpc.get_use_appbase():
            from .comment import Comment
            return [
                Comment(c["comment"], steem_instance=self.steem) for c in self.steem.rpc.get_blog({'account': account, 'start_entry_id': entryId, 'limit': limit}, api='follow')["blog"]
            ]
        else:
            from .comment import Comment
            return [
                Comment(c["comment"], steem_instance=self.steem) for c in self.steem.rpc.get_blog(account, entryId, limit, api='follow')
            ]

    def get_blog_account(self, account=None):
        if account is None:
            account = self["name"]
        if self.steem.rpc.get_use_appbase():
            return self.steem.rpc.get_blog_authors({'blog_account': account}, api='follow')['blog_authors']
        else:
            self.steem.register_apis(["follow"])
            return self.steem.rpc.get_blog_authors(account, api='follow')

    def get_follow_count(self, account=None):
        """ get_follow_count """
        if account is None:
            account = self["name"]
        if self.steem.rpc.get_use_appbase():
            return self.steem.rpc.get_follow_count({'account': account}, api='follow')
        else:
            self.steem.register_apis(["follow"])
            return self.steem.rpc.get_follow_count(account, api='follow')

    def get_followers(self, raw_data=True):
        """ Returns the account followers as list
        """
        if raw_data:
            return [
                x['follower'] for x in self._get_followers(direction="follower")
            ]
        else:
            return [
                Account(x['follower'], steem_instance=self.steem) for x in self._get_followers(direction="follower")
            ]

    def get_following(self, raw_data=True):
        """ Returns who the account is following as list
        """
        if raw_data:
            return [
                x['following'] for x in self._get_followers(direction="following")
            ]
        else:
            return [
                Account(x['following'], steem_instance=self.steem) for x in self._get_followers(direction="following")
            ]

    def _get_followers(self, direction="follower", last_user=""):
        """ Help function, used in get_followers and get_following
        """
        if self.steem.rpc.get_use_appbase():
            query = {'account': self.name, 'start': last_user, 'type': "blog", 'limit': 100}
            if direction == "follower":
                followers = self.steem.rpc.get_followers(query, api='follow')['followers']
            elif direction == "following":
                followers = self.steem.rpc.get_following(query, api='follow')['following']
        else:
            self.steem.register_apis(["follow"])
            if direction == "follower":
                followers = self.steem.rpc.get_followers(self.name, last_user, "blog", 100, api='follow')
            elif direction == "following":
                followers = self.steem.rpc.get_following(self.name, last_user, "blog", 100, api='follow')

        if len(followers) >= 100:
            followers += self._get_followers(
                direction=direction, last_user=followers[-1][direction])[1:]
        return followers

    @property
    def available_balances(self):
        """ List balances of an account. This call returns instances of
            :class:`steem.amount.Amount`.
        """
        amount_list = ["balance", "sbd_balance", "vesting_shares"]
        available_amount = []
        for amount in amount_list:
            if amount in self:
                available_amount.append(self[amount])
        return available_amount

    @property
    def saving_balances(self):
        savings_amount = []
        amount_list = ["savings_balance", "savings_sbd_balance"]
        for amount in amount_list:
            if amount in self:
                savings_amount.append(self[amount])
        return savings_amount

    @property
    def reward_balances(self):
        amount_list = ["reward_steem_balance", "reward_sbd_balance", "reward_vesting_balance"]
        rewards_amount = []
        for amount in amount_list:
            if amount in self:
                rewards_amount.append(self[amount])
        return rewards_amount

    @property
    def total_balances(self):
        symbols = [self.available_balances[0]["symbol"], self.available_balances[1]["symbol"], self.available_balances[2]["symbol"]]
        return [
            self.get_balance(self.available_balances, symbols[0]) + self.get_balance(self.saving_balances, symbols[0]) +
            self.get_balance(self.reward_balances, symbols[0]),
            self.get_balance(self.available_balances, symbols[1]) + self.get_balance(self.saving_balances, symbols[1]) +
            self.get_balance(self.reward_balances, symbols[1]),
            self.get_balance(self.available_balances, symbols[2]) + self.get_balance(self.reward_balances, symbols[2]),
        ]

    @property
    def balances(self):
        return self.get_balances()

    def get_balances(self):

        return {
            'available': self.available_balances,
            'savings': self.saving_balances,
            'rewards': self.reward_balances,
            'total': self.total_balances,
        }

    def get_balance(self, balances, symbol):
        """ Obtain the balance of a specific Asset. This call returns instances of
            :class:`steem.amount.Amount`.
        """
        if isinstance(balances, string_types):
            if balances == "available":
                balances = self.available_balances
            elif balances == "saving":
                balances = self.saving_balances
            elif balances == "reward":
                balances = self.reward_balances
            elif balances == "total":
                balances = self.total_balances
            else:
                return
        from .amount import Amount
        if isinstance(symbol, dict) and "symbol" in symbol:
            symbol = symbol["symbol"]

        for b in balances:
            if b["symbol"] == symbol:
                return b
        return Amount(0, symbol, steem_instance=self.steem)

    def interest(self):
        """ Caluclate interest for an account
            :param str account: Account name to get interest for
        """
        last_payment = formatTimeString(self["sbd_last_interest_payment"])
        next_payment = last_payment + timedelta(days=30)
        interest_rate = self.steem.get_dynamic_global_properties()[
            "sbd_interest_rate"] / 100  # percent
        interest_amount = (interest_rate / 100) * int(
            int(self["sbd_seconds"]) / (60 * 60 * 24 * 356)) * 10**-3
        utc = pytz.timezone('UTC')
        return {
            "interest": interest_amount,
            "last_payment": last_payment,
            "next_payment": next_payment,
            "next_payment_duration": next_payment - utc.localize(datetime.now()),
            "interest_rate": interest_rate,
        }

    @property
    def is_fully_loaded(self):
        """ Is this instance fully loaded / e.g. all data available?
        """
        return (self.full)

    def ensure_full(self):
        if not self.is_fully_loaded:
            self.full = True
            self.refresh()

    def get_bandwidth(self, bandwidth_type=1, account=None, raw_data=False):
        """ get_account_bandwidth """
        if account is None:
            account = self["name"]
        if raw_data and self.steem.rpc.get_use_appbase():
            return self.steem.rpc.get_account_bandwidth({'account': account, 'type': 'post'}, api="witness")
        elif raw_data and not self.steem.rpc.get_use_appbase():
            return self.steem.rpc.get_account_bandwidth(account, bandwidth_type)
        else:
            global_properties = self.steem.get_dynamic_global_properties()
            reserve_ratio = self.steem.get_reserve_ratio()
            received_vesting_shares = self["received_vesting_shares"].amount
            vesting_shares = self["vesting_shares"].amount
            max_virtual_bandwidth = float(reserve_ratio["max_virtual_bandwidth"])
            total_vesting_shares = Amount(global_properties["total_vesting_shares"], steem_instance=self.steem).amount
            allocated_bandwidth = (max_virtual_bandwidth * (vesting_shares + received_vesting_shares) / total_vesting_shares)
            allocated_bandwidth = round(allocated_bandwidth / 1000000)
            if self.steem.rpc.get_use_appbase():
                return {"used": 0,
                        "allocated": allocated_bandwidth}
            total_seconds = 604800
            date_bandwidth = formatTimeString(self["last_bandwidth_update"])
            utc = pytz.timezone('UTC')
            seconds_since_last_update = utc.localize(datetime.utcnow()) - date_bandwidth
            seconds_since_last_update = seconds_since_last_update.total_seconds()
            average_bandwidth = float(self["average_bandwidth"])
            used_bandwidth = 0
            if seconds_since_last_update < total_seconds:
                used_bandwidth = (((total_seconds - seconds_since_last_update) * average_bandwidth) / total_seconds)
            used_bandwidth = round(used_bandwidth / 1000000)

            return {"used": used_bandwidth,
                    "allocated": allocated_bandwidth}
            # print("bandwidth percent used: " + str(100 * used_bandwidth / allocated_bandwidth))
            # print("bandwidth percent remaining: " + str(100 - (100 * used_bandwidth / allocated_bandwidth)))

    def get_owner_history(self, account=None):
        """ get_owner_history """
        if account is None:
            account = self["name"]
        if self.steem.rpc.get_use_appbase():
            return self.steem.rpc.find_owner_histories({'owner': account}, api="database")['owner_auths']
        else:
            return self.steem.rpc.get_owner_history(account)

    def get_conversion_requests(self, account=None):
        """ get_owner_history """
        if account is None:
            account = self["name"]
        if self.steem.rpc.get_use_appbase():
            return self.steem.rpc.find_sbd_conversion_requests({'account': account}, api="database")['requests']
        else:
            return self.steem.rpc.get_conversion_requests(account)

    def get_withdraw_routes(self, account=None):
        """Returns withdraw_routes """
        if account is None:
            account = self["name"]
        if self.steem.rpc.get_use_appbase():
            return self.steem.rpc.find_withdraw_vesting_routes({'account': account, 'order': 'by_withdraw_route'}, api="database")['routes']
        else:
            return self.steem.rpc.get_withdraw_routes(account, 'all')

    def get_recovery_request(self, account=None):
        """ get_recovery_request """
        if account is None:
            account = self["name"]
        if self.steem.rpc.get_use_appbase():
            return self.steem.rpc.find_account_recovery_requests({'account': account}, api="database")['requests']
        else:
            return self.steem.rpc.get_recovery_request(account)

    def verify_account_authority(self, keys, account=None):
        """ verify_account_authority """
        if account is None:
            account = self["name"]
        if self.steem.rpc.get_use_appbase():
            return self.steem.rpc.verify_account_authority({'account': account, 'signers': keys}, api="database")
        else:
            return self.steem.rpc.verify_account_authority(account, keys)

    def get_account_votes(self, account=None):
        """Returns all votes that the account has done"""
        if account is None:
            account = self
        else:
            account = Account(account, steem_instance=self.steem)
        if self.steem.rpc.get_use_appbase():
            return self.steem.rpc.get_account_votes(account["name"])
            # vote_hist = account.history_reverse(only_ops=["vote"], batch_size=1000, raw_output=True)
            # votes = []
            # for vote in vote_hist:
            #     votes.append(vote[1]["op"][1])
            # return votes
        else:
            return self.steem.rpc.get_account_votes(account["name"])

    def get_vote(self, comment):
        """Returns a vote if the account has already voted for comment.

            :param str/Comment comment: can be a Comment object or a authorpermlink
        """
        from beem.comment import Comment
        c = Comment(comment, steem_instance=self.steem)
        for v in c["active_votes"]:
            if v["voter"] == self["name"]:
                return v
        return None

    def has_voted(self, comment):
        """Returns if the account has already voted for comment

            :param str/Comment comment: can be a Comment object or a authorpermlink
        """
        from beem.comment import Comment
        c = Comment(comment, steem_instance=self.steem)
        active_votes = {v["voter"]: v for v in c["active_votes"]}
        return self["name"] in active_votes

    def virtual_op_count(self, until=None):
        """Returns the number of individual account transactions"""
        if until is not None and isinstance(until, datetime):
            limit = until
            last_gen = self.history_reverse(limit=limit)
            last_item = 0
            for item in last_gen:
                last_item = item[0]
            return last_item
        else:
            try:
                if self.steem.rpc.get_use_appbase():
                    try:
                        return self.steem.rpc.get_account_history({'account': self["name"], 'start': -1, 'limit': 0}, api="account_history")['history'][0][0]
                    except:
                        return self.steem.rpc.get_account_history(self["name"], -1, 0)[0][0]
                else:
                    return self.steem.rpc.get_account_history(self["name"], -1, 0, api="database")[0][0]
            except IndexError:
                return 0

    def get_curation_reward(self, days=7):
        """Returns the curation reward of the last `days` days

            :param int days: limit number of days to be included int the return value
        """
        utc = pytz.timezone('UTC')
        stop = utc.localize(datetime.utcnow()) - timedelta(days=days)
        reward_vests = Amount("0 VESTS", steem_instance=self.steem)
        for reward in self.history_reverse(stop=stop, only_ops=["curation_reward"]):
            reward_vests += Amount(reward['reward'], steem_instance=self.steem)
        return self.steem.vests_to_sp(reward_vests.amount)

    def curation_stats(self):
        return {"24hr": self.get_curation_reward(days=1),
                "7d": self.get_curation_reward(days=7),
                "avg": self.get_curation_reward(days=7) / 7}

    def get_account_history(self, index, limit, order=-1, start=None, stop=None, only_ops=[], exclude_ops=[], raw_output=False):
        """ Returns a generator for individual account transactions. This call can be used in a
            ``for`` loop.
            :param int index: first number of transactions to
                return
            :param int limit: limit number of transactions to
                return
            :param int/datetime start: start number/date of transactions to
                return (*optional*)
            :param int/datetime stop: stop number/date of transactions to
                return (*optional*)
            :param array only_ops: Limit generator by these
                operations (*optional*)
            :param array exclude_ops: Exclude thse operations from
                generator (*optional*)
            :param int batch_size: internal api call batch size (*optional*)
            :param (-1, 1) order: 1 for chronological, -1 for reverse order
        """
        if order != -1 and order != 1:
            raise ValueError("order must be -1 or 1!")
        if self.steem.rpc.get_use_appbase():
            try:
                txs = self.steem.rpc.get_account_history({'account': self["name"], 'start': index, 'limit': limit}, api="account_history")['history']
            except:
                txs = self.steem.rpc.get_account_history(self["name"], index, limit)
        else:
            txs = self.steem.rpc.get_account_history(self["name"], index, limit, api="database")

        if start and isinstance(start, datetime) and start.tzinfo is None:
            utc = pytz.timezone('UTC')
            start = utc.localize(start)
        if stop and isinstance(stop, datetime) and stop.tzinfo is None:
            utc = pytz.timezone('UTC')
            stop = utc.localize(stop)

        if order == -1:
            txs_list = reversed(txs)
        else:
            txs_list = txs
        for item in txs_list:
            item_index, event = item
            if start and isinstance(start, datetime):
                timediff = start - formatTimeString(event["timestamp"])
                if timediff.total_seconds() * float(order) > 0:
                    continue
            elif start and order == 1 and item_index < start:
                continue
            elif start and order == -1 and item_index > start:
                continue
            if stop and isinstance(stop, datetime):
                timediff = stop - formatTimeString(event["timestamp"])
                if timediff.total_seconds() * float(order) < 0:
                    return
            elif stop and order == 1 and item_index > stop:
                return
            elif stop and order == -1 and item_index < stop:
                return
            op_type, op = event['op']
            block_props = remove_from_dict(event, keys=['op'], keep_keys=False)

            def construct_op(account_name):
                # verbatim output from steemd
                if raw_output:
                    return item

                # index can change during reindexing in
                # future hard-forks. Thus we cannot take it for granted.
                immutable = op.copy()
                immutable.update(block_props)
                immutable.update({
                    'account': account_name,
                    'type': op_type,
                })
                _id = Blockchain.hash_op(immutable)
                immutable.update({
                    '_id': _id,
                    'index': item_index,
                })
                return immutable

            if exclude_ops and op_type in exclude_ops:
                continue
            if not only_ops or op_type in only_ops:
                yield construct_op(self["name"])

    def history(
        self, start=None, stop=None,
        only_ops=[], exclude_ops=[], batch_size=1000, raw_output=False
    ):
        """ Returns a generator for individual account transactions. The
            earlist operation will be first. This call can be used in a
            ``for`` loop.

            :param int/datetime start: start number/date of transactions to
                return (*optional*)
            :param int/datetime stop: stop number/date of transactions to
                return (*optional*)
            :param array only_ops: Limit generator by these
                operations (*optional*)
            :param array exclude_ops: Exclude thse operations from
                generator (*optional*)
            :param int batch_size: internal api call batch size (*optional*)
        """
        _limit = batch_size
        max_index = self.virtual_op_count()
        if not max_index:
            return
        if start is None:
            start_index = 0
        else:
            if isinstance(start, datetime):
                start_index = 0
            else:
                start_index = start
        if start and isinstance(start, datetime) and start.tzinfo is None:
            utc = pytz.timezone('UTC')
            start = utc.localize(start)
        if stop and isinstance(stop, datetime) and stop.tzinfo is None:
            utc = pytz.timezone('UTC')
            stop = utc.localize(stop)

        first = start_index + _limit
        while True:
            # RPC call
            for item in self.get_account_history(first, _limit, start=None, stop=None, order=1, raw_output=raw_output):
                if raw_output:
                    item_index, event = item
                    op_type, op = event['op']
                    timestamp = event["timestamp"]
                else:
                    item_index = item['index']
                    op_type = item['type']
                    timestamp = item["timestamp"]
                if start and isinstance(start, datetime):
                    timediff = start - formatTimeString(timestamp)
                    if timediff.total_seconds() > 0:
                        continue
                elif start and item_index < start:
                    continue
                if stop and isinstance(stop, datetime):
                    timediff = stop - formatTimeString(timestamp)
                    if timediff.total_seconds() < 0:
                        first = max_index + _limit
                        return
                elif stop and item_index > stop:
                    return
                if exclude_ops and op_type in exclude_ops:
                    continue
                if not only_ops or op_type in only_ops:
                    yield item
            first += (_limit + 1)
            if stop and isinstance(stop, int) and first >= stop + _limit:
                break
            elif first >= max_index + _limit:
                break

    def history_reverse(
        self, start=None, stop=None,
        only_ops=[], exclude_ops=[], batch_size=1000, raw_output=False
    ):
        """ Returns a generator for individual account transactions. The
            latest operation will be first. This call can be used in a
            ``for`` loop.

            :param int/datetime start: start number/date of transactions to
                return. If negative the virtual_op_count is added. (*optional*)
            :param int/datetime stop: stop number/date of transactions to
                return. If negative the virtual_op_count is added. (*optional*)
            :param array only_ops: Limit generator by these
                operations (*optional*)
            :param array exclude_ops: Exclude thse operations from
                generator (*optional*)
            :param int batch_size: internal api call batch size (*optional*)
        """
        _limit = batch_size
        first = self.virtual_op_count()
        if not first or not batch_size:
            return
        if start is not None and isinstance(start, int) and start < 0:
            start += first
        elif start is not None and isinstance(start, int):
            first = start
        if stop is not None and isinstance(stop, int) and stop < 0:
            stop += first
        if start and isinstance(start, datetime) and start.tzinfo is None:
            utc = pytz.timezone('UTC')
            start = utc.localize(start)
        if stop and isinstance(stop, datetime) and stop.tzinfo is None:
            utc = pytz.timezone('UTC')
            stop = utc.localize(stop)

        while True:
            # RPC call
            if first - _limit < 0:
                _limit = first
            for item in self.get_account_history(first, _limit, start=None, stop=None, order=-1, only_ops=only_ops, exclude_ops=exclude_ops, raw_output=raw_output):
                if raw_output:
                    item_index, event = item
                    op_type, op = event['op']
                    timestamp = event["timestamp"]
                else:
                    item_index = item['index']
                    op_type = item['type']
                    timestamp = item["timestamp"]
                if start and isinstance(start, datetime):
                    timediff = start - formatTimeString(timestamp)
                    if timediff.total_seconds() < 0:
                        continue
                elif start and item_index > start:
                    continue
                if stop and isinstance(stop, datetime):
                    timediff = stop - formatTimeString(timestamp)
                    if timediff.total_seconds() > 0:
                        first = 0
                        return
                elif stop and item_index < stop:
                    first = 0
                    return
                if exclude_ops and op_type in exclude_ops:
                    continue
                if not only_ops or op_type in only_ops:
                    yield item
            first -= (_limit + 1)
            if first < 1:
                break

    def unfollow(self, unfollow, what=["blog"], account=None):
        """ Unfollow another account's blog
            :param str unfollow: Follow this account
            :param list what: List of states to follow
                (defaults to ``['blog']``)
            :param str account: (optional) the account to allow access
                to (defaults to ``default_account``)
        """
        # FIXME: removing 'blog' from the array requires to first read
        # the follow.what from the blockchain
        return self.follow(unfollow, what=[], account=account)

    def follow(self, follow, what=["blog"], account=None):
        """ Follow another account's blog
            :param str follow: Follow this account
            :param list what: List of states to follow
                (defaults to ``['blog']``)
            :param str account: (optional) the account to allow access
                to (defaults to ``default_account``)
        """
        if not account:
            account = self["name"]
        if not account:
            raise ValueError("You need to provide an account")

        json_body = [
            'follow', {
                'follower': account,
                'following': follow,
                'what': what
            }
        ]
        return self.steem.custom_json(
            id="follow", json=json_body, required_posting_auths=[account])

    def update_account_profile(self, profile, account=None):
        """ Update an account's meta data (json_meta)
            :param dict json: The meta data to use (i.e. use Profile() from
                account.py)
            :param str account: (optional) the account to allow access
                to (defaults to ``default_account``)
        """
        if not account:
            account = self
        if not account:
            raise ValueError("You need to provide an account")
        account = Account(account, steem_instance=self.steem)
        op = operations.Account_update(
            **{
                "account": account["name"],
                "memo_key": account["memo_key"],
                "json_metadata": profile,
                "prefix": self.steem.prefix,
            })
        return self.steem.finalizeOp(op, account, "active")

    # -------------------------------------------------------------------------
    #  Approval and Disapproval of witnesses
    # -------------------------------------------------------------------------
    def approvewitness(self, witness, account=None, approve=True, **kwargs):
        """ Approve a witness

            :param list witnesses: list of Witness name or id
            :param str account: (optional) the account to allow access
                to (defaults to ``default_account``)
        """
        if not account:
            account = self["name"]
        if not account:
            raise ValueError("You need to provide an account")
        account = Account(account, steem_instance=self.steem)

        # if not isinstance(witnesses, (list, set, tuple)):
        #     witnesses = {witnesses}

        # for witness in witnesses:
        #     witness = Witness(witness, steem_instance=self)

        op = operations.Account_witness_vote(**{
            "account": account["name"],
            "witness": witness,
            "approve": approve,
            "prefix": self.steem.prefix,
        })
        return self.steem.finalizeOp(op, account, "active", **kwargs)

    def disapprovewitness(self, witness, account=None, **kwargs):
        """ Disapprove a witness

            :param list witnesses: list of Witness name or id
            :param str account: (optional) the account to allow access
                to (defaults to ``default_account``)
        """
        return self.approvewitness(
            witness=witness, account=account, approve=False)

    def update_memo_key(self, key, account=None, **kwargs):
        """ Update an account's memo public key

            This method does **not** add any private keys to your
            wallet but merely changes the memo public key.

            :param str key: New memo public key
            :param str account: (optional) the account to allow access
                to (defaults to ``default_account``)
        """
        if not account:
            account = self
        if not account:
            raise ValueError("You need to provide an account")

        PublicKey(key, prefix=self.steem.prefix)

        account = Account(account, steem_instance=self.steem)
        account["memo_key"] = key
        op = operations.Account_update(**{
            "account": account["name"],
            "memo_key": account["memo_key"],
            "json_metadata": account["json_metadata"],
            "prefix": self.steem.prefix,
        })
        return self.steem.finalizeOp(op, account, "active", **kwargs)

    # -------------------------------------------------------------------------
    # Simple Transfer
    # -------------------------------------------------------------------------
    def transfer(self, to, amount, asset, memo="", account=None, **kwargs):
        """ Transfer an asset to another account.

            :param str to: Recipient
            :param float amount: Amount to transfer
            :param str asset: Asset to transfer
            :param str memo: (optional) Memo, may begin with `#` for encrypted
                messaging
            :param str account: (optional) the source account for the transfer
                if not ``default_account``
        """

        if not account:
            account = self
        if not account:
            raise ValueError("You need to provide an account")

        account = Account(account, steem_instance=self.steem)
        amount = Amount(amount, asset, steem_instance=self.steem)
        to = Account(to, steem_instance=self.steem)
        if memo and memo[0] == "#":
            from .memo import Memo
            memoObj = Memo(
                from_account=account,
                to_account=to,
                steem_instance=self.steem
            )
            memo = memoObj.encrypt(memo[1:])["message"]

        op = operations.Transfer(**{
            "amount": amount,
            "to": to["name"],
            "memo": memo,
            "from": account["name"],
            "prefix": self.steem.prefix,
        })
        return self.steem.finalizeOp(op, account, "active", **kwargs)

    def transfer_to_vesting(self, amount, to=None, account=None, **kwargs):
        """ Vest STEEM

            :param float amount: Amount to transfer
            :param str to: Recipient (optional) if not set equal to account
            :param str account: (optional) the source account for the transfer
                if not ``default_account``
        """
        if not account:
            account = self
        if not account:
            raise ValueError("You need to provide an account")
        if not to:
            to = account  # powerup on the same account
        account = Account(account, steem_instance=self.steem)
        if isinstance(amount, (string_types, Amount)):
            amount = Amount(amount, steem_instance=self.steem)
        else:
            amount = Amount(amount, "STEEM", steem_instance=self.steem)
        if not amount["symbol"] == "STEEM":
            raise AssertionError()
        to = Account(to, steem_instance=self.steem)

        op = operations.Transfer_to_vesting(**{
            "from": account["name"],
            "to": to["name"],
            "amount": amount,
            "prefix": self.steem.prefix,
        })
        return self.steem.finalizeOp(op, account, "active", **kwargs)

    def convert(self, amount, account=None, request_id=None):
        """ Convert SteemDollars to Steem (takes one week to settle)
            :param float amount: number of VESTS to withdraw
            :param str account: (optional) the source account for the transfer
            if not ``default_account``
            :param str request_id: (optional) identifier for tracking the
            conversion`
        """
        if not account:
            account = self
        if not account:
            raise ValueError("You need to provide an account")
        account = Account(account, steem_instance=self.steem)
        if isinstance(amount, (string_types, Amount)):
            amount = Amount(amount, steem_instance=self.steem)
        else:
            amount = Amount(amount, "SBD", steem_instance=self.steem)
        if not amount["symbol"] == "SBD":
            raise AssertionError()
        if request_id:
            request_id = int(request_id)
        else:
            request_id = random.getrandbits(32)
        op = operations.Convert(
            **{
                "owner": account["name"],
                "requestid": request_id,
                "amount": amount,
                "prefix": self.steem.prefix,
            })

        return self.steem.finalizeOp(op, account, "active")

    def transfer_to_savings(self, amount, asset, memo, to=None, account=None):
        """ Transfer SBD or STEEM into a 'savings' account.
            :param float amount: STEEM or SBD amount
            :param float asset: 'STEEM' or 'SBD'
            :param str memo: (optional) Memo
            :param str to: (optional) the source account for the transfer if
            not ``default_account``
            :param str account: (optional) the source account for the transfer
            if not ``default_account``
        """
        if asset not in ['STEEM', 'SBD']:
            raise AssertionError()

        if not account:
            account = self
        if not account:
            raise ValueError("You need to provide an account")
        account = Account(account, steem_instance=self.steem)
        amount = Amount(amount, asset, steem_instance=self.steem)
        if not to:
            to = account  # move to savings on same account

        op = operations.Transfer_to_savings(
            **{
                "from": account["name"],
                "to": to["name"],
                "amount": amount,
                "memo": memo,
                "prefix": self.steem.prefix,
            })
        return self.steem.finalizeOp(op, account, "active")

    def transfer_from_savings(self,
                              amount,
                              asset,
                              memo,
                              request_id=None,
                              to=None,
                              account=None):
        """ Withdraw SBD or STEEM from 'savings' account.
            :param float amount: STEEM or SBD amount
            :param float asset: 'STEEM' or 'SBD'
            :param str memo: (optional) Memo
            :param str request_id: (optional) identifier for tracking or
            cancelling the withdrawal
            :param str to: (optional) the source account for the transfer if
            not ``default_account``
            :param str account: (optional) the source account for the transfer
            if not ``default_account``
        """
        if asset not in ['STEEM', 'SBD']:
            raise AssertionError()

        if not account:
            account = self
        if not account:
            raise ValueError("You need to provide an account")
        account = Account(account, steem_instance=self.steem)
        if not to:
            to = account  # move to savings on same account
        amount = Amount(amount, asset, steem_instance=self.steem)
        if request_id:
            request_id = int(request_id)
        else:
            request_id = random.getrandbits(32)

        op = operations.Transfer_from_savings(
            **{
                "from": account["name"],
                "request_id": request_id,
                "to": to["name"],
                "amount": amount,
                "memo": memo,
                "prefix": self.steem.prefix,
            })
        return self.steem.finalizeOp(op, account, "active")

    def cancel_transfer_from_savings(self, request_id, account=None):
        """ Cancel a withdrawal from 'savings' account.
            :param str request_id: Identifier for tracking or cancelling
            the withdrawal
            :param str account: (optional) the source account for the transfer
            if not ``default_account``
        """
        if not account:
            account = self
        if not account:
            raise ValueError("You need to provide an account")
        account = Account(account, steem_instance=self.steem)
        op = operations.Cancel_transfer_from_savings(**{
            "from": account["name"],
            "request_id": request_id,
            "prefix": self.steem.prefix,
        })
        return self.steem.finalizeOp(op, account, "active")

    def claim_reward_balance(self,
                             reward_steem='0 STEEM',
                             reward_sbd='0 SBD',
                             reward_vests='0 VESTS',
                             account=None):
        """ Claim reward balances.
        By default, this will claim ``all`` outstanding balances. To bypass
        this behaviour, set desired claim amount by setting any of
        `reward_steem`, `reward_sbd` or `reward_vests`.
        Args:
            reward_steem (string): Amount of STEEM you would like to claim.
            reward_sbd (string): Amount of SBD you would like to claim.
            reward_vests (string): Amount of VESTS you would like to claim.
            account (string): The source account for the claim if not
            ``default_account`` is used.
        """
        if not account:
            account = self
        else:
            account = Account(account, steem_instance=self.steem)
        if not account:
            raise ValueError("You need to provide an account")

        # if no values were set by user, claim all outstanding balances on
        # account
        if isinstance(reward_steem, (string_types, Amount)):
            reward_steem = Amount(reward_steem, steem_instance=self.steem)
        else:
            reward_steem = Amount(reward_steem, "STEEM", steem_instance=self.steem)
        if not reward_steem["symbol"] == "STEEM":
            raise AssertionError()

        if isinstance(reward_sbd, (string_types, Amount)):
            reward_sbd = Amount(reward_sbd, steem_instance=self.steem)
        else:
            reward_sbd = Amount(reward_sbd, "SBD", steem_instance=self.steem)
        if not reward_sbd["symbol"] == "SBD":
            raise AssertionError()

        if isinstance(reward_vests, (string_types, Amount)):
            reward_vests = Amount(reward_vests, steem_instance=self.steem)
        else:
            reward_vests = Amount(reward_vests, "VESTS", steem_instance=self.steem)
        if not reward_vests["symbol"] == "VESTS":
            raise AssertionError()
        if reward_steem.amount == 0 and reward_sbd.amount == 0 and reward_vests.amount == 0:
            reward_steem = account.balances["rewards"][0]
            reward_sbd = account.balances["rewards"][1]
            reward_vests = account.balances["rewards"][2]

        op = operations.Claim_reward_balance(
            **{
                "account": account["name"],
                "reward_steem": reward_steem,
                "reward_sbd": reward_sbd,
                "reward_vests": reward_vests,
                "prefix": self.steem.prefix,
            })
        return self.steem.finalizeOp(op, account, "posting")

    def delegate_vesting_shares(self, to_account, vesting_shares,
                                account=None):
        """ Delegate SP to another account.
        Args:
            to_account (string): Account we are delegating shares to
            (delegatee).
            vesting_shares (string): Amount of VESTS to delegate eg. `10000
            VESTS`.
            account (string): The source account (delegator). If not specified,
            ``default_account`` is used.
        """
        if not account:
            account = self["name"]
        if not account:
            raise ValueError("You need to provide an account")
        account = Account(account, steem_instance=self.steem)
        if isinstance(vesting_shares, (string_types, Amount)):
            vesting_shares = Amount(vesting_shares, steem_instance=self.steem)
        else:
            vesting_shares = Amount(vesting_shares, "VESTS", steem_instance=self.steem)
        if not vesting_shares["symbol"] == "VESTS":
            raise AssertionError()
        op = operations.Delegate_vesting_shares(
            **{
                "delegator": account,
                "delegatee": to_account,
                "vesting_shares": vesting_shares,
                "prefix": self.steem.prefix,
            })
        return self.steem.finalizeOp(op, account, "active")

    def withdraw_vesting(self, amount, account=None):
        """ Withdraw VESTS from the vesting account.
            :param float amount: number of VESTS to withdraw over a period of
            104 weeks
            :param str account: (optional) the source account for the transfer
            if not ``default_account``
    """
        if not account:
            account = self
        if not account:
            raise ValueError("You need to provide an account")
        account = Account(account, steem_instance=self.steem)
        if isinstance(amount, (string_types, Amount)):
            amount = Amount(amount, steem_instance=self.steem)
        else:
            amount = Amount(amount, "VESTS", steem_instance=self.steem)
        if not amount["symbol"] == "VESTS":
            raise AssertionError()
        op = operations.Withdraw_vesting(
            **{
                "account": account["name"],
                "vesting_shares": amount,
                "prefix": self.steem.prefix,
            })

        return self.steem.finalizeOp(op, account, "active")

    def allow(
        self, foreign, weight=None, permission="posting",
        account=None, threshold=None, **kwargs
    ):
        """ Give additional access to an account by some other public
            key or account.

            :param str foreign: The foreign account that will obtain access
            :param int weight: (optional) The weight to use. If not
                define, the threshold will be used. If the weight is
                smaller than the threshold, additional signatures will
                be required. (defaults to threshold)
            :param str permission: (optional) The actual permission to
                modify (defaults to ``active``)
            :param str account: (optional) the account to allow access
                to (defaults to ``default_account``)
            :param int threshold: The threshold that needs to be reached
                by signatures to be able to interact
        """
        from copy import deepcopy
        if not account:
            account = self
        if not account:
            raise ValueError("You need to provide an account")

        if permission not in ["owner", "posting", "active"]:
            raise ValueError(
                "Permission needs to be either 'owner', 'posting', or 'active"
            )
        account = Account(account, steem_instance=self.steem)

        if permission not in account:
            account = Account(account, steem_instance=self.steem, lazy=False, full=True)
            account.clear_cache()
            account.refresh()
        if permission not in account:
            account = Account(account, steem_instance=self.steem)
        if permission not in account:
            raise AssertionError("Could not access permission")

        if not weight:
            weight = account[permission]["weight_threshold"]

        authority = deepcopy(account[permission])
        try:
            pubkey = PublicKey(foreign, prefix=self.steem.prefix)
            authority["key_auths"].append([
                str(pubkey),
                weight
            ])
        except:
            try:
                foreign_account = Account(foreign, steem_instance=self.steem)
                authority["account_auths"].append([
                    foreign_account["name"],
                    weight
                ])
            except:
                raise ValueError(
                    "Unknown foreign account or invalid public key"
                )
        if threshold:
            authority["weight_threshold"] = threshold
            self.steem._test_weights_treshold(authority)

        op = operations.Account_update(**{
            "account": account["name"],
            permission: authority,
            "memo_key": account["memo_key"],
            "json_metadata": account["json_metadata"],
            "prefix": self.steem.prefix
        })
        if permission == "owner":
            return self.steem.finalizeOp(op, account, "owner", **kwargs)
        else:
            return self.steem.finalizeOp(op, account, "active", **kwargs)

    def disallow(
        self, foreign, permission="posting",
        account=None, threshold=None, **kwargs
    ):
        """ Remove additional access to an account by some other public
            key or account.

            :param str foreign: The foreign account that will obtain access
            :param str permission: (optional) The actual permission to
                modify (defaults to ``active``)
            :param str account: (optional) the account to allow access
                to (defaults to ``default_account``)
            :param int threshold: The threshold that needs to be reached
                by signatures to be able to interact
        """
        if not account:
            account = self
        if not account:
            raise ValueError("You need to provide an account")

        if permission not in ["owner", "active", "posting"]:
            raise ValueError(
                "Permission needs to be either 'owner', 'posting', or 'active"
            )
        account = Account(account, steem_instance=self.steem)
        authority = account[permission]

        try:
            pubkey = PublicKey(foreign, prefix=self.steem.prefix)
            affected_items = list(
                [x for x in authority["key_auths"] if x[0] == str(pubkey)])
            authority["key_auths"] = list([x for x in authority["key_auths"] if x[0] != str(pubkey)])
        except:
            try:
                foreign_account = Account(foreign, steem_instance=self.steem)
                affected_items = list(
                    [x for x in authority["account_auths"] if x[0] == foreign_account["name"]])
                authority["account_auths"] = list([x for x in authority["account_auths"] if x[0] != foreign_account["name"]])
            except:
                raise ValueError(
                    "Unknown foreign account or unvalid public key"
                )

        if not affected_items:
            raise ValueError("Changes nothing!")
        removed_weight = affected_items[0][1]

        # Define threshold
        if threshold:
            authority["weight_threshold"] = threshold

        # Correct threshold (at most by the amount removed from the
        # authority)
        try:
            self.steem._test_weights_treshold(authority)
        except:
            log.critical(
                "The account's threshold will be reduced by %d"
                % (removed_weight)
            )
            authority["weight_threshold"] -= removed_weight
            self.steem._test_weights_treshold(authority)

        op = operations.Account_update(**{
            "account": account["name"],
            permission: authority,
            "memo_key": account["memo_key"],
            "json_metadata": account["json_metadata"],
            "prefix": self.steem.prefix,
        })
        if permission == "owner":
            return self.steem.finalizeOp(op, account, "owner", **kwargs)
        else:
            return self.steem.finalizeOp(op, account, "active", **kwargs)
