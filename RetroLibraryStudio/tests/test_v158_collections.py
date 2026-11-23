"""Synthetic multi-disc regression tests. Not physical CHDman or RG Rotate evidence."""
from pathlib import Path
from threading import Event
import os
import pytest

from core import inventory
from library_presentation import group_games, format_badge_info
from ps1_collections import disc_identity, folder_title, publish_playlist
from ps1_pipeline import guided_import


def make_disc(source, name, tracks=1):
    source.mkdir(parents=True,exist_ok=True)
    cue=source/(name+'.cue')
    bins=[]
    for i in range(1,tracks+1):
        p=source/(name+(f' (Track {i})' if tracks>1 else '')+'.bin')
        p.write_bytes(bytes([i])*2352*3);bins.append(p)
    cue.write_text(''.join(f'FILE "{p.name}" BINARY\n TRACK {i:02d} MODE2/2352\n INDEX 01 00:00:00\n'
                           for i,p in enumerate(bins,1)))
    return cue,bins


def fake_converter(cue,out,binary,**kw):
    file=Path(out)/(Path(cue).stem+'.chd')
    file.write_bytes(b'MOCK CHD '+str(cue).encode())
    return {'output':str(file),'verified':True,'cancelled':False}


def tool(tmp_path):
    p=tmp_path/'chdman.exe';p.write_bytes(b'mock');return p


def groups(card):
    return group_games(inventory(card)[0])


def test_resident_evil_two_disc_one_tile_parent_and_preserved_sources(tmp_path):
    src=tmp_path/'src';card=tmp_path/'card'
    c2,b2=make_disc(src,'Resident Evil 2 (USA) (Disc 2)',2)
    c1,b1=make_disc(src,'Resident Evil 2 (USA) (Disc 1)')
    result=guided_import([c2,*b2,c1,*b1],card,'PS1',tool(tmp_path),
                         auto_artwork=False,converter=fake_converter)
    assert not result['errors']
    assert result['converted']==2 and result['playlists']==1
    folder=card/'ROMs'/'psx'/'Resident Evil 2 (USA)'
    playlist=folder/'Resident Evil 2 (USA).m3u'
    assert playlist.read_text().splitlines()==[
        'Resident Evil 2 (USA) (Disc 1).chd','Resident Evil 2 (USA) (Disc 2).chd']
    assert len(list(folder.glob('*.chd')))==2
    assert not list(folder.glob('*.bin')) and not list(folder.glob('*.cue'))
    visible=groups(card)
    assert len(visible)==1 and len(visible[0])==3
    assert visible[0][0].extension=='.m3u'
    assert format_badge_info(visible[0][0],visible[0])['badge']=='2 DISCS'
    assert all(p.is_file() for p in [c1,*b1,c2,*b2])


def test_ff7_three_and_ff8_four_are_distinct_game_collections(tmp_path):
    src=tmp_path/'src';card=tmp_path/'card'
    cues=[make_disc(src,f'Final Fantasy {roman} (USA) (Disc {i})')[0]
          for roman,n in [('VII',3),('VIII',4)] for i in range(1,n+1)]
    result=guided_import(cues[::-1],card,'PS1',tool(tmp_path),
                         auto_artwork=False,converter=fake_converter)
    assert not result['errors'] and result['converted']==7 and result['playlists']==2
    assert sorted(len(group)-1 for group in groups(card))==[3,4]
    for roman,n in [('VII',3),('VIII',4)]:
        folder=card/'ROMs'/'psx'/f'Final Fantasy {roman} (USA)'
        assert len(list(folder.glob('*.chd')))==n


def test_import_disc_3_later_extends_playlist_and_preserves_same_gallery_tile(tmp_path):
    src=tmp_path/'src';card=tmp_path/'card';binary=tool(tmp_path)
    cues=[make_disc(src,f'Final Fantasy VII (USA) (Disc {n})')[0] for n in (1,2,3)]
    kw={'auto_artwork':False,'converter':fake_converter,
        'verify_existing':lambda *a,**k:None}
    first=guided_import([cues[0]],card,'PS1',binary,**kw)
    assert first['artwork_games']==[{'system':'PS1','label':'Final Fantasy VII (USA)'}]
    second=guided_import([cues[1]],card,'PS1',binary,**kw)
    assert second['playlists']==1 and len(groups(card))==1
    third=guided_import([cues[2]],card,'PS1',binary,**kw)
    assert third['playlists_updated']==1 and not third['errors']
    assert len(groups(card))==1 and len(groups(card)[0])==4
    assert guided_import([cues[2]],card,'PS1',binary,**kw)['playlists_updated']==0


