import sys
import random
import os

# add the parent folder so we can easily import the library
sys.path.append('..')
import SimpleWeb3py

# convenience function to execute the 'createAccount' smart contract function to create
#  a new student account and then output the Event data
def create_student_account(_contract, username, account_address, age, email_address,
                           program_level, blockchain_track_enrolled):
    print(f'Creating student account for {username}!')

    student_account = {
        'username': username,
        'accountAddress': account_address,
        'age': age,
        'emailAddress': email_address,
        'programLevel': program_level,
        'blockchainTrackEnrolled': blockchain_track_enrolled
    }
    event_data = _contract.execute_function('createAccount', event_name='AccountCreated', param_dict=student_account)
    print(f'createAccount Event Data: {event_data}')

    print(f'Account for {username} created!')


# define the StudentAccount struct as it exists in the contract so that we can
#  create a dictionary when querying the studentAccounts array
# this could theoretically be pulled from the ABI but not easily
STUDENT_ACCOUNT_STRUCT = [
    'username',
    'accountAddress',
    'age',
    'emailAddress',
    'programLevel',
    'blockchainTrackEnrolled'
]


simple_web3 = SimpleWeb3py.SimpleWeb3(infura_project_id='<your infura project id>')

# import the accounts that you created in the week 2 assignment
account1 = SimpleWeb3py.import_account('key', secret_path='account1_secret.txt')
account2 = SimpleWeb3py.import_account('key', secret_path='account2_secret.txt')
account3 = SimpleWeb3py.import_account('key', secret_path='account3_secret.txt')
account4 = SimpleWeb3py.import_account('mnemonic', secret_path='account4_secret.txt')
account5 = SimpleWeb3py.import_account('mnemonic', secret_path='account5_secret.txt')

print(f'account has {simple_web3.get_address_balance()} ether available')

contract = SimpleWeb3py.SimpleWeb3Contract(simple_web3,
                                           contract_filepath=os.path.join('SolidityContracts', 'Week4Assignment.sol'),
                                           contract_name='Week4Assignment')

# this will compile and deploy the contract and make it available to interact with
contract.initialize(account1)

create_student_account(contract, 'student1', account2.address, 33, 'student1@uark.edu',  'Graduate', True)
create_student_account(contract, 'student2', account3.address, 31, 'student2@uark.edu',  'Graduate', True)
create_student_account(contract, 'student3', account4.address, 35, 'student3@uark.edu',  'Graduate', True)
create_student_account(contract, 'student4', account5.address, 25, 'student4@uark.edu',  'Graduate', True)

user_count = contract.call_function('studentCount')
print(f'There are now {user_count} accounts!')

# pick a random student to query and then delete
target_student_index = random.randint(0, user_count-1)

# query the student account at specified index of the studentAccounts array
# returned as a list; to make it easier to work with, convert it into a dictionary
student_account_values = contract.call_function('studentAccounts', target_student_index)
student_account_dict = dict(zip(STUDENT_ACCOUNT_STRUCT, student_account_values))
print(f'student account at index 2 is {student_account_dict}')

print(f'Deleting account for {student_account_dict["username"]}!')
contract.execute_function('deleteAccount', param_dict=dict(index=target_student_index))

print(f'Account for {student_account_dict["username"]} deleted! '
      f'There are now {contract.call_function("studentCount")} accounts!')

# after deleting the account, check the values again
# if it was deleted correctly, the values should have been reset to the default for the struct
student_account_values = contract.call_function('studentAccounts', target_student_index)
student_account_dict = dict(zip(STUDENT_ACCOUNT_STRUCT, student_account_values))
print(f'student account at index {target_student_index} is {student_account_dict}')




