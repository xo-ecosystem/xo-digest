// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {ERC20} from "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";

/// @title SeasonalMemecoin
/// @notice Simple ERC20 that mints full initial supply in constructor to a treasury (owner or specified).
contract SeasonalMemecoin is ERC20, Ownable {
    uint8 private immutable _decimals;

    constructor(
        string memory name_,
        string memory symbol_,
        uint8 decimals_,
        uint256 initialSupply, // in tokens with decimals applied (e.g., 1_000_000e18)
        address mintTo,
        address initialOwner
    ) ERC20(name_, symbol_) Ownable(initialOwner) {
        _decimals = decimals_;
        _mint(mintTo == address(0) ? initialOwner : mintTo, initialSupply);
    }

    function decimals() public view override returns (uint8) {
        return _decimals;
    }
}

// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

interface IMiniAMM {
    function swapTokensForETH(uint256 tokenIn, uint256 minEthOut, address to) external;
}

contract SeasonalMemecoin is ERC20, Ownable {
    address public vault;
    uint256 public feeBps = 200; // 2%
    mapping(address => bool) public feeExempt;
    uint256 public accumulatedFees; // tokens sitting in this contract

    event VaultUpdated(address indexed vault);
    event FeeBpsUpdated(uint256 feeBps);
    event FeesConverted(uint256 tokenSold, uint256 minEthOut, address to);

    constructor(address owner_) ERC20("XO Seasonal Meme (Demo)", "SEASON") Ownable(owner_) {
        feeExempt[msg.sender] = true;
        _mint(owner_, 10_000_000e18); // demo supply
    }

    function setVault(address v) external onlyOwner { vault = v; emit VaultUpdated(v); }
    function setFeeBps(uint256 bps) external onlyOwner { require(bps <= 1000, "fee>10%"); feeBps = bps; emit FeeBpsUpdated(bps); }
    function setFeeExempt(address a, bool ex) external onlyOwner { feeExempt[a] = ex; }

    function _update(address from, address to, uint256 value) internal override {
        if (value == 0 || feeExempt[from] || feeExempt[to] || vault == address(0)) {
            super._update(from, to, value);
            return;
        }
        uint256 fee = (value * feeBps) / 10_000;
        uint256 net = value - fee;

        // collect fee into this contract to batch-convert later
        super._update(from, address(this), fee);
        super._update(from, to, net);

        accumulatedFees += fee;
    }

    /// Approve AMM to pull from *this* contract when converting fees
    function approveAMM(address amm) external onlyOwner {
        _approve(address(this), amm, type(uint256).max);
    }

    /// Convert accumulated fee tokens to ETH via AMM and forward ETH to vault
    function convertFees(address amm, uint256 tokenAmount, uint256 minEthOut) external onlyOwner {
        require(vault != address(0), "vault=0");
        require(tokenAmount > 0 && tokenAmount <= accumulatedFees, "bad amount");
        accumulatedFees -= tokenAmount;
        IMiniAMM(amm).swapTokensForETH(tokenAmount, minEthOut, vault);
        emit FeesConverted(tokenAmount, minEthOut, vault);
    }

    receive() external payable {}
}
