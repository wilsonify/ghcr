# test_determine_tag.py
import pytest

from determine_tag import (
    read_dockerfile,
    find_first_from_line,
    strip_build_alias,
    extract_tag_from_from_line,
    write_to_github_env,
    extract_tag,
)


# ----------------------------
# Tests for read_dockerfile
# ----------------------------
def test_read_dockerfile(tmp_path):
    file_path = tmp_path / "Dockerfile"
    file_path.write_text("FROM ubuntu:22.04\nRUN echo hi\n")
    lines = read_dockerfile(str(file_path))
    assert lines == ["FROM ubuntu:22.04\n", "RUN echo hi\n"]


def test_read_dockerfile_file_not_found():
    with pytest.raises(FileNotFoundError):
        read_dockerfile("nonexistent.Dockerfile")


# ----------------------------
# Tests for find_first_from_line
# ----------------------------
def test_find_first_from_line_basic():
    lines = ["# comment\n", "FROM ubuntu:22.04\n", "RUN echo hi\n"]
    assert find_first_from_line(lines) == "FROM ubuntu:22.04"


def test_find_first_from_line_uppercase():
    lines = ["from alpine:3.18\n"]
    assert find_first_from_line(lines) == "from alpine:3.18"


def test_find_first_from_line_missing():
    lines = ["RUN echo hi\n"]
    with pytest.raises(ValueError):
        find_first_from_line(lines)


# ----------------------------
# Tests for strip_build_alias
# ----------------------------
def test_strip_build_alias_basic():
    line = "FROM wordpress:6.8-php8.3 AS builder"
    assert strip_build_alias(line) == "FROM wordpress:6.8-php8.3"


def test_strip_build_alias_no_alias():
    line = "FROM alpine:3.18"
    assert strip_build_alias(line) == "FROM alpine:3.18"


def test_strip_build_alias_lowercase_as():
    line = "FROM ubuntu:22.04 as stage1"
    assert strip_build_alias(line) == "FROM ubuntu:22.04"


# ----------------------------
# Tests for extract_tag_from_from_line
# ----------------------------
def test_extract_tag_basic():
    line = "FROM ubuntu:22.04"
    assert extract_tag_from_from_line(line) == "22.04"


def test_extract_tag_multiple_colons():
    line = "FROM some.registry.com/repo:tag"
    assert extract_tag_from_from_line(line) == "tag"


def test_extract_tag_no_colon():
    line = "FROM ubuntu"
    with pytest.raises(ValueError):
        extract_tag_from_from_line(line)


# ----------------------------
# Tests for write_to_github_env
# ----------------------------
def test_write_to_github_env(tmp_path):
    env_file = tmp_path / "env"
    write_to_github_env("mytag", str(env_file))
    content = env_file.read_text()
    assert content.strip() == "TAG=mytag"


def test_write_to_github_env_no_file():
    # Should silently do nothing if github_env is None
    write_to_github_env("mytag", None)


# ----------------------------
# Tests for extract_tag (integration)
# ----------------------------
def test_extract_tag_basic2(tmp_path):
    file_path = tmp_path / "Dockerfile"
    file_path.write_text("FROM wordpress:6.8-php8.3 AS builder\nRUN echo hi\n")
    tag = extract_tag(str(file_path))
    assert tag == "6.8-php8.3"


def test_extract_tag_missing_tag(tmp_path):
    file_path = tmp_path / "Dockerfile"
    file_path.write_text("FROM ubuntu\n")
    with pytest.raises(ValueError):
        extract_tag(str(file_path))
