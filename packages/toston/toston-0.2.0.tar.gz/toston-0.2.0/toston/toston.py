# -*- coding: utf-8 -*-

"""Main module."""

import secrets


def seckey(size):
    """Generates a secret key with size variable (1-32)"""
    secret_key = secrets.token_hex(size)
    print(f'Generated secret key of {size} bytes = {secret_key}')
