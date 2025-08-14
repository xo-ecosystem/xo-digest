// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {ERC20} from "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";

/// @notice Minimal demo AMM pair (constant product). Not production safe.
///         LP token is this contract (ERC20). 0.3% fee skim to feeTo (optional).
contract DemoPair is ERC20, Ownable {
    address public token0;
    address public token1;
    address public feeTo;      // e.g., ShieldAether vault
    uint256 public feeBps;     // 30 = 0.3%

    uint112 private reserve0;
    uint112 private reserve1;

    error InvalidToken();
    error InsufficientLiquidity();
    error InsufficientInput();

    constructor(address _t0, address _t1, address _owner, address _feeTo, uint256 _feeBps)
        ERC20("XO-LP", "XO-LP")
        Ownable(_owner)
    {
        require(_t0 != _t1 && _t0 != address(0) && _t1 != address(0), "bad tokens");
        token0 = _t0; token1 = _t1;
        feeTo = _feeTo;
        feeBps = _feeBps;
    }

    function setFee(address _feeTo, uint256 _feeBps) external onlyOwner {
        require(_feeBps <= 100, "max 1%");
        feeTo = _feeTo;
        feeBps = _feeBps;
    }

    function getReserves() public view returns (uint112, uint112) { return (reserve0, reserve1); }

    function _update(uint256 bal0, uint256 bal1) private {
        reserve0 = uint112(bal0);
        reserve1 = uint112(bal1);
    }

    function _balance0() private view returns (uint256) { return IERC20(token0).balanceOf(address(this)); }
    function _balance1() private view returns (uint256) { return IERC20(token1).balanceOf(address(this)); }

    function addLiquidity(uint256 /* amount0 */, uint256 /* amount1 */) external returns (uint256 liquidity) {
        // Router should have transferred tokens to this contract already
        (uint112 r0, uint112 r1) = (reserve0, reserve1);
        uint256 bal0 = _balance0();
        uint256 bal1 = _balance1();
        uint256 amt0 = bal0 - uint256(r0);
        uint256 amt1 = bal1 - uint256(r1);

        if (r0 == 0 && r1 == 0) {
            liquidity = sqrt(amt0 * amt1);
        } else {
            uint256 l0 = (totalSupply() * amt0) / r0;
            uint256 l1 = (totalSupply() * amt1) / r1;
            liquidity = l0 < l1 ? l0 : l1;
        }
        require(liquidity > 0, "liquidity=0");
        _mint(msg.sender, liquidity);
        _update(_balance0(), _balance1());
    }

    function removeLiquidity(uint256 liquidity) external returns (uint256 out0, uint256 out1) {
        require(liquidity > 0 && liquidity <= balanceOf(msg.sender), "bad liq");
        uint256 supply = totalSupply();
        out0 = (IERC20(token0).balanceOf(address(this)) * liquidity) / supply;
        out1 = (IERC20(token1).balanceOf(address(this)) * liquidity) / supply;
        _burn(msg.sender, liquidity);
        IERC20(token0).transfer(msg.sender, out0);
        IERC20(token1).transfer(msg.sender, out1);
        _update(_balance0(), _balance1());
    }

    function swap(address inToken, uint256 amountIn, address to) external returns (uint256 amountOut) {
        if (!(inToken == token0 || inToken == token1)) revert InvalidToken();
        require(amountIn > 0, "zero in");
        address outToken = inToken == token0 ? token1 : token0;

        // Tokens should already be transferred to this contract by the router
        (uint112 r0, uint112 r1) = (reserve0, reserve1);
        uint256 xRes = inToken == token0 ? uint256(r0) : uint256(r1);
        uint256 yRes = inToken == token0 ? uint256(r1) : uint256(r0);

        // Determine actual amount in from balance delta
        uint256 balIn = inToken == token0 ? _balance0() : _balance1();
        uint256 amountInGross = balIn - xRes;
        require(amountInGross >= amountIn, "insufficient in");

        // Apply fee (skim from pair to feeTo)
        uint256 fee = (amountInGross * feeBps) / 10_000;
        uint256 amountAfterFee = amountInGross - fee;
        if (fee > 0 && feeTo != address(0)) {
            IERC20(inToken).transfer(feeTo, fee);
            // Recompute balIn after fee transfer for accurate reserves update later
            balIn -= fee;
        }

        require(xRes > 0 && yRes > 0, "empty pool");
        uint256 k = xRes * yRes;
        uint256 newX = xRes + amountAfterFee;
        uint256 newY = k / newX;
        amountOut = yRes - newY;
        require(amountOut > 0, "no out");

        IERC20(outToken).transfer(to, amountOut);
        _update(_balance0(), _balance1());
    }

    function sqrt(uint256 y) private pure returns (uint256 z) {
        if (y > 3) { z = y; uint256 x = y / 2 + 1; while (x < z) { z = x; x = (y / x + x) / 2; } }
        else if (y != 0) { z = 1; }
    }
}
