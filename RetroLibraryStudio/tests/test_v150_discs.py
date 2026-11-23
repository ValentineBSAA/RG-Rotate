import subprocess
from pathlib import Path
from threading import Event
import pytest

from disc_sets import inspect_cue, write_playlist, convert_discs
from chd_convert import convert_cue


def disc(tmp_path, name='Disc 1'):
    cue = tmp_path / (name + '.cue')
    track = tmp_path / (name + '.bin')
    track.write_bytes(b'CD DATA' * 1000)
    cue.write_text(f'FILE "{track.name}" BINARY\n TRACK 01 MODE2/2352\n INDEX 01 00:00:00\n', encoding='utf-8')
    return cue, track


def test_multifile_relative_paths_audio_and_shared_file_tracks(tmp_path):
    audio = tmp_path / 'Audio tracks'; audio.mkdir()
    (audio / 'Track 02.wav').write_bytes(b'RIFF' * 1000)
    cue, track = disc(tmp_path)
    with cue.open('a') as stream:
        stream.write(' TRACK 02 AUDIO\n INDEX 01 02:00:00\nFILE "Audio tracks\\Track 02.wav" WAVE\n TRACK 03 AUDIO\n INDEX 01 00:00:00\n')
    result = inspect_cue(cue)
    assert not result['errors']
    assert len(result['files']) == 2 and len(result['tracks']) == 3
    assert result['tracks'][2]['mode'] == 'AUDIO'
    assert result['files'][1]['bytes'] == 4000


def test_missing_track_names_expected_path_and_preserves_cue(tmp_path):
    cue, track = disc(tmp_path)
    original = cue.read_bytes(); track.rename(tmp_path / 'Wrong name.bin')
    result = inspect_cue(cue)
    assert str(track) in result['errors'][0] and 'missing track' in result['errors'][0]
    assert cue.read_bytes() == original


@pytest.mark.parametrize('payload', [b'', bytes(4000), bytes(200000)])
def test_suspicious_data_warns_without_rewriting_or_rejecting(tmp_path, payload):
    cue, track = disc(tmp_path); track.write_bytes(payload)
    result = inspect_cue(cue)
    assert result['warnings'] and not result['errors']
    assert track.read_bytes() == payload


def test_sample_warning_does_not_claim_entire_large_track_zero(tmp_path):
    cue, track = disc(tmp_path); track.write_bytes(bytes(300000))
    assert 'not a full scan' in inspect_cue(cue)['warnings'][0]


@pytest.mark.parametrize('text', ['FILE "bad.bin BINARY', 'TRACK 01 AUDIO', 'REM no files'])
def test_invalid_sheets_are_actionable(tmp_path, text):
    cue = tmp_path / 'Broken.cue'; cue.write_text(text)
    assert inspect_cue(cue)['errors']


def test_individual_bin_is_not_a_complete_disc(tmp_path):
    _, track = disc(tmp_path)
    assert 'individual BIN' in inspect_cue(track)['errors'][0]


def test_duplicate_track_numbers(tmp_path):
    cue, _ = disc(tmp_path)
    with cue.open('a') as stream: stream.write('TRACK 01 AUDIO\n')
    assert any('duplicate' in e for e in inspect_cue(cue)['errors'])


def test_inspection_cancel_stops_before_sampling(tmp_path):
    cue, _ = disc(tmp_path); stop = Event(); stop.set()
    with pytest.raises(InterruptedError): inspect_cue(cue, stop)


def test_cp1252_filename(tmp_path):
    track = tmp_path / 'Café.bin'; track.write_bytes(b'Audio' * 1000)
    cue = tmp_path / 'Game.cue'; cue.write_bytes('FILE "Café.bin" BINARY\nTRACK 01 AUDIO'.encode('cp1252'))
    result = inspect_cue(cue)
    assert not result['errors'] and 'legacy' in result['warnings'][0]


def test_m3u_order_unicode_and_no_overwrite(tmp_path):
    files = [tmp_path / 'Game Disc 2.chd', tmp_path / 'Game Disc 1.chd']
    for file in files: file.write_bytes(b'verified fixture')
    playlist = tmp_path / 'Game.m3u'
    write_playlist(files, playlist)
    assert playlist.read_text().splitlines() == [p.name for p in files]
    with pytest.raises(FileExistsError): write_playlist(files[::-1], playlist)
    assert playlist.read_text().splitlines()[0] == files[0].name


def test_playlist_cannot_reference_other_folder_or_missing_disc(tmp_path):
    with pytest.raises(ValueError): write_playlist([tmp_path / 'absent.chd'], tmp_path / 'Game.m3u')


@pytest.mark.parametrize('fail_stage', ['createcd', 'verify'])
def test_actual_chd_error_retained_and_unverified_output_not_published(tmp_path, fail_stage):
    cue, track = disc(tmp_path); binary = tmp_path / 'chdman.exe'; binary.write_bytes(b'mock')
    class Process:
        def __init__(self, code): self.returncode = code
        def poll(self): return self.returncode
    def runner(args, stdout, **kwargs):
        assert kwargs['shell'] is False
        if args[1] == 'createcd': Path(args[-1]).write_bytes(b'partial CHD')
        stdout.write('ERROR: track size mismatch in Disc 1'); stdout.flush()
        return Process(1 if args[1] == fail_stage else 0)
    with pytest.raises(RuntimeError, match='track size mismatch'):
        convert_cue(cue, tmp_path, binary, runner=runner)
    assert not (tmp_path / 'Disc 1.chd').exists()
    assert not list(tmp_path.glob('*.retro-converting.chd'))
    assert track.read_bytes() == b'CD DATA' * 1000


def test_missing_track_prevents_chd_launch(tmp_path):
    cue, track = disc(tmp_path); track.unlink()
    binary = tmp_path / 'chdman.exe'; binary.write_bytes(b'mock')
    with pytest.raises(ValueError, match='missing track'):
        convert_cue(cue, tmp_path, binary, runner=lambda *a, **k: pytest.fail('Must not launch'))


def test_one_failed_disc_does_not_hide_later_success(tmp_path, monkeypatch):
    import chd_convert
    def fake(source, *a, **k):
        if source.stem == 'Disc 1': raise RuntimeError('bad track')
        return {'verified': True, 'output': str(tmp_path / 'Disc 2.chd')}
    monkeypatch.setattr(chd_convert, 'convert_cue', fake)
    report = convert_discs(['Disc 1.cue', 'Disc 2.cue'], tmp_path, 'chdman.exe')
    assert len(report['results']) == 2
    assert report['results'][0]['error'] == 'bad track'
    assert report['results'][1]['verified']


def test_adb_version_probe_rejects_wrong_binary_and_uses_safe_args(tmp_path):
    from tool_setup import _verify_adb
    (tmp_path / 'adb.exe').write_bytes(b'version probe fixture')
    def good(args, **kwargs):
        assert args == [str(tmp_path / 'adb.exe'), 'version'] and kwargs['shell'] is False
        return subprocess.CompletedProcess(args, 0, 'Android Debug Bridge version 1.0.41', '')
    _verify_adb(tmp_path / 'adb.exe', runner=good)
    with pytest.raises(RuntimeError, match='executable check failed'):
        _verify_adb(tmp_path / 'adb.exe', runner=lambda *a, **k: subprocess.CompletedProcess([], 0, 'wrong program', ''))