def test_missing_reference_never_publishes_and_broken_m3u_never_hides_discs(tmp_path):
    src=tmp_path/'src';card=tmp_path/'card'
    cue,tracks=make_disc(src,'Game (Disc 1)',2)
    tracks[0].rename(src/'wrong-name.bin')
    result=guided_import([cue,*tracks[1:]],card,'PS1',tool(tmp_path),
                         auto_artwork=False,converter=fake_converter)
    assert result['errors'] and result['converted']==0
    assert not list(card.glob('**/*.chd'))
    assert cue.is_file()
    folder=card/'ROMs'/'psx'/'Other (USA)';folder.mkdir(parents=True)
    a=folder/'Other (USA) (Disc 1).chd';b=folder/'Other (USA) (Disc 2).chd'
    a.write_bytes(b'one');b.write_bytes(b'two')
    m=folder/'Other (USA).m3u';m.write_text(a.name+'\nmissing.chd\n')
    assert len(groups(card))==3
    m.write_text(a.name+'\n'+b.name+'\n')
    assert len(groups(card))==1


def test_conflicting_playlist_refused_incremental_subset_updated(tmp_path):
    chds=[tmp_path/f'Game (Disc {n}).chd' for n in (1,2,3)]
    for p in chds:p.write_bytes(b'fixture')
    m=tmp_path/'Game.m3u'
    m.write_text(chds[1].name+'\n'+chds[0].name+'\n')
    original=m.read_bytes()
    with pytest.raises(FileExistsError):publish_playlist(chds,m)
    assert m.read_bytes()==original
    m.write_text(chds[0].name+'\n'+chds[1].name+'\n')
    assert publish_playlist(chds,m)=='updated'
    assert publish_playlist(chds,m)=='unchanged'
    assert m.read_text().splitlines()==[p.name for p in chds]


def test_disc_gap_and_distinct_editions(tmp_path):
    src=tmp_path/'src';card=tmp_path/'card'
    cues=[make_disc(src,f'Game (Disc {n})')[0] for n in (1,3)]
    result=guided_import(cues,card,'PS1',tool(tmp_path),
                         auto_artwork=False,converter=fake_converter)
    assert result['converted']==2 and result['errors']
    assert not list(card.glob('**/*.m3u'))
    assert disc_identity('Resident Evil 2 - Dual Shock Ver. (USA) (Disc 2) (Claire)')==(
        'Resident Evil 2 - Dual Shock Ver. (USA)',2)
    assert disc_identity('Resident Evil 2 (USA) (Disc 1)')[0] != (
        disc_identity('Resident Evil 2 - Dual Shock Ver. (USA) (Disc 2) (Claire)')[0])
    assert disc_identity('Game (Track 2)')==('Game (Track 2)',None)
    for name in ('CON','A:B','trailing.','../escape'):
        with pytest.raises(ValueError):folder_title(name)


def test_direct_chds_are_verified_not_recompressed(tmp_path):
    src=tmp_path/'src';src.mkdir();card=tmp_path/'card'
    discs=[]
    for n in (1,2,3,4):
        p=src/f'Final Fantasy VIII (USA) (Disc {n}).chd'
        p.write_bytes(b'PRECOMPRESSED'+bytes([n]))
        discs.append(p)
    verified=[]
    result=guided_import(discs,card,'PS1',tool(tmp_path),auto_artwork=False,
        converter=lambda *a,**k:pytest.fail('must not recompress existing CHDs'),
        verify_existing=lambda p,*a,**k: verified.append(Path(p)))
    assert result['converted']==0 and result['playlists']==1 and not result['errors']
    assert len(verified)>=8 and len(groups(card))==1
    assert all(p.exists() for p in discs)


@pytest.mark.parametrize('scale',[100,125,150])
def test_qt_renders_one_cover_tile_and_disc_badge(tmp_path,monkeypatch,scale):
    pytest.importorskip('PySide6')
    os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
    from PySide6.QtWidgets import QApplication,QPushButton
    from PySide6.QtCore import QSettings,Qt
    import app
    qt=QApplication.instance() or QApplication([])
    root=tmp_path/'card';folder=root/'ROMs'/'psx'/'Game (USA)'
    folder.mkdir(parents=True)
    a=folder/'Game (USA) (Disc 1).chd';b=folder/'Game (USA) (Disc 2).chd'
    a.write_bytes(b'A'*300);b.write_bytes(b'B'*300)
    (folder/'Game (USA).m3u').write_text(a.name+'\n'+b.name+'\n')
    settings=QSettings(str(tmp_path/'settings.ini'),QSettings.Format.IniFormat)
    settings.setValue('workspace',str(root))
    monkeypatch.setattr(app,'QSettings',lambda *a:settings)
    for method in ('offer_first_location','refresh','update_tools_status','update_workspace_location'):
        monkeypatch.setattr(app.Window,method,lambda *a,**kw:None)
    window=app.Window();window.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen,True)
    try:
        window.scale_percent=scale;window.apply_scale();window.show()
        window.card_entries=inventory(root)[0]
        window.navigate(1,refresh_apps=False);window.fill_card();qt.processEvents()
        live=[window.gallery_grid.itemAt(i).widget() for i in range(window.gallery_grid.count())]
        tiles=[w for w in live if w.objectName()=='GameTile']
        assert len(tiles)==1
        assert '2 DISCS' in [b.text() for b in tiles[0].findChildren(QPushButton)]
        assert '1 games shown' in window.library_count.text()
    finally:
        window.close();qt.processEvents()
