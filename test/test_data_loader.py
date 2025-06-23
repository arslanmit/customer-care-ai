import json

from dashboard.data_loader import load_conversation_data


def test_load_conversation_data(tmp_path):
    test_file = tmp_path / "test.json"
    sample = {
        "conversations": [
            {
                "user_id": "u1",
                "messages": [
                    {"type": "user", "text": "hi"},
                    {"type": "bot", "text": "hello"},
                ],
                "timestamp": "2024-01-01T00:00:00",
                "duration": 2,
            }
        ]
    }
    test_file.write_text(json.dumps(sample))
    data = load_conversation_data(custom_path=str(test_file))
    assert data and data[0]["user_id"] == "u1"
