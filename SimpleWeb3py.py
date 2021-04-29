import json
import os
import time
import datetime
from web3 import Web3
import web3
from web3.middleware import construct_sign_and_send_raw_middleware
from eth_account import Account
from web3.gas_strategies.time_based import fast_gas_price_strategy, medium_gas_price_strategy, slow_gas_price_strategy

# pip3 install web3 mnemonic


# do this so we can use the mnemonic library however it is not fully tested yet
#  so is not recommended for anything other than testing!
Account.enable_unaudited_hdwallet_features()

# base URL for the Infura Ropsten API
INFURA_API_URL = 'wss://ropsten.infura.io/ws/v3/'

# base URL for the Ropsten etherscan website
ETHERSCAN_URL = 'https://ropsten.etherscan.io'

ROPSTEN_CHAIN_ID = 3

class SimpleWeb3Contract(object):

    def __init__(self, simple_web3, contract_address=None, abi_filepath=None, bytecode_filepath=None,
                 contract_filepath=None, contract_name=None, contract_constructors=None):

        self.simple_web3 = simple_web3

        # path to a Solidity Smart Contract
        self.contract_filepath = contract_filepath

        # the path to the HealthPass ABI
        self.abi_filepath = abi_filepath

        # the path to the HealthPass Bytecode
        self.bytecode_filepath = bytecode_filepath

        # optional; if the contract has already been deployed we can use that instead of deploying again
        self.address = contract_address
        self.name = contract_name

        # dictionary with any arguments that need to be passed to the constructor()
        #  of a smart contract when it gets deployed
        self.contract_constructors = contract_constructors

        # these will be initialized later as needed
        self.abi = None
        self.bytecode = None
        self.contract = None
        self.estimated_gas_cost = None

    def estimate_deploy_cost(self):
        self.initialize(None, estimate_gas_only=True)
        estimated_gas_price = self.simple_web3.eth.generateGasPrice()
        estimated_eth_cost = self.simple_web3.fromWei(estimated_gas_price * self.estimated_gas_cost, 'ether')
        print(f'Estimated cost to deploy this contract is {estimated_eth_cost:f} ETH')
        return estimated_eth_cost

    # initialize the contract, either by deploying a new contract or by providing
    #  the address of a contract that was previously deployed
    def initialize(self, account, estimate_gas_only=False):

        # to make it easier to deploy and interact with the contract, tell Web3 to use a specific account
        #  when sending transactions
        if account:
            self.simple_web3.middleware_onion.add(construct_sign_and_send_raw_middleware(account))
            self.simple_web3.eth.default_account = account.address

        # load ABI from file if it was supplied
        if self.abi_filepath and os.path.exists(self.abi_filepath):
            print(f'Loading ABI from {self.abi_filepath}')
            with open(self.abi_filepath) as f:
                self.abi = json.load(f)

        # load bytecode from file if it was supplied
        if self.bytecode_filepath and os.path.exists(self.bytecode_filepath):
            print(f'Loading bytecode from {self.bytecode_filepath}')
            with open(self.bytecode_filepath) as f:
                self.bytecode = f.read()

        # if we couldn't load the ABI then we need to compile ourselves
        if not self.abi:
            self.compile()

        # if an address was supplied then use that to initialize the contract
        if self.address:
            print(f'Loading existing contract at address {self.address}')
            self.contract = self.simple_web3.eth.contract(address=self.address, abi=self.abi)
            print(f'Existing contract with address {self.address} initialized')

        # otherwise we need to deploy a new contract
        else:
            print(f'Deploying new contract {self.name}')
            self.deploy(estimate_gas_only=estimate_gas_only)

            if not estimate_gas_only:
                # sometimes there is a delay after deploying a contract so we
                #  need to wait until its for sure available
                code = self.simple_web3.eth.getCode(self.address)
                while code in ['0x', '0x0']:
                    print('contract not found? waiting...')
                    time.sleep(1)

                print('New contract initialized')

    # compile the contract using solc, optionally specifying a location to save the abi and bytecode
    def compile(self):
        # check what kind of contract we are compiling
        if self.contract_filepath.endswith('.vy'):
            contract_type = 'vyper'
        else:
            contract_type = 'solidity'

        print(f'Compiling {contract_type.title()} contract {self.name} from {self.contract_filepath}')

        contract_filename = os.path.basename(self.contract_filepath)

        # load the contract source code from file
        with open(self.contract_filepath, 'r') as f:
            contract_content = f.read()

        if contract_type == 'solidity':
            from solc import compile_standard

            # compile the contract source code
            compiled_sol = compile_standard({
                "language": "Solidity",
                "sources": {
                    contract_filename: {
                        "content": contract_content
                    }
                },
                "settings":
                    {
                        "outputSelection": {
                            "*": {
                                "*": [
                                    "metadata", "evm.bytecode", "evm.bytecode.sourceMap"
                                ]
                            }
                        }
                    }
            })

            # the contract ABI, used by web3 to interact with the contract
            self.abi = json.loads(compiled_sol['contracts'][contract_filename][self.name]['metadata'])['output']['abi']

            # the compiled bytecode, used for deploying the contract
            self.bytecode = compiled_sol['contracts'][contract_filename][self.name]['evm']['bytecode']['object']

        if contract_type == 'vyper':
            from vyper.cli.vyper_compile import compile_files

            output = compile_files(input_files=[self.contract_filepath], output_formats=['abi', 'bytecode'])
            self.abi = output[self.contract_filepath]['abi']
            self.bytecode = output[self.contract_filepath]['bytecode']

        # optionally save the ABI to file so that it can be re-used
        if self.abi_filepath:
            print(f'saving ABI to {self.abi_filepath}')
            with open(self.abi_filepath, 'w') as f:
                json.dump(self.abi, f)

        # optionally save the bytecode to file so that it can be re-used
        if self.bytecode_filepath:
            print(f'saving bytecode to {self.bytecode_filepath}')
            with open(self.bytecode_filepath, 'w') as f:
                f.write(self.bytecode)

    # deploy the contract to the blockchain
    def deploy(self, estimate_gas_only=False):

        # initialize the contract
        contract = self.simple_web3.eth.contract(abi=self.abi, bytecode=self.bytecode)

        if self.contract_constructors:
            constructor = contract.constructor(**self.contract_constructors)
        else:
            constructor = contract.constructor()

        if estimate_gas_only:
            self.estimated_gas_cost = constructor.estimateGas()
            print(f'Estimated gas amount for deploying contract: {self.estimated_gas_cost}')
            return

        print('Deploying contract')

        tx_hash = constructor.transact()

        print(f'Contract transaction URL: {ETHERSCAN_URL}/tx/{tx_hash.hex()}')

        # Wait for the transaction to be mined, and get the transaction receipt
        tx_receipt = self.simple_web3.wait_for_transaction(tx_hash, wait_time=self.simple_web3.timeout)

        if not tx_receipt:
            print('Failed to get transaction receipt.  Please check contract transaction on Etherscan for the address')
        else:
            print(f'Contract URL: {ETHERSCAN_URL}/address/{tx_receipt.contractAddress}')
            print(f'Transaction Cost: {self.simple_web3.calculate_transaction_cost(tx_receipt=tx_receipt)} ETH')

            self.address = tx_receipt.contractAddress

            # re-initialize the contract using the new address
            self.contract = self.simple_web3.eth.contract(address=tx_receipt.contractAddress, abi=self.abi)

    # this is used for querying the values of mappings, arrays and other variables that do not
    #  require a transaction
    def call_function(self, function_name, *args, **kwargs):
        result = getattr(self.contract.functions, function_name)(*args, **kwargs).call()
        return result

    # this is used for executing functions that require the posting of a transaction to the blockchain
    # function parameters can be passed as either a list or a dictionary
    # if wanting to check the output from any emitted events, supply the event_name
    def execute_function(self, function_name, event_name=None, wait_time=None, param_list=None, param_dict=None):

        # if the list or dict aren't passed initialize them empty
        param_list = param_list if param_list else []
        param_dict = param_dict if param_dict else {}

        tx_hash = getattr(self.contract.functions, function_name)(*param_list, **param_dict).transact()
        print(f'Function {function_name} executed! Transaction URL: '
              f'{ETHERSCAN_URL}/tx/{tx_hash.hex()}')

        tx_receipt = self.simple_web3.wait_for_transaction(tx_hash, wait_time=wait_time)
        if tx_receipt:
            print(f'Transaction Cost: {self.simple_web3.calculate_transaction_cost(tx_receipt=tx_receipt)} ETH')

            # in order to see the event we need to
            if event_name:
                event = getattr(self.contract.events, event_name)().processReceipt(tx_receipt)
                return event[0]['args']

