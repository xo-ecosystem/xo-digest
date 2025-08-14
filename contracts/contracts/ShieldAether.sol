// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {ERC20} from "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";

/// @title ShieldAether (sAETH)
/// @notice ETH-backed “shield” token. Vault holds ETH. Redeem pays a % of backing per token (performance peg).
///         For a live product you’ll likely prefer WETH custody + audits. This is demo-grade.
contract ShieldAether is ERC20, Ownable {
    /// @dev Redeem basis points; e.g., 2100 => 21% of backing per token redeemed.
    uint256 public redeemBps;       // default e.g., 2100 (21%)
    uint256 public keeperRewardBps; // reward on convertFees (in ETH share of transferred-in amount)

    event Deposited(address indexed from, uint256 amount);
    event Redeemed(address indexed to, uint256 sAmount, uint256 ethOut);
    event FeesConverted(address indexed keeper, uint256 ethIn, uint256 rewardPaid);
    event ParamsSet(uint256 redeemBps, uint256 keeperRewardBps);

    constructor(address initialOwner, uint256 redeemBps_, uint256 keeperRewardBps_)
        ERC20("Shield Aether", "sAETH")
        Ownable(initialOwner)
    {
        redeemBps = redeemBps_;
        keeperRewardBps = keeperRewardBps_;
    }

    /// @notice 1:1 mint on deposit for demo (1 ETH -> 1 sAETH).
    ///         You can adjust to a bonding curve or time-based schedule later.
    function deposit() external payable {
        require(msg.value > 0, "no ETH");
        _mint(msg.sender, msg.value);
        emit Deposited(msg.sender, msg.value);
    }

    /// @dev Backing per token = address(this).balance / totalSupply (in 1e18 scale since we use ETH and 18 d.p.)
    function backingPerToken() public view returns (uint256) {
        uint256 ts = totalSupply();
        if (ts == 0) return 0;
        return address(this).balance * 1e18 / ts;
    }

    function setParams(uint256 redeemBps_, uint256 keeperRewardBps_) external onlyOwner {
        require(redeemBps_ <= 10_000 && keeperRewardBps_ <= 2000, "bps out of range");
        redeemBps = redeemBps_;
        keeperRewardBps = keeperRewardBps_;
        emit ParamsSet(redeemBps, keeperRewardBps);
    }

    /// @notice Burn sAETH to redeem ETH; receives redeemBps% of backing-per-token * amount.
    function redeem(uint256 sAmount) external {
        require(sAmount > 0, "zero");
        uint256 bpt = backingPerToken(); // in 1e18 ETH units per sAETH
        uint256 ethGross = sAmount * bpt / 1e18;
        uint256 ethOut   = ethGross * redeemBps / 10_000;
        require(ethOut <= address(this).balance, "insufficient vault");
        _burn(msg.sender, sAmount);
        (bool ok, ) = msg.sender.call{value: ethOut}("");
        require(ok, "ETH xfer fail");
        emit Redeemed(msg.sender, sAmount, ethOut);
    }

    /// @notice Demo keeper hook: when LP fees (ETH) are sent here, caller triggers accounting & is paid keeper reward.
    ///         In this simple version, we assume fees are transferred into this contract before calling.
    function convertFees() external {
        // Track pre-balance? For demo we treat entire msg.value==0, so use delta via parameter? Simpler:
        // In practice, router/pair would call this with value; here we just reward small tip from vault to caller.
        uint256 reward = address(this).balance * keeperRewardBps / 10_000;
        if (reward > 0) {
            (bool ok, ) = msg.sender.call{value: reward}("");
            require(ok, "keeper reward fail");
        }
        emit FeesConverted(msg.sender, 0, reward);
    }

    receive() external payable {}
}

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
