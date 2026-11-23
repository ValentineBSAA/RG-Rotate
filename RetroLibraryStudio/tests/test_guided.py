import io
import json
import zipfile
from pathlib import Path
from unittest.mock import patch
import pytest
from core import prepare_layout
from library_import import infer_system, import_grouped
from tool_setup import (
    tool_status, _extract_platform_zip, _find_seven_zip_stream,
    official_mame_release,
)


def test_infer_only_unambiguous_formats():
    assert infer_system(Path('/downloads/game.cso'), 'PS1') == 'PSP'
    assert infer_system(Path('/downloads/game.gba'), 'PS1') == 'GBA'
    assert infer_system(Path('/downloads/game.cue'), 'PSP') == 'PS1'
    assert infer_system(Path('/downloads/game.iso'), 'PSP') == 'PSP'
    assert infer_system(Path('/downloads/game.chd'), 'PSP') == 'PSP'
    assert infer_system(Path('/downloads/game.pbp'), 'PS1') == 'PS1'
    assert infer_system(Path('/downloads/psp/game.iso'), 'PS1') == 'PSP'
    assert infer_system(Path('/downloads/psx/game.chd'), 'PSP') == 'PS1'


def test_import_mixed_game_folder_and_preserve_originals(tmp_path):
    src = tmp_path/'Downloads'; src.mkdir()
    (src/'gb_game.gb').write_bytes(b'gb-data')
    (src/'psp_game.cso').write_bytes(b'psp-data')
    (src/'ambiguous.iso').write_bytes(b'psp-iso')
    dest=tmp_path/'VirtualCard'; prepare_layout(dest)
    res=import_grouped(list(src.iterdir()),dest,'PSP')
    assert res['copied']==3 and not res['errors']
    assert (dest/'ROMs'/'gb'/'gb_game.gb').read_bytes()==b'gb-data'
    assert (dest/'ROMs'/'psp'/'psp_game.cso').read_bytes()==b'psp-data'
    assert (dest/'ROMs'/'psp'/'ambiguous.iso').read_bytes()==b'psp-iso'
    assert (src/'ambiguous.iso').read_bytes()==b'psp-iso'


def test_host_tool_readiness_does_not_require_running_binary(tmp_path):
    status=tool_status(tmp_path)
    assert not status['Android Platform Tools']['installed']
    (tmp_path/'platform-tools').mkdir()
    (tmp_path/'platform-tools'/'adb.exe').write_bytes(b'placeholder')
    assert tool_status(tmp_path)['Android Platform Tools']['file_present']
    assert not tool_status(tmp_path)['Android Platform Tools']['installed']


def test_platform_tools_zip_safe_extraction(tmp_path):
    path=tmp_path/'adb.zip'
    with zipfile.ZipFile(path,'w') as z:
        z.writestr('platform-tools/adb.exe',b'Exe')
        z.writestr('platform-tools/AdbWinApi.dll',b'Lib')
    out=tmp_path/'out';out.mkdir()
    _extract_platform_zip(path,out)
    assert (out/'platform-tools'/'adb.exe').read_bytes()==b'Exe'


def test_platform_tools_rejects_path_traversal(tmp_path):
    path=tmp_path/'evil.zip'
    with zipfile.ZipFile(path,'w') as z:
        z.writestr('platform-tools/../../outside.txt',b'no')
        z.writestr('platform-tools/adb.exe',b'Exe')
    with pytest.raises(ValueError):
        _extract_platform_zip(path,tmp_path/'extract')
    assert not (tmp_path/'outside.txt').exists()


def test_mame_package_sfx_payload_carving(tmp_path):
    source=tmp_path/'mame.exe'
    source.write_bytes(b'MZ' + b'\x00'*150 + b"7z\xbc\xaf\x27\x1c" + b'simulated-7z-data')
    out=tmp_path/'mame.7z'
    _find_seven_zip_stream(source,out)
    assert out.read_bytes().startswith(b"7z\xbc\xaf\x27\x1c")


def test_mame_asset_origin_validation(monkeypatch):
    class Response:
        def __enter__(self):return self
        def __exit__(self,*args):pass
        def read(self,*args):return json.dumps({'assets':[{
            'name':'mame0289b_x64.exe',
            'browser_download_url':'https://not-official.example/mame.exe'
        }]}).encode()
    monkeypatch.setattr('urllib.request.urlopen',lambda *args,**kwargs:Response())
    with pytest.raises(RuntimeError, match='Unexpected MAME'):
        official_mame_release()


