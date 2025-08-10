// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC1155/ERC1155.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Strings.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

/**
 * @title XOSeason1Drop
 * @dev ERC-1155 contract for XO Season 1 drops with trait-based minting
 */
contract XOSeason1Drop is ERC1155, Ownable, ReentrancyGuard {
    using Strings for uint256;

    // Drop information
    struct Drop {
        string name;
        string description;
        string imageURI;
        string externalURL;
        uint256 maxSupply;
        uint256 currentSupply;
        uint256 price;
        bool isActive;
        string[] traits;
    }

    // Mapping from drop ID to drop info
    mapping(uint256 => Drop) public drops;

    // Mapping from drop ID to trait metadata
    mapping(uint256 => mapping(string => string)) public traitMetadata;

    // Events
    event DropCreated(uint256 indexed dropId, string name, uint256 maxSupply, uint256 price);
    event DropMinted(uint256 indexed dropId, address indexed to, uint256 amount);
    event TraitAdded(uint256 indexed dropId, string trait, string metadata);

    // Constants
    uint256 public constant MINT_FEE = 0.021 ether;
    uint256 public nextDropId = 1;

    constructor() ERC1155("") {
        // Initialize with empty base URI
    }

    /**
     * @dev Create a new drop
     */
    function createDrop(
        string memory _name,
        string memory _description,
        string memory _imageURI,
        string memory _externalURL,
        uint256 _maxSupply,
        uint256 _price,
        string[] memory _traits
    ) external onlyOwner {
        require(_maxSupply > 0, "Max supply must be greater than 0");
        require(_price >= MINT_FEE, "Price must be at least mint fee");

        uint256 dropId = nextDropId++;

        drops[dropId] = Drop({
            name: _name,
            description: _description,
            imageURI: _imageURI,
            externalURL: _externalURL,
            maxSupply: _maxSupply,
            currentSupply: 0,
            price: _price,
            isActive: true,
            traits: _traits
        });

        emit DropCreated(dropId, _name, _maxSupply, _price);
    }

    /**
     * @dev Mint a drop
     */
    function mintDrop(uint256 _dropId) external payable nonReentrant {
        Drop storage drop = drops[_dropId];
        require(drop.isActive, "Drop is not active");
        require(drop.currentSupply < drop.maxSupply, "Drop is sold out");
        require(msg.value >= drop.price, "Insufficient payment");

        // Mint the token
        _mint(msg.sender, _dropId, 1, "");
        drop.currentSupply++;

        // Refund excess payment
        if (msg.value > drop.price) {
            payable(msg.sender).transfer(msg.value - drop.price);
        }

        emit DropMinted(_dropId, msg.sender, 1);
    }

    /**
     * @dev Add trait metadata to a drop
     */
    function addTrait(uint256 _dropId, string memory _trait, string memory _metadata) external onlyOwner {
        require(drops[_dropId].isActive, "Drop does not exist");
        traitMetadata[_dropId][_trait] = _metadata;
        emit TraitAdded(_dropId, _trait, _metadata);
    }

    /**
     * @dev Get drop information
     */
    function getDrop(uint256 _dropId) external view returns (
        string memory name,
        string memory description,
        string memory imageURI,
        string memory externalURL,
        uint256 maxSupply,
        uint256 currentSupply,
        uint256 price,
        bool isActive,
        string[] memory traits
    ) {
        Drop storage drop = drops[_dropId];
        return (
            drop.name,
            drop.description,
            drop.imageURI,
            drop.externalURL,
            drop.maxSupply,
            drop.currentSupply,
            drop.price,
            drop.isActive,
            drop.traits
        );
    }

    /**
     * @dev Get trait metadata
     */
    function getTraitMetadata(uint256 _dropId, string memory _trait) external view returns (string memory) {
        return traitMetadata[_dropId][_trait];
    }

    /**
     * @dev Toggle drop active status
     */
    function toggleDrop(uint256 _dropId) external onlyOwner {
        drops[_dropId].isActive = !drops[_dropId].isActive;
    }

    /**
     * @dev Update drop price
     */
    function updateDropPrice(uint256 _dropId, uint256 _newPrice) external onlyOwner {
        require(_newPrice >= MINT_FEE, "Price must be at least mint fee");
        drops[_dropId].price = _newPrice;
    }

    /**
     * @dev Withdraw contract balance
     */
    function withdraw() external onlyOwner {
        uint256 balance = address(this).balance;
        require(balance > 0, "No balance to withdraw");
        payable(owner()).transfer(balance);
    }

    /**
     * @dev Get token URI for metadata
     */
    function uri(uint256 _tokenId) public view virtual override returns (string memory) {
        require(drops[_tokenId].isActive, "Drop does not exist");
        return drops[_tokenId].imageURI;
    }

    /**
     * @dev Get total supply of a drop
     */
    function totalSupply(uint256 _dropId) external view returns (uint256) {
        return drops[_dropId].currentSupply;
    }

    /**
     * @dev Check if drop is sold out
     */
    function isSoldOut(uint256 _dropId) external view returns (bool) {
        return drops[_dropId].currentSupply >= drops[_dropId].maxSupply;
    }

    /**
     * @dev Get all traits for a drop
     */
    function getDropTraits(uint256 _dropId) external view returns (string[] memory) {
        return drops[_dropId].traits;
    }
}
