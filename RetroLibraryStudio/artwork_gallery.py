"""Artwork catalog, conservative title matching, and NAS-safe cover staging.

The original cover is kept in Media/BoxArt on the virtual card, while Windows
keeps a local preview cache. No NAS image reads occur in the Qt paint path.
"""
from __future__ import annotations

import hashlib
import html
import json
import os
import re
import shutil
import time
import urllib.error
import urllib.parse
import urllib.request
from difflib import SequenceMatcher
from html.parser import HTMLParser
from pathlib import Path

from artwork import SYSTEM_ART, cover_destination, MAX_COVER

BASE_URL = 'https://thumbnails.libretro.com/'
MAX_INDEX_BYTES = 15 * 1024 * 1024
CACHE_TTL = 72 * 3600
REGION_RE = re.compile(r'\s*\((?:USA|Europe|Japan|World|Asia|Australia|Brazil|Korea|Taiwan|China|France|Germany|Spain|Italy|Rev\s*\w+|Disc\s*\d+|Disk\s*\d+|En|En,[^)]*|[A-Za-z]{2}(?:,[A-Za-z]{2})+)\)', re.I)
DISC_RE = re.compile(r'\s*\[(?:disc|disk|cd)\s*\d+\]', re.I)
PUNCT_RE = re.compile(r'[^\w]+', re.UNICODE)
PATCH_TAG = re.compile(r'\s*\((?:English Patch(?:ed)?(?: Version)?|Fan Translation|T-En[^)]*)\)', re.I)


def clean_title(stem: str) -> str:
    """Remove only well-known release tags; never drop meaningful editions."""
    title = str(stem).strip()
    title = REGION_RE.sub('', PATCH_TAG.sub('', title))
    title = DISC_RE.sub('', title)
    return re.sub(r'\s+', ' ', title).strip(' -._')


def key_title(stem: str) -> str:
    return ' '.join(PUNCT_RE.sub(' ', clean_title(stem).casefold()).split())


def candidate_score(game: str, candidate: str) -> float:
    a, b = key_title(game), key_title(candidate)
    if not a or not b:
        return 0.0
    if a == b:
        return 1.0
    sa, sb = set(a.split()), set(b.split())
    overlap = len(sa & sb) / max(1, len(sa | sb))
    if not overlap:
        return 0.0
    return round(.65 * SequenceMatcher(None, a, b).ratio() + .35 * overlap, 4)


def region_priority(name: str) -> int:
    return 4 if '(USA)' in name else 3 if '(World)' in name else 2 if '(Europe)' in name else 1


def find_art_matches(stem: str, catalog: list[str], limit: int = 6) -> dict:
    """Auto-assign only normalized exact names. Fuzzy results are REVIEW ONLY."""
    game_key = key_title(stem)
    exact = [c for c in catalog if key_title(c) == game_key] if game_key else []
    auto = sorted(exact, key=lambda x: (-region_priority(x), len(x), x))[0] if exact else None
    ranked = sorted(((candidate_score(stem, c), c) for c in catalog), reverse=True)
    suggestions = [dict(title=c, score=score) for score, c in ranked
                   if score >= .35][:max(0, limit)]
    return {'automatic': auto, 'suggestions': suggestions, 'needs_review': not bool(auto)}


def manual_search_results(query: str, catalog: list[str], limit: int = 40) -> list[dict]:
    """Search an artwork catalog by USER-entered title, without assigning a cover.

    Prioritize exact/prefix/substring terms before fuzzy results. A manual
    result always requires the user to choose it, even when the title matches.
    """
    needle = key_title(query)
    if not needle:
        return []
    parts = needle.split()
    scored = []
    seen = set()
    for name in catalog:
        if not isinstance(name, str) or not name or name in seen:
            continue
        seen.add(name)
        candidate = key_title(name)
        if not candidate:
            continue
        if candidate == needle:
            bucket = 0
        elif candidate.startswith(needle):
            bucket = 1
        elif needle in candidate:
            bucket = 2
        elif all(any(token.startswith(part) for token in candidate.split()) for part in parts):
            bucket = 3
        else:
            # Fuzzy matching is useful for typos, but never treat it as a
            # confirmed edition. Avoid noisy results for very short queries.
            similarity = candidate_score(needle, name)
            if len(needle) < 4 or similarity < 0.56:
                continue
            bucket = 4
        scored.append((bucket, -candidate_score(needle, name), -region_priority(name),
                       len(candidate), name.casefold(), name))
    scored.sort()
    return [{'title': item[-1], 'score': round(-item[1], 4)}
            for item in scored[:max(0, min(100, limit))]]


