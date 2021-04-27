import SimpleWeb3py
import time
import os

# convenience function to execute the 'transfer' smart contract function to send
#  SimpleCoins to an address and then output the Event data and check the account balance
def send_simplecoins(_contract, to_name, to_address, amount):
    print(f'sending {amount} SimpleCoins to {to_name}!')
    event_data = _contract.execute_function('transfer', event_name='Transfer',
                                            param_dict={'_to': to_address, '_amount': amount})
    print(f'Transfer Event Data: {event_data}')

    account_balance = _contract.call_function('coinBalance', to_address)
    print(f'{to_name} now has {account_balance} SimpleCoins!')
    print()


simple_web3 = SimpleWeb3py.SimpleWeb3(infura_project_id='<your infura project id>')

# create a new account using a generated private key and save it to file
account1 = SimpleWeb3py.create_new_account(save_path='account1_secret.txt')

# request ether from faucet.ropsten.be
SimpleWeb3py.request_ether(account1.address)

# wait until we receive ether from the faucet (can take anywhere from 30 seconds to hours)
while simple_web3.get_address_balance(account1.address) <= 0:
    time.sleep(30)

# create 2 accounts using a generated private key
account2 = SimpleWeb3py.create_new_account(save_path='account2_secret.txt')
account3 = SimpleWeb3py.create_new_account(save_path='account3_secret.txt')

# create 2 accounts using a mnemonic seed phrase
account4 = SimpleWeb3py.create_new_account(use_mnemonic=True, save_path='account4_secret.txt')
account5 = SimpleWeb3py.create_new_account(use_mnemonic=True, save_path='account5_secret.txt')


print(f'account has {simple_web3.get_address_balance(account1.address)} Eth available to send!')

# send some eth to each account
simple_web3.transfer_eth(account1, account2.address, 0.00002)
simple_web3.transfer_eth(account1, account3.address, 0.00003)
simple_web3.transfer_eth(account1, account4.address, 0.00004)
simple_web3.transfer_eth(account1, account5.address, 0.00005)

# check the account balanaces of each account
print(f'account2 now has {simple_web3.get_address_balance(account2.address)} Eth!')
print(f'account3 now has {simple_web3.get_address_balance(account3.address)} Eth!')
print(f'account4 now has {simple_web3.get_address_balance(account4.address)} Eth!')
print(f'account5 now has {simple_web3.get_address_balance(account5.address)} Eth!')

account1_balance = simple_web3.get_address_balance(account1.address)
print(f'account1 has {account1_balance} Eth remaining!')

# build a contract object
# if you already have the compiled ABI and bytecode you can specify the path to them
contract = SimpleWeb3py.SimpleWeb3Contract(simple_web3,
                                           abi_filepath=os.path.join('SolidityContracts', 'SimpleCoinABI.json'),
                                           bytecode_filepath=os.path.join('SolidityContracts', 'SimpleCoinBytecode'),
                                           contract_constructors={'_initialSupply': 10000})

# otherwise, if compiling yourself, specify the contract filepath and name
#  as well as any constructor arguments (if any) defined by the contract
'''
contract = SimpleWeb3py.SimpleWeb3Contract(simple_web3,
                                           contract_filepath=os.path.join('SolidityContracts', 'SimpleCoin.sol'),
                                           contract_name='SimpleCoin',
                                           contract_constructors={'_initialSupply': 10000})
'''


estimated_eth_cost = contract.estimate_deploy_cost()

if estimated_eth_cost > account1_balance:
    print(f'account1 only has {account1_balance} Eth left, not enough to deploy contract!')

else:
    # initialize the contract object, based on the parameters supplied above this will either deploy a new
    #  contract or use an existing one
    contract.initialize(account1)

    # use the coinBalance mapping to get the number of SimpleCoins that account1 has
    account1_balance = contract.call_function('coinBalance', account1.address)
    print(f'account1 has {account1_balance} SimpleCoins!')

    send_simplecoins(contract, 'account2', account2.address, 200)
    send_simplecoins(contract, 'account3', account3.address, 300)
    send_simplecoins(contract, 'account4', account4.address, 400)
    send_simplecoins(contract, 'account5', account5.address, 500)

    account1_balance = contract.call_function('coinBalance', account1.address)
    print(f'account1 only has {account1_balance} SimpleCoins left!')

