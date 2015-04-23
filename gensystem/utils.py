"""Utilities for working with gensystem."""

import urllib2

from bs4 import BeautifulSoup


def soupify(url_path):
    """Get a BeautifulSoup representation of a web page.

    Args:
        url_path (str): Full path to a URL to soupify.

    Returns:
        bs4.BeautifulSoup: Soup representation of `url_path`.

    Raises:
        RuntimeError: When urllib2 cannot communicate with `url_path`.

    """
    try:
        response = urllib2.urlopen(url_path)
    except urllib2.URLError:
        raise RuntimeError("Could NOT talk to %s." % url_path)

    return BeautifulSoup(response.read())


def get_choices(items, sort=True):
    """Get choices for a given list of items.

    Args:
        items (list): Items to get choices for.
        sort (bool, optional): Whether to sort items.

    Returns:
        dict: Choices for the specified items.
        The return format is: {item1: 1, item2: 2, item3: 3, ...}

    """
    if sort:
        items = sorted(items)

    return {item: choice for choice, item in enumerate(items, 1)}


def get_user_choice(prompt, choices):
    """Prompt user for a choice and ensure user input is valid.

    Input for a choice will always be presented as an integer. Prompt the
    user until valid input is received (an integer).

    Args:
        prompt (str): Message to prompt the user with.
        valid_choices (dict): Valid choices a user can make.

    Returns:
        int: A valid user choice.

    """
    valid_choices = choices.values()

    while True:
        try:
            choice = int(get_raw_input(prompt))
            assert choice in valid_choices
        except (ValueError, AssertionError):
            continue
        else:
            break

    return get_choice_value(choice, choices)


def get_raw_input(prompt):
    """Get raw input from user using raw_input.

    This function exists only to wrap raw_input so that it can be mocked
    for unit testing.

    Args:
        prompt (str): Message to prompt user with.

    Returns:
        str: Raw input from user.

    """
    return raw_input(prompt)  # pragma: no cover


def get_choice_value(user_choice, choices):
    """Get the value associated with a user choice.

    Args:
        user_choice (int): A valid user choice.
        choices (dict): Valid choices a user can make.

    Returns:
        int: The choice value for a `user_choice`.

    """
    choice_value = None
    for name, choice in choices.iteritems():
        choice_value = name if user_choice == choice else choice_value

    return choice_value


def format_choice(choice, ten_or_more_choices=False):
    """Format a choice so that columns always line up in stdout.

    Args:
        choice (int): A choice (e.g. 1, 2, 3).
        ten_or_more_choices (bool): Whether there are 10 or more choices.

    Returns:
        str: A formatted choice in format [ %s] or [%s].

    """
    if choice < 10 and ten_or_more_choices:
        choice_format = "[ %s]"
    else:
        choice_format = "[%s]"

    return choice_format % str(choice)
