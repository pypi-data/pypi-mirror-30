#!/usr/bin/env python3

import argparse
import logging

from ctfdfetch.ctfd import login, get_challenges
from ctfdfetch.store import set_out_dir, set_nesting, save_challenges

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Fetch challenges from a CTFd competition')
    parser.add_argument('-s', '--server', required=True, help='ctfd server')
    parser.add_argument('-u', '--user', required=True, help='username for account')
    parser.add_argument('-o', '--out', help='directory to save challenges')
    parser.add_argument('-n', '--nest', help='nest challenges under categories',
                        action='store_true', default=False)
    parser.add_argument('-v', help='verbose', action='store_true')
    parser.add_argument('-q', help='quiet', action='store_true')
    return parser.parse_args()

def setup_verbosity(args):
    """setup logging/printing"""
    logging.basicConfig(format='%(message)s')
    if args.v:
        logging.getLogger().setLevel(logging.DEBUG)
    elif args.q:
        logging.getLogger().setLevel(logging.ERROR)
    else:
        logging.getLogger().setLevel(logging.INFO)

def main():
    # get args and setup
    args = parse_args()
    setup_verbosity(args)

    # change output directory (default is FQDN of server)
    if not set_out_dir(args):
        logging.error("Error: out directory not found")
        exit(1)

    if args.nest:
        set_nesting()

    # Authenticate
    if not login(args.user, args.server.rstrip('/')):
        exit(1)

    logging.info("Getting Challenges...")
    chals = get_challenges()

    logging.info("Saving Challenges...")
    save_challenges(chals)


if __name__ == "__main__":
    main()
