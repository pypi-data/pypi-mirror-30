#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import importlib

from parameterized import parameterized

from wdom.tag import Tag, NestedTag
from wdom.themes import theme_list
from wdom.util import suppress_logging

from .base import TestCase


def setUpModule():
    suppress_logging()


class TestThemesImport(TestCase):
    @parameterized.expand(theme_list)
    def test_import_all(self, theme):
        a = importlib.import_module('wdom.themes.' + theme)
        self.assertIn('name', dir(a))
        self.assertIn('project_url', dir(a))
        self.assertIn('project_repository', dir(a))
        self.assertIn('license', dir(a))
        self.assertIn('license_url', dir(a))
        self.assertIn('css_files', dir(a))
        self.assertIn('js_files', dir(a))
        self.assertIn('headers', dir(a))
        self.assertIn('extended_classes', dir(a))

    @parameterized.expand(theme_list)
    def test_extended_is(self, theme):
        """Extended classes must have is_ attr or custom tag."""
        a = importlib.import_module('wdom.themes.' + theme)
        for obj in a.extended_classes:
            self.assertTrue(issubclass(obj, (Tag, NestedTag)))
            if obj.tag in ('div', 'span', 'pre', 'a'):
                self.assertNotEqual(obj.is_, '')