class SimpleWeb3(Web3):

    def __init__(self, infura_project_id=None, gas_price_strategy=fast_gas_price_strategy,
                 chain_id=ROPSTEN_CHAIN_ID, timeout=120):

        # the URL of the Infura API that will be used to interact with the ethereum network
        Web3.__init__(self, self.WebsocketProvider(f'{INFURA_API_URL}{infura_project_id}'))

        # set the strategy used when generating gas prices
        self.eth.setGasPriceStrategy(gas_price_strategy)

        # the chain id to use in some transactions, 3 is for Ropsten
        self.chain_id = chain_id

        # the default length of time in seconds to wait for transactions to complete
        self.timeout = timeout

    # wait for a transaction to complete and return the receipt
    def wait_for_transaction(self, tx_hash, wait_time=None):
        wait_time = wait_time if wait_time else self.timeout
        print(f'Waiting up to {wait_time} seconds for transaction to be mined')
        try:
            # by default this will check every 0.1 seconds but to avoid
            #  spamming Infura, check every 3 seconds instead
            tx_receipt = self.eth.wait_for_transaction_receipt(tx_hash, timeout=wait_time, poll_latency=3)
            print(f'Transaction complete!')
        except web3.exceptions.TimeExhausted:
            print(f'Transaction not mined after {wait_time} seconds! giving up')
            return
        return tx_receipt

    # calculate the Eth cost of a submitted transaction
    def calculate_transaction_cost(self, tx_hash=None, tx_receipt=None):

        # if we don't have the whole receipt we need to look it up
        if not tx_receipt:
            tx_receipt = self.eth.getTransactionReceipt(tx_hash)

        # returned in wei
        gas_price = self.eth.getTransaction(tx_receipt.transactionHash).gasPrice

        # total wei spent
        wei_cost = tx_receipt.gasUsed * gas_price

        # total eth spent
        eth_cost = self.fromWei(wei_cost, 'ether')

        return eth_cost

    def transfer_eth(self, from_account, to_address, amount, gas_price=None, gas_price_limit=None,
                      gas_amount=21000, wait_time=None):

        print(f'Sending {amount:f} ETH from {from_account.address} to {to_address}!')

        # build the transaction
        transaction = {
            'from': from_account.address,
            'to': to_address,
            'value': self.toWei(amount, "ether"),
            'chainId': self.chain_id,
            'nonce': self.eth.get_transaction_count(from_account.address),
            'gas': gas_amount,
            'gasPrice': self.eth.gas_price
        }

        # optionally specify a gas price to pay
        if gas_price:
            transaction['gasPrice'] = gas_price

        # optionally specify a limit on the gas price
        if gas_price_limit:
            gas_price = self.eth.generateGasPrice()
            if gas_price > gas_price_limit:
                print(f'Estimated gas price is {gas_price}, above the limit of {gas_price_limit}! Aborting transaction')
                return

        # sign the transaction details with the account's private key
        signed_txn = self.eth.account.sign_transaction(transaction, from_account.key)

        # send the transaction
        tx_hash = self.eth.send_raw_transaction(signed_txn.rawTransaction)

        # output the details
        #print(f'Sent {amount:f} ETH from {from_account.address} to {to_address}!')
        print(f'Transaction URL: {ETHERSCAN_URL}/tx/{tx_hash.hex()}')

        #
        self.wait_for_transaction(tx_hash, wait_time=wait_time)

    # get the account balance of the provided address and convert it to eth
    def get_address_balance(self, address):
        return self.fromWei(self.eth.get_balance(address), 'ether')

    # send the entire account balance from one address to another
    def transfer_account_balance(self, from_account, to_address, gas_price_limit=None):

        # check how much Wei we currently have
        account_balance = self.eth.get_balance(from_account.address)

        # if we don't have any Wei to send, return
        if account_balance == 0:
            print('Account balance is 0, nothing to send!')
            return

        # generate a gas price so we'll know how much we're paying
        gas_price = self.eth.generateGasPrice()

        # need to calculate how much its going to take to transfer the Eth and then send what's left
        # 21000 is the set amount of gas needed to transfer Eth
        balance_minus_gas = self.fromWei(account_balance - (21000 * gas_price), 'ether')

        self.transfer_eth(from_account, to_address, balance_minus_gas, gas_price=gas_price,
                          gas_price_limit=gas_price_limit, gas_amount=21000)


