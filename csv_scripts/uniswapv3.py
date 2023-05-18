import csv

from typing import Optional

from csv_scripts.thegraph import run_graph_query
from csv_scripts.constants import UNISWAPV3_CSV_PATH


def fetch_uniswapv3_pools(graph_url: Optional[str] = None) -> None:
    pool_addresses = []

    query = """
    {
    pools(first: 1000, orderBy: createdAtTimestamp, orderDirection: asc) 
    { id, createdAtBlockNumber, createdAtTimestamp }
    }
    """
    pools = run_graph_query(query)["data"]["pools"]
    last_ts = pools[-1]["createdAtTimestamp"]

    for pool in pools:
        pool_id = pool["id"]
        pool_addresses.append(pool_id)

    while len(pools) == 1000:
        query = f"""{{pools(first: 1000, orderBy: createdAtTimestamp, orderDirection: asc where: {{ createdAtTimestamp_gt: {last_ts} }})  {{ id, createdAtBlockNumber, createdAtTimestamp }}}}"""
        pools = run_graph_query(query)["data"]["pools"]
        last_ts = pools[-1]["createdAtTimestamp"]

        for pool in pools:
            pool_id = pool["id"]
            pool_addresses.append(pool_id)

    with open(UNISWAPV3_CSV_PATH, "w") as file:
        csv_writer = csv.writer(file)
        for address in pool_addresses:
            csv_writer.writerow([address])

    return pool_addresses


if __name__ == "__main__":
    """
    NOTE Chains other than ethereum don't have an implemented subgraph and so i can't get the other chain's address list this way.

    The following network are the supported and available blockchain data you can get using the code above:
    - ethereum
    - ...
    """
    graph_url = ""
    fetch_uniswapv3_pools(graph_url=graph_url)
