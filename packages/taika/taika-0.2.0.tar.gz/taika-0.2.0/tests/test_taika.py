#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `taika` package."""

from pathlib import Path

from click.testing import CliRunner

from taika import cli, taika


def test_run():
    """Tests the function run in the taika module."""
    source = Path("test_source")
    dest = Path("test_dest")

    taika.run(source, dest)

    assert dest.is_dir()
    for path in source.glob("**/*.rst"):
        assert dest.joinpath(path.name).with_suffix(".html").is_file()

    dest.rmdir()


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli.main)
    assert result.exit_code == 0
    assert 'taika.cli.main' in result.output
    help_result = runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0
    assert '--help  Show this message and exit.' in help_result.output
