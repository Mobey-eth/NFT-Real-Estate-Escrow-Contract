from brownie import Escrow, RealEstate, accounts, web3
import brownie


def test_realEstateNftMint():
    # Arrange
    seller = accounts[0]
    buyer = accounts[1]
    inspector = accounts[2]
    lender = accounts[3]
    tokenID = 1
    purchase_price = web3.toWei(90, "ether")
    down_payment = web3.toWei(20, "ether")

    # Act

    # deploy contracts
    real_estate = RealEstate.deploy({"from": seller})
    escrow = Escrow.deploy(real_estate.address, {"from": seller})
    assert real_estate.ownerOf(tokenID) == seller.address

    # Approve nft spend from ERC721 contract
    txn = real_estate.approve(escrow.address, tokenID, {"from": seller})
    txn.wait(1)

    # Set Facilitators
    tx0 = escrow.setFacilitators(
        inspector.address, buyer.address, lender.address, {"from": seller}
    )
    tx0.wait(1)
    print("Escrow inspection status is: ", escrow.inspectionStatus())

    # Inpector updates Inspection status
    tx2 = escrow.updateInspectionStatus(True, {"from": inspector})
    tx2.wait(1)
    print("Escrow inspection status is: ", escrow.inspectionStatus())

    # Make down payment and test reverts
    tx = escrow.deposit({"from": buyer, "value": down_payment})
    tx.wait(1)
    print(
        "the current Escrow contract balance is: ",
        web3.fromWei(escrow.getContractBalance(), "ether"),
    )
    assert escrow.getContractBalance() == down_payment
    assert escrow.senderToAmount(buyer) == down_payment
    with brownie.reverts():
        escrow.deposit({"from": buyer, "value": down_payment - 100000000000000000})

    lender.transfer(escrow.address, web3.toWei(70, "ether"))
    print(
        "the current Escrow contract balance is: ",
        web3.fromWei(escrow.getContractBalance(), "ether"),
    )

    # Approve sale fxn
    escrow.approveSaleFxn({"from": seller})
    escrow.approveSaleFxn({"from": lender})
    escrow.approveSaleFxn({"from": buyer})
    seller_balance = seller.balance()
    # To finalise sale!
    tx1 = escrow.finalizeSale(tokenID, {"from": seller})
    tx1.wait(1)

    assert real_estate.ownerOf(tokenID) == buyer.address
    assert seller.balance() == seller_balance + purchase_price
    print(seller.balance())

    """
    To test the cancelSale function
    
    print(seller.balance())
    print(buyer.balance())
    print(lender.balance())

    escrow.cancelSale({"from": buyer})
    print("---------------------------------------------------------------")
    print(seller.balance())
    print(buyer.balance())
    print(lender.balance())

    """
