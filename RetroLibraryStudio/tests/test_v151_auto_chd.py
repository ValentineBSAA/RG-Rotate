"""User acceptance cases for the Clock Tower import and automatic CHD pipeline."""
from __future__ import annotations
import json
from pathlib import Path
from threading import Event

from core import inventory
from disc_sets import inspect_cue
from ps1_pipeline import guided_import, disc_identity, stage_ps1_cues


def make_disc(folder, title='Clock Tower - The First Fear', tracks=2):
    folder.mkdir(parents=True, exist_ok=True)
    cue = folder / (title + '.cue')
    parts=[]
    for n in range(1, tracks+1):
        f = folder / f'{title} (Track {n}).bin'
        f.write_bytes(bytes([n])* (n * 2352 * 2))
        parts.append(f)
    cue.write_text(''.join(f'FILE "{p.name}" BINARY\n TRACK {i} '+
                            ('MODE2/2352' if i == 1 else 'AUDIO') + '\n INDEX 01 00:00:00\n'
                            for i, p in enumerate(parts, 1)), encoding='utf-8')
    return cue, parts


def fake_converter(cue, output, binary, **kwargs):
    out = Path(output) / (Path(cue).stem + '.chd')
    out.write_bytes(b'CHD SIMULATION / VERIFIED BY TEST DOUBLE / ' + Path(cue).name.encode())
    if kwargs.get('progress'):
        kwargs['progress']('Converting PS1 disc to CHD', 0, 0)
        kwargs['progress']('Verifying converted CHD', 0, 0)
    return {'output': str(out), 'verified': True, 'cancelled': False}


def tool(tmp_path):
    tool = tmp_path/'chdman.exe'; tool.write_bytes(b'test double')
    return tool


def test_clock_tower_tracks_convert_one_chd_originals_preserved(tmp_path):
    cue, bins = make_disc(tmp_path/'originals')
    card = tmp_path/'virtual'
    shown=[]
    result = guided_import([cue, *bins], card, 'PS1', tool(tmp_path),
                           auto_artwork=False, converter=fake_converter,
                           progress=lambda msg,c,t: shown.append((msg,c,t)))
    assert result['converted'] == 1 and not result['errors']
    assert result['playlists'] == 0
    assert (card/'ROMs'/'psx'/(cue.stem+'.chd')).is_file()
    assert not list((card/'ROMs'/'psx').glob('*.bin'))
    assert not list((card/'ROMs'/'psx').glob('*.cue'))
    assert cue.is_file() and all(p.is_file() for p in bins)
    assert any('Converting' in m for m,_,_ in shown)
    assert shown[-1][1:] == (100, 100)


def test_two_disc_conversion_makes_one_playlist_in_order(tmp_path):
    source = tmp_path/'downloads'
    cue2,_ = make_disc(source, 'Final Fantasy VII (USA) (Disc 2)',1)
    cue1,_ = make_disc(source, 'Final Fantasy VII (USA) (Disc 1)',1)
    card=tmp_path/'card'
    result=guided_import([cue2,cue1],card,'PS1',tool(tmp_path),auto_artwork=False,converter=fake_converter)
    folder=card/'ROMs'/'psx'/'Final Fantasy VII (USA)'
    m3u=folder/'Final Fantasy VII (USA).m3u'
    assert result['converted'] == 2 and result['playlists'] == 1
    assert m3u.read_text().splitlines() == ['Final Fantasy VII (USA) (Disc 1).chd',
                                            'Final Fantasy VII (USA) (Disc 2).chd']
    assert set(x.suffix for x in folder.iterdir()) == {'.chd','.m3u'}


def test_disc2_later_creates_playlist_instead_of_duplicate(tmp_path):
    source=tmp_path/'source'; card=tmp_path/'virtual'; binary=tool(tmp_path)
    disc1,_=make_disc(source,'Game (USA) (Disc 1)',1)
    disc2,_=make_disc(source,'Game (USA) (Disc 2)',1)
    one=guided_import([disc1],card,'PS1',binary,auto_artwork=False,converter=fake_converter,verify_existing=lambda *a,**k: None)
    two=guided_import([disc2],card,'PS1',binary,auto_artwork=False,converter=fake_converter,verify_existing=lambda *a,**k: None)
    assert one['playlists']==0 and two['playlists']==1
    assert (card/'ROMs'/'psx'/'Game (USA)'/'Game (USA).m3u').is_file()


def test_existing_clock_tower_can_be_optimized_without_moving_raw_sources(tmp_path):
    card=tmp_path/'card'; folder=card/'ROMs'/'psx'/'Clock Tower'
    cue,bins=make_disc(folder)
    binary=tool(tmp_path)
    result=guided_import([cue],card,'PS1',binary,auto_artwork=False,
                         converter=fake_converter,optimize_existing=True)
    assert result['converted'] == 1
    assert (folder/(cue.stem+'.chd')).is_file()
    assert cue.is_file() and all(p.is_file() for p in bins)


