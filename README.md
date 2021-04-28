# SimpleWeb3py
A wrapper around the Web3.py library that simplifies certain actions.  
Built as part of a University of Arkansas Blockchain class project.  Designed to make it easier to complete some of the class homework assignments on Ethereum's Ropsten test network using Web3.py instead of Remix and Metamask.  Also, re-creates some of the Solidity contracts with Vyper, because Python.


## Requirements
* Infura API Key for interacting with the Ethereum network.
    1. Create a free account at https://infura.io/.  
    2. On the left select Ethereum and then Create New Project.
    3. Give it a name and submit. 
    4. On the next page, under KEYS, copy the PROJECT ID.
* Python3

## Installation - Windows
Download and install Python3.6 or higher from https://www.python.org/downloads/

Then from a command window run:
```
pip3 install -U web3 mnemonic
# OR
python3 -m pip install -U web3 mnemonic

# OPTIONAL, only necessary if wanting to compile Vyper smart contracts
pip3 install -U vyper
```


## Installation - Ubuntu
From a clean Ubuntu install run the following commands to install the necessary packages and, optionally, the Solidity compiler and python bindings.
```
sudo apt install -y python3 python3-dev python3-pip
sudo pip3 install -U web3 mnemonic

# OPTIONAL, only necessary if wanting to compile Vyper smart contracts
sudo pip3 install -U vyper

# OPTIONAL, only necessary if wanting to compile Solidity smart contracts
sudo add-apt-repository ppa:ethereum/ethereum
sudo apt update
sudo apt install -y solc
sudo pip3 install -U py-solc py-evm py-solc-x solc-select

solc-select install 0.8.3
solc-select use 0.8.3
```
<br/>

## How To
Clone or download a zip of the repo then edit the examples to update the INFURA_PROJECT_ID variable with your Infura project id.  Then you can run the example.  By default, the examples use the pre-compiled ABI and bytecode from the Solidity contracts so a Solidity or Vyper compiler are not necessary. 

## Limitations
Because this was designed to use with some class assignments, it is only setup to work with Infura.io and the Ropsten test network.  This could easily be changed however by editing SimpleWeb3py.py and modifying the SimpleWeb3's class __init__ to work with other providers and/or networks. 

## License
Apache MIT