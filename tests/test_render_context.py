"""Concurrent and rerun isolation of the actual legacy renderer handles."""
from concurrent.futures import ThreadPoolExecutor
from contextvars import Context
import inspect
from threading import Barrier, Event
import unittest
from unittest.mock import patch

import streamlit as st
from app.desktop_datetime_ui import install_desktop_datetime_ui
from app.render_context import (
    RenderContext, electrical_images, reset_render_contexts, serialized_installation,
)
from app.sopraciliare_ui import _ElectricalHelperPopover


def installed_contexts():
    # Walk the real installed wrapper chain, not separate test-only handles.
    result = []
    current = st.columns
    visited = set()
    while callable(current) and id(current) not in visited:
        visited.add(id(current))
        values = inspect.getclosurevars(current).nonlocals
        for key in ('context', 'electrical_pair'):
            handle = values.get(key)
            if handle is not None:
                result.append(handle)
        current = values.get('current_columns', values.get('original_columns'))
    return result


class RenderContextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with patch('app.desktop_datetime_ui.full_device_is_mobile', return_value=False):
            install_desktop_datetime_ui()

    def tearDown(self):
        reset_render_contexts()

    def test_installed_renderer_handles_do_not_leak_between_threads(self):
        handles = installed_contexts()
        self.assertEqual(len(handles), 3)
        rendezvous = Barrier(2)

        def session(number):
            # Defaults must not be a mutable dictionary shared by new threads.
            self.assertTrue(all(h.get('session_marker') is None for h in handles))
            for handle in handles:
                handle['session_marker'] = number
                handle['time_container'] = object()
            electrical_images['suppressed'] = bool(number)
            rendezvous.wait(timeout=5)
            return ([h['session_marker'] for h in handles], electrical_images['suppressed'])

        with ThreadPoolExecutor(max_workers=2) as pool:
            first, second = [pool.submit(session, n) for n in (0, 1)]
            self.assertEqual(first.result(timeout=10), ([0, 0, 0], False))
            self.assertEqual(second.result(timeout=10), ([1, 1, 1], True))

    def test_interleaved_contexts_on_one_thread_keep_their_own_containers(self):
        handle = RenderContext('test-interleaved', {'container': None})
        first, second = Context(), Context()
        a, b = object(), object()
        first.run(handle.__setitem__, 'container', a)
        second.run(handle.__setitem__, 'container', b)
        self.assertIs(first.run(handle.__getitem__, 'container'), a)
        self.assertIs(second.run(handle.__getitem__, 'container'), b)
        first.run(reset_render_contexts)
        self.assertIsNone(first.run(handle.__getitem__, 'container'))
        self.assertIs(second.run(handle.__getitem__, 'container'), b)

    def test_new_page_releases_old_containers_and_suppression_flags(self):
        handles = installed_contexts()
        for handle in handles:
            handle['time_container'] = object()
            handle['session_marker'] = 'previous run'
        electrical_images['suppressed'] = True
        reset_render_contexts()
        for handle in handles:
            self.assertIsNone(handle.get('time_container'))
            self.assertIsNone(handle.get('session_marker'))
        self.assertFalse(electrical_images['suppressed'])

    def test_image_suppression_is_restored_after_nested_helpers_and_errors(self):
        with patch('app.sopraciliare_ui._render_click_help'):
            with self.assertRaisesRegex(RuntimeError, 'test'):
                with _ElectricalHelperPopover('outer', 'outer'):
                    with _ElectricalHelperPopover('inner', 'inner'):
                        self.assertTrue(electrical_images['suppressed'])
                    self.assertTrue(electrical_images['suppressed'])
                    raise RuntimeError('test')
        self.assertFalse(electrical_images['suppressed'])

    def test_simultaneous_first_visits_install_only_once(self):
        ready = Barrier(2)
        entered, release = Event(), Event()
        installed = []

        @serialized_installation
        def install():
            if installed:
                return
            entered.set()
            self.assertTrue(release.wait(timeout=5))
            installed.append('wrapper')

        def visit():
            ready.wait(timeout=5)
            install()

        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(visit) for _ in range(2)]
            self.assertTrue(entered.wait(timeout=5))
            release.set()
            for future in futures:
                future.result(timeout=10)
        self.assertEqual(installed, ['wrapper'])
