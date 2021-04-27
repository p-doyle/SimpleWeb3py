pragma solidity =0.8.3;

contract Week4Assignment {
    
    // var to hold the owner
    address public owner;
    
    // set the owner 
    constructor() {
        owner = msg.sender;
    }

    // attributes we want to track for each account
    struct StudentAccount {
            string username;   
            address accountAddress; 
            uint age;
            string emailAddress;
            string programLevel;
            bool blockchainTrackEnrolled;
    }
    
    // list of student accounts  
    StudentAccount[] public studentAccounts;
    
    // track the length of the array
    // cannot use array.length because it does not get updated when elements are deleted
    uint256 public studentCount;
    
    // unable to create event with just the Struct unless using ABIEncoderV2??
    //event AccountCreated(StudentAccount);
    event AccountCreated(string username, address accountAddress, uint age, string emailAddress, string programLevel, bool blockchainTrackEnrolled);
    
    // modifier to restrict actions to just the owner
    modifier onlyOwner {
        require(msg.sender == owner);
        _;
    }
  
    // function to create a new account
    function createAccount(string memory username, address accountAddress, uint age, string memory emailAddress, string memory programLevel, bool blockchainTrackEnrolled) public {
        
        // create a StudentAccount object with the supplied values
        studentAccounts.push(StudentAccount({username: username, accountAddress: accountAddress, age: age, emailAddress: emailAddress, programLevel: programLevel, blockchainTrackEnrolled: blockchainTrackEnrolled}));
        
        // increment the user count
        studentCount += 1;
        
        // emit the account created event
        emit AccountCreated(username, accountAddress, age, emailAddress, programLevel, blockchainTrackEnrolled);
    }
        
    // delete an account at the specific index 
    function deleteAccount(uint index) public 
        onlyOwner {
           
           // delete the account at specified index
           // actually just resets the struct at that index to the default values
           delete studentAccounts[index];

           // decrement the user count
           studentCount -= 1;
    }
}