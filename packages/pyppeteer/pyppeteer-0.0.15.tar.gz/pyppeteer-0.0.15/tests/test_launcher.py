#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest

from syncer import sync

from pyppeteer import launch
from pyppeteer.launcher import Launcher
from pyppeteer.chromium_downloader import chromium_excutable


class TestLauncher(unittest.TestCase):
    def setUp(self):
        self.headless_options = [
            '--headless',
            '--disable-gpu',
            '--hide-scrollbars',
            '--mute-audio',
        ]

    def check_default_args(self, launcher):
        for opt in self.headless_options:
            self.assertIn(opt, launcher.chrome_args)
        self.assertTrue(any(opt for opt in launcher.chrome_args
                            if opt.startswith('--user-data-dir')))

    def test_no_option(self):
        launcher = Launcher()
        self.check_default_args(launcher)
        self.assertEqual(launcher.exec, str(chromium_excutable()))

    def test_disable_headless(self):
        launcher = Launcher({'headless': False})
        for opt in self.headless_options:
            self.assertNotIn(opt, launcher.chrome_args)

    def test_disable_default_args(self):
        launcher = Launcher(ignoreDefaultArgs=True)
        # check defatul args
        self.assertNotIn('--no-first-run', launcher.chrome_args)
        # check dev tools port
        self.assertNotIn(
            '--remote-debugging-port={}'.format(launcher.port),
            launcher.chrome_args,
        )
        # check automation args
        self.assertNotIn('--enable-automation', launcher.chrome_args)

    def test_executable(self):
        launcher = Launcher({'executablePath': '/path/to/chrome'})
        self.assertEqual(launcher.exec, '/path/to/chrome')

    def test_args(self):
        launcher = Launcher({'args': ['--some-args']})
        self.check_default_args(launcher)
        self.assertIn('--some-args', launcher.chrome_args)

    def test_user_data_dir(self):
        launcher = Launcher({'args': ['--user-data-dir=/path/to/profile']})
        self.check_default_args(launcher)
        self.assertIn('--user-data-dir=/path/to/profile', launcher.chrome_args)
        self.assertIsNone(launcher._tmp_user_data_dir)

    @sync
    async def test_close_no_connection(self):
        browser = await launch(args=['--no-sandbox'])
        await browser.close()
