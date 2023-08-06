# -- coding: utf-8 --

"""Ouptuts formatted, colored log messages to the console."""

from __future__ import absolute_import, print_function, unicode_literals

import sys

from colorama import init as colorama_init
from colorama import Fore, Style

from six.moves import input

colorama_init(autoreset=True)

# Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
# Back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
# Style: DIM, NORMAL, BRIGHT, RESET_ALL

# BRIGHT_WHITE = Fore.WHITE + Style.BRIGHT

# -----------------------------------------------------------------------------
# User feedback
# -----------------------------------------------------------------------------


def divline():
    """Prints a divider line."""
    print('-' * 80)


def header(string):
    """Prints a header."""
    value = Fore.GREEN + '==> ' + Fore.WHITE + Style.BRIGHT + string
    print(value)


def success(string):
    """Prints a success message."""
    if sys.platform == 'win32':
        symbol = '[+] '
    else:
        symbol = '[✓] '
    value = Fore.GREEN + symbol + Fore.WHITE + string
    print(value)


def error(string):
    """Prints a error message."""
    if sys.platform == 'win32':
        symbol = '[-] '
    else:
        symbol = '[✗] '
    value = Fore.RED + symbol + Fore.WHITE + string
    print(value)


def warning(string):
    """Prints a warning message."""
    value = Fore.YELLOW + '[!] ' + Fore.WHITE + string
    print(value)


def info(string):
    """Prints a info message."""
    value = Fore.CYAN + '[i] ' + string
    print(value)


def note(string):
    """Prints a note message."""
    value = Style.DIM + string
    print(value)

# For backwards compatibility as we renamed our methods
log_divline = divline
log_header = header
log_success = success
log_error = error
log_warning = warning
log_info = info

# -----------------------------------------------------------------------------
# User Input
# -----------------------------------------------------------------------------


def prompt(question):
    """Prompts user for input."""
    # Python 2to3 compatbility
    response = input('[?] {} '.format(question))
    return response


def confirm(question):
    """Prompts user to confirm with (y/n)."""
    # Python 2to3 compatbility
    response = input('[?] {}? (y/n) '.format(question))

    if response in ['y', 'yes']:
        return True
    return False

# -----------------------------------------------------------------------------

if __name__ == "__main__":
    divline()
    header('Header')
    success('Success')
    error('Error')
    warning('Warning')
    info('Info')
    note('Note goes here')

    name = prompt('What is your name?')
    success(name)

    if confirm('Confirm this'):
        success('You confirmed!')
    else:
        error('Not confirmed')
