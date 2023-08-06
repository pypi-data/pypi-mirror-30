from __future__ import unicode_literals

import unittest

import mock

from mopidy import core

import pykka

from mopidy_mpris import objects

from tests import dummy_backend


class RootInterfaceTest(unittest.TestCase):
    def setUp(self):
        config = {
            'mpris': {
                'desktop_file': '/tmp/foo.desktop',
            }
        }

        objects.MprisObject._connect_to_dbus = mock.Mock()
        self.backend = dummy_backend.create_proxy()
        self.core = core.Core.start(backends=[self.backend]).proxy()
        self.mpris = objects.MprisObject(config=config, core=self.core)

    def tearDown(self):
        pykka.ActorRegistry.stop_all()

    def test_constructor_connects_to_dbus(self):
        self.assert_(self.mpris._connect_to_dbus.called)

    def test_fullscreen_returns_false(self):
        result = self.mpris.Get(objects.ROOT_IFACE, 'Fullscreen')
        self.assertFalse(result)

    def test_setting_fullscreen_fails_and_returns_none(self):
        result = self.mpris.Set(objects.ROOT_IFACE, 'Fullscreen', 'True')
        self.assertIsNone(result)

    def test_can_set_fullscreen_returns_false(self):
        result = self.mpris.Get(objects.ROOT_IFACE, 'CanSetFullscreen')
        self.assertFalse(result)

    def test_can_raise_returns_false(self):
        result = self.mpris.Get(objects.ROOT_IFACE, 'CanRaise')
        self.assertFalse(result)

    def test_raise_does_nothing(self):
        self.mpris.Raise()

    def test_can_quit_returns_true(self):
        result = self.mpris.Get(objects.ROOT_IFACE, 'CanQuit')
        self.assertTrue(result)

    def test_quit_does_nothing(self):
        self.mpris.Quit()

    def test_has_track_list_returns_false(self):
        result = self.mpris.Get(objects.ROOT_IFACE, 'HasTrackList')
        self.assertFalse(result)

    def test_identify_is_mopidy(self):
        result = self.mpris.Get(objects.ROOT_IFACE, 'Identity')
        self.assertEquals(result, 'Mopidy')

    def test_desktop_entry_is_based_on_DESKTOP_FILE_setting(self):
        result = self.mpris.Get(objects.ROOT_IFACE, 'DesktopEntry')
        self.assertEquals(result, 'foo')

    def test_supported_uri_schemes_includes_backend_uri_schemes(self):
        result = self.mpris.Get(objects.ROOT_IFACE, 'SupportedUriSchemes')
        self.assertEquals(len(result), 1)
        self.assertEquals(result[0], 'dummy')

    def test_supported_mime_types_has_hardcoded_entries(self):
        result = self.mpris.Get(objects.ROOT_IFACE, 'SupportedMimeTypes')
        self.assertEqual(result, [
            'audio/mpeg',
            'audio/x-ms-wma',
            'audio/x-ms-asf',
            'audio/x-flac',
            'audio/flac',
            'audio/l16;channels=2;rate=44100',
            'audio/l16;rate=44100;channels=2',
        ])
