"""User-selected cover-art import and opt-in Libretro thumbnail lookup.

No unlicensed ROMs, no filesystem-wide scrape. Users choose individual images
or explicitly request a best-effort game filename match from Libretro.
"""
from __future__ import annotations
import re
import shutil
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from core import SYSTEM_DIR

ART_SOURCE = 'https://thumbnails.libretro.com/'
SYSTEM_ART = {
  'PS1':'Sony - PlayStation', 'PSP':'Sony - PlayStation Portable',
  'GBA':'Nintendo - Game Boy Advance', 'GB':'Nintendo - Game Boy',
  'GBC':'Nintendo - Game Boy Color', 'NES':'Nintendo - Nintendo Entertainment System',
  'SNES':'Nintendo - Super Nintendo Entertainment System', 'Genesis':'Sega - Mega Drive - Genesis',
  'Nintendo 64':'Nintendo - Nintendo 64', 'Nintendo DS':'Nintendo - Nintendo DS',
  'Dreamcast':'Sega - Dreamcast',
  'PS2':'Sony - PlayStation 2', 'GameCube':'Nintendo - GameCube',
}
MAX_COVER = 8*1024*1024


def safe_art_name(name: str) -> str:
    name = re.sub(r'[\\/:*?"<>|\x00-\x1f]', '_', name).strip(' .')
    if not name or name in {'.', '..'}: raise ValueError('Invalid artwork name')
    return name[:180]


def cover_destination(root: Path, system: str, game_stem: str) -> Path:
    if system not in SYSTEM_DIR: raise ValueError('Unknown game system')
    return Path(root)/'Media'/'BoxArt'/SYSTEM_DIR[system]/(safe_art_name(game_stem)+'.png')


def add_local_cover(image: Path, root: Path, system: str, game_stem: str) -> Path:
    image = Path(image)
    if image.suffix.lower() != '.png':
        raise ValueError('Please choose a PNG cover image')
    if not image.is_file() or not 0 < image.stat().st_size <= MAX_COVER:
        raise ValueError('Cover image is missing or too large')
    if image.read_bytes()[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError('This is not a valid PNG file')
    dest = cover_destination(root, system, game_stem)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        raise FileExistsError('Artwork already exists; no file was overwritten')
    shutil.copy2(image, dest)
    return dest


def download_boxart(root: Path, system: str, game_stem: str, progress=None, cancel=None) -> dict:
    """Best effort exact-name thumbnail matching (no fuzzy false positives)."""
    if system not in SYSTEM_ART: return {'status':'unsupported'}
    dest = cover_destination(root, system, game_stem)
    if dest.exists(): return {'status':'already present', 'path':str(dest)}
    game = safe_art_name(game_stem)
    # Libretro thumbnails follow game-title names, including region tags.
    url = ART_SOURCE + urllib.parse.quote(SYSTEM_ART[system], safe='') + '/Named_Boxarts/' + urllib.parse.quote(game + '.png', safe='')
    request = urllib.request.Request(url, headers={'User-Agent':'RetroLibraryStudio/1.2.0'})
    try:
        with urllib.request.urlopen(request, timeout=18) as r:
            if urllib.parse.urlparse(r.geturl()).hostname != 'thumbnails.libretro.com':
                raise RuntimeError('Unexpected artwork download redirect')
            data = r.read(MAX_COVER+1)
    except urllib.error.HTTPError as exc:
        if exc.code == 404: return {'status':'not found'}
        return {'status':f'HTTP {exc.code}'}
    if cancel is not None and cancel.is_set(): return {'status':'cancelled'}
    if not (8 < len(data) <= MAX_COVER and data[:8] == b'\x89PNG\r\n\x1a\n'):
        raise ValueError('Downloaded cover was not a valid PNG')
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open('xb') as f: f.write(data)
    if progress: progress('Cover downloaded: ' + game, 1, 1)
    return {'status':'downloaded', 'path':str(dest)}



def unique_game_art_entries(entries):
    """Skip PS1 data tracks and avoid duplicate art requests for the same game."""
    all_items = [item for item in entries if item.system in SYSTEM_ART]
    cue_stems = {(item.system, item.label.casefold()) for item in all_items
                 if item.extension.lower() in ('.cue','.m3u')}
    seen = set()
    output = []
    for item in all_items:
        ext = item.extension.lower()
        key = (item.system, item.label.casefold())
        if ext in ('.bin','.img') and key in cue_stems:
            continue
        if key in seen:
            continue
        seen.add(key)
        output.append(item)
    return output

def fetch_cover_batch(entries, root, progress=None, cancel=None, max_items=200):
    results = []
    # Restrict volume and rate. Explicit user-triggered lookup only.
    for i, entry in enumerate(entries[:max_items]):
        if cancel is not None and cancel.is_set(): break
        try:
            row = download_boxart(root, entry.system, entry.label, cancel=cancel)
        except Exception as exc:
            row = {'status':'error: '+str(exc)}
        results.append((entry.label, row))
        if progress: progress(f'Looking up covers: {i+1}/{min(len(entries),max_items)}', i+1, min(len(entries),max_items))
    return results
