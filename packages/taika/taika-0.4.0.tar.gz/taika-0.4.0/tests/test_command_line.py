#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for the command line of `taika` package."""

from shutil import rmtree
from pathlib import Path

from click.testing import CliRunner

from taika import cli


def test_basic():
    """Test the most basic command."""
    runner = CliRunner()
    source = Path("test_source")
    dest = Path("test_dest")

    result = runner.invoke(cli.main, [str(source), str(dest)])

    assert result.exit_code == 0
    assert dest.is_dir()
    assert dest.glob("*")

    rmtree(dest)


def test_help():
    """Test the help."""
    runner = CliRunner()

    help_result = runner.invoke(cli.main, ['--help'])

    assert help_result.exit_code == 0
    assert '--help  Show this message and exit.' in help_result.output
