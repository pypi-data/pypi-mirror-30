# -*- coding: utf-8 -*-

"""Main module."""

import logging
from pathlib import Path

from docutils.core import publish_parts

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger("taika")


RST_PARSE_OPTIONS = {
    "tab_width": 4,
    "stylesheet_path": None,
    "doctitle_xform": False,
}


def run(source, dest):
    """Read all '\*.rst' files from `source`, parse them and write them back as HTML in `dest`."""
    source = Path(source)
    dest = Path(dest)

    for source_path in source.glob("**/*.rst"):
        source_path = Path(source_path)
        LOGGER.debug("Reading: %s", source_path)

        source_content = source_path.read_text()
        dest_content = parse_restructuredtext(source_content)

        dest_path = dest.joinpath(source_path.name).with_suffix(".html")
        LOGGER.debug("Writing: %s", dest_path)

        dest_path.parent.mkdir(parents=True, exist_ok=True)
        dest_path.touch()
        dest_path.write_text(dest_content)


def parse_restructuredtext(content):
    """Parse ReStructuredText from `content` and return it as HTML."""
    html = publish_parts(
        content, writer_name="html5", settings_overrides=RST_PARSE_OPTIONS
    )["whole"]

    return html
