# -*- coding: utf-8 -*-

from app.device_mode import classify_mobile_headers


def test_client_hint_mobile_prevale():
    assert classify_mobile_headers({
        "Sec-CH-UA-Mobile": "?1",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)",
    }) is True


def test_client_hint_desktop_prevale_anche_su_android():
    assert classify_mobile_headers({
        "Sec-CH-UA-Mobile": "?0",
        "User-Agent": "Mozilla/5.0 (Linux; Android 14; Tablet)",
    }) is False


def test_iphone_e_android_mobile_sono_mobile():
    assert classify_mobile_headers({
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X)",
    }) is True
    assert classify_mobile_headers({
        "User-Agent": "Mozilla/5.0 (Linux; Android 15; Pixel 9) AppleWebKit/537.36 Mobile Safari/537.36",
    }) is True


def test_desktop_non_e_mobile():
    assert classify_mobile_headers({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/151.0 Safari/537.36",
    }) is False


def test_header_case_insensitive_con_mapping_semplice():
    assert classify_mobile_headers({
        "sec-ch-ua-mobile": "?1",
        "user-agent": "desktop",
    }) is True
