import sys
import csv
from brownie import network, multicall, Contract, chain

from csv_scripts.constants import SUSHISWAPV2_CSV_PATH


def fetch_sushiswapv2_pools() -> None:
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
            "name": "Sushiswap",
            "factory_address": "0xC0AEe478e3658e2610c5F7A4A2E1777cE9e4f2Ac",
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

    with open(SUSHISWAPV2_CSV_PATH, "w") as file:
        csv_writer = csv.writer(file)
        for address in pool_addresses:
            csv_writer.writerow([address])


if __name__ == "__main__":
    # TODO Go over the code and make sure no sensitive information is present.
    """
    This code might not work if you haven't configured brownie properly.

    To configure brownie properly follow the following guide:
    https://www.notion.so/Brownie-1b33335a114e4680a5369d007b1e4411?pvs=4

    If the link doesn't work then make sure you are connected to notion on your used browser and are present in Rubedo's notion (DeFi Research project)
    """
    fetch_sushiswapv2_pools()
