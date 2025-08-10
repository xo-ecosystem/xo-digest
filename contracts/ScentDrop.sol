// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC1155/ERC1155.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Strings.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

/**
 * @title ScentDrop
 * @dev ERC-1155 contract for XO Scent drops with olfactory traits
 */
contract ScentDrop is ERC1155, Ownable, ReentrancyGuard {
    using Strings for uint256;

    // Scent information
    struct Scent {
        string name;
        string description;
        string imageURI;
        string externalURL;
        uint256 maxSupply;
        uint256 currentSupply;
        uint256 price;
        bool isActive;
        string[] olfactoryNotes;
        string intensity; // light, medium, strong
        string season; // spring, summer, autumn, winter
    }

    // Mapping from scent ID to scent info
    mapping(uint256 => Scent) public scents;

    // Mapping from scent ID to olfactory metadata
    mapping(uint256 => mapping(string => string)) public olfactoryMetadata;

    // Events
    event ScentCreated(uint256 indexed scentId, string name, uint256 maxSupply, uint256 price);
    event ScentMinted(uint256 indexed scentId, address indexed to, uint256 amount);
    event OlfactoryNoteAdded(uint256 indexed scentId, string note, string metadata);

    // Constants
    uint256 public constant MINT_FEE = 0.015 ether;
    uint256 public nextScentId = 1;

    constructor() ERC1155("") {
        // Initialize with empty base URI
    }

    /**
     * @dev Create a new scent
     */
    function createScent(
        string memory _name,
        string memory _description,
        string memory _imageURI,
        string memory _externalURL,
        uint256 _maxSupply,
        uint256 _price,
        string[] memory _olfactoryNotes,
        string memory _intensity,
        string memory _season
    ) external onlyOwner {
        require(_maxSupply > 0, "Max supply must be greater than 0");
        require(_price >= MINT_FEE, "Price must be at least mint fee");

        uint256 scentId = nextScentId++;

        scents[scentId] = Scent({
            name: _name,
            description: _description,
            imageURI: _imageURI,
            externalURL: _externalURL,
            maxSupply: _maxSupply,
            currentSupply: 0,
            price: _price,
            isActive: true,
            olfactoryNotes: _olfactoryNotes,
            intensity: _intensity,
            season: _season
        });

        emit ScentCreated(scentId, _name, _maxSupply, _price);
    }

    /**
     * @dev Mint a scent
     */
    function mintScent(uint256 _scentId) external payable nonReentrant {
        Scent storage scent = scents[_scentId];
        require(scent.isActive, "Scent is not active");
        require(scent.currentSupply < scent.maxSupply, "Scent is sold out");
        require(msg.value >= scent.price, "Insufficient payment");

        // Mint the token
        _mint(msg.sender, _scentId, 1, "");
        scent.currentSupply++;

        // Refund excess payment
        if (msg.value > scent.price) {
            payable(msg.sender).transfer(msg.value - scent.price);
        }

        emit ScentMinted(_scentId, msg.sender, 1);
    }

    /**
     * @dev Add olfactory note metadata to a scent
     */
    function addOlfactoryNote(uint256 _scentId, string memory _note, string memory _metadata) external onlyOwner {
        require(scents[_scentId].isActive, "Scent does not exist");
        olfactoryMetadata[_scentId][_note] = _metadata;
        emit OlfactoryNoteAdded(_scentId, _note, _metadata);
    }

    /**
     * @dev Get scent information
     */
    function getScent(uint256 _scentId) external view returns (
        string memory name,
        string memory description,
        string memory imageURI,
        string memory externalURL,
        uint256 maxSupply,
        uint256 currentSupply,
        uint256 price,
        bool isActive,
        string[] memory olfactoryNotes,
        string memory intensity,
        string memory season
    ) {
        Scent storage scent = scents[_scentId];
        return (
            scent.name,
            scent.description,
            scent.imageURI,
            scent.externalURL,
            scent.maxSupply,
            scent.currentSupply,
            scent.price,
            scent.isActive,
            scent.olfactoryNotes,
            scent.intensity,
            scent.season
        );
    }

    /**
     * @dev Get olfactory note metadata
     */
    function getOlfactoryMetadata(uint256 _scentId, string memory _note) external view returns (string memory) {
        return olfactoryMetadata[_scentId][_note];
    }

    /**
     * @dev Toggle scent active status
     */
    function toggleScent(uint256 _scentId) external onlyOwner {
        scents[_scentId].isActive = !scents[_scentId].isActive;
    }

    /**
     * @dev Update scent price
     */
    function updateScentPrice(uint256 _scentId, uint256 _newPrice) external onlyOwner {
        require(_newPrice >= MINT_FEE, "Price must be at least mint fee");
        scents[_scentId].price = _newPrice;
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
        require(scents[_tokenId].isActive, "Scent does not exist");
        return scents[_tokenId].imageURI;
    }

    /**
     * @dev Get total supply of a scent
     */
    function totalSupply(uint256 _scentId) external view returns (uint256) {
        return scents[_scentId].currentSupply;
    }

    /**
     * @dev Check if scent is sold out
     */
    function isSoldOut(uint256 _scentId) external view returns (bool) {
        return scents[_scentId].currentSupply >= scents[_scentId].maxSupply;
    }

    /**
     * @dev Get all olfactory notes for a scent
     */
    function getScentOlfactoryNotes(uint256 _scentId) external view returns (string[] memory) {
        return scents[_scentId].olfactoryNotes;
    }

    /**
     * @dev Get scents by season
     */
    function getScentsBySeason(string memory _season) external view returns (uint256[] memory) {
        uint256[] memory seasonScents = new uint256[](nextScentId - 1);
        uint256 count = 0;

        for (uint256 i = 1; i < nextScentId; i++) {
            if (keccak256(bytes(scents[i].season)) == keccak256(bytes(_season)) && scents[i].isActive) {
                seasonScents[count] = i;
                count++;
            }
        }

        // Resize array to actual count
        uint256[] memory result = new uint256[](count);
        for (uint256 i = 0; i < count; i++) {
            result[i] = seasonScents[i];
        }

        return result;
    }

    /**
     * @dev Get scents by intensity
     */
    function getScentsByIntensity(string memory _intensity) external view returns (uint256[] memory) {
        uint256[] memory intensityScents = new uint256[](nextScentId - 1);
        uint256 count = 0;

        for (uint256 i = 1; i < nextScentId; i++) {
            if (keccak256(bytes(scents[i].intensity)) == keccak256(bytes(_intensity)) && scents[i].isActive) {
                intensityScents[count] = i;
                count++;
            }
        }

        // Resize array to actual count
        uint256[] memory result = new uint256[](count);
        for (uint256 i = 0; i < count; i++) {
            result[i] = intensityScents[i];
        }

        return result;
    }
}
