#!/usr/bin/env python

"""Tests for `viewclust_vis` package."""


import unittest
from click.testing import CliRunner

from viewclust_vis import viewclust_vis
from viewclust_vis import cli


class TestViewclust_vis(unittest.TestCase):
    """Tests for `viewclust_vis` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_something(self):
        """Test something."""

    def test_command_line_interface(self):
        """Test the CLI."""
        runner = CliRunner()
        result = runner.invoke(cli.main)
        assert result.exit_code == 0
        assert 'viewclust_vis.cli.main' in result.output
        help_result = runner.invoke(cli.main, ['--help'])
        assert help_result.exit_code == 0
        assert '--help  Show this message and exit.' in help_result.output
