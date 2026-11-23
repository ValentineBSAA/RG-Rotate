"""PSXtract tool setup tests: trusted asset hash and safe ZIP structure only.

Never executes a downloaded binary or accesses user keys.
"""
from __future__ import annotations

import json
import stat
import zipfile
from pathlib import Path

import pytest

from tool_setup import (_extract_psxtract_zip, PSXTRACT_SHA256, PSXTRACT_ZIP,
                        tool_status, install_psxtract)


def archive(tmp_path, entries):
    source = tmp_path/'fixture.zip'
    with zipfile.ZipFile(source,'w') as z:
        for name, data in entries.items():
            z.writestr(name, data)
    return source


def test_pinned_upstream_release_and_helper_location():
    assert PSXTRACT_ZIP.startswith(
        'https://github.com/has207/psxtract-2/releases/download/v3.0/')
    assert len(PSXTRACT_SHA256)==64
    assert tool_status(Path('/not-a-real-setup-root'))['PSXtract']['installed'] is False


def test_safe_extractor_keeps_exe_dll_and_cue_metadata(tmp_path):
    sample=archive(tmp_path, {
        'PSXtract-v3/psxtract.exe':b'MOCK_EXE',
        'PSXtract-v3/atrac3.dll':b'MOCK_DLL',
        'PSXtract-v3/cue/FFVII.cue':b'SAMPLE',
    })
    unpack=tmp_path/'unpack';unpack.mkdir()
    exe=_extract_psxtract_zip(sample,unpack)
    assert exe.name=='psxtract.exe'
    assert (exe.parent/'atrac3.dll').read_bytes()==b'MOCK_DLL'
    assert (exe.parent/'cue'/'FFVII.cue').read_bytes()==b'SAMPLE'


@pytest.mark.parametrize('name',['../outside.exe','C:/evil.txt','CON','folder/file:ads'])
def test_rejects_unsafe_archive_paths(tmp_path,name):
    zipfile_path=archive(tmp_path,{'psxtract.exe':b'OK',name:b'NO'})
    dest=tmp_path/'out';dest.mkdir()
    with pytest.raises((ValueError,RuntimeError)):
        _extract_psxtract_zip(zipfile_path,dest)


def test_rejects_duplicate_case_insensitive_paths(tmp_path):
    file=archive(tmp_path,{'psxtract.exe':b'A','PSXTRACT.EXE':b'B'})
    target=tmp_path/'out';target.mkdir()
    with pytest.raises(ValueError,match='Duplicate'):
        _extract_psxtract_zip(file,target)


def test_existing_manual_helper_not_silently_overwritten(tmp_path):
    dest=tmp_path/'psxtract';dest.mkdir()
    (dest/'psxtract.exe').write_bytes(b'USER_BINARY')
    with pytest.raises(FileExistsError):
        install_psxtract(tmp_path)
    assert (dest/'psxtract.exe').read_bytes()==b'USER_BINARY'
