#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `taika` package."""

from pathlib import Path
from shutil import rmtree

from taika import taika


def test_run():
    """Tests the function run in the taika module."""
    source = Path("test_source")
    dest = Path("test_dest")

    taika.run(source, dest)

    assert dest.is_dir()
    for path in source.glob("**/*.rst"):
        assert dest.joinpath(path.name).with_suffix(".html").is_file()

    rmtree(dest)
