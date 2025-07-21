// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC1155/ERC1155.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/common/ERC2981.sol";

contract XOSealsDrop is ERC1155, Ownable, ERC2981 {
    string public name = "XO Seals Drop";
    string public symbol = "XOSD";

    mapping(uint256 => string) private _uriMapping;

    constructor(string memory defaultUri, address initialOwner)
        ERC1155(defaultUri)
        Ownable(initialOwner)
    {}

    function mintTo(address to, uint256 id, uint256 amount) public onlyOwner {
        _mint(to, id, amount, "");
    }

    function mintBatchTo(address to, uint256[] memory ids, uint256[] memory amounts) public onlyOwner {
        _mintBatch(to, ids, amounts, "");
    }

    function setURI(string memory newuri) public onlyOwner {
        _setURI(newuri);
    }

    function setTokenURI(uint256 tokenId, string memory uri) public onlyOwner {
        _uriMapping[tokenId] = uri;
    }

    function uri(uint256 tokenId) public view override returns (string memory) {
        string memory tokenUri = _uriMapping[tokenId];
        if (bytes(tokenUri).length > 0) {
            return tokenUri;
        }
        return super.uri(tokenId);
    }

    function setRoyaltyInfo(address receiver, uint96 feeNumerator) public onlyOwner {
        _setDefaultRoyalty(receiver, feeNumerator);
    }

    function supportsInterface(bytes4 interfaceId) public view override(ERC1155, ERC2981) returns (bool) {
        return super.supportsInterface(interfaceId);
    }
}
