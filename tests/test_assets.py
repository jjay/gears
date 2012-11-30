import codecs
import os
import sys

from gears.assets import CircularDependencyError, Asset, StaticAsset, build_asset
from gears.compat import str, bytes
from gears.environment import Environment
from gears.finders import FileSystemFinder

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


class BuildAssetTests(TestCase):

    def setUp(self):
        self.environment = get_environment('build_asset')

    def test_has_processors(self):
        asset = build_asset(self.environment, 'source.js')
        self.assertIsInstance(asset, Asset)

    def test_has_no_processors(self):
        asset = build_asset(self.environment, 'source.md')
        self.assertIsInstance(asset, StaticAsset)
