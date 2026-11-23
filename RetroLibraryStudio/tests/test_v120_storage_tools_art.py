"""v1.2 additions: storage location, NAS option, installer, covers, CHD safety."""
import io
import json
import subprocess
import zipfile
from pathlib import Path
from threading import Event

import pytest

from core import CAPACITY, FREE_RESERVE, COMPANION_BUDGET, prepare_layout
from storage_probe import has_workspace_payload_fast, has_interrupted_files, check_space, usable_stage_bytes, is_network_path, describe_bytes
from chd_convert import verify_tool, convert_cue
from artwork import add_local_cover, cover_destination, download_boxart
from batch_setup import readiness, manual_apk_for, prepare_batch
from workspace_setup import count_workspace_files
import tool_setup


def test_empty_structured_card_switch_fast(tmp_path):
    card = tmp_path / 'Card'
    prepare_layout(card)
    assert not has_workspace_payload_fast(card)
    (card / 'ROMs' / 'psp' / 'example.cso').write_bytes(b'GAME')
    assert has_workspace_payload_fast(card)


def test_setup_receipt_counts_as_payload_for_migration(tmp_path):
    card = tmp_path / 'Card'
    prepare_layout(card)
    receipts = card / '.retro-library' / 'receipts'
    receipts.mkdir(parents=True)
    (receipts / 'download.json').write_text('{}')
    assert has_workspace_payload_fast(card)


def test_disk_capacity_not_preallocated(tmp_path):
    card = tmp_path / 'My Virtual Card'
    prepare_layout(card)
    space = check_space(card)
    assert space.free > 0 and space.total >= space.free
    assert sum(f.stat().st_size for f in card.rglob('*') if f.is_file()) == 0
    assert usable_stage_bytes(0, 10_000_000_000, CAPACITY, COMPANION_BUDGET, FREE_RESERVE) == 10_000_000_000
    assert usable_stage_bytes(0, 600_000_000_000, CAPACITY, COMPANION_BUDGET, FREE_RESERVE) == CAPACITY - COMPANION_BUDGET - FREE_RESERVE


def test_unc_network_location_recognized():
    assert is_network_path(Path(r'\\NAS\Games\RG Rotate'))
    assert is_network_path(Path('//NAS/Games/RG Rotate'))


def test_missing_workspace_does_not_fallback_to_wrong_drive(tmp_path):
    with pytest.raises(FileNotFoundError):
        check_space(tmp_path / 'unplugged' / 'Card')


def make_apk(path: Path):
    with zipfile.ZipFile(path, 'w') as z:
        z.writestr('AndroidManifest.xml', b'ANDROID')
        z.writestr('classes.dex', b'dex1234')


def test_local_cocoon_installer_is_recognized_but_not_publisher_verified(tmp_path, monkeypatch):
    from apk_import import stage_local_apks
    source = tmp_path / 'Cocoon-3.11.apk'
    make_apk(source)
    card = tmp_path / 'Card'; prepare_layout(card)
    imported = stage_local_apks([source], card)
    assert imported['added'] == 1
    assert manual_apk_for(card, 'Cocoon Shell').name == source.name
    monkeypatch.setattr(tool_setup, 'tool_status',lambda root:{
        'Android Platform Tools':{'installed':False}, 'CHDman':{'installed':False}})
    status = readiness(card, tmp_path/'WindowsTools')
    assert 'publisher unverified' in status['Cocoon Shell']
    monkeypatch.setattr('software.download_apk', lambda *a, **k: pytest.fail('Should use imported Cocoon'))
    report = prepare_batch(['Cocoon Shell'], card, tmp_path/'WindowsTools')
    assert report['results'][0]['ok']
    assert 'publisher unverified' in report['results'][0]['state']


def test_modified_imported_apk_is_not_trusted(tmp_path):
    from apk_import import stage_local_apks
    source=tmp_path/'Cocoon.apk'; make_apk(source)
    card=tmp_path/'Card';prepare_layout(card)
    stage_local_apks([source], card)
    with (card/'SetupPackages'/'Cocoon.apk').open('ab') as f: f.write(b'altered')
    assert manual_apk_for(card,'Cocoon Shell') is None


def test_chdman_requires_operational_status_not_just_exe(tmp_path, monkeypatch):
    root=tmp_path/'Tools'; folder=root/'chdman';folder.mkdir(parents=True)
    exe=folder/'chdman.exe'; exe.write_bytes(b'not executable')
    assert tool_setup.tool_status(root)['CHDman']['installed'] is False
    monkeypatch.setattr(tool_setup,'verify_tool',lambda x: (True,'mock usage'))
    tool_setup._check_and_mark_chd(exe)
    assert tool_setup.tool_status(root)['CHDman']['installed'] is True
    exe.write_bytes(b'changed')
    assert tool_setup.tool_status(root)['CHDman']['installed'] is False


def test_chd_usage_check_validates_output(tmp_path):
    binary=tmp_path/'chdman.exe';binary.write_bytes(b'x')
    def fake_run(args, **kwargs):
        return subprocess.CompletedProcess(args,1,stdout='',stderr='Usage: chdman <command>')
    assert verify_tool(binary, fake_run)[0]
    def wrong(args,**kwargs): return subprocess.CompletedProcess(args,0,stdout='unrelated',stderr='')
    assert not verify_tool(binary,wrong)[0]


