import json
import constants
from web3 import Web3
from solcx import compile_standard, install_solc
import os
from dotenv import load_dotenv

load_dotenv()

# For connecting to ganache
# w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:7545"))
w3 = Web3(Web3.HTTPProvider(constants.provider_address))
# constants.chain_id = 1337
# constants.my_address = "0x5cB4BA24fb4Ca0f7D2A88942c9bc01D9c5a3C128"
# constants.private_key = "d9c74a6a0942fdea70100b77fb73c8488e15c396b4489d5e1c6a7e8a75773b18"

with open(os.getcwd() + "\\app\\contracts\\" + "CastedVotes.sol", "r") as file:
    casted_votes_file = file.read()
  
# Solidity source code
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"./contracts/CastedVotes.sol": {"content": casted_votes_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.bytecode.sourceMap"]
                }
            }
        },
    },
    solc_version="0.6.0",
)

with open(os.getcwd() + "\\app\\contracts\\" + "compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)

# Everything above needs to be done only once

# get bytecode
bytecode = compiled_sol["contracts"]["./contracts/CastedVotes.sol"]["CastVotes"]["evm"][
    "bytecode"
]["object"]

# get abi
abi = json.loads(
    compiled_sol["contracts"]["./contracts/CastedVotes.sol"]["CastVotes"]["metadata"]
)["output"]["abi"]

# Create the contract in Python
CastVotes = w3.eth.contract(abi=abi, bytecode=bytecode)
# Get the latest transaction
nonce = w3.eth.getTransactionCount(constants.my_address)
# Submit the transaction that deploys the contract
transaction = CastVotes.constructor().buildTransaction(
    {
        "chainId": constants.chain_id,
        "gasPrice": w3.eth.gas_price,
        "from": constants.my_address,
        "nonce": nonce,
    }
)
# Sign the transaction
signed_txn = w3.eth.account.sign_transaction(transaction, private_key=constants.private_key)
print("Deploying Contract!")
# Send it!
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
# Wait for the transaction to be mined, and get the transaction receipt
print("Waiting for transaction to finish...")
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print(f"Done! Contract deployed to {tx_receipt.contractAddress}")