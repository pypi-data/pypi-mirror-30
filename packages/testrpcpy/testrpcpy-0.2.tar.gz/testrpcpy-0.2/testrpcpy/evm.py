import requests
import json


def snapshot(rpc_host="http://localhost:8545"):
    """
    Execute the TestRPC EVM snapshot command and return the snapshot identifier
    :param rpc_host: String specifying the url to the JSON-RPC provider
    defaults to http://localhost:8545
    :return: Tuple of integer value and hex string of the snapshot ID
    """
    r = requests.post(rpc_host, json.dumps({
        "jsonrpc": "2.0",
        "method": "evm_snapshot",
        "params": [],
        "id": 1
    }), timeout=10)
    hex_value = r.json()['result']
    return int(hex_value, 16), hex_value


def revert(snapshot_id, rpc_host="http://localhost:8545"):
    """
    Revert the TestRPC EVM at the specified JSON-RPC endpoint to the specified
    snapshot ID
    :param snapshot_id: Snapshot number to revert to
    :param rpc_host: String specifying the url to the JSON-RPC provider
    defaults to http://localhost:8545
    :return: True or throws a ReadTimeout if the snapshot could not be applied
    """
    r = requests.post(rpc_host, json.dumps({
        "jsonrpc": "2.0",
        "method": "evm_revert",
        "params": [hex(snapshot_id)],
        "id": 1
    }), timeout=10)
    return r.json()['result']

