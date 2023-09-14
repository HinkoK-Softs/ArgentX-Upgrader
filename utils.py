import random
import time

from logger import logging
from starknet_py.contract import Contract
from starknet_py.net.account.account import Account
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.models import chain_from_network
from starknet_py.net.signer.stark_curve_signer import KeyPair, StarkCurveSigner


def get_account(
    network: str,
    private_key: str,
    address: str,
    proxy: dict[str, str] = None,
    signer_class=None
) -> Account:
    client = GatewayClient(
        network,
        proxy=proxy if proxy is None else proxy['http'],
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
    )

    key_pair = KeyPair.from_private_key(
        key=private_key
    )

    if signer_class is None:
        signer_class = StarkCurveSigner

    signer = signer_class(
        address,
        key_pair,
        chain_from_network(client.net)
    )

    return Account(
        client=client,
        address=address,
        signer=signer
    )


def get_starknet_contract(
    address: str,
    abi: list,
    provider: Account
) -> Contract:
    return Contract(
        address=address,
        abi=abi,
        provider=provider
    )


def shorten_private_key(private_key: str) -> str:
    if len(private_key) <= 16:
        return private_key
    return f'{private_key[:8]}...{private_key[-8:]}'


def int_hash_to_hex(hast_int: int, hash_lenght: int = 64) -> str:
    hash_hex = hex(hast_int)[2:]
    hash_hex = hash_hex.rjust(hash_lenght, '0')
    return f'0x{hash_hex}'


def sleep(sleep_time: float):
    logging.info(f'Sleeping for {round(sleep_time, 2)} seconds. If you want to skip this, press Ctrl+C')
    try:
        time.sleep(sleep_time)
    except KeyboardInterrupt:
        logging.info('[Sleep] Skipping sleep')


def random_sleep():
    min_sleep_time = getattr(random_sleep, 'min_sleep_time', 60)
    max_sleep_time = getattr(random_sleep, 'max_sleep_time', 180)
    sleep_time = round(random.uniform(min_sleep_time, max_sleep_time), 2)
    sleep(sleep_time)