def test_bad_cue_does_not_stage_incomplete_chd(tmp_path):
    cue,tracks=make_disc(tmp_path/'src')
    tracks[1].unlink()
    result=guided_import([cue],tmp_path/'card','PS1',tool(tmp_path),auto_artwork=False,converter=fake_converter)
    assert result['converted']==0 and result['errors']
    assert not (tmp_path/'card'/'ROMs'/'psx').exists()


def test_no_chdman_does_not_import_raw_ps1_tracks(tmp_path):
    cue,tracks=make_disc(tmp_path/'src')
    result=guided_import([cue,*tracks],tmp_path/'card','PS1',tmp_path/'notinstalled',auto_artwork=False,
                         converter=fake_converter)
    assert result['converted']==0 and 'CHDman' in result['errors'][0]
    assert not (tmp_path/'card'/'ROMs'/'psx').exists()


def test_cue_display_shows_total_disc_size_not_228_bytes(tmp_path):
    card=tmp_path/'card'; cue,bins=make_disc(card/'ROMs'/'psx'/'Clock Tower')
    entries,used,n=inventory(card)
    entry=next(e for e in entries if e.extension == '.cue')
    assert entry.size == cue.stat().st_size+sum(p.stat().st_size for p in bins)
    assert used==sum(p.stat().st_size for p in [cue,*bins])


def test_bad_existing_chd_cannot_be_implicitly_trusted(tmp_path):
    cue,tracks=make_disc(tmp_path/'source')
    card=tmp_path/'card'; dest=card/'ROMs'/'psx'/(cue.stem+'.chd')
    dest.parent.mkdir(parents=True); dest.write_bytes(b'bad')
    def fail(*args, **kwargs): raise ValueError('Existing CHD failed verification')
    result=stage_ps1_cues([cue],card,tool(tmp_path),converter=fake_converter,verify_existing=fail)
    assert result['errors'] and not result['converted']
    assert dest.read_bytes()==b'bad'


def test_cancelled_pipeline_never_publishes_chd(tmp_path):
    cue,tracks=make_disc(tmp_path/'src')
    cancel=Event(); cancel.set()
    result=guided_import([cue],tmp_path/'card','PS1',tool(tmp_path),auto_artwork=False,
                         converter=fake_converter,cancel=cancel)
    assert result['cancelled']
    assert not list(tmp_path.glob('**/*.chd'))


def test_disc_titles_keep_different_editions_separate():
    assert disc_identity('Resident Evil 2 - Dual Shock Ver. (USA) (Disc 2) (Claire)') == ('Resident Evil 2 - Dual Shock Ver. (USA)',2)
    assert disc_identity('Final Fantasy VIII (USA) (Disc 3)') == ('Final Fantasy VIII (USA)',3)
    assert disc_identity('Resident Evil Gore Edition') == ('Resident Evil Gore Edition', None)


def test_english_patch_artwork_alias_does_not_remove_real_editions():
    from artwork_gallery import clean_title, find_art_matches
    assert clean_title('Clock Tower - The First Fear (English Patched) (Japan)') == 'Clock Tower - The First Fear'
    assert find_art_matches('Clock Tower - The First Fear (English Patched)',
                            ['Clock Tower - The First Fear (Japan)'])['automatic']
    assert find_art_matches('Resident Evil Gore Edition', ['Resident Evil (USA)'])['automatic'] is None


def test_artwork_fallback_when_catalog_down_but_exact_png_available(tmp_path):
    from artwork_gallery import direct_cover_fallback
    from urllib.error import HTTPError
    attempts=[]
    def fake(workspace, system, stem, title):
        attempts.append(title)
        if title.endswith('(Japan)'):
            return {'status':'downloaded','source_title':title}
        raise HTTPError('https://thumbnails.libretro.com/', 404, 'not found', {}, None)
    report=direct_cover_fallback(tmp_path,'PS1','Clock Tower - The First Fear',downloader=fake)
    assert report['status']=='downloaded' and len(attempts)==3


def test_zip_extracts_then_converts_complete_disc_automatically(tmp_path):
    import zipfile
    cue, bins=make_disc(tmp_path/'original')
    archive=tmp_path/'Clock Tower.zip'
    with zipfile.ZipFile(archive,'w') as z:
        for f in [cue,*bins]: z.write(f, f.name)
    result=guided_import([archive],tmp_path/'virtual','PS1',tool(tmp_path),
                         auto_artwork=False,converter=fake_converter)
    assert result['converted']==1 and not result['errors']
    assert (tmp_path/'virtual'/'ROMs'/'psx'/(cue.stem+'.chd')).is_file()
    assert archive.exists() and cue.exists()


