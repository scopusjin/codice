"""Transient renderer state scoped to one Streamlit script execution.

Wrappers are installed once per process, but their containers must never be
shared between users or kept across reruns. This state deliberately stays out
of session_state (and therefore out of form snapshots and saved FC choices).
"""
from collections.abc import MutableMapping
from contextvars import ContextVar
from functools import wraps
from threading import RLock
from types import MappingProxyType

_contexts = ContextVar('mortem_render_contexts', default=None)
_installation_lock = RLock()


def reset_render_contexts():
    """Start a fresh layout before rendering a page, also on the same thread."""
    _contexts.set({})


class RenderContext(MutableMapping):
    """Shared handle, execution-local contents; defaults must be immutable."""
    def __init__(self, name, defaults):
        self._name = name
        self._defaults = MappingProxyType(dict(defaults))

    def _values(self):
        contexts = _contexts.get()
        if contexts is None:
            reset_render_contexts()
            contexts = _contexts.get()
        if self._name not in contexts:
            contexts[self._name] = dict(self._defaults)
        return contexts[self._name]

    def __getitem__(self, key):
        return self._values()[key]

    def __setitem__(self, key, value):
        self._values()[key] = value

    def __delitem__(self, key):
        del self._values()[key]

    def __iter__(self):
        return iter(self._values())

    def __len__(self):
        return len(self._values())


def serialized_installation(install):
    """Keep concurrent first visits from installing duplicate wrapper chains."""
    @wraps(install)
    def wrapped(*args, **kwargs):
        with _installation_lock:
            return install(*args, **kwargs)
    return wrapped


electrical_images = RenderContext('electrical_images', {'suppressed': False})
