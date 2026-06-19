from appsec_kit.detector import detect_project_type


def test_detects_python_via_pyproject(tmp_path):
    (tmp_path / "pyproject.toml").touch()
    assert detect_project_type(tmp_path) == "python"


def test_detects_python_via_requirements(tmp_path):
    (tmp_path / "requirements.txt").touch()
    assert detect_project_type(tmp_path) == "python"


def test_detects_python_via_setup_py(tmp_path):
    (tmp_path / "setup.py").touch()
    assert detect_project_type(tmp_path) == "python"


def test_detects_python_via_pipfile(tmp_path):
    (tmp_path / "Pipfile").touch()
    assert detect_project_type(tmp_path) == "python"


def test_detects_node_via_package_json(tmp_path):
    (tmp_path / "package.json").touch()
    assert detect_project_type(tmp_path) == "node"


def test_returns_none_when_both_present(tmp_path):
    (tmp_path / "pyproject.toml").touch()
    (tmp_path / "package.json").touch()
    assert detect_project_type(tmp_path) is None


def test_returns_none_when_empty_directory(tmp_path):
    assert detect_project_type(tmp_path) is None
