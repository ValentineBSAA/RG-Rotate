"""Batch PS1 Classics ZIP/7Z/PBP queue never mixes games or keys."""
from pathlib import Path
import threading
import pytest

from ps1_batch import batch_guided_import


def result(*,converted=0,playlists=0,skipped=0,errors=None):
    return {'converted':converted,'playlists':playlists,'skipped':skipped,
            'copied':converted,'playlists_updated':0,'errors':list(errors or []),
            'cancelled':False,'artwork_attempted':False,
            'artwork':{},'artwork_games':[],'duplicate_notes':[]}


def test_separate_archives_get_separate_jobs_and_a_failure_does_not_break_others(
        tmp_path,monkeypatch):
    import ps1_batch
    archives=[tmp_path/(name+'.7z') for name in ('Final Fantasy VII','Final Fantasy VIII','Final Fantasy IX')]
    for p in archives:p.write_bytes(b'NOT_REAL_ARCHIVE')
    seen=[]
    def fake_guided(files, workspace, fallback, binary, **kw):
        seen.append([f.name for f in files])
        kw['progress']('Extracting PS1 Classic • Disc 1 identified',0,0)
        if 'VIII' in files[0].name:
            raise ValueError('unreadable PSN package')
        return result(converted=3,playlists=1)
    monkeypatch.setattr(ps1_batch,'guided_import',fake_guided)
    messages=[]
    report=batch_guided_import(archives,tmp_path/'virtual','PS1',tmp_path/'chdman.exe',
                               progress=lambda m,n,total:messages.append(m))
    assert len(seen)==3 and all(len(x)==1 for x in seen)
    assert [row['status'] for row in report['batch_items']] == ['imported','needs attention','imported']
    assert report['converted']==6 and report['playlists']==2
    assert report['batch_completed']==2 and report['batch_needs_attention']==1
    assert report['errors'] and 'VIII' in report['errors'][0]
    assert any('Batch 3/3' in m for m in messages)


def test_multiple_pbp_packages_never_give_a_keys_file_its_own_job(tmp_path,monkeypatch):
    import ps1_batch
    seen=[]
    files=[]
    for name in ('GameOne','GameTwo'):
        path=tmp_path/name;path.mkdir()
        pbp=path/'EBOOT.PBP';pbp.write_bytes(b'FAKE')
        key=path/'KEYS.BIN';key.write_bytes(b'PRIVATE_KEY')
        files.extend([pbp,key])
    def fake_guided(selected,*a,**kw):
        seen.append(selected)
        return result(converted=2,playlists=1)
    monkeypatch.setattr(ps1_batch,'guided_import',fake_guided)
    report=batch_guided_import(files,tmp_path/'virtual','PS1',tmp_path/'chdman.exe')
    assert len(seen)==2 and all(p[0].name=='EBOOT.PBP' and len(p)==1 for p in seen)
    assert report['batch_total']==2 and report['converted']==4
    assert all(p.read_bytes()==b'PRIVATE_KEY' for p in tmp_path.glob('Game*/KEYS.BIN'))


def test_batch_stops_before_following_package_when_cancelled(tmp_path,monkeypatch):
    import ps1_batch
    cancel=threading.Event()
    calls=[]
    def fake_guided(selected,*a,**kw):
        calls.append(selected[0].name)
        cancel.set()
        return result(converted=3,playlists=1)
    monkeypatch.setattr(ps1_batch,'guided_import',fake_guided)
    items=[tmp_path/'a.zip',tmp_path/'b.zip']
    report=batch_guided_import(items,tmp_path/'virtual','PS1',tmp_path/'chdman.exe',
                               cancel=cancel)
    assert calls==['a.zip'] and report['cancelled'] is True
    assert report['batch_total']==2


def test_batch_psn_folder_worker_passes_only_packages(tmp_path,monkeypatch):
    import import_worker
    import ps1_batch
    root=tmp_path/'source';root.mkdir()
    for name in ('One.7z','Two.zip','EBOOT.PBP','KEYS.BIN','Loose.gba'):
        (root/name).write_bytes(b'FAKE')
    recorded=[]
    def fake_batch(files,*args,**kw):
        recorded.extend(p.name for p in files)
        return {'cancelled':False,'copied':0,'skipped':0,'errors':[]}
    monkeypatch.setattr(ps1_batch,'batch_guided_import',fake_batch)
    monkeypatch.setattr(import_worker,'emit',lambda *args,**kw:None)
    report=import_worker.handle({
        'mode':'batch_psn_folder','folder':str(root),
        'workspace':str(tmp_path/'virtual'),'fallback':'PS1',
        'auto_ps1_chd':True,'binary':str(tmp_path/'chdman.exe'),
    },threading.Event())
    assert sorted(recorded)==sorted(['One.7z','Two.zip','EBOOT.PBP'])
    assert report['errors']==[]
