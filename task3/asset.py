#!/usr/bin/env python3
import time
from argparse import ArgumentParser, FileType
import sys
import logging

DEFAULT_SMALL_TIME_SLEEP = 3

logger = logging.getLogger("asset")


def do_busy_work(sleep_time=DEFAULT_SMALL_TIME_SLEEP):
    time.sleep(sleep_time)


class Asset:
    def __init__(self, name: str, capital: float, interest: float):
        self.name = name
        self.capital = capital
        self.interest = interest

    def calculate_revenue(self, years: int) -> float:
        revenue = self.capital * ((1.0 + self.interest) ** years - 1.0)
        return revenue

    @classmethod
    def build_from_str(cls, raw: str):
        logger.debug("building asset object...")
        name, capital, interest = raw.strip().split()
        capital = float(capital)
        interest = float(interest)
        asset = cls(name=name, capital=capital, interest=interest)
        return asset

    def __repr__(self):
        repr_ = f"{self.__class__.__name__}({self.name}, {self.capital}, {self.interest})"
        return repr_


def load_asset_from_file(fileio):
    logger.info("reading asset file...")
    raw = fileio.read()
    asset = Asset.build_from_str(raw)
    return asset


def process_cli_arguments(arguments):
    print_asset_revenue(arguments.asset_fin, arguments.periods)


def print_asset_revenue(asset_fin, periods):
    asset = load_asset_from_file(asset_fin)
    for period in periods:
        revenue = asset.calculate_revenue(period)
        logger.debug("asset %s for period %s gives %s", asset, period, revenue)
        print(f"{period:5}: {revenue}")
        # consider nice formatting:
        # print(f"{period:5}: {revenue:10.3f}")


def setup_parser(parser):
    parser.add_argument("-f", "--filepath", dest="asset_fin", default=sys.stdin, type=FileType("r"))
    parser.add_argument("-p", "--periods", nargs="+", type=int, metavar="YEARS", required=True)
    parser.set_defaults(callback=process_cli_arguments)


def main():
    parser = ArgumentParser(
        prog="asset",
        description="tool to forecast asset revenue",
    )
    setup_parser(parser)
    arguments = parser.parse_args()
    arguments.callback(arguments)


if __name__ == "__main__":
    main()
