import requests
import csv

from web3 import Web3, HTTPProvider
from typing import NamedTuple, Optional

from csv_scripts.exceptions import DeserializationError, RemoteError
from csv_scripts.constants import (
    CURVE_API_URLS,
    CURVEV2_CSV_PATH,
    ChecksumEvmAddress,
    EvmAddress,
)


ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"
w3 = Web3(HTTPProvider(""))


def deserialize_evm_address(address: EvmAddress) -> ChecksumEvmAddress:
    """Deserialize a symbol, check that it's a valid ethereum address
    and return it checksummed.

    This function can raise DeserializationError if the address is not
    valid
    """
    try:
        return Web3.toChecksumAddress(address)
    except ValueError as e:
        raise DeserializationError(
            f"Invalid evm address: {address}",
        ) from e


class CurvePoolData(NamedTuple):
    pool_address: ChecksumEvmAddress
    pool_name: str
    lp_token_address: ChecksumEvmAddress
    gauge_address: Optional[ChecksumEvmAddress]
    coins: list[ChecksumEvmAddress]
    underlying_coins: Optional[list[ChecksumEvmAddress]]


def query_curve_data_from_api(get_pool_data: bool, chain: str) -> list[CurvePoolData]:
    """
    Query all curve information(lp tokens, pools, gagues, pool coins) from curve api.

    May raise:
    - RemoteError if failed to query curve api
    """
    pool_address_list = []
    all_api_pools = []
    for api_url in CURVE_API_URLS:
        api_url = api_url.format(chain)
        response_json = requests.get(api_url).json()
        if response_json["success"] is False:
            raise RemoteError(
                f"Curve api endpoint {api_url} returned failure. Response: {response_json}"
            )  # noqa: E501

        try:
            all_api_pools.extend(response_json["data"]["poolData"])
        except KeyError as e:
            raise RemoteError(
                f"Curve api endpoint {api_url} response is missing {e!s} key"
            ) from e  # noqa: E501

    processed_new_pools = []
    for api_pool_data in all_api_pools:
        try:
            pool_address = deserialize_evm_address(api_pool_data["address"])

            coins = []
            for coin_data in api_pool_data["coins"]:
                coins.append(deserialize_evm_address(coin_data["address"]))
            underlying_coins = None
            if "underlyingCoins" in api_pool_data:
                underlying_coins = []
                for underlying_coin_data in api_pool_data["underlyingCoins"]:
                    underlying_coins.append(
                        deserialize_evm_address(underlying_coin_data["address"])
                    )  # noqa: E501

            processed_new_pools.append(
                CurvePoolData(
                    pool_address=pool_address,
                    pool_name=api_pool_data["name"],
                    lp_token_address=deserialize_evm_address(
                        api_pool_data["lpTokenAddress"]
                    ),
                    gauge_address=deserialize_evm_address(api_pool_data["gaugeAddress"])
                    if "gaugeAddress" in api_pool_data
                    else None,  # noqa: E501
                    coins=coins,
                    underlying_coins=underlying_coins,
                )
            )
            pool_address_list.append(pool_address)
        except KeyError as e:
            raise RemoteError(
                f"Curve pool data {api_pool_data} are missing key {e!s}"
            ) from e
        except DeserializationError as e:
            print(
                f"Could not deserialize evm address while decoding curve pool {pool_address} "
                f"information from curve api: {e!s}",
            )
    if get_pool_data == False:
        with open(CURVEV2_CSV_PATH.format(chain), "w") as file:
            csv_writer = csv.writer(file)
            for address in pool_address_list:
                csv_writer.writerow([address])
        return
    return processed_new_pools


if __name__ == "__main__":
    """
    Details about the curve api:
    https://github.com/curvefi/curve-api/blob/main/endpoints.md#getpools

    Possible chains:
    - ethereum
    - polygon
    - fantom
    - arbitrum
    - avalanche
    - optimism
    - xdai (Take really long time to finish)
    """
    query_curve_data_from_api(get_pool_data=False, chain="xdai")
