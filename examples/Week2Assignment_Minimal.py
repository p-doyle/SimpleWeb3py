import sys
import time
import os

# add the parent folder so we can easily import the library
sys.path.append('..')
import SimpleWeb3py

# initialize SimpleWeb3py
simple_web3 = SimpleWeb3py.SimpleWeb3(infura_project_id='<your infura project id>')

# create a new account using a generated private key and save it to file
account = SimpleWeb3py.create_new_account(save_path='account1_secret.txt')

# request ether from faucet.ropsten.be
SimpleWeb3py.request_ether(account.address)

# wait until we receive ether from the faucet (can take anywhere from 30 seconds to hours)
while simple_web3.get_address_balance(account.address) <= 0:
    time.sleep(30)

# check account balance
print(f'Account has {simple_web3.get_address_balance(account.address)} ether available!')

# create a contract object using an existing solidity smart contract
contract = SimpleWeb3py.SimpleWeb3Contract(simple_web3,
                                           contract_filepath=os.path.join('SolidityContracts', 'SimpleCoin.sol'),
                                           contract_name='SimpleCoin',
                                           contract_constructors={'_initialSupply': 10000})

# compile and deploy the contract using our account
contract.initialize(account)

# use the coinBalance mapping to get the number of SimpleCoins that our account has
print(f'Our account has {contract.call_function("coinBalance", account.address)} SimpleCoins!')

# create a second account so we can send it some SimpleCoins, this time create the account with a mnemonic phrase
account2 = SimpleWeb3py.create_new_account(use_mnemonic=True, save_path='my_secret_phrase.txt')

# execute the 'transfer' smart contract function to send some SimpleCoins to Account 2
contract.execute_function('transfer', param_dict={'_to': account2.address, '_amount': 500})

# verify that Account 2 has received the SimpleCoins
print(f'Account 2 now has {contract.call_function("coinBalance", account2.address)} SimpleCoins!')


