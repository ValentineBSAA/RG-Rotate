"""Only authorized Android installer sources; no commercial ROM / BIOS downloading."""
from __future__ import annotations
import hashlib
import json
import os
import re
import urllib.parse
import urllib.request
import zipfile
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from core import CAPACITY, COMPANION_BUDGET, FREE_RESERVE, inventory, safe_walk

USER_AGENT = 'RetroLibraryStudio/1.0 (+https://cocoon-shell.com/resources/)'
GITHUB_RELEASE_API = 'https://api.github.com/repos/KansoMirai/CocoonFE/releases/latest'
GITHUB_RELEASE_API_FALLBACK = 'https://api.github.com/repos/inssekt/CocoonFE/releases/latest'
PPSSPP_PAGE = 'https://www.ppsspp.org/download/'
RETROARCH_PAGE = 'https://www.retroarch.com/platforms.html'
SOFTWARE = {
  'Cocoon Shell': {'homepage': 'https://cocoon-shell.com/resources/', 'mode':'github', 'default':True,
                   'notes':'Default Android home frontend. Android installation and first-run permissions still required.'},
  'PPSSPP': {'homepage': PPSSPP_PAGE, 'mode':'ppsspp', 'default':True,
             'notes':'Recommended PSP emulator.'},
  'RetroArch': {'homepage': RETROARCH_PAGE, 'mode':'retroarch', 'default':True,
                'notes':'Multi-system emulator; cores and settings configured on the device.'},
  'DuckStation': {'homepage': 'https://downloads.duckstation.org/android-testing/', 'mode':'manual', 'default':False,
                  'notes':'Optional. Current Android beta may not work when launched from Cocoon.'},
  'ADB Platform Tools': {'homepage':'https://developer.android.com/tools/releases/platform-tools', 'mode':'manual', 'default':False,
                          'notes':'Optional Windows USB setup; install ADB yourself and authorize device.'},
  'CHDman': {'homepage':'https://docs.mamedev.org/tools/chdman.html', 'mode':'manual', 'default':False,
             'notes':'Optional user-installed disc conversion tool; no blind conversion.'},
}

class ApkLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            href = dict(attrs).get('href', '')
            if '.apk' in href.lower():
                self.links.append(href)


def _urlopen(url: str, timeout=30):
    request = urllib.request.Request(url, headers={'User-Agent': USER_AGENT, 'Accept':'application/json' if 'api.github.com/' in url else '*/*'})
    return urllib.request.urlopen(request, timeout=timeout)


def resolve(name: str) -> tuple[str, str]:
    """Lookup current official APK; errors are explicit, not mirrored or guessed."""
    if name not in SOFTWARE:
        raise ValueError('Unknown app')
    mode = SOFTWARE[name]['mode']
    if mode == 'manual':
        raise ValueError(f'{name} requires manual inspection: {SOFTWARE[name]["homepage"]}')
    if mode == 'github':
        try:
            with _urlopen(GITHUB_RELEASE_API) as stream:
                data = json.load(stream)
        except Exception:
            # Official website links to the same CocoonFE project after its owner moved.
            with _urlopen(GITHUB_RELEASE_API_FALLBACK) as stream:
                data = json.load(stream)
        apks = [x for x in data.get('assets', []) if x.get('name','').lower().endswith('.apk')]
        if not apks:
            raise RuntimeError('Cocoon release has no official APK asset; use its website')
        # Do not select arbitrary non-Android release assets.
        apks.sort(key=lambda x: ('universal' not in x['name'].lower(), 'arm64' not in x['name'].lower(), x['name']))
        url = apks[0]['browser_download_url']
        path = urllib.parse.urlparse(url)
        if path.scheme != 'https' or path.hostname != 'github.com' or not (path.path.startswith('/KansoMirai/CocoonFE/releases/download/') or
            path.path.startswith('/inssekt/CocoonFE/releases/download/')):
            raise RuntimeError('Unexpected Cocoon download origin')
        return url, apks[0]['name']
    page = PPSSPP_PAGE if mode == 'ppsspp' else RETROARCH_PAGE
    with _urlopen(page) as f:
        html = f.read(2_500_000).decode('utf-8', errors='replace')
    parser = ApkLinks(); parser.feed(html)
    base = urllib.parse.urlparse(page)
    links = [urllib.parse.urljoin(page, x) for x in parser.links]
    if mode == 'ppsspp':
        links = [x for x in links if urllib.parse.urlparse(x).hostname in {'www.ppsspp.org', 'ppsspp.org'}
                 and re.search(r'ppsspp.*\.apk(?:\?|$)', x.lower())]
    else:
        links = [x for x in links if (urllib.parse.urlparse(x).hostname or '').endswith('libretro.com')
                 and 'aarch64' in x.lower()]
    if not links:
        raise RuntimeError(f'Official {name} site does not expose a compatible automatic APK link; use homepage')
    url = links[0]
    filename = Path(urllib.parse.urlsplit(url).path).name
    return url, filename


