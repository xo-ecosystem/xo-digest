// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

/**
 * @title NGOToken
 * @dev ERC-20 token for XO 21NGO with 21% sell tax and governance features
 */
contract NGOToken is ERC20, Ownable, ReentrancyGuard {
    
    // Tax configuration
    uint256 public constant SELL_TAX_PERCENTAGE = 21;
    uint256 public constant TAX_DENOMINATOR = 100;
    
    // Addresses
    address public treasuryWallet;
    address public liquidityWallet;
    
    // Trading state
    bool public tradingEnabled = false;
    mapping(address => bool) public isExcludedFromTax;
    
    // Events
    event TreasuryWalletUpdated(address indexed oldWallet, address indexed newWallet);
    event LiquidityWalletUpdated(address indexed oldWallet, address indexed newWallet);
    event TradingEnabled(bool enabled);
    event TaxExclusionUpdated(address indexed account, bool excluded);
    event TaxCollected(address indexed from, uint256 amount);
    
    constructor(
        string memory name,
        string memory symbol,
        uint256 initialSupply,
        address _treasuryWallet,
        address _liquidityWallet
    ) ERC20(name, symbol) {
        require(_treasuryWallet != address(0), "Treasury wallet cannot be zero address");
        require(_liquidityWallet != address(0), "Liquidity wallet cannot be zero address");
        
        treasuryWallet = _treasuryWallet;
        liquidityWallet = _liquidityWallet;
        
        // Exclude owner and wallets from tax
        isExcludedFromTax[owner()] = true;
        isExcludedFromTax[_treasuryWallet] = true;
        isExcludedFromTax[_liquidityWallet] = true;
        
        // Mint initial supply to owner
        _mint(owner(), initialSupply * 10**decimals());
    }
    
    /**
     * @dev Override transfer function to apply sell tax
     */
    function _transfer(
        address from,
        address to,
        uint256 amount
    ) internal virtual override {
        require(from != address(0), "Transfer from zero address");
        require(to != address(0), "Transfer to zero address");
        require(amount > 0, "Transfer amount must be greater than zero");
        
        // Check if trading is enabled
        if (!tradingEnabled && !isExcludedFromTax[from] && !isExcludedFromTax[to]) {
            revert("Trading not enabled");
        }
        
        // Calculate tax
        uint256 taxAmount = 0;
        if (!isExcludedFromTax[from] && !isExcludedFromTax[to]) {
            // Apply sell tax (when selling to liquidity pool)
            if (to == liquidityWallet) {
                taxAmount = (amount * SELL_TAX_PERCENTAGE) / TAX_DENOMINATOR;
            }
        }
        
        uint256 transferAmount = amount - taxAmount;
        
        // Transfer tokens
        super._transfer(from, to, transferAmount);
        
        // Collect tax
        if (taxAmount > 0) {
            super._transfer(from, treasuryWallet, taxAmount);
            emit TaxCollected(from, taxAmount);
        }
    }
    
    /**
     * @dev Mint tokens (owner only)
     */
    function mint(address to, uint256 amount) external onlyOwner {
        _mint(to, amount);
    }
    
    /**
     * @dev Burn tokens
     */
    function burn(uint256 amount) external {
        _burn(msg.sender, amount);
    }
    
    /**
     * @dev Burn tokens from specific address (owner only)
     */
    function burnFrom(address account, uint256 amount) external onlyOwner {
        _burn(account, amount);
    }
    
    /**
     * @dev Update treasury wallet
     */
    function updateTreasuryWallet(address newTreasuryWallet) external onlyOwner {
        require(newTreasuryWallet != address(0), "Treasury wallet cannot be zero address");
        address oldWallet = treasuryWallet;
        treasuryWallet = newTreasuryWallet;
        
        // Update tax exclusion
        isExcludedFromTax[oldWallet] = false;
        isExcludedFromTax[newTreasuryWallet] = true;
        
        emit TreasuryWalletUpdated(oldWallet, newTreasuryWallet);
    }
    
    /**
     * @dev Update liquidity wallet
     */
    function updateLiquidityWallet(address newLiquidityWallet) external onlyOwner {
        require(newLiquidityWallet != address(0), "Liquidity wallet cannot be zero address");
        address oldWallet = liquidityWallet;
        liquidityWallet = newLiquidityWallet;
        
        // Update tax exclusion
        isExcludedFromTax[oldWallet] = false;
        isExcludedFromTax[newLiquidityWallet] = true;
        
        emit LiquidityWalletUpdated(oldWallet, newLiquidityWallet);
    }
    
    /**
     * @dev Enable/disable trading
     */
    function setTradingEnabled(bool enabled) external onlyOwner {
        tradingEnabled = enabled;
        emit TradingEnabled(enabled);
    }
    
    /**
     * @dev Exclude/include address from tax
     */
    function setTaxExclusion(address account, bool excluded) external onlyOwner {
        isExcludedFromTax[account] = excluded;
        emit TaxExclusionUpdated(account, excluded);
    }
    
    /**
     * @dev Batch exclude/include addresses from tax
     */
    function batchSetTaxExclusion(address[] memory accounts, bool excluded) external onlyOwner {
        for (uint256 i = 0; i < accounts.length; i++) {
            isExcludedFromTax[accounts[i]] = excluded;
            emit TaxExclusionUpdated(accounts[i], excluded);
        }
    }
    
    /**
     * @dev Get tax amount for a transfer
     */
    function getTaxAmount(uint256 amount) external pure returns (uint256) {
        return (amount * SELL_TAX_PERCENTAGE) / TAX_DENOMINATOR;
    }
    
    /**
     * @dev Get transfer amount after tax
     */
    function getTransferAmountAfterTax(uint256 amount) external pure returns (uint256) {
        return amount - ((amount * SELL_TAX_PERCENTAGE) / TAX_DENOMINATOR);
    }
    
    /**
     * @dev Check if address is excluded from tax
     */
    function isExcludedFromTaxCheck(address account) external view returns (bool) {
        return isExcludedFromTax[account];
    }
    
    /**
     * @dev Get contract information
     */
    function getContractInfo() external view returns (
        uint256 totalSupply_,
        uint256 sellTaxPercentage_,
        address treasuryWallet_,
        address liquidityWallet_,
        bool tradingEnabled_
    ) {
        return (
            totalSupply(),
            SELL_TAX_PERCENTAGE,
            treasuryWallet,
            liquidityWallet,
            tradingEnabled
        );
    }
    
    /**
     * @dev Emergency function to recover stuck tokens
     */
    function recoverTokens(address tokenAddress, uint256 amount) external onlyOwner {
        require(tokenAddress != address(this), "Cannot recover own token");
        IERC20(tokenAddress).transfer(owner(), amount);
    }
    
    /**
     * @dev Emergency function to recover stuck ETH
     */
    function recoverETH() external onlyOwner {
        uint256 balance = address(this).balance;
        require(balance > 0, "No ETH to recover");
        payable(owner()).transfer(balance);
    }
}
