import pytest
import connect_ai


def test_connection_check_does_not_write_credentials(monkeypatch):
    class Response:
        status_code = 200
        ok = True
        def json(self):
            return {"choices": [{"message": {"content": "OK"}}]}
    monkeypatch.setattr(connect_ai.requests, "post", lambda *args, **kwargs: Response())
    connect_ai.verify("sk-" + "synthetic" * 5)


@pytest.mark.parametrize("status", [401, 429, 403, 500])
def test_failed_connection_is_actionable(monkeypatch, status):
    class Response:
        status_code = status
        ok = False
        def json(self):
            return {"error": {"message": "Test failure", "code": "test_error"}}
    monkeypatch.setattr(connect_ai.requests, "post", lambda *args, **kwargs: Response())
    with pytest.raises(ValueError):
        connect_ai.verify("sk-" + "synthetic" * 5)


def test_400_detail_redacts_key(monkeypatch):
    class Response:
        status_code = 400
        ok = False
        def json(self):
            return {"error": {"code": "unsupported_parameter", "message": "Bad parameter for sk-syntheticsecret; key synthetic-test-key"}}
    monkeypatch.setattr(connect_ai.requests, "post", lambda *args, **kwargs: Response())
    with pytest.raises(ValueError) as caught:
        connect_ai.verify("sk-" + "synthetic" * 5)
    assert "unsupported_parameter" in str(caught.value)
    assert "sk-syntheticsecret" not in str(caught.value)


def test_non_json_error_not_echoed():
    class Response:
        def json(self):
            raise ValueError("HTML error")
    assert "Non-JSON" in connect_ai.safe_error(Response(), "synthetic")


@pytest.mark.parametrize("key", ["key_tracking123", "sk-abc", "\x16sk-" + "x"*30, "sk-" + "x"*30 + "\u200b"])
def test_bad_paste_never_sent(monkeypatch, key):
    def forbidden(*args, **kwargs):
        pytest.fail("Malformed key must not leave the machine")
    monkeypatch.setattr(connect_ai.requests, "post", forbidden)
    with pytest.raises(ValueError, match="pasted text"):
        connect_ai.verify(key)