def preview_search_cover(workspace: Path, system: str, source_title: str, opener=None) -> Path:
    """Download only a local Windows preview. Never touch the NAS or ROMs."""
    if system not in SYSTEM_ART:
        raise ValueError('Artwork not supported for this system')
    if not source_title or len(source_title) > 240:
        raise ValueError('Invalid artwork title')
    identity = hashlib.sha256(source_title.encode('utf-8')).hexdigest()[:28]
    preview = local_cache_root(workspace) / 'search-previews' / system / (identity + '.png')
    if preview.is_file():
        return preview
    directory = urllib.parse.quote(SYSTEM_ART[system], safe='')
    filename = urllib.parse.quote(source_title + '.png', safe='')
    request = urllib.request.Request(f'{BASE_URL}{directory}/Named_Boxarts/{filename}',
                                     headers={'User-Agent':'RetroLibraryStudio/1.3.1'})
    open_fn = opener or urllib.request.urlopen
    with open_fn(request, timeout=16) as response:
        if urllib.parse.urlsplit(response.geturl()).hostname != 'thumbnails.libretro.com':
            raise ValueError('Unexpected artwork preview redirect')
        content = response.read(MAX_COVER + 1)
    _safe_png(content)
    preview.parent.mkdir(parents=True, exist_ok=True)
    temp = preview.with_suffix('.png.tmp')
    try:
        temp.write_bytes(content)
        temp.replace(preview)
    finally:
        temp.unlink(missing_ok=True)
    return preview


class _Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
    def handle_starttag(self, tag, attrs):
        if tag.lower() == 'a':
            self.links.extend(value for name, value in attrs if name.lower() == 'href' and value)


def parse_index_text(body: bytes) -> list[str]:
    """Libretro's optional .index listing may be plain newline-delimited paths."""
    found = []
    seen = set()
    for row in body.decode('utf-8', errors='replace').splitlines():
        item = urllib.parse.unquote(row.strip().strip('"').replace('\\', '/'))
        if not item.lower().endswith('.png'):
            continue
        name = item.rsplit('/',1)[-1][:-4]
        if name and name not in seen:
            seen.add(name)
            found.append(name)
    return found


def parse_index(body: bytes) -> list[str]:
    parser = _Links()
    parser.feed(body.decode('utf-8', errors='replace'))
    names = []
    seen = set()
    for href in parser.links:
        path = urllib.parse.urlsplit(html.unescape(href)).path
        if not path.lower().endswith('.png'):
            continue
        name = urllib.parse.unquote(path.rsplit('/', 1)[-1])
        if not name.lower().endswith('.png') or '/' in name or '\\' in name:
            continue
        stem = name[:-4]
        if stem and stem not in seen:
            seen.add(stem)
            names.append(stem)
    return names


def local_cache_root(workspace: Path) -> Path:
    base = Path(os.environ.get('LOCALAPPDATA', '') or (Path.home() / '.retro-library-studio'))
    # Path is used as a cache key, not as a security boundary.
    key = hashlib.sha256(os.path.normcase(os.path.abspath(str(workspace))).encode('utf-8')).hexdigest()[:20]
    return base / 'RetroLibraryStudio' / 'ArtworkCache' / key


def cached_preview(workspace: Path, system: str, stem: str) -> Path:
    from artwork import safe_art_name
    return local_cache_root(workspace) / 'images' / system / (safe_art_name(stem) + '.png')


