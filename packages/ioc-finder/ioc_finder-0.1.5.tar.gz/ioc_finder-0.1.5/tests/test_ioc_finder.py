#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest


from ioc_finder import find_iocs


@pytest.fixture
def text_a():
    """Provide some generic text for the tests below."""
    return 'example.com is a nice domain if you consider http://bad.com/test/bingo.php to be bad. {} {} {} 1.2.3.4 192.64.55.61 bad12312@example.org'.format('a'*32, 'b'*40, 'c'*64)


def test_ioc_finder(text_a):
    iocs = find_iocs(text_a)
    assert len(iocs['domain']) == 3
    assert 'example.com' in iocs['domain']
    assert 'example.org' in iocs['domain']
    assert 'bad.com' in iocs['domain']

    assert len(iocs['email']) == 1
    assert 'bad12312@example.org' in iocs['email']

    assert len(iocs['ipv4']) == 2
    assert '1.2.3.4' in iocs['ipv4']
    assert '192.64.55.61' in iocs['ipv4']

    assert len(iocs['url']) == 1
    assert 'http://bad.com/test/bingo.php' in iocs['url']

    assert len(iocs['md5']) == 1
    assert 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa' in iocs['md5']

    assert len(iocs['sha1']) == 1
    assert 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb' in iocs['sha1']

    assert len(iocs['sha256']) == 1
    assert 'cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc' in iocs['sha256']


def test_url_parsing():
    """Test some specific url examples."""
    s = "https://github.com/StylishThemes/GitHub-Dark/blob/master/tools/authors.sh"
    iocs = find_iocs(s)
    assert len(iocs['url']) == 1
    assert 'https://github.com/StylishThemes/GitHub-Dark/blob/master/tools/authors.sh' in iocs['url']


def test_address_email_address():
    s = "test@[192.168.2.1]"
    iocs = find_iocs(s)
    assert len(iocs['ipv4_email']) == 1
    assert 'test@[192.168.2.1]' in iocs['ipv4_email']
    assert len(iocs['ipv4']) == 1
    assert '192.168.2.1' in iocs['ipv4']


def test_address_domain_url():
    s = "http://192.64.55.61/test.php"
    iocs = find_iocs(s)
    assert len(iocs['url']) == 1
    assert 'http://192.64.55.61/test.php' in iocs['url']
    assert len(iocs['ipv4']) == 1
    assert '192.64.55.61' in iocs['ipv4']


def test_ipv4_hostname_email_address():
    s = "bad@[192.168.7.3]"
    iocs = find_iocs(s)
    assert len(iocs['ipv4']) == 1
    assert '192.168.7.3' in iocs['ipv4']
    assert len(iocs['ipv4_email']) == 1
    assert 'bad@[192.168.7.3]' in iocs['ipv4_email']


def test_unicode_domain_name():
    s = "ȩxample.com"
    iocs = find_iocs(s)
    assert len(iocs['domain']) == 1
    assert '\\u0229xample.com' in iocs['domain']


def test_ioc_deduplication():
    """Make sure the results returned from the ioc_finder are deduplicated."""
    iocs = find_iocs('example.com example.com')
    assert len(iocs['domain']) == 1
