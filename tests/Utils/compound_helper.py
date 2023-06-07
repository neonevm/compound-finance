def pre_borrow(cToken, borrower, amount):
    cToken.comptroller.setBorrowAllowed(True, {"from": borrower})
    cToken.comptroller.setBorrowVerify(True, {"from": borrower})
    cToken.interestRateModel.setFailBorrowRate(False, {"from": borrower})
    if cToken.underlying is not None:
        cToken.underlying.harnessSetBalance(cToken.token.address, amount, {"from": borrower})
    cToken.token.harnessSetFailTransferToAddress(borrower, False, {"from": borrower})
    cToken.token.harnessSetAccountBorrows(borrower, 0, 0, {"from": borrower})
    cToken.token.harnessSetTotalBorrows(0, {"from": borrower})


def pre_repay(cToken, benefactor, borrower, amount):
    cToken.comptroller.setRepayBorrowAllowed(True, {"from": borrower})
    cToken.comptroller.setRepayBorrowVerify(True, {"from": borrower})
    cToken.interestRateModel.setFailBorrowRate(False, {"from": borrower})
    cToken.underlying.harnessSetFailTransferFromAddress(benefactor, False, {"from": borrower})
    cToken.underlying.harnessSetFailTransferFromAddress(borrower, False, {"from": borrower})
    cToken.underlying.harnessSetBalance(borrower, amount, {"from": borrower})
    pretend_borrow(cToken, borrower,borrower, 1, 1, amount)
    cToken.underlying.approve(cToken.token.address, amount, {"from": borrower})
    cToken.underlying.approve(cToken.token.address, amount, {"from": benefactor})


def pretend_borrow(cToken,borrower, sender, account_index, market_index, principal_raw, block_number=2e7 ):
    cToken.token.harnessSetTotalBorrows(principal_raw, {"from": sender})
    cToken.token.harnessSetAccountBorrows(borrower.address, principal_raw, account_index, {"from": sender})
    cToken.token.harnessSetBorrowIndex(market_index, {"from": sender})
    cToken.token.harnessSetAccrualBlockNumber(block_number, {"from": sender})
    cToken.token.harnessSetBlockNumber(block_number, {"from": sender})

def pre_mint(cToken, minter, amount, exchange_rate):
    if cToken.underlying is not None:
        cToken.underlying.approve(cToken.token.address, amount, {"from": minter})
    cToken.comptroller.setMintAllowed(True, {"from": minter})
    cToken.comptroller.setMintVerify(True, {"from": minter})
    cToken.interestRateModel.setFailBorrowRate(False, {"from": minter})
    if cToken.underlying is not None:
        cToken.underlying.harnessSetFailTransferFromAddress(minter.address, False, {"from": minter})
    cToken.token.harnessSetBalance(minter.address, 0, {"from": minter})
    cToken.token.harnessSetExchangeRate(exchange_rate, {"from": minter})


def pre_redeem(cToken, redeemer, tokens, amount, exchange_rate):
    cToken.token.harnessSetTotalSupply(tokens, {"from": redeemer} )
    cToken.token.harnessSetBalance(redeemer, tokens, {"from": redeemer})
    cToken.comptroller.setRedeemAllowed(True, {"from": redeemer})
    cToken.comptroller.setRedeemVerify(True, {"from": redeemer})
    cToken.interestRateModel.setFailBorrowRate(False, {"from": redeemer})
    cToken.underlying.harnessSetBalance(cToken.token.address, amount, {"from": redeemer})
    cToken.underlying.harnessSetBalance(redeemer, 0, {"from": redeemer})
    cToken.underlying.harnessSetFailTransferToAddress(redeemer, False, {"from": redeemer})
    cToken.token.harnessSetExchangeRate(exchange_rate, {"from": redeemer})

def pre_liquidate(cToken, liquidator, borrower, sender, repay_amount, cToken_collateral):
    seize_tokens  = repay_amount * 4
    cToken.comptroller.setLiquidateBorrowAllowed(True, {"from": sender})
    cToken.comptroller.setLiquidateBorrowVerify(True,{"from": sender})
    cToken.comptroller.setRepayBorrowAllowed(True,{"from": sender})
    cToken.comptroller.setRepayBorrowVerify(True, {"from": sender})
    cToken.comptroller.setSeizeAllowed(True, {"from": sender})
    cToken.comptroller.setSeizeVerify(True, {"from": sender})
    cToken.comptroller.setFailCalculateSeizeTokens(False, {"from": sender})
    cToken.underlying.harnessSetFailTransferFromAddress(liquidator.address, False, {"from": sender})
    cToken.interestRateModel.setFailBorrowRate(False, {"from": sender})
    cToken_collateral.interestRateModel.setFailBorrowRate(False, {"from": sender})
    cToken_collateral.comptroller.setCalculatedSeizeTokens(seize_tokens, {"from": sender})
    cToken_collateral.token.harnessSetTotalSupply(1000000, {"from": sender})

    cToken_collateral.token.harnessSetBalance(liquidator.address, 0,{"from": sender})
    cToken_collateral.token.harnessSetBalance(borrower.address, seize_tokens, {"from": sender})
    pretend_borrow(cToken_collateral,borrower,sender, 0, 1, 0)
    pretend_borrow(cToken, borrower,sender, 1, 1, repay_amount)
    cToken.underlying.approve(cToken.token.address, repay_amount, {"from": liquidator})


def set_ether_balance(cEther, balance, root):
    current = cEther.balance()
    cEther.harnessDoTransferOut(root, current, {"from": root})
    cEther.harnessDoTransferIn(root, balance, {"from": root, "value": balance})

