import asyncio
import json
from pathlib import Path

import pandas as pd

import constants
import enums
import utils
from logger import logging
from starknet_py.cairo.felt import decode_shortstring


async def upgrade(
    private_key: str,
    address: str,
    network_name: enums.NetworkNames,
    proxy: dict[str, str]
) -> enums.UpgradeResult:
    logging.info(f'Upgrading account with address {address}')

    network = constants.NETWORKS[network_name]

    account = utils.get_account(
        network=network.rpc_url,
        private_key=private_key,
        address=address,
        proxy=proxy
    )

    with open(Path(__file__).parent / 'abi' / 'argentx.json') as file:
        wallet_abi = json.load(file)

    account_contract = utils.get_starknet_contract(
        address=address,
        abi=wallet_abi,
        provider=account,
    )

    version = (
        await account_contract.functions['getVersion'].call()
    ).version

    version = decode_shortstring(version)

    if version == constants.LAST_VERSION:
        logging.info(f'Account with address {address} is already upgraded')
        return enums.UpgradeResult.SUCCESS

    upgrade_call = account_contract.functions['upgrade'].prepare(
        implementation=constants.IMPLEMENTATION_ADDRESS,
        calldata=[
            0
        ]
    )

    try:
        resp = await account.execute(
            [
                upgrade_call
            ],
            auto_estimate=True
        )
    except BaseException as e:
        if 'assert_not_zero' in str(e):
            logging.critical(f'Insufficient balance to upgrade wallet')
        else:
            logging.error(f'Exception occured while estimating gas: {e}')
        return enums.UpgradeResult.FAILED

    logging.info(f'Transaction: {network.txn_explorer_url}{utils.int_hash_to_hex(resp.transaction_hash)}')

    try:
        receipt = await account.client.wait_for_tx(resp.transaction_hash)
    except BaseException as e:
        logging.error(f'Exception occured while waiting for transaction: {e}')
        return enums.UpgradeResult.FAILED

    return enums.UpgradeResult.SUCCESS


async def main():
    wallets_filename = 'wallets.csv'
    wallets_csv_path = Path(__file__).parent / wallets_filename

    if not wallets_csv_path.exists():
        logging.critical(f'File {wallets_filename} does not exist')
        return

    wallets = pd.read_csv(
        wallets_csv_path,
        dtype={
            'private_key': str,
            'address': str,
            'proxy': str
        }
    )

    wallets.proxy = wallets.proxy.fillna('')

    total_wallets = 0
    successful_wallets = 0

    for index, row in wallets.iterrows():
        if not row.address and not row.private_key:
            continue

        if not row.private_key:
            logging.error(f'No private key specified for {row.address}')
            continue

        if not row.address:
            logging.error(f'No address specified for {utils.shorten_private_key(row.private_key)}')
            continue

        total_wallets += 1

        if row.proxy:
            proxy = {
                'http': f'http://{row.proxy}',
                'https': f'http://{row.proxy}'
            }
        else:
            proxy = None

        upgrade_result = await upgrade(
            private_key=row.private_key,
            address=row.address,
            network_name=enums.NetworkNames.Starknet,
            proxy=proxy
        )

        if upgrade_result != enums.UpgradeResult.FAILED:
            successful_wallets += 1

    logging.info(f'Successfully upgraded {successful_wallets}/{total_wallets} wallets')


if __name__ == '__main__':
    asyncio.run(main())
