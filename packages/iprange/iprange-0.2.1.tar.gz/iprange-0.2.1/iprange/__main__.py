#!/usr/bin/python3
import argparse

from .ipaddress import IPv4Address
from . import generate_range



def main():
    pars = argparse.ArgumentParser()
    pars.add_argument('ip_start')
    pars.add_argument('ip_end')

    args = pars.parse_args()

    for i in generate_range(args.ip_start, args.ip_end):
        print(i)


if __name__ == '__main__':
    main()
