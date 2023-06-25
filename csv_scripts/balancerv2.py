import csv

from typing import Optional

from thegraph import run_graph_query
from csv_scripts.constants import BALANCERV2_CSV_PATH


def fetch_balancerv2_pools(graph_url: Optional[str] = None, chain="ethereum") -> None:
    pool_addresses = []

    count = 0
    query = f"""{{ pools(first: 1000, skip: {count*1000}) {{address}} }}"""
    pools = run_graph_query(query, graph_url=graph_url)["data"]["pools"]

    for pool in pools:
        pool_address = pool["address"]
        pool_addresses.append(pool_address)

    while len(pools) == 1000:
        count += 1
        query = f"""{{ pools(first: 1000, skip: {count*1000}) {{address}} }}"""
        pools = run_graph_query(query, graph_url=graph_url)["data"]["pools"]

        for pool in pools:
            pool_address = pool["address"]
            pool_addresses.append(pool_address)

    with open(BALANCERV2_CSV_PATH.format(chain), "w") as file:
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
    graph_url = "https://api.thegraph.com/subgraphs/name/balancer-labs/balancer-v2"
    fetch_balancerv2_pools(graph_url=graph_url, chain="ethereum")
