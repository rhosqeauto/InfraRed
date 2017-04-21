import os

import pytest

from infrared.core.cli import cli
from infrared.core.utils import exceptions


@pytest.fixture
def list_value_type():
    """
    Create a new list value complex type
    """
    return cli.ListValue("test", [os.getcwd(), ], 'cmd')


@pytest.fixture
def ini_type():
    """Create a new IniType complex type
    """
    return cli.IniType("TestIniType", None, None)


@pytest.mark.parametrize(
    "test_value,expected", [
        ("item1,item2", ["item1", "item2"]),
        ("item1", ["item1", ]),
        ("item1,item2,item3,", ["item1", "item2", "item3", ''])])
def test_list_value_resolve(list_value_type, test_value, expected):
    """
    Verifies the string value can be resolved to the list.
    """
    assert expected == list_value_type.resolve(test_value)


@pytest.mark.parametrize("input_value, expected_return", [
    (['k1=v1'], {'defaults': {'k1': 'v1'}}),
    (['s1.k1=v1'], {'s1': {'k1': 'v1'}}),
    ([' s1.k1=v1 '], {'s1': {'k1': 'v1'}}),
    (['s1.k1=v1', 's1.k2=v2', 's2.k3=v3'],
     {'s1': {'k1': 'v1', 'k2': 'v2'}, 's2': {'k3': 'v3'}}),
    ('k1=v1', {'defaults': {'k1': 'v1'}}),
    ('s1.k1=v1', {'s1': {'k1': 'v1'}}),
    (' s1.k1=v1 ', {'s1': {'k1': 'v1'}}),
    ('s1.k1=v1,s1.k2=v2,s2.k3=v3',
     {'s1': {'k1': 'v1', 'k2': 'v2'}, 's2': {'k3': 'v3'}}),
    ('s1.k1=v1, s1.k2=v2, s2.k3=v3',
     {'s1': {'k1': 'v1', 'k2': 'v2'}, 's2': {'k3': 'v3'}}),
])
def test_ini_type_resolve(input_value, expected_return, ini_type):
    """Verifies the return value of 'resolve' method in 'IniType' Complex type
    """
    assert ini_type.resolve(input_value) == expected_return


@pytest.fixture(scope="module")
def file_root_dir(tmpdir_factory):
    """Prepares the testing dirs for file tests"""
    root_dir = tmpdir_factory.mktemp('complex_file_dir')

    for file_path in ['file1.yml',
                      'arg/name/file2',
                      'defaults/arg/name/file.yml',
                      'defaults/arg/name/file2',
                      'vars/arg/name/file1.yml',
                      'vars/arg/name/file3.yml',
                      'vars/arg/name/nested/file4.yml']:
        root_dir.join(file_path).ensure()

    return root_dir


@pytest.fixture(scope="module")
def dir_root_dir(tmpdir_factory):
    """Prepares the testing dirs for dir tests"""
    root_dir = tmpdir_factory.mktemp('complex_dir')

    for dir_path in ['dir0/1.file',
                     'arg/name/dir1/1.file',
                     'vars/arg/name/dir2/1.file',
                     'defaults/arg/name/dir3/1.file']:
        # creating a file will create a dir
        root_dir.join(dir_path).ensure()

    return root_dir


def create_file_type(root_dir, type_class):
    return type_class("arg-name",
                      (root_dir.join('vars').strpath,
                       root_dir.join('defaults').strpath),
                      None)


@pytest.fixture
def file_type(file_root_dir, request):
    return create_file_type(file_root_dir, request.param)


@pytest.fixture
def dir_type(dir_root_dir, request):
    return create_file_type(dir_root_dir, request.param)


@pytest.mark.parametrize('file_type', [cli.FileType], indirect=True)
def test_file_type_resolve(file_root_dir, file_type, monkeypatch):
    """Verifies the file complex type"""
    # change cwd to the temp dir
    monkeypatch.setattr("os.getcwd", lambda: file_root_dir.strpath)

    assert file_type.resolve('file1') == file_root_dir.join(
        'file1.yml').strpath
    assert file_type.resolve('file2') == file_root_dir.join(
        'arg/name/file2').strpath
    with pytest.raises(exceptions.IRFileNotFoundException):
        file_type.resolve('file.yml')


@pytest.mark.parametrize('file_type', [cli.VarFileType], indirect=True)
def test_var_file_type_resolve(file_root_dir, file_type, monkeypatch):
    """Verifies the file complex type"""
    # change cwd to the temp dir
    monkeypatch.setattr("os.getcwd", lambda: file_root_dir.strpath)

    assert file_type.resolve('file1') == file_root_dir.join(
        'file1.yml').strpath
    assert file_type.resolve(
        os.path.abspath('file1')) == file_root_dir.join('file1.yml').strpath
    assert file_type.resolve('file2') == file_root_dir.join(
        'arg/name/file2').strpath
    assert file_type.resolve('file.yml') == file_root_dir.join(
        'defaults/arg/name/file.yml').strpath
    assert file_type.resolve('file3') == file_root_dir.join(
        'vars/arg/name/file3.yml').strpath
    assert file_type.resolve('nested/file4.yml') == file_root_dir.join(
        'vars/arg/name/nested/file4.yml').strpath

    with pytest.raises(exceptions.IRFileNotFoundException):
        file_type.resolve('file5')


@pytest.mark.parametrize('file_type', [cli.ListFileType], indirect=True)
def test_list_of_var_files(file_root_dir, file_type, monkeypatch):
    """Verifies the list of files"""
    monkeypatch.setattr("os.getcwd", lambda: file_root_dir.strpath)

    assert file_type.resolve('file1') == [
        file_root_dir.join('file1.yml').strpath]
    assert file_type.resolve('file1,file2') == [
        file_root_dir.join('file1.yml').strpath,
        file_root_dir.join('arg/name/file2').strpath]
    assert file_type.resolve('file3.yml,vars/arg/name/file3') == [
        file_root_dir.join('vars/arg/name/file3.yml').strpath,
        file_root_dir.join('vars/arg/name/file3.yml').strpath]


@pytest.mark.parametrize('dir_type', [cli.VarDirType], indirect=True)
def test_dir_type_resolve(dir_root_dir, dir_type, monkeypatch):
    """Verifies the file complex type"""
    # change cwd to the temp dir
    monkeypatch.setattr("os.getcwd", lambda: dir_root_dir.strpath)

    assert dir_type.resolve('dir0') == dir_root_dir.join(
        'dir0/').strpath
    assert dir_type.resolve('dir1') == dir_root_dir.join(
        'arg/name/dir1/').strpath
    assert dir_type.resolve('dir2') == dir_root_dir.join(
        'vars/arg/name/dir2/').strpath
    assert dir_type.resolve('dir3') == dir_root_dir.join(
        'defaults/arg/name/dir3/').strpath
    with pytest.raises(exceptions.IRFileNotFoundException):
        dir_type.resolve('dir4')
