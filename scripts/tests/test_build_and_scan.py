import subprocess
import os
import stat
import tempfile
import textwrap
from pathlib import Path


MOCK_DOCKER = textwrap.dedent("""#!/usr/bin/env bash
set -euo pipefail
# Simple mock docker for tests. It simulates `docker build` and `docker run` behavior
if [ "$1" = "build" ]; then
  echo "MOCK: docker build $@" >&2
  exit 0
fi
if [ "$1" = "run" ]; then
  # Try to find -o <outpath> and create an output file in trivy-reports when present
  out=""
  next=0
  for a in "$@"; do
    if [ "$next" -eq 1 ]; then
      out="$a"
      next=0
      continue
    fi
    if [ "$a" = "-o" ]; then
      next=1
    fi
  done
  if [ -n "$out" ]; then
    fname=$(basename "$out")
    mkdir -p trivy-reports
    echo '{"mock": "report"}' > "trivy-reports/$fname"
    exit 0
  fi
  # otherwise print a mock table
  echo "MOCK TRIVY TABLE"
  exit 0
fi
echo "MOCK docker (default): $@" >&2
exit 0
""")


def _make_mock_docker(tmp_path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    docker_path = bin_dir / "docker"
    docker_path.write_text(MOCK_DOCKER)
    docker_path.chmod(docker_path.stat().st_mode | stat.S_IEXEC)
    return str(bin_dir)


def test_build_and_scan_creates_report(tmp_path, monkeypatch):
    # Prepare a fake project with a dockerfile
    proj = tmp_path / "proj"
    proj.mkdir()
    ddir = proj / "app"
    ddir.mkdir()
    (ddir / "dockerfile").write_text("FROM alpine")

    # Prepare mock docker in PATH
    mock_bin = _make_mock_docker(tmp_path)
    env = os.environ.copy()
    env["PATH"] = mock_bin + os.pathsep + env.get("PATH", "")

    repo_root = Path(__file__).resolve().parents[2]
    script = str(repo_root / "scripts" / "build-and-scan.sh")

    # Run the script with cwd at proj so it writes reports under proj/trivy-reports
    p = subprocess.run(["bash", script, str(ddir / "dockerfile"), "app"], cwd=proj, env=env, capture_output=True, text=True)
    print(p.stdout)
    print(p.stderr)
    assert p.returncode == 0
    report = proj / "trivy-reports" / "app.json"
    assert report.exists()
    content = report.read_text()
    assert "mock" in content
