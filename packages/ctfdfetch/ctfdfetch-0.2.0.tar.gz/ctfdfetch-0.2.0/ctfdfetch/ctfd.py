""" Functions for interating with CTFd instance and downloading files"""

import getpass
import json
import logging
import os

from bs4 import BeautifulSoup, SoupStrainer
import markdown
import requests
import tld

# Global state for http client
host = ""
s = None

def login(user, server):
    """Login to CTFd instance and store a global authenticated session"""
    global s
    global host
    host = server
    login_url = host + "/login"
    logging.info("Login to: {}".format(login_url))

    # Prompt user for password
    pw = getpass.getpass()

    # Initial GET request to get cookie and nonce
    sess = requests.Session()
    r = sess.get(login_url)
    if r.status_code != 200:
        logging.error("Error: on login GET: {}".format(r.status_code))
        return False

    # Extract CSRF nonce to send in next request
    soup = BeautifulSoup(r.text, 'html.parser')
    nonce = soup.find("input", {"name": "nonce"})['value']

    # POST request to actually login (expect redirect)
    data = {"nonce": nonce, "name": user, "password": pw}
    r = sess.post(login_url, data=data, allow_redirects=False)
    if r.status_code != 302:
        logging.error("Error: invalid login")
        return False

    # Set global authenticated session
    s = sess
    return True

def get_challenges():
    """Get the challenges JSON from /chals"""
    chals_url = host + "/chals"
    r = s.get(chals_url)
    if r.status_code != 200:
        logging.error("Error: on chals GET: {}".format(r.status_code))
        return []
    chalj = json.loads(r.text)
    if 'game' in chalj:
        return chalj['game']
    else:
        return []

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
            logging.warn("Error: in GET request: {} : {}".format(r.status_code, u))
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

def get_host():
    """Allow other modules to access host var"""
    return host
