#!/usr/bin/env python3

import argparse
import getpass
import json
import logging
import os

import markdown
import requests
import tld
from bs4 import BeautifulSoup, SoupStrainer

# Global state for http client
host = ""
s = None

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Fetch challenges from a CTFd competition')
    parser.add_argument('-s', '--server', required=True, help='ctfd server')
    parser.add_argument('-u', '--user', required=True, help='username for account')
    parser.add_argument('-o', '--out', help='directory to save challenges')
    parser.add_argument('-v', help='verbose', action='store_true')
    parser.add_argument('-q', help='quiet', action='store_true')
    return parser.parse_args()


def login(user):
    """Login to CTFd instance and return an authenticated session"""
    login_url = host + "/login"
    logging.info("Login to: {}".format(login_url))

    # Prompt user for password
    pw = getpass.getpass()

    # Intitial GET request to get cookie and nonce
    s = requests.Session()
    r = s.get(login_url)
    if r.status_code != 200:
        logging.error("on login GET: {}".format(r.status_code))
        return None

    # Extract CSRF nonce to send in next request
    soup = BeautifulSoup(r.text, 'html.parser')
    nonce = soup.find("input", {"name": "nonce"})['value']

    # POST request to actually login
    data = {"nonce": nonce, "name": user, "password": pw}
    r = s.post(login_url, data=data)
    if r.status_code != 200:
        logging.erorr("on login POST: {}".format(r.status_code))
        return None

    # Return authenticated session
    return s

def get_challenges():
    """Get the challenges JSON from /chals"""
    chals_url = host + "/chals"
    r = s.get(chals_url)
    if r.status_code != 200:
        logging.error("on chals GET: {}".format(r.status_code))
        return []
    chalj = json.loads(r.text)
    if 'game' in chalj:
        return chalj['game']
    else:
        return []

def slugify(name):
    """Utility to create a cleaner printable name (eg: for directories)"""
    return name.replace(' ', '_')

def download_files(urls, down_dir):
    """Given a list of urls download all to a given directory.  Skip if file
    already exists to be respectful of CTF server resources"""
    for u in urls:
        f_name = os.path.basename(u)
        down_name = os.path.join(down_dir, f_name)
        if os.path.exists(down_name):
            logging.debug("already exists so skipping {}".format(down_name))
            continue
        # ref: https://stackoverflow.com/a/16696317
        r = s.get(u, stream=True)
        if r.status_code != 200:
            logging.warn("error in GET request: {} : {}".format(r.status_code, u))
            continue
        with open(down_name, 'wb') as f:
            logging.debug("downloading {}".format(down_name))
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)

def same_tld(url):
    """Used to check if links are to """
    url_tld = tld.get_tld(url)
    host_tld = tld.get_tld(host)
    return url_tld == host_tld

def urls_from_description(desc):
    """Extract urls that are referenced in the challenge description, so long
    as they are from the same TLD as the host"""
    m = markdown.markdown(desc)
    # ref: https://stackoverflow.com/a/1080472
    soup = BeautifulSoup(m, 'html.parser', parse_only=SoupStrainer('a'))
    links = [lnk['href'] for lnk in soup if lnk.has_attr('href')]
    # add host for relative links
    links = [host + u if "http" not in u else u for u in links]
    # filter to only urls on the same tld (or a subdomain)
    links = [u for u in links if same_tld(u)]
    external = [u for u in links if not same_tld(u)]

    if len(external) > 0:
        logging.debug("skipping external links: ", external)
    return links

def save_challenges(chals):
    for c in chals:
        slug = slugify(c['name'])
        logging.info("challenge: {}".format(slug))
        file_urls = [host + "/files/" + u for u in c['files']]
        urls = file_urls + urls_from_description(c['description'])
        if len(urls) > 0:
            os.makedirs(slug, exist_ok=True)
            download_files(urls, slug)


def main():
    global s
    global host

    # get args and setup
    args = parse_args()
    host = args.server.rstrip('/')

    # setup logging/printing
    logging.basicConfig(format='%(message)s')
    if args.v:
        logging.getLogger().setLevel(logging.DEBUG)
    elif args.q:
        logging.getLogger().setLevel(logging.ERROR)
    else:
        logging.getLogger().setLevel(logging.INFO)

    # change output directory (default is current directory)
    if args.out is not None:
        try:
            os.chdir(args.out)
        except FileNotFoundError:                       # noqa: F821
            logging.error("out directory not found")
            exit(1)

    s = login(args.user)
    if s is None:
        exit(1)

    logging.info("Getting Challenges...")
    chals = get_challenges()
    logging.debug("Got {}".format(len(chals)))
    logging.info("Saving Challenges...")
    save_challenges(chals)


if __name__ == "__main__":
    main()