def _apk_ok(path: Path) -> None:
    if not zipfile.is_zipfile(path):
        raise ValueError('Download is not a valid APK/ZIP')
    with zipfile.ZipFile(path) as z:
        if 'AndroidManifest.xml' not in z.namelist():
            raise ValueError('Missing AndroidManifest.xml; not an APK')


def download_apk(name: str, workspace: Path, progress=None, cancel=None) -> dict:
    url, filename = resolve(name)
    package_root = workspace / 'SetupPackages'
    package_root.mkdir(parents=True, exist_ok=True)
    # Normalized basename protects against website filename manipulation.
    filename = re.sub(r'[^A-Za-z0-9._-]+', '_', filename)
    if not filename.lower().endswith('.apk'):
        raise ValueError('Not an APK file')
    dest = package_root / filename
    if dest.exists():
        _apk_ok(dest)
        with dest.open('rb') as existing:
            digest = hashlib.file_digest(existing, 'sha256').hexdigest()
        receipt_path = workspace / '.retro-library' / 'receipts' / (name.replace(' ', '_') + '.json')
        try:
            receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
            verified = (receipt.get('sha256') == digest and receipt.get('url') == url and
                        Path(receipt['file']).resolve() == dest.resolve())
        except (OSError, ValueError, KeyError, TypeError):
            verified = False
        if not verified:
            raise FileExistsError(
                f'{filename} is already present but its official download origin is unverified. '
                'Keep the local APK if you trust it, or rename it before retrying the official download. '
                'Existing files were not overwritten.')
        return {'app':name, 'file':str(dest), 'status':'already downloaded', 'sha256':digest}
    partial = package_root / (filename + '.download-part')
    try:
        with _urlopen(url, timeout=60) as response:
            final_url = response.geturl()
            h = urllib.parse.urlparse(final_url)
            if h.scheme != 'https' or h.hostname not in {'github.com','release-assets.githubusercontent.com','objects.githubusercontent.com',
                                                         'www.ppsspp.org','ppsspp.org','buildbot.libretro.com'}:
                raise ValueError('Redirected to an unapproved download host')
            length = int(response.headers.get('Content-Length') or 0)
            if length > 750 * 1024**2:
                raise ValueError('APK is unusually large')
            _,occupied,_ = inventory(workspace)
            if occupied + (length or 750*1024**2) + COMPANION_BUDGET + FREE_RESERVE > CAPACITY:
                raise OSError('Not enough virtual-card capacity for installer')
            downloaded=0
            digest=hashlib.sha256()
            with partial.open('xb') as output:
                while True:
                    if cancel is not None and cancel.is_set():
                        raise InterruptedError('Download cancelled')
                    chunk=response.read(1024**2)
                    if not chunk:
                        break
                    downloaded+=len(chunk)
                    if downloaded>750*1024**2:
                        raise ValueError('Download exceeds 750 MiB maximum')
                    output.write(chunk); digest.update(chunk)
                    if progress: progress(name, downloaded, length or downloaded)
        _apk_ok(partial)
        partial.rename(dest)
        receipt={'app':name,'url':url,'file':str(dest),'sha256':digest.hexdigest(),'bytes':downloaded,'status':'verified APK structure'}
        receipt_dir = workspace/'.retro-library'/'receipts'
        receipt_dir.mkdir(parents=True,exist_ok=True)
        (receipt_dir / (name.replace(' ','_')+'.json')).write_text(json.dumps(receipt,indent=2),encoding='utf-8')
        return receipt
    finally:
        partial.unlink(missing_ok=True)


def download_selected(names: list[str], workspace: Path, progress=None, cancel=None) -> list[dict]:
    results=[]
    for idx,name in enumerate(names,1):
        if cancel is not None and cancel.is_set():
            break
        if progress: progress(f'{idx}/{len(names)} Downloading {name}', idx-1,len(names))
        try:
            results.append(download_apk(name,workspace,progress,cancel))
        except Exception as exc:
            results.append({'app':name,'status':'failed','error':str(exc)})
    return results
