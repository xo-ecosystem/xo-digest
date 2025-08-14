// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {ERC721} from "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";
import {Strings} from "@openzeppelin/contracts/utils/Strings.sol";

/// @title PiggyNFT
/// @notice Fun demo NFT: free-mint for first N, then paid. Simple tokenURI base.
///         Use this to gate /ops/broadcast or to boost redeem/mint logic in UI off-chain.
contract PiggyNFT is ERC721, Ownable {
    using Strings for uint256;

    uint256 public immutable MAX_SUPPLY;
    uint256 public freeMintCap;
    uint256 public priceWei;
    string public baseURI;
    uint256 public totalMinted;

    constructor(
        string memory name_,
        string memory symbol_,
        uint256 maxSupply_,
        uint256 freeMintCap_,
        uint256 priceWei_,
        string memory baseURI_,
        address initialOwner
    ) ERC721(name_, symbol_) Ownable(initialOwner) {
        MAX_SUPPLY = maxSupply_;
        freeMintCap = freeMintCap_;
        priceWei = priceWei_;
        baseURI = baseURI_;
    }

    function setPrice(uint256 newPrice) external onlyOwner { priceWei = newPrice; }
    function setFreeMintCap(uint256 cap) external onlyOwner { freeMintCap = cap; }
    function setBaseURI(string memory uri) external onlyOwner { baseURI = uri; }

    function mint() external payable {
        require(totalMinted < MAX_SUPPLY, "sold out");
        if (totalMinted >= freeMintCap) {
            require(msg.value >= priceWei, "insufficient payment");
        }
        uint256 id = ++totalMinted;
        _safeMint(msg.sender, id);
    }

    function tokenURI(uint256 tokenId) public view override returns (string memory) {
        require(_ownerOf(tokenId) != address(0), "not minted");
        return string(abi.encodePacked(baseURI, tokenId.toString(), ".json"));
    }

    function withdraw(address payable to) external onlyOwner {
        (bool ok,) = to.call{value: address(this).balance}("");
        require(ok, "withdraw fail");
    }

    receive() external payable {}
}
