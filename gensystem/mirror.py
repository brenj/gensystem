"""Collect Gentoo mirrors from gentoo.org."""

import json
import os
from urlparse import urlparse

import gensystem.utils as gensystem_utils

GENTOO_MIRRORS_URL = 'https://www.gentoo.org/downloads/mirrors/'
GENTOO_RELEASES_TEMPLATE = 'releases/%s/autobuilds/%s/'

SUPPORTED_COUNTRIES = [
    'CA', 'US', 'AR', 'BR', 'AT', 'BG', 'CZ', 'FI', 'FR', 'DE', 'GR', 'IE',
    'NL', 'PL', 'PT', 'RO', 'SE', 'SK', 'ES', 'CH', 'TR', 'UA', 'UK', 'AU',
    'CN', 'HK', 'JP', 'KR', 'RU', 'TW', 'IL', 'KZ']


def get_mirrors_from_web(country=None):
    """Get gentoo.org mirrors from GENTOO_MIRRORS_URL.

    Get a BeautifulSoup representation of GENTOO_MIRRORS_URL, then get all
    gentoo mirrors by country, or just for a specified country. We assume
    a particular HTML layout and will explode horribly if it isn't right.

    Args:
        country (str): The only country name to return.

    Returns:
        dict: All or one gentoo mirror(s) by country.

        {'Netherlands':
            {u'LeaseWeb (ftp)': u'ftp://mirror.leaseweb.com/gentoo/',
             u'LeaseWeb (http)': u'http://mirror.leaseweb.com/gentoo/',
            ...
            }
         ...
        }

    Examples:
        Expected HTML format of GENTOO_MIRRORS_URL.

        <h3 id="CA">CA &ndash; Canada</h3>
        <table class="table table-condensed">
        <tr>
            <th style="width: 30%;">Name</th>
            <th style="width: 10%;">Protocol</th>
            <th style="width: 10%;">IPv4/v6</th>
            <th style="width: 50%;">URL</th>
        </tr>
        <tr>
            <td rowspan="1">Arctic Network Mirrors</td>
            <td>
                <span class="label label-primary">http</span>
            </td>
            <td>
                <span class="label label-info">IPv4 only</span>
            </td>
            <td>
                <a href="http://gentoo..."><code>http://gentoo...</code></a>
            </td>
        </tr>
        ...
        <h3 id="US">US &ndash; USA</h3>
        ...

    """
    mirrors = {}
    country_name = None

    mirrors_soup = gensystem_utils.soupify(GENTOO_MIRRORS_URL)
    for tag in mirrors_soup.find_all(True):

        if tag.name == 'h3' and tag.get('id') in SUPPORTED_COUNTRIES:
            # Assumes format "ID SEPARATOR COUNTRY" e.g. (CA - Canada)
            country_name = tag.string.split()[2]
            mirrors[country_name] = {}
            continue

        # Hit <table> tag after our country section heading
        if country_name is not None and tag.name == 'table':

            # Get all the mirror names and links in table
            for descendant in tag.descendants:
                # Assumes the name column spans rows
                if descendant.name == 'td' and descendant.get('rowspan'):
                    mirror_name = descendant.string
                if descendant.name == 'a':
                    mirror_link = descendant['href']
                    protocol = urlparse(mirror_link).scheme
                    name_with_protocol = '%s (%s)' % (mirror_name, protocol)
                    # Only support http for now (not rsync or ftp)
                    if protocol == 'http':
                        mirrors[country_name][name_with_protocol] = (
                            mirror_link)

            # Reset country_name
            country_name = None

    return {country: mirrors[country]} if country else mirrors


def get_mirrors_from_json(country=None):
    """Get Gentoo mirrors from data/mirrors.json.

    Args:
        country (str): The only country name to return.

    Returns:
        dict: All or one gentoo mirror(s) by country.

    """
    mirrors_file_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), 'data/mirrors.json')
    try:
        with open(mirrors_file_path, 'r') as mirrors_file:
            mirrors = json.load(mirrors_file)
            return {country: mirrors[country]} if country else mirrors
    except (IOError, ValueError):
        raise RuntimeError(
            "Mirrors file was not found or could not be loaded.")


GENTOO_MIRRORS = get_mirrors_from_json()
