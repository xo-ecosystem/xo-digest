// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract MiniAMM {
    IERC20 public immutable token;
    uint112 public reserveToken; // token reserve
    uint112 public reserveETH;   // ETH reserve (in wei)
    uint32  public blockTimestampLast;

    event Sync(uint112 reserveToken, uint112 reserveETH);
    event AddLiquidity(address indexed provider, uint256 tokenIn, uint256 ethIn);
    event SwapT2E(address indexed caller, uint256 tokenIn, uint256 ethOut, address to);
    event SwapE2T(address indexed caller, uint256 ethIn, uint256 tokenOut, address to);

    constructor(address token_) { token = IERC20(token_); }

    function _update(uint256 balToken, uint256 balETH) internal {
        reserveToken = uint112(balToken);
        reserveETH   = uint112(balETH);
        blockTimestampLast = uint32(block.timestamp);
        emit Sync(reserveToken, reserveETH);
    }

    function sync() public {
        _update(token.balanceOf(address(this)), address(this).balance);
    }

    function addLiquidity(uint256 tokenAmount) external payable {
        require(tokenAmount > 0 && msg.value > 0, "bad liq");
        require(token.transferFrom(msg.sender, address(this), tokenAmount), "t xfer fail");
        _update(token.balanceOf(address(this)), address(this).balance);
        emit AddLiquidity(msg.sender, tokenAmount, msg.value);
    }

    function _getOut(uint256 amtIn, uint256 resIn, uint256 resOut) internal pure returns (uint256) {
        // 0.3% fee
        uint256 amtInWithFee = amtIn * 997;
        return (amtInWithFee * resOut) / (resIn * 1000 + amtInWithFee);
    }

    function swapTokensForETH(uint256 tokenIn, uint256 minEthOut, address to) external {
        require(token.transferFrom(msg.sender, address(this), tokenIn), "t xferFrom fail");
        uint256 ethOut = _getOut(tokenIn, reserveToken, reserveETH);
        require(ethOut >= minEthOut, "slippage");
        (bool ok,) = payable(to).call{value: ethOut}("");
        require(ok, "eth xfer fail");
        _update(token.balanceOf(address(this)), address(this).balance);
        emit SwapT2E(msg.sender, tokenIn, ethOut, to);
    }

    function swapETHForTokens(uint256 minTokenOut, address to) external payable {
        uint256 tokenOut = _getOut(msg.value, reserveETH, reserveToken);
        require(tokenOut >= minTokenOut, "slippage");
        require(token.transfer(to, tokenOut), "t xfer fail");
        _update(token.balanceOf(address(this)), address(this).balance);
        emit SwapE2T(msg.sender, msg.value, tokenOut, to);
    }

    receive() external payable {}
}
