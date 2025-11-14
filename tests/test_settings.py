"""Tests for pplyz.settings."""

import os

from pplyz import settings


def test_determine_config_dir_prefers_override(monkeypatch, tmp_path):
    """PPLYZ_CONFIG_DIR should take precedence."""
    override = tmp_path / "custom"
    monkeypatch.setenv(settings.CONFIG_DIR_ENV, str(override))

    path = settings.determine_config_dir()

    assert path == override


def test_load_runtime_configuration_reads_toml(monkeypatch, tmp_path):
    """Values from config.toml populate environment variables."""
    project_root = tmp_path / "proj"
    project_root.mkdir()
    monkeypatch.setattr(settings, "PROJECT_ROOT", project_root)

    config_dir = tmp_path / ".config" / "pplyz"
    config_dir.mkdir(parents=True)

    config_file = config_dir / settings.CONFIG_TOML_NAME
    config_file.write_text(
        """
[env]
GEMINI_API_KEY = "gemini-key"
OPENAI_API_KEY = "openai-key"

[pplyz]
default_model = "gemini/example-model"
default_input = "title,abstract"
default_output = "summary:str"
"""
    )

    monkeypatch.setenv(settings.CONFIG_DIR_ENV, str(config_dir))
    for key in (
        "OPENAI_API_KEY",
        "GEMINI_API_KEY",
        "PPLYZ_DEFAULT_MODEL",
        "PPLYZ_DEFAULT_INPUT",
        "PPLYZ_DEFAULT_OUTPUT",
    ):
        monkeypatch.delenv(key, raising=False)

    settings.load_runtime_configuration()

    assert os.environ["OPENAI_API_KEY"] == "openai-key"
    assert os.environ["GEMINI_API_KEY"] == "gemini-key"
    assert os.environ["PPLYZ_DEFAULT_MODEL"] == "gemini/example-model"
    assert os.environ["PPLYZ_DEFAULT_INPUT"] == "title,abstract"
    assert os.environ["PPLYZ_DEFAULT_OUTPUT"] == "summary:str"


def test_local_config_takes_precedence(monkeypatch, tmp_path):
    """Project-local config should override user-level config."""
    project_root = tmp_path / "proj"
    project_root.mkdir()
    local_file = project_root / settings.LOCAL_CONFIG_NAME
    local_file.write_text(
        """
[env]
OPENAI_API_KEY = "local-openai"

[pplyz]
default_model = "local-model"
default_input = "local-col"
default_output = "flag:bool"
"""
    )
    monkeypatch.setattr(settings, "PROJECT_ROOT", project_root)

    config_dir = tmp_path / ".config" / "pplyz"
    config_dir.mkdir(parents=True)
    config_file = config_dir / settings.CONFIG_TOML_NAME
    config_file.write_text(
        """
[env]
OPENAI_API_KEY = "global-openai"
GEMINI_API_KEY = "global-gemini"

[pplyz]
default_model = "global-model"
default_input = "global-col"
default_output = "summary:str"
"""
    )

    monkeypatch.setenv(settings.CONFIG_DIR_ENV, str(config_dir))
    for key in (
        "OPENAI_API_KEY",
        "GEMINI_API_KEY",
        "PPLYZ_DEFAULT_MODEL",
        "PPLYZ_DEFAULT_INPUT",
        "PPLYZ_DEFAULT_OUTPUT",
    ):
        monkeypatch.delenv(key, raising=False)

    settings.load_runtime_configuration()

    assert os.environ["OPENAI_API_KEY"] == "local-openai"
    assert os.environ["GEMINI_API_KEY"] == "global-gemini"
    assert os.environ["PPLYZ_DEFAULT_MODEL"] == "local-model"
    assert os.environ["PPLYZ_DEFAULT_INPUT"] == "local-col"
    assert os.environ["PPLYZ_DEFAULT_OUTPUT"] == "flag:bool"
