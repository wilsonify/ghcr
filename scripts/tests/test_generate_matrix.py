import json
import subprocess
import tempfile
import os
import sys
from pathlib import Path


def test_generate_matrix_empty(tmp_path, monkeypatch):
    # Run the script in an empty temp dir -> should output []
    cwd = tmp_path
    repo_root = Path(__file__).resolve().parents[2]
    script = str(repo_root / "scripts" / "generate-matrix.py")
    result = subprocess.run([sys.executable, script], cwd=cwd, capture_output=True, text=True)
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert isinstance(data, list)
    assert data == []


def test_generate_matrix_with_files(tmp_path):
    # Create some dockerfile paths
    (tmp_path / "a").mkdir()
    (tmp_path / "a" / "dockerfile").write_text("FROM alpine")
    (tmp_path / "b" / "nested").mkdir(parents=True)
    (tmp_path / "b" / "nested" / "dockerfile").write_text("FROM debian")

    repo_root = Path(__file__).resolve().parents[2]
    script = str(repo_root / "scripts" / "generate-matrix.py")
    result = subprocess.run([sys.executable, script], cwd=tmp_path, capture_output=True, text=True)
    assert result.returncode == 0
    data = json.loads(result.stdout)
    paths = sorted([item["path"] for item in data])
    assert "a/dockerfile" in paths
    assert "b/nested/dockerfile" in paths
