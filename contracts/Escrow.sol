// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

// import "./RealEstate.sol";
import "@openzeppelin/contracts/token/ERC721/IERC721.sol";

contract Escrow {
    address public seller;
    address public buyer;
    uint256 public tokenID;
    uint256 public purchasePrice;
    uint256 public downPayment;
    address public inspector;
    address public lender;
    mapping(address => uint256) public senderToAmount;
    mapping(address => bool) public approveSale;

    enum Status {
        APPROVED,
        ONGOING,
        FAILED
    }

    Status public inspectionStatus;
    bool public approveBool;

    IERC721 public realEstate;

    constructor(address _realEstateAddress) {
        seller = msg.sender;
        realEstate = IERC721(_realEstateAddress);
        inspectionStatus = Status.ONGOING;
        purchasePrice = 90 * 10**18;
        downPayment = 20 * 10**18;
    }

    receive() external payable {}

    modifier onlySeller() {
        require(
            msg.sender == seller,
            "Only seller authorised to call this fxn!!"
        );
        _;
    }

    function setFacilitators(
        address _inspector,
        address _buyer,
        address _lender
    ) public onlySeller {
        inspector = _inspector;
        buyer = _buyer;
        lender = _lender;
    }

    function updateInspectionStatus(bool _approveBool) public {
        require(
            msg.sender == inspector,
            "Only inspector authorised to call this fxn!! "
        );
        require(
            inspectionStatus == Status.ONGOING,
            "Inspection is no longer Ongoing"
        );
        approveBool = _approveBool;
        if (approveBool == true) {
            inspectionStatus = Status.APPROVED;
        } else {
            inspectionStatus = Status.FAILED;
        }
    }

    // assuming purchase price is 100ETH and down payment is 20% of that ...
    function deposit() public payable {
        require(
            msg.value >= downPayment,
            "Minimum allowable amount for property is 20ETH"
        );
        senderToAmount[msg.sender] += msg.value;
    }

    function getContractBalance() public view returns (uint256) {
        return address(this).balance;
    }

    function approveSaleFxn() public {
        approveSale[msg.sender] = true;
    }

    // Transfer Ownership of property
    function finalizeSale(uint256 _tokenID) public {
        require(
            inspectionStatus == Status.APPROVED,
            "Inspection is not yet Approved!"
        );
        require(approveSale[seller] == true, "Must be approved by Seller!");
        require(approveSale[lender], "Must be approved by Lender!");
        require(approveSale[buyer], "Must be approved by Buyer!");
        require(
            getContractBalance() >= purchasePrice,
            "ETH in contract is less than selling Price"
        );
        tokenID = _tokenID;
        payable(seller).transfer(address(this).balance);
        realEstate.transferFrom(seller, buyer, tokenID);
    }

    function cancelSale() public {
        require(inspectionStatus == Status.FAILED, "Inspection did not FAIL!");
        payable(buyer).transfer(downPayment);
        payable(lender).transfer(70 * 10**18);
    }
}
