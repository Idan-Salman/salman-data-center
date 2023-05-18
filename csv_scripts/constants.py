from typing import NewType

SUSHISWAPV2_CSV_PATH = "csv_files/sushiswapv2_csv.csv"
UNISWAPV2_CSV_PATH = "csv_files/uniswapv2_csv.csv"
UNISWAPV3_CSV_PATH = "csv_files/uniswapv3_csv.csv"
CURVEV2_CSV_PATH = "csv_files/curvev2_{0}_csv.csv"

CURVE_API_URLS = [
    "https://api.curve.fi/api/getPools/{0}/main",
    "https://api.curve.fi/api/getPools/{0}/crypto",
    "https://api.curve.fi/api/getPools/{0}/factory",
    "https://api.curve.fi/api/getPools/{0}/factory-crypto",
]

ChecksumEvmAddress = NewType("ChecksumEvmAddress", str)
EvmAddress = NewType("EvmAddress", str)
