"""Offline regression coverage for truthful format badges and artwork fallback."""
import base64
import io
import json
import urllib.error
from pathlib import Path

import artwork_gallery as art
from core import Entry
from library_presentation import format_badge_info

PNG = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAOZrkK0AAAAASUVORK5CYII=')

def game(name, size=118_000_000):
    p = Path('/virtual/ROMs/psx') / name
    return Entry(p, p.stem, 'PS1', size, p.suffix)

def test_format_badges_truthfully_describe_actual_extensions():
    for name, badge in [('Clock Tower.cue', 'BIN/CUE'),('Clock Tower.chd','CHD'),
                        ('Final Fantasy VII.m3u','M3U'),('Socom.iso','ISO'),
                        ('Game.pbp','PBP')]:
        info = format_badge_info(game(name))
        assert info['badge'] == badge
    assert 'NOT a CHD' in format_badge_info(game('Clock Tower.cue'))['verification']
    assert 'NOT been independently rechecked' in format_badge_info(game('Clock Tower.chd'))['verification']

class Reply:
    def __init__(self, url, body):
        self.url = url; self.data = io.BytesIO(body)
    def __enter__(self): return self
    def __exit__(self, *args): pass
    def geturl(self): return self.url
    def read(self, amount): return self.data.read(amount)

def fake_catalog_open(request, timeout=None):
    url = request.full_url
    if url.startswith('https://thumbnails.libretro.com'):
        raise urllib.error.URLError('simulated Libretro outage')
    if url.startswith('https://api.github.com'):
        return Reply(url, json.dumps({'truncated':False,'tree':[
           {'type':'blob','path':'Named_Boxarts/Clock Tower - The First Fear (Japan).png'},
           {'type':'blob','path':'Named_Boxarts/Dino Crisis (USA).png'},
           {'type':'blob','path':'Named_Titles/Dino Crisis (USA).png'}
        ]}).encode())
    raise AssertionError(url)

def test_manual_catalog_uses_github_fallback_during_libretro_outage(tmp_path, monkeypatch):
    monkeypatch.setenv('LOCALAPPDATA', str(tmp_path/'local'))
    found = art.catalog_for('PS1', tmp_path/'card', opener=fake_catalog_open)
    assert found == ['Clock Tower - The First Fear (Japan)', 'Dino Crisis (USA)']
    assert art.manual_search_results('Clock Tower', found)[0]['title'].startswith('Clock Tower')
    assert art.catalog_for('PS1', tmp_path/'card', opener=lambda *args, **kwargs: 1) == found

def test_preview_cover_tries_official_mirror_when_primary_is_unavailable(tmp_path, monkeypatch):
    monkeypatch.setenv('LOCALAPPDATA', str(tmp_path/'local'))
    seen=[]
    def opener(req, timeout=0):
        seen.append(req.full_url)
        if 'thumbnails.libretro.com' in req.full_url:
            raise urllib.error.URLError('Libretro offline')
        return Reply(req.full_url, PNG)
    result=art.preview_search_cover(tmp_path/'card','PS1','Clock Tower - The First Fear (Japan)',opener=opener)
    assert result.read_bytes() == PNG
    assert len(seen)==2 and 'raw.githubusercontent.com' in seen[1]

def test_redirect_outside_allowed_artwork_hosts_is_rejected(tmp_path, monkeypatch):
    def opener(req, timeout=0):
        return Reply('https://untrusted.example/cover.png', PNG)
    import pytest
    with pytest.raises(ValueError):
        art.fetch_artwork_image('PS1','Clock Tower',opener=opener)
