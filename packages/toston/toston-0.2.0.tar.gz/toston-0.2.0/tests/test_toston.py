#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `toston` package."""

import pytest

from click.testing import CliRunner

from toston import toston
from toston import cli


@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument."""
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli.main)
    assert result.exit_code == 0
    assert 'toston.cli.main' in result.output
    help_result = runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0
    assert '--help  Show this message and exit.' in help_result.output

def test_seckey(capsys):
    """We use the capsys argument to capture printing to stdout."""
    # The seckey function prints the results, but returns nothing.
    assert toston.seckey(8) == None

    # Capture the result of the toston.seckey() function call.
    captured = capsys.readouterr()
    size_captured = len(captured.out)

    message = "Generated secret key of 8 bytes = 742af1bdb188f66a\n"

    # If we check captured, we can see that the secket key have been printed.
    assert len(message) == size_captured
