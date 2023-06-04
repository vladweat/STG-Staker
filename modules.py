import pytz
import datetime
from time import sleep
from dateutil.relativedelta import relativedelta


import requests
from loguru import logger


from config import *
from utils import *
from _abis.abis import *


def get_0x_quote(
    network: str, from_token: str, to_token: str, value: int, slippage: float
):
    try:
        url_chains = {
            "Ethereum": "",
            "Bsc": "bsc.",
            "Arbitrum": "arbitrum.",
            "Optimism": "optimism.",
            "Polygon": "polygon.",
            "Fantom": "fantom.",
            "Avalanche": "avalanche.",
        }

        url = f"https://{url_chains[network]}api.0x.org/swap/v1/quote?buyToken={to_token}&sellToken={from_token}&sellAmount={value}&slippagePercentage={slippage/100}"

        response = requests.get(url)

        if response.status_code == 200:
            result = [response.json()]
            return result

        else:
            logger.error(f"response.status_code : {response.status_code}")
            return False

    except Exception as error:
        logger.error(error)
        return False


def zeroX_swap(network: str, private_key: str, _amount: float, retry=0):
    while True:
        try:
            web3 = web3_by_network(network)
            address = get_address(private_key)

            from_token = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
            to_token = STG_ADDRESSES[network]
            amount = convert_to_ether_format(_amount)

            json_data = get_0x_quote(network, from_token, to_token, amount, 1)

            if json_data != False:
                spender = json_data[0]["allowanceTarget"]

                tx = {
                    "from": address,
                    "chainId": web3.eth.chain_id,
                    "gasPrice": 0,
                    "nonce": get_nonce(web3, private_key),
                    "gas": 0,
                    "to": Web3.to_checksum_address(json_data[0]["to"]),
                    "data": json_data[0]["data"],
                    "value": int(json_data[0]["value"]),
                }

                if network == "Bsc":
                    tx["gasPrice"] = random.randint(1000000000, 1050000000)
                else:
                    tx = add_gas_price(web3, tx)
                tx = add_gas_limit(web3, tx)

                signed_tx = sign_transaction(web3, tx, private_key)
                tx_hash = send_and_get_tx_hash(web3, signed_tx)

                logger.success(
                    f"SWAP | Wallet {address} swap {_amount} Native Token to STG via 0x_swap | {network} | Waiting for confirm"
                )

                tx_status = check_status_tx(web3, tx_hash)

                if tx_status == 1:
                    logger.success(f"Tx {tx_hash} CONFIRMED")
                    sleeping(30, 140)
                    break

                else:
                    logger.error(f"Tx {tx_hash} FAILED")
                    retry += 1
                    if retry <= RETRY_SWAPS:
                        logger.info(f"Try again | Wallet {address} | retry {retry}")
                        sleeping(10, 15)
                    else:
                        break

        except Exception as e:
            logger.error(f"Error in 'zeroX_swap()' | {e}")
            retry += 1
            if retry <= RETRY_SWAPS:
                logger.info(f"Try again | Wallet {address} | retry {retry}")
                sleeping(10, 15)
            else:
                break


def unix_time_in_months(months, timezone):
    current_date = datetime.datetime.now(pytz.timezone(timezone))
    sunday = current_date - datetime.timedelta(days=current_date.weekday())
    future_sunday = sunday + relativedelta(months=+months)
    start_of_day = datetime.datetime(
        future_sunday.year,
        future_sunday.month,
        future_sunday.day,
        tzinfo=pytz.timezone(timezone),
    )
    result_date = start_of_day - datetime.timedelta(days=1)
    unix_time = int(result_date.timestamp())
    return unix_time


