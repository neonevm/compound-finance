import typing
from dataclasses import dataclass

from brownie import Contract


@dataclass
class Contracts:
    token: Contract
    comptroller: Contract
    interestRateModel: Contract
    underlying: typing.Optional[Contract] = None
