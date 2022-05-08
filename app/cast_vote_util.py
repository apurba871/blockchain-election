import json
from web3 import Web3
from solcx import compile_standard, install_solc
import app.constants as constants
import os
from dotenv import load_dotenv

load_dotenv()

# For connecting to Ganache
# constants.provider_address = "HTTP://127.0.0.1:7545"
# For connecting to ganache
w3 = Web3(Web3.HTTPProvider(constants.provider_address))
# For Ganache and Blockchain
# constants.chain_id = 1337
# constants.my_address = "0x5cB4BA24fb4Ca0f7D2A88942c9bc01D9c5a3C128"
# constants.private_key = "d9c74a6a0942fdea70100b77fb73c8488e15c396b4489d5e1c6a7e8a75773b18"
# constants.contractAddress = '0x246aa894C1e439eaFC8787c3CDDdA5DD73d38Cde'

print(os.getcwd())

with open(os.getcwd() + "\\app\\contracts\\" + "compiled_code.json", "r") as file:
    compiled_sol = json.loads(file.read())

# get bytecode
bytecode = compiled_sol["contracts"]["./contracts/CastedVotes.sol"]["CastVotes"]["evm"][
    "bytecode"
]["object"]

# get abi
abi = json.loads(
    compiled_sol["contracts"]["./contracts/CastedVotes.sol"]["CastVotes"]["metadata"]
)["output"]["abi"]


# Working with deployed Contracts
casted_votes = w3.eth.contract(address=constants.contractAddress, abi=abi)

def addCastedVote(voter_id, election_id):
  # Get the latest transaction
  nonce = w3.eth.getTransactionCount(constants.my_address)
  # print(f"Initial Stored Value {simple_storage.functions.retrieve().call()}")
  greeting_transaction = casted_votes.functions.addCastedVote(voter_id, election_id).buildTransaction(
      {
          "chainId": constants.chain_id,
          "gasPrice": w3.eth.gas_price,
          "from": constants.my_address,
          "nonce": nonce,
      }
  )
  signed_greeting_txn = w3.eth.account.sign_transaction(
      greeting_transaction, private_key=constants.private_key
  )
  tx_greeting_hash = w3.eth.send_raw_transaction(signed_greeting_txn.rawTransaction)
  print("Updating stored Value...")
  tx_receipt = w3.eth.wait_for_transaction_receipt(tx_greeting_hash)
  print("Stored value")


def checkIfPresent(voter_id, election_id):
  response = casted_votes.functions.getCastedVote(voter_id, election_id).call()
  print(f"OUTPUT = {response}")
  if response == "found":
    return True
  else:
    return False

def countVotesInBallot(election_id):
  return casted_votes.functions.countCastedVotes(election_id).call()
