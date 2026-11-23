import io
import json
import threading
import zipfile
from pathlib import Path
from unittest.mock import patch

import pytest
from core import CAPACITY, COMPANION_BUDGET, FREE_RESERVE, GAME_BUDGET, prepare_layout, import_files
from sync_engine import make_plan, transfer_verified
import software
import android_setup


def fixtures(tmp_path):
    src=tmp_path/'virtual';target=tmp_path/'target'
    prepare_layout(src);target.mkdir()
    (src/'ROMs'/'psx'/'a.chd').write_bytes(b'A'*70)
    (src/'ROMs'/'psp'/'b.cso').write_bytes(b'B'*65)
    return src,target


def test_budget_math():
    assert GAME_BUDGET==CAPACITY-COMPANION_BUDGET-FREE_RESERVE
    assert FREE_RESERVE==8*1024**3


def test_plan_and_simulated_sync(tmp_path):
    src,target=fixtures(tmp_path)
    plan=make_plan(src,target,simulation=True)
    assert plan.files==2 and plan.bytes_total==135 and plan.bytes_new==135
    updates=[]
    result=transfer_verified(src,target,simulation=True,progress=lambda *args:updates.append(args))
    assert result['copied']==2 and result['verified']==2 and not result['errors']
    assert len(updates)>=2 and updates[-1][2]==135
    result=transfer_verified(src,target,simulation=True)
    assert result['skipped']==2 and result['verified']==2


def test_different_existing_file_never_overwritten(tmp_path):
    src,target=fixtures(tmp_path)
    existing=target/'ROMs'/'psx'/'a.chd';existing.parent.mkdir(parents=True)
    existing.write_bytes(b'NOT SAME CONTENT EVEN IF SAME LENGTH')
    res=transfer_verified(src,target,simulation=True)
    assert res['errors'] and existing.read_bytes()==b'NOT SAME CONTENT EVEN IF SAME LENGTH'


def test_resume_success(tmp_path):
    src,target=fixtures(tmp_path)
    partial=target/'ROMs'/'psx'/'a.chd.retro-part';partial.parent.mkdir(parents=True)
    partial.write_bytes(b'A'*17)
    res=transfer_verified(src,target,simulation=True)
    assert res['verified']==2 and res['copied']==2 and not res['errors']
    assert not partial.exists()
    assert (target/'ROMs'/'psx'/'a.chd').read_bytes()==b'A'*70


def test_corrupt_resume_rejected(tmp_path):
    src,target=fixtures(tmp_path)
    partial=target/'ROMs'/'psx'/'a.chd.retro-part';partial.parent.mkdir(parents=True)
    partial.write_bytes(b'wrong bytes')
    res=transfer_verified(src,target,simulation=True)
    assert res['errors'] and partial.read_bytes()==b'wrong bytes'
    assert not (target/'ROMs'/'psx'/'a.chd').exists()


def test_cancel_retains_partial_and_can_resume(tmp_path):
    src,target=fixtures(tmp_path)
    cancel=threading.Event();cancel.set()
    res=transfer_verified(src,target,simulation=True,cancel=cancel)
    assert res['cancelled'] and res['copied']==0
    assert transfer_verified(src,target,simulation=True)['verified']==2


def test_space_reserve_blocks_transfer(tmp_path):
    src,target=fixtures(tmp_path)
    result=transfer_verified(src,target,simulation=False,reserve_bytes=10**18)
    assert result['errors'] and result['copied']==0


def test_companion_budget_enforced(tmp_path):
    src,target=fixtures(tmp_path)
    (src/'CompanionData'/'Memory'/'memory.bin').write_bytes(b'123456')
    plan=make_plan(src,target,companion_budget=4,simulation=True)
    assert 'CompanionData exceeds' in ';'.join(plan.conflicts)


def test_official_github_asset_validation(monkeypatch):
    class Result:
        def __enter__(self):return self
        def __exit__(self,*a):pass
        def read(self,*a):return json.dumps({'assets':[{'name':'Cocoon.apk','browser_download_url':'https://github.com/KansoMirai/CocoonFE/releases/download/test/Cocoon.apk'}]}).encode()
    monkeypatch.setattr(software,'_urlopen',lambda *args,**kwargs:Result())
    url,name=software.resolve('Cocoon Shell')
    assert url.startswith('https://github.com/KansoMirai/') and name=='Cocoon.apk'


def test_untrusted_github_asset_rejected(monkeypatch):
    class Result:
        def __enter__(self):return self
        def __exit__(self,*a):pass
        def read(self,*a):return json.dumps({'assets':[{'name':'Cocoon.apk','browser_download_url':'https://example.org/evil.apk'}]}).encode()
    monkeypatch.setattr(software,'_urlopen',lambda *args,**kwargs:Result())
    with pytest.raises(RuntimeError,match='Unexpected'):
        software.resolve('Cocoon Shell')


def test_adb_requires_installed_tool(monkeypatch):
    monkeypatch.setattr(android_setup,'adb_binary',lambda:None)
    with pytest.raises(FileNotFoundError):android_setup.connected_devices()


def test_invalid_install_filename_rejected(monkeypatch,tmp_path):
    monkeypatch.setattr(android_setup,'adb_binary',lambda:'adb')
    monkeypatch.setattr(android_setup,'connected_devices',lambda:[('X','device')])
    with pytest.raises(ValueError,match='basenames'):
        android_setup.install_local_apks(tmp_path,'X',['../evil.apk'])

def test_library_health_detects_broken_cue_and_duplicates(tmp_path):
    from health import inspect_library
    stage=tmp_path/'virtual';prepare_layout(stage)
    one=stage/'ROMs'/'psx'/'first.bin';one.write_bytes(b'track'*30)
    second=stage/'ROMs'/'psx'/'second.bin';second.write_bytes(b'track'*30)
    (stage/'ROMs'/'psx'/'missing.cue').write_text('FILE "absent.bin" BINARY')
    result=inspect_library(stage)
    assert result['broken_playlists_or_cues']
    assert any('first.bin' in str(g) and 'second.bin' in str(g) for g in result['possible_duplicates'])
