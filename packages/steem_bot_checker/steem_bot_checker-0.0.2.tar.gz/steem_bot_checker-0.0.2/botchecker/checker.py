from .bots import bid_bots, other_bots
from .datastructures import Bot


def check(account):
    if account in bid_bots:
        return True, Bot(account=account, type="bid_bot")
    if account in other_bots:
        return True, Bot(account=account, type="other_bot")

    return False, None
