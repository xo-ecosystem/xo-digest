// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";

interface IPair {
    function token0() external view returns (address);
    function token1() external view returns (address);
    function addLiquidity(uint256 amount0, uint256 amount1) external returns (uint256 liquidity);
    function removeLiquidity(uint256 liquidity) external returns (uint256 out0, uint256 out1);
    function swap(address inToken, uint256 amountIn, address to) external returns (uint256 amountOut);
}

contract DemoRouter is Ownable {
    constructor(address initialOwner) Ownable(initialOwner) {}

    function addLiquidity(
        address pair,
        uint256 amt0,
        uint256 amt1
    ) external returns (uint256 lpOut) {
        address t0 = IPair(pair).token0();
        address t1 = IPair(pair).token1();
        IERC20(t0).transferFrom(msg.sender, pair, amt0);
        IERC20(t1).transferFrom(msg.sender, pair, amt1);
        lpOut = IPair(pair).addLiquidity(0, 0); // pair already received tokens
    }

    function removeLiquidity(address pair, uint256 lp) external returns (uint256 out0, uint256 out1) {
        // Pull LP in then transfer to pair? Simpler: pair burns from sender; approve pair first.
        (out0, out1) = IPair(pair).removeLiquidity(lp);
    }

    function swapExactTokensForTokens(address pair, address inToken, uint256 amountIn, address to)
        external
        returns (uint256 amountOut)
    {
        IERC20(inToken).transferFrom(msg.sender, pair, amountIn);
        amountOut = IPair(pair).swap(inToken, amountIn, to);
    }
}
