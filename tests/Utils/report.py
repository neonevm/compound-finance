import json
import pathlib


class Report:
    def __init__(self, name, ):
        self.name = name
        self.actions = []

    def add_action(self, name, used_gas, gas_price, tx):
        self.actions.append({"name": name,
                             "usedGas": used_gas,
                             "gasPrice": gas_price,
                             "tx": tx})

    def save_to_json(self, prefix):
        data = {"name": self.name, "actions": self.actions}
        base_path = pathlib.Path(__file__).parent.parent.parent
        with open(f'{base_path}/{prefix}-report.json', 'w') as f:
            json.dump(data, f)
