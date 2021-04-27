coinBalance: public(HashMap[address, uint256])

event Transfer:
    _from: indexed(address)
    to: indexed(address)
    value: uint256

@external
def __init__( _initialSupply: uint256):
    self.coinBalance[msg.sender] = _initialSupply


@external
def transfer(_to: address, _amount: uint256):
    assert self.coinBalance[msg.sender] > _amount
    assert self.coinBalance[_to] + _amount >= self.coinBalance[_to]

    self.coinBalance[msg.sender] -= _amount
    self.coinBalance[_to] += _amount
    log Transfer(msg.sender, _to, _amount)