def catalog_for(system: str, workspace: Path, opener=None) -> list[str]:
    if system not in SYSTEM_ART:
        return []
    directory = local_cache_root(workspace) / 'catalog'
    file = directory / (system + '.json')
    if file.is_file() and time.time() - file.stat().st_mtime < CACHE_TTL:
        try:
            data = json.loads(file.read_text(encoding='utf-8'))
            if isinstance(data, list) and all(isinstance(x, str) for x in data):
                return data
        except (OSError, ValueError):
            pass
    encoded = urllib.parse.quote(SYSTEM_ART[system], safe='')
    url = BASE_URL + encoded + '/Named_Boxarts/'
    open_fn = opener or urllib.request.urlopen
    try:
        names = []
        # The .index file, where published, is far smaller than an HTML listing.
        for candidate_url, parser in ((url + '.index', parse_index_text), (url, parse_index)):
            try:
                request = urllib.request.Request(candidate_url,
                            headers={'User-Agent': 'RetroLibraryStudio/1.3.0'})
                with open_fn(request, timeout=12) as response:
                    final = urllib.parse.urlsplit(response.geturl()).hostname
                    if final != 'thumbnails.libretro.com':
                        raise ValueError('Unexpected artwork catalog redirect')
                    body = response.read(MAX_INDEX_BYTES + 1)
                if len(body) > MAX_INDEX_BYTES:
                    raise ValueError('Artwork listing is too large')
                names = parser(body)
                if names:
                    break
            except (OSError, ValueError, urllib.error.URLError):
                continue
        if not names:
            raise ValueError('Artwork catalog not reachable')
        directory.mkdir(parents=True, exist_ok=True)
        temp = file.with_suffix('.json.tmp')
        temp.write_text(json.dumps(names, ensure_ascii=False), encoding='utf-8')
        temp.replace(file)
        return names
    except (OSError, ValueError, urllib.error.URLError):
        # Network unavailable: allow stale LOCAL catalog rather than freeze the app.
        if file.exists():
            try:
                return json.loads(file.read_text(encoding='utf-8'))
            except (OSError, ValueError):
                pass
        return []


def _safe_png(data: bytes):
    if not (32 <= len(data) <= MAX_COVER and data.startswith(b'\x89PNG\r\n\x1a\n')):
        raise ValueError('Cover is not a supported PNG or is too large')


def save_cover_bytes(workspace: Path, system: str, stem: str, data: bytes,
                     replace: bool = False, source: str = '') -> dict:
    """Atomic NAS publish and local preview; never silently replace another cover."""
    _safe_png(data)
    target = cover_destination(workspace, system, stem)
    cache = cached_preview(workspace, system, stem)
    cache.parent.mkdir(parents=True, exist_ok=True)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and not replace:
        if not cache.exists():
            shutil.copy2(target, cache)
        return {'status': 'already present', 'preview': str(cache), 'target': str(target)}
    part = target.with_name(target.name + '.retro-art-part')
    if part.exists():
        part.unlink()  # only our temporary ARTWORK file, never a ROM
    try:
        with part.open('xb') as stream:
            stream.write(data)
        if target.exists() and not replace:
            part.unlink(missing_ok=True)
            return {'status': 'already present', 'preview': str(cache), 'target': str(target)}
        part.replace(target)
        tmp = cache.with_name(cache.name + '.tmp')
        tmp.write_bytes(data)
        tmp.replace(cache)
    finally:
        part.unlink(missing_ok=True)
    status = 'replaced' if replace else 'downloaded'
    result = {'status': status, 'preview': str(cache), 'target': str(target)}
    if source:
        result['source_title'] = source
    return result


def stage_online_cover(workspace: Path, system: str, stem: str, source_title: str,
                       replace: bool = False, opener=None) -> dict:
    if system not in SYSTEM_ART:
        return {'status': 'unsupported'}
    target = cover_destination(workspace, system, stem)
    cache = cached_preview(workspace, system, stem)
    if target.exists() and not replace:
        if not cache.exists():
            cache.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(target, cache)
        return {'status': 'already present', 'preview': str(cache), 'target': str(target)}
    directory = urllib.parse.quote(SYSTEM_ART[system], safe='')
    image_name = urllib.parse.quote(source_title + '.png', safe='')
    url = f'{BASE_URL}{directory}/Named_Boxarts/{image_name}'
    open_fn = opener or urllib.request.urlopen
    req = urllib.request.Request(url, headers={'User-Agent': 'RetroLibraryStudio/1.3.0'})
    with open_fn(req, timeout=16) as response:
        if urllib.parse.urlsplit(response.geturl()).hostname != 'thumbnails.libretro.com':
            raise ValueError('Unexpected cover redirect')
        data = response.read(MAX_COVER + 1)
    return save_cover_bytes(workspace, system, stem, data, replace=replace, source=source_title)



def direct_cover_fallback(workspace: Path, system: str, stem: str, downloader=None) -> dict:
    """Try a few exact canonical region variants when Libretro's index is offline.

    No fuzzy auto-assignment. A special edition remains a special edition.
    Avoid a large number of requests and return a readable, retryable result.
    """
    downloader = downloader or stage_online_cover
    clean = clean_title(stem)
    if not clean or len(clean) > 160:
        return {'status': 'review', 'message': 'Use manual artwork search'}
    options = list(dict.fromkeys([clean, clean+' (USA)', clean+' (Japan)', clean+' (Europe)']))
    for title in options:
        try:
            return downloader(workspace, system, stem, title)
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                continue
            return {'status': 'error', 'message': f'Artwork server returned HTTP {exc.code}'}
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            # Don't retry four 16-second requests when the entire server is offline.
            return {'status': 'error', 'message': 'Artwork server unavailable; retry later or choose your own cover'}
    return {'status': 'review', 'message': 'No exact cover found; use Search for a game cover'}

