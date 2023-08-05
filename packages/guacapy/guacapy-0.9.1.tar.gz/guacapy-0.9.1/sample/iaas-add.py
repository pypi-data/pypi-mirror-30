#!/usr/bin/env python
# coding: utf-8

from __future__ import print_function
from __future__ import unicode_literals
from guacapy import Guacamole
import argparse


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-H', '--host',
        help='Guacamole host'
    )
    parser.add_argument(
        '-u', '--username',
        help='Username'
    )
    parser.add_argument(
        '-p', '--password',
        help='Password'
    )
    parser.add_argument(
        '-i', '--identifier',
        help='iaas-id'
    )
    parser.add_argument(
        '-c', '--customer',
        help='Customer name'
    )
    parser.add_argument(
        '-P',  '--parent',
        help='Parent connection group name'
    )
    parser.add_argument(
        '--mgt-admin',
        help='iaas-XXX-mgt01 admin RDP password'
    )
    parser.add_argument(
        '--mgt-cust',
        help='iaas-XXX-mgt01 customer RDP password'
    )
    parser.add_argument(
        '--ssh-password',
        help='root SSH password of the vCenter'
    )
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    g = Guacamole(args.host, args.username, args.password, verify=False)
    print(g.get_connections())