def test_chd_conversion_refuses_overwrite_or_missing_input(tmp_path):
    cue=tmp_path/'game.cue'; cue.write_text('FILE "game.bin" BINARY')
    chd=tmp_path/'chdman.exe';chd.write_bytes(b'placeholder')
    out=tmp_path/'Output';out.mkdir()
    (out/'game.chd').write_bytes(b'original')
    with pytest.raises(FileExistsError):convert_cue(cue,out,chd)
    assert (out/'game.chd').read_bytes()==b'original'
    with pytest.raises(ValueError):convert_cue(tmp_path/'absent.cue',out,chd)


def test_chd_conversion_cancelled_before_start_no_output(tmp_path):
    cue=tmp_path/'game.cue';cue.write_text('data')
    chd=tmp_path/'chdman.exe';chd.write_bytes(b'placeholder')
    event=Event();event.set()
    r=convert_cue(cue,tmp_path,chd,cancel=event)
    assert r['cancelled'] and not (tmp_path/'game.chd').exists()


def test_cover_png_import_is_non_destructive(tmp_path):
    card=tmp_path/'Card';prepare_layout(card)
    image=tmp_path/'cover.png';image.write_bytes(b'\x89PNG\r\n\x1a\n' + b'just test')
    dest=add_local_cover(image,card,'PS1','Game (USA)')
    assert dest.is_file() and dest.read_bytes() == image.read_bytes()
    with pytest.raises(FileExistsError):add_local_cover(image,card,'PS1','Game (USA)')
    with pytest.raises(ValueError):add_local_cover(image,card,'BadConsole','Game')


def test_art_source_exact_match_404_is_safe(tmp_path,monkeypatch):
    import artwork
    import urllib.error
    def error(*a,**k): raise urllib.error.HTTPError('x',404,'not found',None,None)
    monkeypatch.setattr(artwork.urllib.request,'urlopen',error)
    result=download_boxart(tmp_path,'PS1','NotInLibretro')
    assert result['status']=='not found'
    assert not (tmp_path/'Media').exists()


def test_v12_gui_wires_all_core_features_and_has_no_hidden_scan():
    source=(Path(__file__).resolve().parents[1]/'app.py').read_text(encoding='utf-8')
    assert 'has_workspace_payload_fast(self.workspace)' in source
    assert 'self.space_pool.start(work)' in source
    assert 'storage_checked' in source
    assert 'Choose a PS1 CUE and convert' in source
    assert 'Find missing covers' in source
    assert 'mapped Synology NAS drive' in source
    assert 'self.prepare_essentials([name for name, cb in self.software_checks.items() if cb.isChecked()])' in source


def test_interrupted_workspace_file_prevents_silent_abandonment(tmp_path):
    card=tmp_path/'card'; prepare_layout(card)
    (card/'ROMs'/'psp'/'half.iso.retro-part').write_bytes(b'partial')
    assert has_workspace_payload_fast(card)
    assert has_interrupted_files(card)


def test_workspace_change_scan_rejects_unfinished_copy(tmp_path):
    card=tmp_path/'card';prepare_layout(card)
    (card/'ROMs'/'psp'/'game.iso.retro-part').write_bytes(b'partial')
    with pytest.raises(ValueError,match='Unfinished'):
        count_workspace_files(card)


def test_test_chdman_button_marks_executable_as_checked(tmp_path,monkeypatch):
    root=tmp_path/'Tools'; chd=root/'chdman';chd.mkdir(parents=True)
    (chd/'chdman.exe').write_bytes(b'binary for test')
    monkeypatch.setattr(tool_setup,'verify_tool',lambda binary:(True,'mocked'))
    good,detail=tool_setup.validate_installed_chdman(root)
    assert good and 'ready status' in detail
    assert tool_setup.tool_status(root)['CHDman']['installed']


def test_chd_success_verifies_before_renaming_and_preserves_source(tmp_path):
    cue=tmp_path/'puzzle.cue'; cue.write_text('FILE "puzzle.bin" BINARY')
    bin_file=tmp_path/'puzzle.bin'; bin_file.write_bytes(b'original')
    exe=tmp_path/'chdman.exe'; exe.write_bytes(b'mock')
    class Completed:
        returncode=0
        def poll(self): return 0
    calls=[]
    def pretend_popen(args, stdout, stderr, text, shell):
        calls.append(args[1])
        if args[1]=='createcd':
            Path(args[-1]).write_bytes(b'MOCK CHD CONTENT')
        assert shell is False
        return Completed()
    result=convert_cue(cue,tmp_path,exe,runner=pretend_popen)
    assert result['verified'] and (tmp_path/'puzzle.chd').read_bytes()==b'MOCK CHD CONTENT'
    assert bin_file.read_bytes()==b'original' and cue.exists()
    assert calls==['createcd','verify']


def test_art_entry_dedup_skips_ps1_bin_data_tracks():
    from artwork import unique_game_art_entries
    from core import Entry
    entries=[Entry(Path('Game.bin'),'Game','PS1',5,'.bin'),
             Entry(Path('Game.cue'),'Game','PS1',3,'.cue'),
             Entry(Path('Other.iso'),'Other','PSP',5,'.iso')]
    got=unique_game_art_entries(entries)
    assert [(x.label,x.extension) for x in got]==[('Game','.cue'),('Other','.iso')]


def test_storage_display_explicitly_identifies_decimal_and_binary_units():
    assert describe_bytes(1024**3)=='1.00 GiB (1.07 GB)'