def test_existing_chd_m3u_import_stays_playable(tmp_path):
    source=tmp_path/'source'; source.mkdir()
    for i in (1,2):
        (source/f'Game (Disc {i}).chd').write_bytes(b'CHD'+bytes([i]))
    playlist=source/'Game.m3u'; playlist.write_text('Game (Disc 1).chd\nGame (Disc 2).chd\n')
    virtual=tmp_path/'virtual'
    result=guided_import([playlist],virtual,'PS1',tool(tmp_path),auto_artwork=False)
    assert not result['errors']
    assert (virtual/'ROMs'/'psx'/'Game'/'Game.m3u').is_file()
    assert len(list((virtual/'ROMs'/'psx'/'Game').glob('*.chd')))==2


def test_cp1252_cue_companions_detected_for_auto_conversion(tmp_path):
    source=tmp_path/'source'; source.mkdir()
    cue=source/'Café Adventure.cue'; track=source/'Café.bin'; track.write_bytes(b'PS1' * 2352)
    cue.write_bytes('FILE "Café.bin" BINARY\n TRACK 01 MODE2/2352\n INDEX 01 00:00:00'.encode('cp1252'))
    result=guided_import([cue],tmp_path/'card','PS1',tool(tmp_path),
                         auto_artwork=False,converter=fake_converter)
    assert result['converted']==1 and not result['errors']


def test_multidisc_progress_non_decreasing(tmp_path):
    src=tmp_path/'src'; b=tool(tmp_path)
    sources=[make_disc(src,f'Game (Disc {i})',1)[0] for i in (1,2,3)]
    emitted=[]
    guided_import(sources,tmp_path/'virtual','PS1',b,auto_artwork=False,
                  converter=fake_converter,progress=lambda m,c,t: emitted.append((m,c,t)))
    numbers=[c for m,c,t in emitted if t==100]
    assert numbers==sorted(numbers) and numbers[-1]==100


def test_automatic_artwork_is_part_of_one_import_result(tmp_path, monkeypatch):
    import artwork_gallery
    done=[]
    def fake_art(workspace, games, progress=None, **kwargs):
        done.extend(games)
        if progress: progress('Covers complete', 1, 1)
        return {'stats': {'downloaded':1,'review':0,'error':0}, 'cancelled':False}
    monkeypatch.setattr(artwork_gallery, 'process_batch', fake_art)
    cue,_=make_disc(tmp_path/'original')
    ticks=[]
    result=guided_import([cue],tmp_path/'virtual','PS1',tool(tmp_path),
                         converter=fake_converter,auto_artwork=True,
                         progress=lambda msg,n,total: ticks.append((msg,n,total)))
    assert result['converted']==1 and result['artwork_attempted']
    assert result['artwork']['downloaded']==1
    assert done==[{'system':'PS1','label':cue.stem}]
    assert any('Covers' in msg for msg,n,total in ticks)


def test_m3u_display_size_includes_all_discs_without_double_counting_usage(tmp_path):
    from core import inventory
    workspace=tmp_path/'card'; folder=workspace/'ROMs'/'psx'/'Game'
    folder.mkdir(parents=True)
    (folder/'Game (Disc 1).chd').write_bytes(b'A'*100)
    (folder/'Game (Disc 2).chd').write_bytes(b'B'*150)
    playlist=folder/'Game.m3u'
    playlist.write_text('Game (Disc 1).chd\nGame (Disc 2).chd\n')
    items,used,total=inventory(workspace)
    display=next(e.size for e in items if e.extension=='.m3u')
    assert display==playlist.stat().st_size+250
    assert used==playlist.stat().st_size+250


def test_import_worker_dispatches_auto_convert_and_art_in_one_process(tmp_path, monkeypatch):
    import import_worker
    import ps1_pipeline
    observed=[]
    def fake(files, workspace, fallback, binary, **kwargs):
        observed.append((files, workspace, fallback, binary, kwargs['auto_artwork']))
        return {'copied':1,'converted':1,'artwork_attempted':True,'errors':[]}
    monkeypatch.setattr(ps1_pipeline,'guided_import',fake)
    source=tmp_path/'A.cue'; source.write_text('test')
    result=import_worker.handle({'mode':'files','paths':[str(source)],
         'workspace':str(tmp_path/'workspace'),'fallback':'PS1',
         'auto_ps1_chd':True,'auto_artwork':True,'binary':'C:/tools/chdman.exe'},Event())
    assert result['converted']==1 and observed[0][4]


def test_previous_disc_conversion_is_one_visible_worker_task(tmp_path, monkeypatch):
    import import_worker
    import ps1_pipeline
    card=tmp_path/'card'; cue,_=make_disc(card/'ROMs'/'psx'/'Clock Tower')
    observed=[]
    def fake(files, workspace, fallback, binary, **kwargs):
        observed.extend(files)
        assert kwargs['optimize_existing']
        return {'converted':1, 'errors':[]}
    monkeypatch.setattr(ps1_pipeline,'guided_import',fake)
    result=import_worker.handle({'mode':'optimize_existing_ps1','workspace':str(card),
                                 'binary':'C:/chdman.exe','auto_artwork':True},Event())
    assert result['converted']==1 and observed==[cue]
