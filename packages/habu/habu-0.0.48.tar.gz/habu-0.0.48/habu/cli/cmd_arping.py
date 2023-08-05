import logging
import re
from time import sleep

import click

from scapy.all import ARP, IP, TCP, Ether, conf, srp


@click.command()
@click.argument('ip')
@click.option('-i', 'iface', default=None, help='Interface to use')
@click.option('-v', 'verbose', is_flag=True, default=False, help='Verbose output')
def cmd_arping(ip, iface, verbose):

    if verbose:
        logging.basicConfig(level=logging.INFO, format='%(message)s')

    conf.verb = False

    if iface:
        conf.iface = iface

    res, unans = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=ip), timeout=2)
    res.show()

if __name__ == '__main__':
    cmd_arping()

