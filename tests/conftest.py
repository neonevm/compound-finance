import os

import pytest
from brownie import web3, Contract

from tests.Utils.report import Report
from tests.Utils.types import Contracts


@pytest.fixture(scope="session")
def add_accounts(accounts):
    account_keys = os.environ.get("ACCOUNTS").split(',')
    accounts.add(web3.eth.account.from_key(account_keys[0]).key)
    accounts.add(web3.eth.account.from_key(account_keys[1]).key)
    yield accounts


@pytest.fixture(scope="session")
def alice(add_accounts, accounts):
    yield accounts[0]


@pytest.fixture(scope="session")
def bob(add_accounts, accounts):
    yield accounts[1]


@pytest.fixture(scope="session")
def report():
    report = Report('Compound-finance')
    yield report
    report.save_to_json('compound')


def deploy_cdelegator(contract, underlying, interestRateModel, comptroller, cDelegatee, admin):
    exchangeRate = 1
    decimals = 8
    symbol = "cOMG"
    name = "CToken cOMG"
    return contract.deploy(underlying.address, comptroller.address, interestRateModel.address,
                           exchangeRate, name, symbol, decimals,
                           admin, cDelegatee.address, "0x0", {"from": admin})


@pytest.fixture(scope="session")
def cToken(CErc20Delegator, alice, ERC20Harness, CErc20DelegateHarness, bool_comptroller, InterestRateModelHarness):
    underlying = make_erc20(ERC20Harness, alice)
    cDelegatee = CErc20DelegateHarness.deploy({"from": alice})
    interestRateModel = InterestRateModelHarness.deploy(0, {"from": alice})
    cDelegator = deploy_cdelegator(CErc20Delegator, underlying, interestRateModel, bool_comptroller, cDelegatee, alice)
    token = Contract.from_abi("CErc20DelegateHarness", cDelegator.address, CErc20DelegateHarness.abi)
    return Contracts(token, bool_comptroller, interestRateModel, underlying)


@pytest.fixture(scope="session")
def cToken_comp(Comp, CErc20DelegateHarness, CErc20Delegator, bool_comptroller, alice, InterestRateModelHarness):
    underlying = Comp.deploy(alice, {"from": alice})
    cDelegatee = CErc20DelegateHarness.deploy({"from": alice})
    interestRateModel = InterestRateModelHarness.deploy(0, {"from": alice})
    cDelegator = deploy_cdelegator(CErc20Delegator, underlying, interestRateModel, bool_comptroller, cDelegatee, alice)
    token = Contract.from_abi("CErc20DelegateHarness", cDelegator.address, CErc20DelegateHarness.abi)
    return Contracts(token, bool_comptroller, interestRateModel, underlying)


@pytest.fixture(scope="session")
def cToken_collateral(cToken, CErc20Delegator, ERC20Harness,
                      CErc20DelegateHarness, InterestRateModelHarness, alice):
    underlying = make_erc20(ERC20Harness, alice)
    cDelegatee = CErc20DelegateHarness.deploy({"from": alice})
    interestRateModel = InterestRateModelHarness.deploy(0, {"from": alice})
    cdelegator = deploy_cdelegator(CErc20Delegator, underlying, interestRateModel,
                                   cToken.comptroller, cDelegatee, alice)
    token = Contract.from_abi("CErc20DelegateHarness", cdelegator.address, CErc20DelegateHarness.abi)

    token.harnessSetExchangeRate(2, {"from": alice})

    return Contracts(token, cToken.comptroller, interestRateModel, underlying)


@pytest.fixture(scope="session")
def cToken_cether(CEtherHarness, alice, bool_comptroller, InterestRateModelHarness):
    interestRateModel = InterestRateModelHarness.deploy(0, {"from": alice})
    exchange_rate = 1
    decimals = 8
    symbol = "cETH"
    name = "CToken cETH"
    admin = alice
    token = CEtherHarness.deploy(bool_comptroller.address, interestRateModel.address,
                                 exchange_rate, name, symbol, decimals,
                                 admin, {"from": alice})
    return Contracts(token, bool_comptroller, interestRateModel, None)


@pytest.fixture(scope="session")
def cToken_unitroller(ERC20Harness, CErc20DelegateHarness, CErc20Delegator, alice, unitroller_comptroller,
                      InterestRateModelHarness):
    underlying = make_erc20(ERC20Harness, alice)
    cDelegatee = CErc20DelegateHarness.deploy({"from": alice})
    interestRateModel = InterestRateModelHarness.deploy(0, {"from": alice})
    exchangeRate = 1
    decimals = 8
    symbol = "cOMG"
    name = "CToken cOMG"
    admin = alice
    cDelegator = CErc20Delegator.deploy(underlying.address, unitroller_comptroller.address, interestRateModel.address,
                                        exchangeRate, name, symbol, decimals,
                                        admin, cDelegatee.address, "0x0", {"from": alice})
    token = Contract.from_abi("CErc20DelegateHarness", cDelegator.address, CErc20DelegateHarness.abi)
    return Contracts(token, unitroller_comptroller, interestRateModel, underlying)


def make_erc20(contract, sender):
    quantity = 1e25
    decimals = 18
    symbol = 'OMG'
    name = 'Erc20 OMG'
    return contract.deploy(quantity, name, decimals, symbol, {"from": sender})


@pytest.fixture(scope="session")
def bool_comptroller(BoolComptroller, alice):
    return BoolComptroller.deploy({"from": alice})


@pytest.fixture(scope="session")
def unitroller_comptroller(Unitroller, ComptrollerHarness, alice, priceOracle, Comp):
    unitroller = Unitroller.deploy({"from": alice})
    comptroller = ComptrollerHarness.deploy({"from": alice})
    closeFactor = 0.051
    liquidationIncentive = 1
    comp = Comp.deploy(alice.address, {"from": alice})
    compRate = 1e18

    unitroller._setPendingImplementation(comptroller.address, {"from": alice})
    comptroller._become(unitroller.address, {"from": alice})
    # merge interfaces ?
    unitroller = Contract.from_abi("ComptrollerHarness", unitroller.address, ComptrollerHarness.abi)
    unitroller._setLiquidationIncentive(liquidationIncentive, {"from": alice})
    unitroller._setCloseFactor(closeFactor, {"from": alice})
    unitroller._setPriceOracle(priceOracle.address, {"from": alice})
    unitroller.setCompAddress(comp.address, {"from": alice})
    unitroller.harnessSetCompRate(compRate, {"from": alice})

    return unitroller


@pytest.fixture(scope="session")
def priceOracle(SimplePriceOracle, alice):
    return SimplePriceOracle.deploy({"from": alice})
