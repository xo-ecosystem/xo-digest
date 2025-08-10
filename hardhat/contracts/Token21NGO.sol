// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract Token21NGO is ERC20, Ownable {
    // Tax configuration
    uint256 public constant SELL_TAX_PERCENT = 21;
    uint256 public constant TAX_DENOMINATOR = 100;

    // Treasury address to receive tax
    address public treasuryAddress;

    // Anti-bot measures
    mapping(address => bool) public isExcludedFromTax;
    mapping(address => bool) public isExcludedFromMaxTx;

    // Max transaction limit (2% of total supply)
    uint256 public maxTxAmount;

    // Events
    event TreasuryAddressUpdated(address indexed oldTreasury, address indexed newTreasury);
    event TaxCollected(address indexed from, uint256 amount, address indexed treasury);
    event ExcludedFromTax(address indexed account, bool excluded);
    event ExcludedFromMaxTx(address indexed account, bool excluded);

    constructor(
        string memory name,
        string memory symbol,
        uint256 initialSupply,
        address initialOwner,
        address _treasuryAddress
    ) ERC20(name, symbol) Ownable(initialOwner) {
        _mint(initialOwner, initialSupply * 10**decimals());
        treasuryAddress = _treasuryAddress;
        maxTxAmount = totalSupply() * 2 / 100; // 2% of total supply

        // Exclude owner and treasury from tax
        isExcludedFromTax[initialOwner] = true;
        isExcludedFromTax[_treasuryAddress] = true;
        isExcludedFromMaxTx[initialOwner] = true;
        isExcludedFromMaxTx[_treasuryAddress] = true;
    }

    function transfer(address to, uint256 amount) public override returns (bool) {
        return _transferWithTax(msg.sender, to, amount);
    }

    function transferFrom(address from, address to, uint256 amount) public override returns (bool) {
        address spender = _msgSender();
        _spendAllowance(from, spender, amount);
        return _transferWithTax(from, to, amount);
    }

    function _transferWithTax(address from, address to, uint256 amount) internal returns (bool) {
        require(from != address(0), "ERC20: transfer from the zero address");
        require(to != address(0), "ERC20: transfer to the zero address");
        require(amount > 0, "Transfer amount must be greater than zero");

        // Check max transaction limit
        if (!isExcludedFromMaxTx[from] && !isExcludedFromMaxTx[to]) {
            require(amount <= maxTxAmount, "Transfer amount exceeds max transaction limit");
        }

        uint256 transferAmount = amount;
        uint256 taxAmount = 0;

        // Apply sell tax (21% when selling)
        if (!isExcludedFromTax[from] && !isExcludedFromTax[to]) {
            // This is a simplified sell detection - in production you'd want more sophisticated logic
            // For now, we'll apply tax on all transfers except to/from excluded addresses
            taxAmount = amount * SELL_TAX_PERCENT / TAX_DENOMINATOR;
            transferAmount = amount - taxAmount;
        }

        // Transfer the taxed amount to treasury
        if (taxAmount > 0) {
            super._transfer(from, treasuryAddress, taxAmount);
            emit TaxCollected(from, taxAmount, treasuryAddress);
        }

        // Transfer the remaining amount
        super._transfer(from, to, transferAmount);

        return true;
    }

    // Admin functions
    function setTreasuryAddress(address _treasuryAddress) external onlyOwner {
        require(_treasuryAddress != address(0), "Treasury address cannot be zero");
        address oldTreasury = treasuryAddress;
        treasuryAddress = _treasuryAddress;

        // Update exclusions
        isExcludedFromTax[oldTreasury] = false;
        isExcludedFromTax[_treasuryAddress] = true;
        isExcludedFromMaxTx[oldTreasury] = false;
        isExcludedFromMaxTx[_treasuryAddress] = true;

        emit TreasuryAddressUpdated(oldTreasury, _treasuryAddress);
    }

    function setExcludedFromTax(address account, bool excluded) external onlyOwner {
        isExcludedFromTax[account] = excluded;
        emit ExcludedFromTax(account, excluded);
    }

    function setExcludedFromMaxTx(address account, bool excluded) external onlyOwner {
        isExcludedFromMaxTx[account] = excluded;
        emit ExcludedFromMaxTx(account, excluded);
    }

    function setMaxTxAmount(uint256 _maxTxAmount) external onlyOwner {
        require(_maxTxAmount > 0, "Max transaction amount must be greater than zero");
        maxTxAmount = _maxTxAmount;
    }

    // View functions
    function getTaxAmount(uint256 amount) external pure returns (uint256) {
        return amount * SELL_TAX_PERCENT / TAX_DENOMINATOR;
    }

    function getTransferAmount(uint256 amount) external pure returns (uint256) {
        return amount - (amount * SELL_TAX_PERCENT / TAX_DENOMINATOR);
    }
}
