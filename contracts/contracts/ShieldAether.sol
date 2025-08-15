// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

interface IVault {
    function balance() external view returns (uint256);
}

contract ShieldAether is ERC20, Ownable {
    IVault public immutable vault;

    constructor(address vault_, address owner_) ERC20("Shield Aether (Demo)", "sAETH") Ownable(owner_) {
        require(vault_ != address(0), "vault=0");
        vault = IVault(vault_);
    }

    function mint(address to, uint256 amount) external onlyOwner {
        _mint(to, amount);
    }

    function redeem(uint256 amount) external {
        uint256 ts = totalSupply();
        require(ts > 0 && amount > 0, "bad amount");
        uint256 payout = (address(payable(address(vault))).balance * amount) / ts;
        _burn(msg.sender, amount);
        (bool ok,) = payable(msg.sender).call{value: payout}("");
        require(ok, "ETH transfer failed");
    }

    /// ETH (wei) backing per 1e18 sAETH, scaled by 1e18
    function backingPerToken_wei1e18() external view returns (uint256) {
        uint256 ts = totalSupply();
        if (ts == 0) return 0;
        return (address(payable(address(vault))).balance * 1e18) / ts;
    }

    receive() external payable {}
}
