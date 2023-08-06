#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_jinja2_pimport
----------------------------------

Tests for `jinja2_pimport` module.
"""

import pytest


def test_jinja2_pimport():
    """Test if pimport correctly works
    """

    from jinja2 import Environment

    env = Environment(extensions=['jinja2_pimport.PImportExtension'])
    template = env.from_string(
        '{{ ("subprocess"|pimport).check_output("echo hello", shell=True).strip().decode() }}')
    content = template.render()
    assert content == "hello"