def stage_local_cover(workspace: Path, system: str, stem: str, source: Path, replace: bool = False) -> dict:
    source = Path(source)
    if source.suffix.lower() != '.png':
        # JPG and WEBP get converted via the PySide6 Qt image reader in the helper.
        from PySide6.QtGui import QImage
        img = QImage(str(source))
        if img.isNull():
            raise ValueError('Cannot open that cover image')
        from PySide6.QtCore import QBuffer, QByteArray, QIODevice
        data_array = QByteArray()
        buffer = QBuffer(data_array)
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        if not img.save(buffer, 'PNG'):
            raise ValueError('Could not convert the cover to PNG')
        buffer.close()
        data = bytes(data_array)
    else:
        if source.stat().st_size > MAX_COVER:
            raise ValueError('Cover is too large')
        data = source.read_bytes()
    return save_cover_bytes(workspace, system, stem, data, replace=replace, source='manual')


def local_index(workspace: Path) -> dict:
    path = local_cache_root(workspace) / 'matches.json'
    try:
        result = json.loads(path.read_text(encoding='utf-8'))
        return result if isinstance(result, dict) else {}
    except (OSError, ValueError):
        return {}


def store_local_index(workspace: Path, index: dict) -> None:
    path = local_cache_root(workspace) / 'matches.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix('.json.tmp')
    temp.write_text(json.dumps(index, indent=2, ensure_ascii=False), encoding='utf-8')
    temp.replace(path)


def game_key(system: str, stem: str) -> str:
    return system + ':' + stem


def process_batch(workspace: Path, games: list[dict], progress=None, cancelled=None,
                  max_items: int = 80) -> dict:
    """Automatic matching starts only from a caller-visible user-imported library.

    A match is assigned only when the normalized title is EXACT; fuzzy results
    are stored as suggestions for human review and never silently downloaded.
    """
    index = local_index(workspace)
    stats = {'downloaded': 0, 'already present': 0, 'review': 0, 'error': 0}
    results = []
    catalog_cache = {}
    seen = set()
    for i, game in enumerate(games[:max_items]):
        if cancelled is not None and cancelled.is_set():
            break
        system, stem = game['system'], game['label']
        key = game_key(system, stem)
        if key in seen:
            continue
        seen.add(key)
        status = {'system': system, 'label': stem}
        try:
            if system not in SYSTEM_ART:
                status['status'] = 'unsupported'
            else:
                # Inspect NAS file existence only inside this disposable helper.
                # A cover stored with a moved workspace should be reusable offline.
                target = cover_destination(workspace, system, stem)
                preview = cached_preview(workspace, system, stem)
                if target.is_file():
                    if not preview.is_file():
                        preview.parent.mkdir(parents=True, exist_ok=True)
                        tmp = preview.with_name(preview.name + '.tmp')
                        shutil.copy2(target, tmp)
                        tmp.replace(preview)
                    status['status'] = 'already present'
                    status['preview'] = str(preview)
                else:
                    if system not in catalog_cache:
                        catalog_cache[system] = catalog_for(system, workspace)
                    catalog = catalog_cache[system]
                    if not catalog:
                        # The optional catalog listing can fail even when the
                        # individual PNG files are accessible. Don't give up.
                        status.update(direct_cover_fallback(workspace, system, stem))
                    else:
                        match = find_art_matches(stem, catalog)
                        if match['automatic']:
                            saved = stage_online_cover(workspace, system, stem, match['automatic'])
                            status.update(saved)
                        else:
                            status['status'] = 'review'
                            status['suggestions'] = match['suggestions']
            st = status['status']
            stats[st if st in stats else 'review'] += 1
            index[key] = status
        except Exception as exc:
            stats['error'] += 1
            status['status'] = 'error'
            status['message'] = str(exc)[:300]
            index[key] = status
        results.append(status)
        if progress:
            progress(f'Finding covers: {len(results)} of {min(len(games), max_items)}', len(results), min(len(games), max_items))
    store_local_index(workspace, index)
    return {'stats': stats, 'results': results, 'cancelled': bool(cancelled and cancelled.is_set())}
