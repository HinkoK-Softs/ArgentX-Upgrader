from dataclasses import dataclass

import enums
from starknet_py.net import networks as starknet_networks

IMPLEMENTATION_ADDRESS = 0x01a736d6ed154502257f02b1ccdf4d9d1089f80811cd6acad48e6b6a9d1f2003
LAST_VERSION = '0.3.0'

@dataclass
class Network:
    name: str
    rpc_url: str
    txn_explorer_url: str

    def __repr__(self):
        return self.name

NETWORKS = {
    enums.NetworkNames.Starknet: Network(
        'Starknet Mainnet',
        starknet_networks.MAINNET,
        'https://starkscan.co/tx/'
    ),
    enums.NetworkNames.StarknetTestnet: Network(
        'Starknet Goerli',
        starknet_networks.TESTNET,
        'https://testnet.starkscan.co/tx/'
    )
}
