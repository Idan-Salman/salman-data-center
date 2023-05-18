import requests
from typing import Optional


def run_graph_query(query: str, graph_url: Optional[str] = None):
    if graph_url is None:
        graph_url = "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3"
    # endpoint where you are making the request
    request = requests.post(
        graph_url,
        json={"query": query},
    )
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception(
            "Query failed. return code is {}.      {}".format(
                request.status_code, query
            )
        )
