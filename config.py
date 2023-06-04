DATA = {
    "Ethereum": {"RPC": "https://rpc.ankr.com/eth"},
    "Bsc": {"RPC": "https://rpc.ankr.com/bsc"},
    "Avalanche": {"RPC": "https://rpc.ankr.com/avalanche"},
    "Polygon": {"RPC": "https://rpc.ankr.com/polygon"},
    "Arbitrum": {"RPC": "https://rpc.ankr.com/arbitrum"},
    "Optimism": {"RPC": "https://rpc.ankr.com/optimism"},
    "Fantom": {"RPC": "https://rpc.ankr.com/fantom"},
}

STG_ADDRESSES = {
    "Ethereum": "0xaf5191b0de278c7286d6c7cc6ab6bb8a73ba2cd6",
    "Bsc": "0xb0d502e938ed5f4df2e681fe6e419ff29631d62b",
    "Avalanche": "0x2F6F07CDcf3588944Bf4C42aC74ff24bF56e7590",
    "Polygon": "0x2f6f07cdcf3588944bf4c42ac74ff24bf56e7590",
    "Arbitrum": "0x6694340fc020c5e6b96567843da2df01b2ce1eb6",
    "Optimism": "0x296F55F8Fb28E498B858d0BcDA06D955B2Cb3f97",
    "Fantom": "0x2f6f07cdcf3588944bf4c42ac74ff24bf56e7590",
}

STARGATE_FINANCE_ADDRESSES = {
    "Avalanche": "0xca0f57d295bbce554da2c07b005b7d6565a58fce",
    "Optimism": "0x43d2761ed16c89a2c4342e2b16a3c61ccf88f05b",
    "Polygon": "0x3ab2da31bbd886a7edf68a6b60d3cde657d3a15d",
    "Arbitrum": "0xfbd849e6007f9bc3cc2d6eb159c045b8dc660268",
    "Fantom": "0x933421675cdc8c280e5f21f0e061e77849293dba",
    "Bsc": "0xd4888870c8686c748232719051b677791dbda26d",
}

RETRY_SWAPS = 3

with open("_data/private_keys.txt", "r") as file:
    PRIVATE_KEYS = [key.strip() for key in file.readlines()]
