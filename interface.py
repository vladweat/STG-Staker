from modules import *
from config import *
from utils import *

from random import uniform, randint


def create_lock_on_clear_wallet():
    (
        network,
        min_native_to_buy_lock,
        max_native_to_buy_lock,
        min_lock_time,
        max_lock_time,
    ) = ask_settings(new_wallet=True)

    for private_key in PRIVATE_KEYS:
        random_native_amount = uniform(min_native_to_buy_lock, max_native_to_buy_lock)
        random_lock_time = randint(min_lock_time, max_lock_time)

        zeroX_swap(network, private_key, random_native_amount)

        approve_amount = check_approve_on_stargate(network, private_key)

        if approve_amount <= 0:
            approve_stg_on_stargate(network, private_key)
        else:
            pass

        wallet_balance = get_stg_balance(network, private_key)

        balance_to_lock = randint(int(wallet_balance * 0.97), wallet_balance)

        create_lock(network, private_key, balance_to_lock, random_lock_time)


def pro_coder():
    network = "Polygon"
    native_for_stg = [0.001, 0.002]
    amount_stg_to_lock = [0.1, 0.2]
    lock_time = [1, 5]

    random_native_to_buy = uniform(native_for_stg[0], native_for_stg[1])
    random_stg_to_lock = randint(amount_stg_to_lock[0], amount_stg_to_lock[1])
    random_lock_time = randint(lock_time[0], lock_time[1])

    for private_key in PRIVATE_KEYS:
        ### Chose one below

        ### buy STG via 0xswap
        zeroX_swap(network, private_key, random_native_to_buy)

        ### increase lock only lock time in months
        # increase_lock_time(network, private_key, random_lock_time)

        ### increase amount
        # increase_lock_amount(network, private_key, random_stg_to_lock)

        ### increase lock and amount
        # increase_lock_amount_time(
        #     network, private_key, random_stg_to_lock, random_lock_time
        # )