def create_lock(
    network: str, private_key: str, _amount: float, lock_time: int, retry=0
):
    while True:
        try:
            web3 = web3_by_network(network)
            address = get_address(private_key)

            veSTG_contract_address = get_checksum_address(
                STARGATE_FINANCE_ADDRESSES[network]
            )

            veSTG_abi = veSTG_abis

            veSTG_contract = web3.eth.contract(
                address=veSTG_contract_address, abi=veSTG_abi
            )

            create_lock_function = veSTG_contract.get_function_by_name("create_lock")

            amount = convert_to_ether_format(_amount)

            lock_time_end = unix_time_in_months(lock_time, "Etc/Greenwich")

            tx = create_lock_function(amount, lock_time_end).build_transaction(
                {
                    "from": address,
                    "value": 0,
                    "nonce": get_nonce(web3, private_key),
                    "gas": 0,
                    "gasPrice": 0,
                }
            )

            if network == "Bsc":
                tx["gasPrice"] = random.randint(1000000000, 1050000000)
            else:
                tx = add_gas_price(web3, tx)
            tx = add_gas_limit(web3, tx)

            signed_tx = sign_transaction(web3, tx, private_key)

            tx_hash = send_and_get_tx_hash(web3, signed_tx)
            logger.success(
                f"STAKE | Wallet {address} lock {_amount} STG on stargate finance | {network} | Wait for confirm"
            )

            tx_status = check_status_tx(web3, tx_hash)

            if tx_status == 1:
                logger.success(f"Tx {tx_hash} CONFIRMED")
                sleeping(10, 30)
                break

            else:
                logger.error(f"Tx {tx_hash} FAILED")
                retry += 1
                if retry <= RETRY_SWAPS:
                    logger.info(f"Try again | Wallet {address} | retry {retry}")
                    sleeping(10, 15)
                else:
                    break

        except Exception as e:
            logger.error(f"Error in 'create_lock()' | {e}")
            retry += 1
            if retry <= RETRY_SWAPS:
                logger.info(f"Try again | Wallet {address} | retry {retry}")
                sleeping(10, 15)
            else:
                break


def check_lock_status(network: str, private_key: str, retry=0):
    while True:
        try:
            web3 = web3_by_network(network)  # change to any network
            address = get_address(private_key)

            veSTG_contract_address = get_checksum_address(
                STARGATE_FINANCE_ADDRESSES[network]
            )

            veSTG_abi = veSTG_abis

            veSTG_contract = web3.eth.contract(
                address=veSTG_contract_address, abi=veSTG_abi
            )

            check_lock_function = veSTG_contract.get_function_by_name("locked")

            tx = check_lock_function(address).call()

            if tx[0] == 0:
                return False
            else:
                return True, tx

        except Exception as e:
            logger.error(f"Error in 'check_lock_status()' | {e}")
            retry += 1
            if retry <= RETRY_SWAPS:
                logger.info(f"Try again | Wallet {address} | retry {retry}")
                sleeping(10, 15)
            else:
                break


def increase_lock_amount(network: str, private_key: str, lock_amount: int, retry=0):
    while True:
        try:
            web3 = web3_by_network(network)
            address = get_address(private_key)

            veSTG_contract_address = get_checksum_address(
                STARGATE_FINANCE_ADDRESSES[network]
            )

            veSTG_abi = veSTG_abis

            veSTG_contract = web3.eth.contract(
                address=veSTG_contract_address, abi=veSTG_abi
            )

            increase_amount_function = veSTG_contract.get_function_by_selector(
                "0x4957677c"
            )
            _lock_amount = convert_to_ether_format(lock_amount)
            tx = increase_amount_function(_lock_amount).build_transaction(
                {
                    "from": address,
                    "value": 0,
                    "nonce": get_nonce(web3, private_key),
                    "gas": 0,
                    "gasPrice": 0,
                }
            )

            if network == "Bsc":
                tx["gasPrice"] = random.randint(1000000000, 1050000000)
            else:
                tx = add_gas_price(web3, tx)
            tx = add_gas_limit(web3, tx)

            signed_tx = sign_transaction(web3, tx, private_key)

            tx_hash = send_and_get_tx_hash(web3, signed_tx)
            logger.success(
                f"INCREASE LOCK | Wallet {address} increase lock amount by {lock_amount} STG on stargate finance | {network} | Wait for confirm"
            )

            tx_status = check_status_tx(web3, tx_hash)

            if tx_status == 1:
                logger.success(f"Tx {tx_hash} CONFIRMED")
                sleeping(10, 30)
                break

            else:
                logger.error(f"Tx {tx_hash} FAILED")
                retry += 1
                if retry <= RETRY_SWAPS:
                    logger.info(f"Try again | Wallet {address} | retry {retry}")
                    sleeping(10, 15)
                else:
                    break

        except Exception as e:
            logger.error(f"Error in 'increase_lock_amount()' | {e}")
            retry += 1
            if retry <= RETRY_SWAPS:
                logger.info(f"Try again | Wallet {address} | retry {retry}")
                sleeping(10, 15)
            else:
                break


