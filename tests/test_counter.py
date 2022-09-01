from brownie import Counter, accounts, exceptions
import pytest
import brownie


@pytest.fixture
def counter():
    account = accounts[0]
    return Counter.deploy({"from": account})


def test_counter():
    account = accounts[0]
    counter = Counter.deploy({"from": account})

    counter.store(1, {"from": account})

    assert counter.name() == "MAname"
    assert counter.num() == 1
    assert counter.getCount() == 1
    assert counter.getName() == "MAname"

    counter.increase({"from": account})
    assert counter.getCount() == 2

    counter.decrease({"from": account})
    assert counter.getCount() == 1

    counter.store(0, {"from": account})
    with pytest.raises(exceptions.VirtualMachineError):
        counter.decrease({"from": account})


def test_decrease(counter):
    account = accounts[0]
    counter.store(0, {"from": account})
    assert counter.num() == 0
    with brownie.reverts():
        counter.decrease({"from": account})
