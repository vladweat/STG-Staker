import time
import random
from decimal import Decimal
from random import randint
from time import sleep

import requests
from loguru import logger
from tqdm import tqdm
from web3 import HTTPProvider, Web3

from config import DATA


def ask_settings(new_wallet: bool):
    supported_nets = ", ".join(DATA)
    _network = input(f"Network? [{supported_nets}]: ")

    network = _network.capitalize()

    if network not in DATA:
        print("Wrong network")
        exit()
    else:
        pass

    if new_wallet:
        min_native_to_buy_lock = float(
            input(f"Min amount native token to buy and stake STG? [{network}]: ")
        )
        max_native_to_buy_lock = float(
            input(f"Max amount native token to buy and stake STG? [{network}]: ")
        )
        min_lock_time = int(input(f"Min lock time in months?: "))
        max_lock_time = int(input(f"Max lock time in months?: "))
        return (
            network,
            min_native_to_buy_lock,
            max_native_to_buy_lock,
            min_lock_time,
            max_lock_time,
        )
    else:
        # time - increase lock time
        # amount - increase lock amount
        # all - increase lock time / amount
        supported_functions = ["time", "amount", "all"]
        function = input(f"Che uzaem? {', '.join(DATA)}").lower()
        if function not in supported_functions:
            print("Wrong function")
            exit()
        else:
            if function == "time":
                min_lock_time = int(input(f"Min lock time in months?: "))
                max_lock_time = int(input(f"Max lock time in months?: "))
                return network, 0, 0, min_lock_time, max_lock_time, function

            elif function == "amount":
                min_native_to_buy_lock = float(
                    input(
                        f"Min amount native token to buy and stake STG? [{network}]: "
                    )
                )
                max_native_to_buy_lock = float(
                    input(
                        f"Max amount native token to buy and stake STG? [{network}]: "
                    )
                )
                return (
                    network,
                    min_native_to_buy_lock,
                    max_native_to_buy_lock,
                    0,
                    0,
                    function,
                )

            elif function == "all":
                min_native_to_buy_lock = float(
                    input(f"Min amount native token to stake STG? [{network}]: ")
                )
                max_native_to_buy_lock = float(
                    input(f"Max amount native token to stake STG? [{network}]: ")
                )
                min_lock_time = int(input(f"Min lock time in months?: "))
                max_lock_time = int(input(f"Max lock time in months?: "))
                return (
                    network,
                    min_native_to_buy_lock,
                    max_native_to_buy_lock,
                    min_lock_time,
                    max_lock_time,
                    function,
                )


def web3_by_network(network: str):
    SUP_NETS = [network for network in DATA]

    if network in SUP_NETS:
        return Web3(HTTPProvider(DATA[network]["RPC"]))
    else:
        logger.error(f"Wrong ['{network}'] chain, must be 1 of this {SUP_NETS}")
        quit


def pk_to_wallet(private_key: str):
    web3 = web3_by_network("Polygon")
    return web3.eth.account.from_key(private_key)


def get_address(private_key: str):
    return pk_to_wallet(private_key).address


def get_nonce(web3, private_key: str):
    address = get_address(private_key)
    return web3.eth.get_transaction_count(address)


def sleeping(from_sleep, to_sleep):
    x = randint(from_sleep, to_sleep)
    for i in tqdm(range(x), desc="sleep ", bar_format="{desc}: {n_fmt}/{total_fmt}"):
        time.sleep(1)


def convert_from_ether_format(num: int):
    """100000000000000000000 -> 100"""
    web3 = web3_by_network("Polygon")
    try:
        ether_format = web3.from_wei(num, "ether")
        return ether_format
    except Exception as e:
        logger.error(e)


def convert_to_ether_format(num: float):
    """100 -> 100000000000000000000"""
    web3 = web3_by_network("Polygon")
    try:
        wei_format = web3.to_wei(Decimal(num), "ether")
        return wei_format
    except Exception as e:
        logger.error(e)


def convert_from_mwei_format(num: int):
    """1000000 -> 1"""
    web3 = web3_by_network("Polygon")
    try:
        ether_format = web3.from_wei(num, "mwei")
        return ether_format
    except Exception as e:
        logger.error(e)


def convert_to_mwei_format(num: int):
    """1 -> 1000000"""
    web3 = web3_by_network("Polygon")
    try:
        wei_format = web3.to_wei(Decimal(num), "mwei")
        return wei_format
    except Exception as e:
        logger.error(e)


def get_checksum_address(address: str):
    web3 = web3_by_network("Polygon")
    try:
        checksum_address = web3.to_checksum_address(address)
        return checksum_address
    except Exception as e:
        logger.error(e)


def sign_transaction(web3, tx, private_key):
    signed_tx = web3.eth.account.sign_transaction(tx, private_key)
    return signed_tx


def send_and_get_tx_hash(web3, signed_tx):
    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction).hex()
    return tx_hash


def check_status_tx(web3, tx_hash) -> bool:
    while True:
        try:
            tx_status = web3.eth.wait_for_transaction_receipt(
                tx_hash, timeout=7200
            ).status
            return tx_status
        except Exception as e:
            None


def get_STG_USD_price():
    url = "https://api.coingecko.com/api/v3/coins/stargate-finance"
    response = requests.get(url)
    price = response.json()["market_data"]["current_price"]["usd"]
    return price


def add_gas_limit(web3, contract_txn):
    try:
        value = contract_txn["value"]
        contract_txn["value"] = 0
        pluser = [1.02, 1.05]
        gasLimit = web3.eth.estimate_gas(contract_txn)
        contract_txn["gas"] = int(gasLimit * random.uniform(pluser[0], pluser[1]))
    except Exception as error:
        contract_txn["gas"] = random.randint(2000000, 3000000)
        # logger.info(
        #     f"estimate_gas error : {error}. random gasLimit : {contract_txn['gas']}"
        # )

    contract_txn["value"] = value
    return contract_txn


def add_gas_price(web3, contract_txn):
    try:
        gas_price = web3.eth.gas_price
        contract_txn["gasPrice"] = int(gas_price * random.uniform(1.01, 1.02))
    except Exception as error:
        logger.error(error)

    return contract_txn
