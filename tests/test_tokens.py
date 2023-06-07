from tests.Utils.compound_helper import pre_borrow, pre_repay, pre_mint, pre_redeem, pre_liquidate, set_ether_balance


def test_borrow_fresh(cToken, bob, alice, report):
    borrowed_amount = 30
    pre_borrow(cToken, alice, 300)
    protocol_cash_before = cToken.underlying.balanceOf(cToken.token.address)
    account_cash_before = cToken.underlying.balanceOf(bob.address)
    tx = cToken.token.harnessBorrowFresh(bob.address, borrowed_amount, {"from": bob})
    account_cash_after = cToken.underlying.balanceOf(bob.address)
    protocol_cash_after = cToken.underlying.balanceOf(cToken.token.address)
    assert protocol_cash_before - protocol_cash_after == borrowed_amount
    assert account_cash_after - account_cash_before == borrowed_amount
    report.add_action("borrow erc20 cToken", tx.gas_used, tx.gas_price, tx.txid)


def test_borrow_fresh_cether(cToken_cether, bob, alice, report):
    borrowed_amount = 300000
    pre_borrow(cToken_cether, alice, 300)
    set_ether_balance(cToken_cether.token, borrowed_amount, alice)

    total_before = cToken_cether.token.totalBorrows()
    bob_balance_before = bob.balance()
    tx = cToken_cether.token.harnessBorrowFresh(bob.address, borrowed_amount, {"from": bob})
    total_after = cToken_cether.token.totalBorrows()
    assert total_after == total_before + borrowed_amount
    assert bob.balance() < bob_balance_before + borrowed_amount
    report.add_action("borrow ether cToken", tx.gas_used, tx.gas_price, tx.txid)


def test_borrow(cToken, bob, alice):
    borrowed_amount = 30
    pre_borrow(cToken, alice, 300)
    protocol_cash_before = cToken.underlying.balanceOf(cToken.token.address)
    account_cash_before = cToken.underlying.balanceOf(bob.address)

    cToken.token.harnessFastForward(1, {"from": bob})
    cToken.token.borrow(borrowed_amount, {"from": bob})

    account_cash_after = cToken.underlying.balanceOf(bob.address)
    protocol_cash_after = cToken.underlying.balanceOf(cToken.token.address)
    assert protocol_cash_before - protocol_cash_after == borrowed_amount
    assert account_cash_after - account_cash_before == borrowed_amount


def test_repay(cToken, bob, alice, report):
    pre_repay(cToken, bob, bob, 300)
    principal_before = cToken.token.harnessAccountBorrows(bob)[0]
    repay_amount = 40
    cToken.token.harnessFastForward(1, {"from": bob})
    tx = cToken.token.repayBorrowBehalf(bob, repay_amount, {"from": bob})
    principal_after = cToken.token.harnessAccountBorrows(bob)[0]
    assert principal_after == principal_before - repay_amount
    report.add_action("Repay borrow erc20 cToken", tx.gas_used, tx.gas_price, tx.txid)


def test_mint(cToken, alice, report):
    account_cash_before = cToken.underlying.balanceOf(alice.address)
    protocol_cash_before = cToken.underlying.balanceOf(cToken.token.address)
    exchange_rate = 50e3
    mint_amount = 10e4
    pre_mint(cToken, alice, mint_amount, exchange_rate)
    tx = cToken.token.harnessMintFresh(alice, mint_amount, {"from": alice})

    account_cash_after = cToken.underlying.balanceOf(alice.address)
    protocol_cash_after = cToken.underlying.balanceOf(cToken.token.address)
    assert account_cash_after == account_cash_before - mint_amount
    assert protocol_cash_after == protocol_cash_before + mint_amount
    report.add_action("Mint erc20 cToken", tx.gas_used, tx.gas_price, tx.txid)


def test_mint_cether(cToken_cether, alice, report):
    balance_before = alice.balance()
    exchange_rate = 5
    mint_amount = 10000
    pre_mint(cToken_cether, alice, mint_amount, exchange_rate)
    tx = cToken_cether.token.mint({"from": alice, "value": mint_amount})
    balance_after = alice.balance()
    assert balance_after < balance_before - mint_amount
    report.add_action("Mint ether cToken", tx.gas_used, tx.gas_price, tx.txid)


def test_redeem(cToken, alice, report):
    redeem_tokens = 10000
    exchange_rate = 50e3
    redeem_amount = redeem_tokens * exchange_rate
    pre_redeem(cToken, alice, redeem_tokens, redeem_amount, exchange_rate)
    balance_before = cToken.token.balanceOf(alice.address)

    tx = cToken.token.harnessRedeemFresh(alice, redeem_tokens, 0, {"from": alice})

    balance_after = cToken.token.balanceOf(alice.address)
    assert balance_after == balance_before - redeem_tokens
    report.add_action("Redeem erc20 cToken", tx.gas_used, tx.gas_price, tx.txid)


def test_transfer(cToken_unitroller, alice, bob, report):
    cToken_unitroller.comptroller._supportMarket(cToken_unitroller.token.address, {"from": alice})
    cToken_unitroller.token.harnessSetBalance(alice.address, 100, {"from": alice})
    alice_balance_before = cToken_unitroller.token.balanceOf(alice.address)
    bob_balance_before = cToken_unitroller.token.balanceOf(bob.address)
    transfer_amount = 50
    tx = cToken_unitroller.token.transfer(bob.address, transfer_amount, {"from": alice})
    alice_balance_after = cToken_unitroller.token.balanceOf(alice.address)
    bob_balance_after = cToken_unitroller.token.balanceOf(bob.address)
    assert alice_balance_after == alice_balance_before - transfer_amount
    assert bob_balance_after == bob_balance_before + transfer_amount
    report.add_action("Transfer erc20 cToken", tx.gas_used, tx.gas_price, tx.txid)


def test_add_reserves_for_cether(cToken_cether, alice, report):
    reserved_added = 10000
    tx = cToken_cether.token._addReserves({"value": reserved_added, "from": alice})
    assert cToken_cether.token.totalReserves() == reserved_added
    report.add_action("Add reserves for ether cToken", tx.gas_used, tx.gas_price, tx.txid)


def test_liquidate(cToken, cToken_collateral, alice, bob, report):
    repay_amount = 10
    cToken_collateral.token.harnessSetExchangeRate(2, {"from": alice})
    pre_liquidate(cToken, alice, bob, alice, repay_amount, cToken_collateral)
    liquidator_balance_before = cToken.underlying.balanceOf(alice.address)
    contract_balance_before = cToken.underlying.balanceOf(cToken.token.address)
    print(alice.balance())
    print(bob.balance())
    tx = cToken.token.harnessLiquidateBorrowFresh(alice, bob, repay_amount, cToken_collateral.token.address,
                                                  {"from": alice})

    liquidator_balance_after = cToken.underlying.balanceOf(alice.address)
    contract_balance_after = cToken.underlying.balanceOf(cToken.token.address)
    assert liquidator_balance_after == liquidator_balance_before - repay_amount
    assert contract_balance_after == contract_balance_before + repay_amount
    report.add_action("Liquidate borrow", tx.gas_used, tx.gas_price, tx.txid)


def test_comp_like_token(cToken_comp, alice, bob):
    cToken_comp.token._delegateCompLikeTo(bob.address, {"from": alice})
    cToken_comp.underlying.transfer(cToken_comp.token.address, 1, {"from": alice})
    votes = cToken_comp.underlying.getCurrentVotes(bob.address, {"from": alice})
    assert votes == 1
