# STG locker

The script is designed to stake STG on Stargate Finance.

Supported networks: Ethereum, Bsc, Avalanche, Polygon, Arbitrum, Optimism, Fantom

## Setup

Requires python 3.10 or higher to run normally

1. Download script
2. Install python 3.10 or higher
3. Open the folder with the script in any convenient IDE or terminal
4. Create a virtual environment
   
```bash
python -m venv .venv
```

5. Activate the virtual environment (on Windows)
```bash
source .venv/Scripts/activate
```

5. Activate the virtual environment (on Linux/Mac) 
```bash
source .venv/bin/activate
```

6. Install dependencies
```bash
pip install -r requirements.txt
```
7. Place private keys in ***_abis/private_keys.txt*** file (each private on a new line)
8. Start
```bash
python main.py
```

## Litle FAQ

You can use several script modes. On the first run, a simplified version will be launched, but if you wish, you can comment out the ***create_lock_on_clear_wallet()*** function and use the ***pro_coder()*** function, before using it, change the parameters in the function body in the ***interface.py*** file.

EVM: 0x303d720CA67C3DC1108576471F9fbC7cBE5B4DB6