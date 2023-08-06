"""FIXME: Generalize into functions and classes and add argparse blah, blah, blah
"""
import os
import re
from urllib import request
from bs4 import BeautifulSoup


def download_data(url=None, dest=None, verbose=True):
    """Download data from a given URL to a destination.
    """

    if verbose:
        print("Opening request @:", url)
    # Attempt to create the request.
    try:
        req = request.urlopen(url)
    except Exception as err:
        print(err)

    if verbose:
        print("Reading and decoding...")

    # Attempt to read and decode the request.
    try:
        rdata = req.read().decode()
    except Exception as err:
        print(err)

    if verbose:
        print("Writing data to:", dest)

    # Write the data to the destination.
    try:
        with open(dest, "w") as f:
            f.write(rdata)
    except Exception as err:
        print(err)

    if verbose:
        print("Download complete.")


def create_link_list(url):
    """Create list of links from repo.

    FIXME: Create some parsing element that can doe better at selecting
    files with content.
    """
    # Create request.
    req = request.urlopen(url)
    html = req.read().decode()
    soup = BeautifulSoup(html, "lxml")

    # Create basic link list.
    link_list = []
    for a in soup.find_all('a', href=True):
        if "/blob/master/" in a['href']:
            link_list += [a['href']]

    link_list = list(map(lambda x: "/".join(x.split("/")[4:]), link_list))

    # FIXME: GENERALIZE THIS
    usr = re.sub("https://github.com/", "", url)
    # FIXME: GENERALIZE THIS TOO.
    content_url = "https://raw.githubusercontent.com/{}"
    usr_content_url = content_url.format(usr)

    # Generate the content links
    content_links = []
    for i in link_list:
        link = "/".join([usr_content_url, i])
        content_links += [link]

    return content_links



def grab(kind, dest=None, url=None, *args, **kwargs):
    """Grab gitignore files from github's repo.
    """
    # kind = "Python"
    dest = dest or os.getcwd()
    url = url or 'https://github.com/github/gitignore'

    content_links = create_link_list(url)

    result = list(filter(lambda x: kind in x, content_links))

    if len(result) == 1:
        target_url = result[0]
    else:
        target_url = ""
        print(kind, ", not found.")

    target_name = target_url.split("/")[-1]

    gitignore_name = "." + target_name.split(".")[-1]

    dest = os.path.join(dest, gitignore_name)

    download_data(url=target_url, dest=dest)

# if __name__ == "__main__":
#     pass
