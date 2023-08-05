#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `prueba_primo` package."""

import pytest

from click.testing import CliRunner

from prueba_primo import prueba_primo
from prueba_primo import cli


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
    assert 'prueba_primo.cli.main' in result.output
    help_result = runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0
    assert '--help  Show this message and exit.' in help_result.output

def test_es_primo(capsys):
    """We use the capsys argument to capture printing to stdout."""
    # The ingredients function prints the results, but returns nothing.
    assert prueba_primo.es_primo(7) == True

    # Capture the result of the arepas.ingredients() function call.
    captured = capsys.readouterr()

    # If we check captured, we can see that the ingredients have been printed.
    #assert " " in captured.out
