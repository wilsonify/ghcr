# test_determine_tag.py
import pytest
from determine_tag import (
    find_first_from_line,
    strip_build_alias,
    extract_tag_from_from_line,
    extract_tag,
)

# ----------------------------
# Tests for find_first_from_line
# ----------------------------
@pytest.mark.parametrize(
    "lines,expected",
    [
        (["FROM ubuntu:22.04"], "FROM ubuntu:22.04"),
        (["# comment", "FROM alpine:3.18"], "FROM alpine:3.18"),
        (["from debian:12"], "from debian:12"),
    ],
)
def test_find_first_from_line_various(lines, expected):
    assert find_first_from_line(lines) == expected


def test_find_first_from_line_missing():
    lines = ["RUN echo hi"]
    with pytest.raises(ValueError):
        find_first_from_line(lines)


# ----------------------------
# Tests for strip_build_alias
# ----------------------------
@pytest.mark.parametrize(
    "line,expected",
    [
        ("FROM wordpress:6.8-php8.3 AS builder", "FROM wordpress:6.8-php8.3"),
        ("FROM alpine:3.18", "FROM alpine:3.18"),
        ("FROM ubuntu:22.04 as stage1", "FROM ubuntu:22.04"),
        ("FROM python:3.12-alpine As final", "FROM python:3.12-alpine"),
    ],
)
def test_strip_build_alias_various(line, expected):
    assert strip_build_alias(line) == expected


# ----------------------------
# Tests for extract_tag_from_from_line
# ----------------------------
@pytest.mark.parametrize(
    "line,expected",
    [
        ("FROM ubuntu:22.04", "22.04"),
        ("FROM some.registry.com/repo:tag", "tag"),
        ("FROM python:3.12-alpine", "3.12-alpine"),
    ],
)
def test_extract_tag_from_from_line_various(line, expected):
    assert extract_tag_from_from_line(line) == expected


def test_extract_tag_from_from_line_no_colon():
    line = "FROM ubuntu"
    with pytest.raises(ValueError):
        extract_tag_from_from_line(line)


# ----------------------------
# Integration tests for extract_tag
# ----------------------------
def test_extract_tag_integration(tmp_path):
    dockerfile = tmp_path / "Dockerfile"
    dockerfile.write_text("FROM wordpress:6.8-php8.3 AS builder\nRUN echo hi\n")
    assert extract_tag(str(dockerfile)) == "6.8-php8.3"


def test_extract_tag_integration_no_tag(tmp_path):
    dockerfile = tmp_path / "Dockerfile"
    dockerfile.write_text("FROM ubuntu\n")
    with pytest.raises(ValueError):
        extract_tag(str(dockerfile))
