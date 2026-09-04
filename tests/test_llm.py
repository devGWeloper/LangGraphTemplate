import pytest

from app.llm import LLMConfigError, get_llm


def test_get_llm_raises_when_env_missing(monkeypatch):
    for key in ("LLM_BASE_URL", "LLM_API_KEY", "LLM_MODEL"):
        monkeypatch.delenv(key, raising=False)
    with pytest.raises(LLMConfigError) as exc:
        get_llm()
    assert "LLM_BASE_URL" in str(exc.value)


def _set_env(monkeypatch):
    monkeypatch.setenv("LLM_BASE_URL", "https://example.invalid/v1")
    monkeypatch.setenv("LLM_API_KEY", "dummy-key")
    monkeypatch.setenv("LLM_MODEL", "test-model")


def test_get_llm_builds_client_from_env(monkeypatch):
    _set_env(monkeypatch)
    llm = get_llm(temperature=0.7)
    assert llm.model_name == "test-model"
    assert llm.temperature == 0.7


def test_get_llm_model_argument_overrides_env(monkeypatch):
    _set_env(monkeypatch)
    assert get_llm(model="other-model").model_name == "other-model"
