from app.contract import BaseGraphState, make_initial_state


def test_make_initial_state_has_required_keys():
    state = make_initial_state("안녕", [{"role": "user", "content": "이전"}])
    assert state["user_input"] == "안녕"
    assert state["messages"] == [{"role": "user", "content": "이전"}]
    assert state["answer"] == ""


def test_make_initial_state_defaults_messages_to_empty_list():
    assert make_initial_state("안녕", None)["messages"] == []


def test_base_graph_state_declares_three_keys():
    assert set(BaseGraphState.__annotations__) == {"user_input", "messages", "answer"}