def increase_lock_time(network: str, private_key: str, lock_time: int, retry=0):
    while True:
        try:
            web3 = web3_by_network(network)
            address = get_address(private_key)

            veSTG_contract_address = get_checksum_address(
                STARGATE_FINANCE_ADDRESSES[network]
            )

            veSTG_abi = veSTG_abis

            veSTG_contract = web3.eth.contract(
                address=veSTG_contract_address, abi=veSTG_abi
            )

            increase_lock_function = veSTG_contract.get_function_by_selector(
                "0xeff7a612"
            )

            _unlock_time = check_lock_status(network, private_key)[1][1]
            _current_date = unix_time_in_months(0, "Etc/Greenwich")

            _delta_lock_time = _unlock_time - _current_date

            _new_unlock_time = (
                unix_time_in_months(lock_time, "Etc/Greenwich") + _delta_lock_time
            )

            tx = increase_lock_function(_new_unlock_time).build_transaction(
                {
                    "from": address,
                    "value": 0,
                    "nonce": get_nonce(web3, private_key),
                    "gas": 0,
                    "gasPrice": 0,
                }
            )

            if network == "Bsc":
                tx["gasPrice"] = random.randint(1000000000, 1050000000)
            else:
                tx = add_gas_price(web3, tx)
            tx = add_gas_limit(web3, tx)

            signed_tx = sign_transaction(web3, tx, private_key)

            tx_hash = send_and_get_tx_hash(web3, signed_tx)
            logger.success(
                f"INCREASE LOCK | Wallet {address} increase lock time by {lock_time} months on stargate finance | {network} | Wait for confirm"
            )

            tx_status = check_status_tx(web3, tx_hash)

            if tx_status == 1:
                logger.success(f"Tx {tx_hash} CONFIRMED")
                sleeping(10, 30)
                break

            else:
                logger.error(f"Tx {tx_hash} FAILED")
                retry += 1
                if retry <= RETRY_SWAPS:
                    logger.info(f"Try again | Wallet {address} | retry {retry}")
                    sleeping(10, 15)
                else:
                    break

        except Exception as e:
            logger.error(f"Error in 'increase_lock_time()' | {e}")
            retry += 1
            if retry <= RETRY_SWAPS:
                logger.info(f"Try again | Wallet {address} | retry {retry}")
                sleeping(10, 15)
            else:
                break


def increase_lock_amount_time(
    network: str, private_key: str, lock_amount: int, lock_time: int, retry=0
):
    while True:
        try:
            web3 = web3_by_network(network)
            address = get_address(private_key)

            veSTG_contract_address = get_checksum_address(
                STARGATE_FINANCE_ADDRESSES[network]
            )

            veSTG_abi = veSTG_abis

            veSTG_contract = web3.eth.contract(
                address=veSTG_contract_address, abi=veSTG_abi
            )

            increase_lock_data_function = veSTG_contract.get_function_by_selector(
                "0x7142a6a6"
            )

            _lock_amount = convert_to_ether_format(lock_amount)

            _unlock_time = check_lock_status(network, private_key)[1][1]
            _current_date = unix_time_in_months(0, "Etc/Greenwich")
            _delta_lock_time = _unlock_time - _current_date
            _new_unlock_time = (
                unix_time_in_months(lock_time, "Etc/Greenwich") + _delta_lock_time
            )

            tx = increase_lock_data_function(
                _lock_amount, _new_unlock_time
            ).build_transaction(
                {
                    "from": address,
                    "value": 0,
                    "nonce": get_nonce(web3, private_key),
                    "gas": 0,
                    "gasPrice": 0,
                }
            )

            if network == "Bsc":
                tx["gasPrice"] = random.randint(1000000000, 1050000000)
            else:
                tx = add_gas_price(web3, tx)
            tx = add_gas_limit(web3, tx)

            signed_tx = sign_transaction(web3, tx, private_key)

            tx_hash = send_and_get_tx_hash(web3, signed_tx)
            logger.success(
                f"INCREASE LOCK | Wallet {address} increase lock amount/time by {lock_amount} / {lock_time} on stargate finance | {network} | Wait for confirm"
            )

            tx_status = check_status_tx(web3, tx_hash)

            if tx_status == 1:
                logger.success(f"Tx {tx_hash} CONFIRMED")
                sleeping(10, 30)
                break

            else:
                logger.error(f"Tx {tx_hash} FAILED")
                retry += 1
                if retry <= RETRY_SWAPS:
                    logger.info(f"Try again | Wallet {address} | retry {retry}")
                    sleeping(10, 15)
                else:
                    break

        except Exception as e:
            logger.error(f"Error in 'increase_lock_amount_time()' | {e}")
            retry += 1
            if retry <= RETRY_SWAPS:
                logger.info(f"Try again | Wallet {address} | retry {retry}")
                sleeping(10, 15)
            else:
                break


