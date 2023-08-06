"""Functionality for saving CTF information locally """

import logging
import os
from urllib.parse import urlparse

from jinja2 import Environment, PackageLoader, select_autoescape

from ctfdfetch.ctfd import download_files, urls_from_description, get_host
from ctfdfetch.utils import sort_chals, slugify

# Template state
out_dir = None
nest = False
env = Environment(
    loader=PackageLoader('ctfdfetch', 'templates'),
    autoescape=select_autoescape(['html', 'xml'])
)

def set_out_dir(args):
    """Checks for existence of output directory and changes there, defaults to
    the top-level-domain of the server"""
    global out_dir
    if args.out is not None:
        out_dir = args.out
    else:
        out_dir = urlparse(args.server).netloc

    # change to directory to simplify paths
    try:
        os.chdir(out_dir)
        return True
    except FileNotFoundError:                       # noqa: F821
        logging.warn("out directory not found")

    # try again but make directory first
    try:
        os.makedirs(out_dir)
        os.chdir(out_dir)
        return True
    except OSError:
        logging.error("Error: could not create out directory")
        return False

def set_nesting():
    global nest
    nest = True
    logging.debug("storing challenged nested by category")

def chal_to_dir(c):
    """Convert a challenge to it's respective directory"""
    slug = slugify(c['name'])
    if nest:
        return os.path.join(c['category'], slug)
    else:
        return slug

def save_description(chal):
    """Given a challenge save it's description using a markdown template"""
    desc_path = os.path.join(chal_to_dir(chal), "description.md")
    if os.path.exists(desc_path):
        logging.debug("Description already exists, skip: {}".format(desc_path))
        return
    template = env.get_template('description.md.j2')
    # normalize line endings, ref: https://stackoverflow.com/a/1749553
    chal['description'] = '\n'.join(chal['description'].splitlines())
    chal_md = template.render(chal=chal)
    with open(desc_path, 'w') as out:
        out.write(chal_md)

def save_challenges_toc(chals):
    sorted_chals = sort_chals(chals)
    # add local metadata to allow link generation
    for c in sorted_chals:
        c['md_link'] = "[{}]({})".format(c['name'], chal_to_dir(c))
    toc_path = "challenges.md"
    if os.path.exists(toc_path):
        logging.debug("Table of Contents already exists, skip: {}".format(toc_path))
        return
    template = env.get_template('challenges.md.j2')
    toc_md = template.render(server=get_host(), chals=sorted_chals)
    with open(toc_path, 'w') as out:
        out.write(toc_md)

def save_challenges(chals):
    """Given a challenge, create a directory, save it's description and
    download any associated files"""

    save_challenges_toc(chals)
    for c in chals:
        c_dir = chal_to_dir(c)
        logging.info("challenge: {}".format(c['name']))
        file_urls = [get_host() + "/files/" + u for u in c['files']]
        urls = file_urls + urls_from_description(c['description'])

        os.makedirs(c_dir, exist_ok=True)
        save_description(c)
        if len(urls) > 0:
            download_files(urls, c_dir)
