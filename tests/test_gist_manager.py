from typing import Any, Dict
import json
import pytest
from dotenv import find_dotenv, load_dotenv

from gist_storage.manage import GistManager

# load environment variables
load_dotenv(find_dotenv())


# gist created of this pytest suite
@pytest.fixture
def gist_hash() -> str:
    return '38de70e57cbfc92e892cef1fe736ee52'


@pytest.fixture
def filename() -> str:
    return 'test_file.json'


@pytest.fixture
def test_data() -> Dict[str, Any]:
    return {
        'key1': 'value1',
        'key2': 42,
        'key3': True,
    }


@pytest.fixture
def update_data() -> Dict[str, Any]:
    return {
        'key2': 100,
        'key4': 'new_value',
    }


def test_write_read_json_without_encryption(
    gist_hash: str,
    filename: str,
    test_data: Dict[str, Any],
) -> None:
    manager = GistManager(gist_hash, filename, disable_encryption=True)

    assert manager.push_json(test_data)
    fetched_data = manager.fetch_json()

    assert fetched_data == test_data


def test_write_read_json_with_encryption(
    gist_hash: str,
    filename: str,
    test_data: Dict[str, Any],
) -> None:
    manager = GistManager(gist_hash, filename)

    assert manager.push_json(test_data)
    fetched_data = manager.fetch_json()

    assert fetched_data == test_data


def test_update_json_without_encryption(
    gist_hash: str,
    filename: str,
    test_data: Dict[str, Any],
    update_data: Dict[str, Any],
) -> None:
    manager = GistManager(gist_hash, filename, disable_encryption=True)

    assert manager.push_json(test_data)
    assert manager.update_json(update_data)

    expected_data = test_data.copy()
    expected_data.update(update_data)

    fetched_data = manager.fetch_json()
    assert fetched_data == expected_data


def test_update_json_with_encryption(
    gist_hash: str,
    filename: str,
    test_data: Dict[str, Any],
    update_data: Dict[str, Any],
) -> None:
    manager = GistManager(gist_hash, filename)

    assert manager.push_json(test_data)
    assert manager.update_json(update_data)

    expected_data = test_data.copy()
    expected_data.update(update_data)

    fetched_data = manager.fetch_json()
    assert fetched_data == expected_data


def test_pop_content(
    gist_hash: str,
    filename: str,
    test_data: Dict[str, Any],
) -> None:
    manager = GistManager(gist_hash, filename, disable_encryption=True)

    assert manager.push_json(test_data)
    popped_content = manager.pop_content()

    assert json.loads(popped_content) == test_data

    # Expect KeyError when trying to fetch content after popping
    with pytest.raises(KeyError) as excinfo:
        manager.fetch_json()

    assert str(excinfo.value) == f"'{filename}'"
