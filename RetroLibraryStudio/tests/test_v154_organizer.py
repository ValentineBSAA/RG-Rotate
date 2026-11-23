"""Regression checks for the conversion action invoked by right-clicking a PS1 tile."""
from pathlib import Path
from threading import Event

from ps1_organizer import convert_selected_game, _raw_img_mode


def fixture(tmp_path, suffix='.cue'):
    card = tmp_path/'card'
    folder = card/'ROMs'/'psx'/'Clock Tower'
    folder.mkdir(parents=True)
    bin1 = folder/'Clock Tower (Track 1).bin'
    bin2 = folder/'Clock Tower (Track 2).bin'
    bin1.write_bytes(b'01' * 2048)
    bin2.write_bytes(b'02' * 2048)
    cue=folder/'Clock Tower.cue'
    cue.write_text('FILE "Clock Tower (Track 1).bin" BINARY\n TRACK 01 MODE2/2352\n INDEX 01 00:00:00\n'
                   'FILE "Clock Tower (Track 2).bin" BINARY\n TRACK 02 AUDIO\n INDEX 01 00:00:00\n')
    binary=tmp_path/'chdman.exe'; binary.write_bytes(b'fake executable')
    return card, cue, bin1, bin2, binary


def stub_converter(cue, directory, binary, **kwargs):
    dest=Path(directory)/(Path(cue).stem+'.chd')
    dest.write_bytes(b'verified CHD simulation')
    return {'verified':True,'cancelled':False,'output':str(dest)}


def stub_verify(chd, tool, **kw):
    if not Path(chd).read_bytes().startswith(b'verified CHD'):
        raise ValueError('verification failed')


def test_cue_to_chd_moves_old_tracks_outside_virtual_card_and_keeps_cover(tmp_path):
    card,cue,b1,b2,tool=fixture(tmp_path)
    cover=card/'Media'/'BoxArt'/'psx'/'Clock Tower.png'
    cover.parent.mkdir(parents=True)
    cover.write_bytes(b'cover')
    events=[]
    r=convert_selected_game(cue,card,tool,converter=stub_converter,verifier=stub_verify,
                            progress=lambda m,c,t:events.append((m,c,t)))
    assert not r['errors'] and r['converted']==1
    folder=cue.parent
    assert [p.suffix for p in folder.iterdir()] == ['.chd']
    backup=Path(r['backup'])
    assert backup.is_relative_to(card.parent) and not backup.is_relative_to(card)
    assert (backup/cue.name).is_file() and (backup/b1.name).is_file() and (backup/b2.name).is_file()
    assert cover.read_bytes()==b'cover'
    assert events[-1][1:] == (100,100)


def test_verification_failure_preserves_cue_and_bins(tmp_path):
    card,cue,b1,b2,tool=fixture(tmp_path)
    def fail(*args,**kwargs): raise ValueError('CHDman verify failed')
    r=convert_selected_game(cue,card,tool,converter=stub_converter,verifier=fail)
    assert r['errors'] and cue.exists() and b1.exists() and b2.exists()
    assert not list(card.parent.glob('*Conversion Backups*'))


def test_conversion_cancelled_preserves_sources(tmp_path):
    card,cue,b1,b2,tool=fixture(tmp_path)
    flag=Event();flag.set()
    r=convert_selected_game(cue,card,tool,cancel=flag,converter=stub_converter,verifier=stub_verify)
    assert r['cancelled'] and cue.is_file() and b1.is_file() and b2.is_file()


def test_existing_chd_is_reverified_before_tidying(tmp_path):
    card,cue,b1,b2,tool=fixture(tmp_path)
    (cue.parent/'Clock Tower.chd').write_bytes(b'verified CHD from earlier conversion')
    r=convert_selected_game(cue,card,tool,converter=stub_converter,verifier=stub_verify)
    assert r['skipped']==1 and r['converted']==0 and not r['errors']
    assert len(list(cue.parent.iterdir()))==1


def test_external_path_is_rejected(tmp_path):
    card,cue,b1,b2,tool=fixture(tmp_path)
    outside=tmp_path/'outside.cue';outside.write_text(cue.read_text())
    r=convert_selected_game(outside,card,tool,converter=stub_converter,verifier=stub_verify)
    assert r['errors'] and cue.exists()


def test_shared_bin_tracks_are_not_moved(tmp_path):
    card,cue,b1,b2,tool=fixture(tmp_path)
    (cue.parent/'Extra.cue').write_text('FILE "Clock Tower (Track 2).bin" BINARY\n TRACK 01 AUDIO\n INDEX 01 00:00:00')
    r=convert_selected_game(cue,card,tool,converter=stub_converter,verifier=stub_verify)
    assert r['errors'] and cue.exists() and b1.exists() and b2.exists()


def test_raw_img_single_track_mode2_supported_and_staged(tmp_path):
    card,cue,b1,b2,tool=fixture(tmp_path)
    cue.unlink();b1.unlink();b2.unlink()
    sector=b'\x00'+b'\xff'*10+b'\x00'+b'\x00\x00\x00'+b'\x02'+b'\x00'*(2352-16)
    img=cue.parent/'PS1 Test.img';img.write_bytes(sector*20)
    assert _raw_img_mode(img)=='MODE2/2352'
    r=convert_selected_game(img,card,tool,converter=stub_converter,verifier=stub_verify)
    assert not r['errors'] and (img.parent/'PS1 Test.chd').is_file() and not img.exists()
    assert not (img.parent/'PS1 Test.cue').exists()
    assert (Path(r['backup'])/img.name).is_file()


def test_ambiguous_raw_img_refused(tmp_path):
    card,cue,b1,b2,tool=fixture(tmp_path)
    cue.unlink(); b1.unlink();b2.unlink()
    img=cue.parent/'Unidentified.img';img.write_bytes(b'\x11'*2352*4)
    r=convert_selected_game(img,card,tool,converter=stub_converter,verifier=stub_verify)
    assert r['errors'] and img.is_file() and not list(cue.parent.glob('*.chd'))


def test_clonecd_sidecars_are_blocked(tmp_path):
    card,cue,b1,b2,tool=fixture(tmp_path)
    cue.unlink();b1.unlink();b2.unlink()
    img=cue.parent/'Clone.img';img.write_bytes(b'\x00'*2352*10)
    img.with_suffix('.ccd').write_text('CloneCD descriptor')
    r=convert_selected_game(img,card,tool,converter=stub_converter,verifier=stub_verify)
    assert r['errors'] and img.exists() and img.with_suffix('.ccd').exists()


def test_single_chd_no_m3u(tmp_path):
    card,cue,b1,b2,tool=fixture(tmp_path)
    r=convert_selected_game(cue,card,tool,converter=stub_converter,verifier=stub_verify)
    assert not r['errors'] and not list(cue.parent.glob('*.m3u'))
