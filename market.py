import pymarket as pm
import numpy as np


def prepare_bid(id_, net_, price_):
    if np.allclose(net_, 0):
        return None
    else:
        buying = net_ > 0
    
    bids = []
    if buying:
        bid = (min(net_, price_[6]), price_[2], id_, True, 0)
        bids.append(bid)
        if net_ > price_[6]:
            bid = (net_ - price_[6], price_[3], id_, True, 0)
            bids.append(bid)
    else:
        bid = (-max(net_, price_[4]), price_[1], id_, False, 0)
        bids.append(bid)
        if net_ < price_[4]:
            bid = (-(net_ - price_[4]), price_[0], id_, False, 0)
            bids.append(bid)
    return bids


class MarketInterface(pm.Market):
    """
    Extends a normal market to add
    the ability to recieve a callback.
    It is assumed that only one bid will be recieved
    for each broker

    """

    def __init__(self, r=None):
        super().__init__()
        self.used_buying_prices = set()
        self.used_selling_prices = set()

        if r is None:
            self.r = np.random.RandomState(1234)
        else:
            self.r = r

        self.users = -1
        self.users_to_key = {}
        self.key_to_users = {}
        self.users_added = set()

    def accept_bid(self, bid):
        uset = self.used_buying_prices if bid[3] else self.used_selling_prices
        new_p = bid[1]
        owner_id = bid[2]
        eps = 0
        counter = 0
        while ((bid[1] + eps) in uset) and (counter < 1e4):
            eps = self.r.randint(-1e3, 1e3) / 1e4
            counter += 1
        if counter == 1e4:
            raise ValueError('bid could not be added')
        else:
            uset.add(bid[1] + eps)
            if owner_id in self.users_to_key:
                uid = self.users_to_key[owner_id]
            else:
                self.users += 1
                uid = self.users
                self.key_to_users[uid] = owner_id
                self.users_to_key[owner_id] = uid
            new_bid = (bid[0], bid[1] + eps, uid, bid[3], bid[4])
            id_ = super().accept_bid(*new_bid)
            return id_


    def clear(self, method='muda', r=None):
        if method=='huang':
            tr, ex = self.run(method)
        else:
            tr, ex = self.run(method, r=r)

    def get_user_result(self, user_id):
        """
        Finds the total quantity and price traded
        by a given broker
        """
        tr = self.transactions.get_df()
        bids = self.bm.get_df()
        extra = self.extra
        uid_ = self.users_to_key[user_id]
        bid_id = bids.index[bids.user == uid_].tolist()
        buying = bids.iloc[bid_id[0], :].buying
        trans = tr[tr.bid.isin(bid_id)]
        if trans.shape[0] > 0:
            quantity_traded = trans.quantity.sum()
            price = trans.apply(lambda x: x.quantity * x.price, axis=1).sum()
            price += extra['fees'][uid_]
            price_per_unit = price / quantity_traded if quantity_traded > 0 else 0
            if not buying:
                quantity_traded *= -1.0
            return quantity_traded, price_per_unit
        else:
            return 0, 0



