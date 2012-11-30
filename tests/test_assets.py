import codecs
import os
import sys

from gears.assets import (
    CircularDependencyError, BaseAsset, Asset, StaticAsset, build_asset
)
from gears.compat import str, bytes
from gears.environment import Environment
from gears.finders import FileSystemFinder

from mock import sentinel, Mock
from unittest2 import TestCase


TESTS_DIR = os.path.dirname(__file__)
FIXTURES_DIR = os.path.join(TESTS_DIR, 'fixtures', 'assets')


def read(file):
    with codecs.open(file, encoding='utf-8') as f:
        return f.read()


def get_fixture_path(fixture):
    return os.path.join(FIXTURES_DIR, fixture)


def get_finder(fixture):
    return FileSystemFinder([get_fixture_path(fixture)])


def get_environment(fixture):
    environment = Environment(os.path.join(TESTS_DIR, 'static'))
    environment.finders.register(get_finder(fixture))
    environment.register_defaults()
    return environment


def get_asset(fixture):
    return Asset(*get_environment(fixture).find('source.js'))


def get_static_asset(fixture):
    return StaticAsset(*get_environment(fixture).find('source'))


class AssetTests(TestCase):

    def test_circular_dependency(self):
        with self.assertRaises(CircularDependencyError):
            asset = get_asset('circular_dependency')

    def test_unicode_support(self):
        output = read(os.path.join(FIXTURES_DIR, 'unicode_support', 'output.js'))
        asset = get_asset('unicode_support')
        self.assertEqual(str(asset), output)

    def test_is_iterable(self):
        asset = get_asset('unicode_support')
        tuple(asset)

    def test_is_convertible_to_bytes(self):
        asset = get_asset('unicode_support')
        bytes(asset)


class StaticAssetTests(TestCase):

    def test_source(self):
        asset = get_static_asset('static_source')
        asset.source

    def test_hexdigest(self):
        asset = get_static_asset('static_source')
        self.assertEqual(
            asset.hexdigest,
            'c8a756475599e6e3c904b24077b4b0a31983752c',
        )

    def test_is_iterable(self):
        asset = get_static_asset('static_source')
        tuple(asset)

    def test_is_convertible_to_bytes(self):
        asset = get_static_asset('static_source')
        bytes(asset)


class HexdigestPathTests(TestCase):

    def get_asset(self, logical_path):
        attributes = Mock(logical_path=logical_path)
        asset = BaseAsset(attributes, sentinel.absolute_path)
        asset.hexdigest = '123456'
        return asset

    def test_hexdigest_path(self):
        def check(logical_path, result):
            asset = self.get_asset(logical_path)
            self.assertEqual(asset.hexdigest_path, result)

        check('css/style.css', 'css/style.123456.css')
        check('css/style.min.css', 'css/style.min.123456.css')


class BuildAssetTests(TestCase):

    def setUp(self):
        self.environment = get_environment('build_asset')

    def test_has_processors(self):
        asset = build_asset(self.environment, 'source.js')
        self.assertIsInstance(asset, Asset)

    def test_has_no_processors(self):
        asset = build_asset(self.environment, 'source.md')
        self.assertIsInstance(asset, StaticAsset)
