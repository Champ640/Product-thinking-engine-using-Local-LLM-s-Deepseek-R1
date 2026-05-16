"""Tests for LLM service — think block parsing and message preparation."""

from backend.services.llm_service import _parse_think_tokens, _prepare_messages


class TestParseThinkTokens:
    """Test the <think> block parser."""

    def test_plain_content_returns_content_type(self):
        parts = _parse_think_tokens("Hello world", False)
        assert len(parts) == 1
        assert parts[0]["type"] == "content"
        assert parts[0]["text"] == "Hello world"

    def test_think_tag_opens_thinking_block(self):
        parts = _parse_think_tokens("<think>reasoning", False)
        assert any(p["type"] == "thinking" and "reasoning" in p["text"] for p in parts)

    def test_full_think_block_parsed(self):
        parts = _parse_think_tokens("<think>deep thought</think>answer", False)
        types = [p["type"] for p in parts if p["text"]]
        assert "thinking" in types
        assert "content" in types

    def test_inside_think_continues(self):
        parts = _parse_think_tokens("more reasoning", True)
        assert parts[0]["type"] == "thinking"
        assert parts[0]["inside_think"] is True

    def test_close_think_exits(self):
        parts = _parse_think_tokens("end</think>output", True)
        has_content = any(p["type"] == "content" and "output" in p["text"] for p in parts)
        assert has_content

    def test_empty_string_returns_state(self):
        parts = _parse_think_tokens("", False)
        assert len(parts) == 1
        assert parts[0]["inside_think"] is False


class TestPrepareMessages:
    """Test message preparation with /think directives."""

    def test_appends_think_to_last_user_message(self):
        msgs = [{"role": "user", "content": "hello"}]
        result = _prepare_messages(msgs, use_thinking=True)
        assert result[0]["content"].endswith(" /think")

    def test_appends_no_think_when_disabled(self):
        msgs = [{"role": "user", "content": "hello"}]
        result = _prepare_messages(msgs, use_thinking=False)
        assert result[0]["content"].endswith(" /no_think")

    def test_does_not_mutate_original(self):
        msgs = [{"role": "user", "content": "hello"}]
        _prepare_messages(msgs, use_thinking=True)
        assert msgs[0]["content"] == "hello"

    def test_empty_messages_handled(self):
        result = _prepare_messages([], use_thinking=True)
        assert result == []

    def test_finds_last_user_in_multi_turn(self):
        msgs = [
            {"role": "user", "content": "first"},
            {"role": "assistant", "content": "reply"},
            {"role": "user", "content": "second"},
        ]
        result = _prepare_messages(msgs, use_thinking=True)
        assert result[2]["content"].endswith(" /think")
        assert result[0]["content"] == "first"
