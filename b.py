from web3 import Web3
import requests

# Connect to Ethereum node
infura_url = "https://mainnet.infura.io/v3/0b97d099c25e43fca2592ef1f165c538"
web3 = Web3(Web3.HTTPProvider(infura_url))

# Check connection
if not web3.isConnected():
    raise Exception("Failed to connect to Ethereum node")

# Token address
token_address = Web3.toChecksumAddress("0x532f27101965dd16442E59d40670FaF5eBB142E4")

# Uniswap and Sushiswap factory addresses
uniswap_factory_address = Web3.toChecksumAddress("0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f")
sushiswap_factory_address = Web3.toChecksumAddress("0xC0AEe478e3658e2610c5F7A4A2E1777cE9e4f2Ac")

# Uniswap and Sushiswap factory ABI (simplified)
factory_abi = [
    {
        "constant": True,
        "inputs": [{"name": "tokenA", "type": "address"}, {"name": "tokenB", "type": "address"}],
        "name": "getPair",
        "outputs": [{"name": "pair", "type": "address"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    }
]

# Token pairs to check (e.g., against USDC)
usdc_address = Web3.toChecksumAddress("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")

# Get pair addresses
def get_pair_address(factory_address, token0, token1):
    factory_contract = web3.eth.contract(address=factory_address, abi=factory_abi)
    pair_address = factory_contract.functions.getPair(token0, token1).call()
    return pair_address

uniswap_pair_address = get_pair_address(uniswap_factory_address, token_address, usdc_address)
sushiswap_pair_address = get_pair_address(sushiswap_factory_address, token_address, usdc_address)

# Uniswap and Sushiswap pair ABI (simplified) and V3
pair_abi = [
    {
        "constant": True,
        "inputs": [],
        "name": "getReserves",
        "outputs": [
            {"name": "_reserve0", "type": "uint112"},
            {"name": "_reserve1", "type": "uint112"},
            {"name": "_blockTimestampLast", "type": "uint32"}
        ],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    }
]

# Get reserves from pair contract
def get_reserves(pair_address):
    if pair_address == "0x0000000000000000000000000000000000000000":
        return None, None
    pair_contract = web3.eth.contract(address=pair_address, abi=pair_abi)
    reserves = pair_contract.functions.getReserves().call()
    return reserves

uniswap_reserves = get_reserves(uniswap_pair_address)
sushiswap_reserves = get_reserves(sushiswap_pair_address)

# Calculate prices
def calculate_price(reserves, token_address, usdc_address):
    if not reserves:
        return None
    reserve0, reserve1, _ = reserves
    if token_address.lower() < usdc_address.lower():
        token_reserve = reserve0
        usdc_reserve = reserve1
    else:
        token_reserve = reserve1
        usdc_reserve = reserve0
    return usdc_reserve / token_reserve

uniswap_price = calculate_price(uniswap_reserves, token_address, usdc_address)
sushiswap_price = calculate_price(sushiswap_reserves, token_address, usdc_address)

print(f"Uniswap price: {uniswap_price} USDC per token")
print(f"Sushiswap price: {sushiswap_price} USDC per token")

if uniswap_price and sushiswap_price:
    if uniswap_price > sushiswap_price:
        print("Arbitrage opportunity: Buy on Sushiswap, sell on Uniswap")
    elif sushiswap_price > uniswap_price:
        print("Arbitrage opportunity: Buy on Uniswap, sell on Sushiswap")
    else:
        print("No arbitrage opportunity")
else:
    print("Price data not available for one or both exchanges")
