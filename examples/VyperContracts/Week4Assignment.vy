owner: address

@external
def __init__():
    self.owner = msg.sender

struct StudentAccount:
    username: String[32]
    accountAddress: address
    age: uint256
    emailAddress: String[64]
    programLevel: String[32]
    blockchainTrackEnrolled: bool

studentAccounts: public(HashMap[uint256, StudentAccount])
studentIndex: uint256

studentCount: public(uint256)

event AccountCreated:
    username: String[32]
    accountAddress: address
    age: uint256
    emailAddress: String[64]
    programLevel: String[32]
    blockchainTrackEnrolled: bool

@external
def createAccount(username: String[32], accountAddress: address, age: uint256,  emailAddress: String[64],
                  programLevel: String[32], blockchainTrackEnrolled: bool):

    self.studentAccounts[self.studentIndex] = StudentAccount({username: username,
                            accountAddress: accountAddress,  age: age, emailAddress: emailAddress,
                            programLevel: programLevel, blockchainTrackEnrolled: blockchainTrackEnrolled})
    self.studentIndex += 1

    self.studentCount += 1

    log AccountCreated(username, accountAddress, age, emailAddress,
                       programLevel, blockchainTrackEnrolled)

@external
def deleteAccount(index: uint256):
    assert msg.sender == self.owner

    self.studentAccounts[index] = empty(StudentAccount)
    self.studentCount -= 1