# create a new account
def create_new_account(extra_entropy='', use_mnemonic=False, mnemonic_language='english', save_path=None):
    if use_mnemonic:
        from mnemonic import Mnemonic

        mnemo = Mnemonic(mnemonic_language)
        secret = mnemo.generate(strength=256)
        account = Web3().eth.account.from_mnemonic(secret)

    else:
        account = Web3().eth.account.create(extra_entropy)
        secret = account.key.hex()

    if not save_path:
        print('New account created! make sure to save the secret somewhere secure:')
        print(secret)
    else:
        print(f'New account created! saving secret to {save_path}')
        with open(save_path, 'w') as f:
            f.write(secret)

    return account

# import an account object using a private key or mnemonic phrase
def import_account(secret_type, secret=None, secret_path=None):

    if secret_path:
        with open(secret_path, 'r') as f:
            secret = f.read().strip()

    if secret_type == 'key':
        # when the private key is copied directly from metamask it doesn't include
        #  the 0x in front so make sure its there
        if not secret.startswith('0x'):
            secret = '0x' + secret

        account = Web3().eth.account.privateKeyToAccount(secret)

    elif secret_type == 'mnemonic':
        account = Web3().eth.account.from_mnemonic(secret)
    else:
        print(f'invalid secret type {secret_type}')
        account = None

    return account

# this faucet can be finicky and if you submit a request more than once every hour or so
#  you will get 'greylisted' for increasing longer periods of time
#  this limiting is based on both your IP address and the account address used
# depending on how many other people are requesting ether, may take hours or days...
def request_ether(to_address):
    import requests
    print(f'Requesting 1 ether be sent to address {to_address}')
    r = requests.get('https://faucet.ropsten.be/donate/{}'.format(to_address))


    if r.json().get('message'):
        print(f'Error sending request?  Message was: {r.json()["message"]}')
    else:
        if not r.json().get('paydate'):
            pay_date = 'Unknown'
        else:
            pay_date = datetime.datetime.fromtimestamp(r.json()['paydate']/1000)

        amount = Web3().fromWei(r.json()['amount'], 'ether')
        print(f'{amount} ETH was requested to be sent to {r.json()["address"]}! Estimated Payment Date: {pay_date}')

        if r.json().get('txhash'):
            print(f'Transaction URL: {ETHERSCAN_URL}/tx/{r.json()["txhash"]}')
        else:
            print(f'No transaction hash returned, check your address later at: '
                  f'{ETHERSCAN_URL}/address/{r.json()["address"]}')