def test_new_user_with_empty_downloads_can_import_without_an_incoming_queue(tmp_path):
    from core import incoming_inventory, inventory
    from sync_engine import transfer_verified
    downloads=tmp_path/'Downloads'; downloads.mkdir()
    workspace=tmp_path/'VirtualCard'; prepare_layout(workspace)
    assert incoming_inventory(downloads)==([],0)
    own_games=tmp_path/'My Saved Games'; own_games.mkdir()
    file=own_games/'Racing Game.cso'; file.write_bytes(b'PSP_CONTENT' * 7)
    imported=import_grouped([file],workspace,'PS1')
    assert imported['copied']==1 and imported['errors']==[]
    entries,used,count=inventory(workspace)
    assert count==1 and entries[0].system=='PSP'
    target=tmp_path/'PracticeCard'; target.mkdir()
    done=transfer_verified(workspace,target,simulation=True)
    assert done['verified']==1 and not done['errors']
    assert (target/'ROMs'/'psp'/'Racing Game.cso').read_bytes()==file.read_bytes()
    assert file.is_file()  # Originals stay untouched.


def test_two_systems_and_zip_archive_import_to_expected_directories(tmp_path):
    downloads=tmp_path/'GameFolders';downloads.mkdir()
    gba=downloads/'Super Puzzle.gba';gba.write_bytes(b'GBA')
    zipgame=downloads/'PSP'/'handheld.zip';zipgame.parent.mkdir()
    with zipfile.ZipFile(zipgame,'w') as z:
        z.writestr('Handheld.iso',b'ISO')
    virtual=tmp_path/'Card';prepare_layout(virtual)
    result=import_grouped([gba,zipgame],virtual,'PS1')
    assert not result['errors']
    assert (virtual/'ROMs'/'gba'/'Super Puzzle.gba').read_bytes()==b'GBA'
    assert any(path.read_bytes()==b'ISO' for path in (virtual/'ROMs'/'psp').rglob('*.iso'))


def test_ui_source_has_persisted_geometry_and_scale():
    # Headless source contract test where the current CI lacks Qt/PySide6.
    text=(Path(__file__).resolve().parents[1]/'app.py').read_text(encoding='utf-8')
    assert "setValue('window_geometry'" in text
    assert "restoreGeometry(geometry)" in text
    assert "('125%', 125)" in text
    assert "Your first games go here" in text
    assert "Try a safe practice copy first" in text


def test_adb_installer_unpacks_without_executing_anything(tmp_path, monkeypatch):
    import tool_setup
    # Version probe executes the extracted helper, never the downloaded installer.
    checked = []
    monkeypatch.setattr(tool_setup, '_verify_adb', lambda p: checked.append(p))
    def fake_download(url, dest, maximum, progress=None, cancel=None):
        assert url == tool_setup.ADB_URL
        with zipfile.ZipFile(dest, 'w') as archive:
            archive.writestr('platform-tools/adb.exe', b'fake-adb')
            archive.writestr('platform-tools/AdbWinApi.dll', b'fake-dll')
        return '00' * 32
    monkeypatch.setattr(tool_setup, '_download', fake_download)
    result = tool_setup.install_adb(tmp_path)
    assert result['ok']
    assert (tmp_path/'platform-tools'/'adb.exe').read_bytes() == b'fake-adb'
    assert (tmp_path/'platform-tools.json').is_file()
    result2 = tool_setup.install_adb(tmp_path)
    assert result2['state']=='already ready'


def test_chdman_installer_only_unpacks_official_package(tmp_path, monkeypatch):
    import tool_setup
    monkeypatch.setattr(tool_setup, 'official_mame_release',
                        lambda: ('https://github.com/mamedev/mame/releases/download/mame0289/mame0289b_x64.exe','mame0289b_x64.exe'))
    def fake_download(url, dest, maximum, progress=None, cancel=None):
        dest.write_bytes(b'MZplaceholder')
        return '11' * 32
    monkeypatch.setattr(tool_setup, '_download', fake_download)
    monkeypatch.setattr(tool_setup, '_find_seven_zip_stream',
                        lambda source, out: out.write_bytes(b'7zpayload'))
    def fake_extract(archive, folder):
        pack=folder/'mame';pack.mkdir()
        (pack/'chdman.exe').write_bytes(b'fake-chdman')
        return pack
    monkeypatch.setattr(tool_setup, '_extract_chdman', fake_extract)
    # The old fixture contains a pretend EXE; mock harmless executable validation.
    monkeypatch.setattr(tool_setup, 'verify_tool', lambda exe: (True, 'Mock verified'))
    result = tool_setup.install_chdman(tmp_path)
    assert result['ok']
    assert (tmp_path/'chdman'/'chdman.exe').read_bytes()==b'fake-chdman'
    assert (tmp_path/'chdman.json').is_file()


def test_cocoon_official_repository_move_is_accepted(monkeypatch):
    import software
    class Response:
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def read(self, *args):
            return json.dumps({'assets':[{'name':'Cocoon.apk',
                'browser_download_url':'https://github.com/inssekt/CocoonFE/releases/download/beta-3.11/Cocoon.apk'}]}).encode()
    monkeypatch.setattr(software, '_urlopen', lambda *args,**kwargs: Response())
    url,name=software.resolve('Cocoon Shell')
    assert url.startswith('https://github.com/inssekt/CocoonFE/')
    assert name == 'Cocoon.apk'