def check_approve_on_stargate(network: str, private_key: str, retry=0):
    while True:
        try:
            web3 = web3_by_network(network)
            address = get_address(private_key)

            STG_contract_address = get_checksum_address(STG_ADDRESSES[network])
            STG_abi = erc20_token_abi

            STG_contract = web3.eth.contract(address=STG_contract_address, abi=STG_abi)

            allowance_function = STG_contract.get_function_by_name("allowance")

            spender = get_checksum_address(STARGATE_FINANCE_ADDRESSES[network])

            allowance_amount = allowance_function(address, spender).call()

            return allowance_amount

        except Exception as e:
            logger.error(f"Error in 'check_approve_on_stargate()' | {e}")
            retry += 1
            if retry <= RETRY_SWAPS:
                logger.info(f"Try again | Wallet {address} | retry {retry}")
                sleeping(10, 15)
            else:
                break


def approve_stg_on_stargate(network: str, private_key: str, retry=0):
    while True:
        try:
            web3 = web3_by_network(network)
            address = get_address(private_key)

            STG_contract_address = get_checksum_address(STG_ADDRESSES[network])
            STG_abi = erc20_token_abi

            STG_contract = web3.eth.contract(address=STG_contract_address, abi=STG_abi)

            approve_function = STG_contract.get_function_by_selector("0x095ea7b3")

            spender = get_checksum_address(STARGATE_FINANCE_ADDRESSES[network])
            amount = 115792089237316195423570985008687907853269984665640564039457584007913129639935

            tx = approve_function(spender, amount).build_transaction(
                {
                    "from": address,
                    "value": 0,
                    "nonce": get_nonce(web3, private_key),
                    "gas": 0,
                    "gasPrice": 0,
                }
            )

            if network == "Bsc":
                tx["gasPrice"] = random.randint(1000000000, 1050000000)
            else:
                tx = add_gas_price(web3, tx)
            tx = add_gas_limit(web3, tx)

            signed_tx = sign_transaction(web3, tx, private_key)

            tx_hash = send_and_get_tx_hash(web3, signed_tx)
            logger.success(
                f"APPROVE | Wallet {address} approve STG on stargate finance | {network} | Wait for confirm"
            )

            tx_status = check_status_tx(web3, tx_hash)

            if tx_status == 1:
                logger.success(f"Tx {tx_hash} CONFIRMED")
                sleeping(10, 30)
                break

            else:
                logger.error(f"Tx {tx_hash} FAILED")
                retry += 1
                if retry <= RETRY_SWAPS:
                    logger.info(f"Try again | Wallet {address} | retry {retry}")
                    sleeping(10, 15)
                else:
                    break

        except Exception as e:
            logger.error(f"Error in 'approve_stg_on_stargate()' | {e}")
            retry += 1
            if retry <= RETRY_SWAPS:
                logger.info(f"Try again | Wallet {address} | retry {retry}")
                sleeping(10, 15)
            else:
                break

def get_stg_balance(network: str, private_key: str, retry=0):
    while True:
        try:
            web3 = web3_by_network(network)
            address = get_address(private_key)

            STG_contract_address = get_checksum_address(STG_ADDRESSES[network])
            STG_abi = erc20_token_abi

            STG_contract = web3.eth.contract(address=STG_contract_address, abi=STG_abi)

            balance_function = STG_contract.get_function_by_name("balanceOf")

            balance_amount = balance_function(address).call()

            return balance_amount

        except Exception as e:
            logger.error(f"Error in 'check_approve_on_stargate()' | {e}")
            retry += 1
            if retry <= RETRY_SWAPS:
                logger.info(f"Try again | Wallet {address} | retry {retry}")
                sleeping(10, 15)
            else:
                break

