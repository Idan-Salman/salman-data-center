import sys
import csv
from brownie import network, multicall, Contract, chain

from csv_scripts.constants import UNISWAPV2_CSV_PATH


def fetch_uniswapv2_pools() -> None:
    BROWNIE_NETWORK = "mainnet"
    FLUSH_INTERVAL = 500
    multicall.address = "0xcA11bde05977b3631167028862bE2a173976CA11"

    try:
        network.connect(BROWNIE_NETWORK)
    except:
        sys.exit(
            "Could not connect! Verify your Brownie network settings using 'brownie networks list'"
        )

    exchanges = [
        {
            "name": "Uniswap",
            "factory_address": "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f",
        },
    ]

    for _, factory_address in [
        (
            exchange["name"],
            exchange["factory_address"],
        )
        for exchange in exchanges
    ]:

        factory = Contract.from_explorer(
            address=factory_address,
            silent=True,
        )

        current_block = chain.height

        # count the number of pairs tracked by the factory
        pool_count = int(factory.allPairsLength())

        # build a list of pools, initially populated
        # with batched addresses gathered
        # from the factory (using multicall)
        pool_addresses = []
        print("• Getting pool addresses")
        with multicall(
            block_identifier=current_block,
            address="0xcA11bde05977b3631167028862bE2a173976CA11",
        ):
            for pool_id in range(pool_count):
                if pool_id % FLUSH_INTERVAL == 0 and pool_id != 0:
                    multicall.flush()
                    print(f"found {pool_id} pools")
                pool_addresses.append(factory.allPairs(pool_id))

    with open(UNISWAPV2_CSV_PATH, "w") as file:
        csv_writer = csv.writer(file)
        for address in pool_addresses:
            csv_writer.writerow([address])


if __name__ == "__main__":
    """
    I think UniswapV2 is only present in the Ethereum blockchain,
    If you find any other chain create a pull request with the appropriate extra code (And csv).
    """
    fetch_uniswapv2_pools()
