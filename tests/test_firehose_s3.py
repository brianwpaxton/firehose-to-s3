import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

import firehose_s3


def test_load_record_reads_json_object(tmp_path: Path) -> None:
    file_path = tmp_path / "record.json"
    file_path.write_text('{"hello": "world"}', encoding="utf-8")

    assert firehose_s3.load_record(file_path) == {"hello": "world"}


def test_load_record_rejects_non_object_json(tmp_path: Path) -> None:
    file_path = tmp_path / "record.json"
    file_path.write_text("[1, 2]", encoding="utf-8")

    with pytest.raises(ValueError, match="must be an object"):
        firehose_s3.load_record(file_path)


def test_main_sends_json_record_to_firehose(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    file_path = tmp_path / "record.json"
    file_path.write_text('{"hello": "world"}', encoding="utf-8")
    firehose_client = Mock()
    firehose_client.put_record.return_value = {"RecordId": "record-123"}

    with patch.object(firehose_s3.boto3, "client", return_value=firehose_client) as client_factory:
        assert firehose_s3.main(
            ["--stream-name", "demo-stream", "--region", "us-west-2", "--file", str(file_path)]
        ) == 0

    client_factory.assert_called_once_with("firehose", region_name="us-west-2")
    firehose_client.put_record.assert_called_once_with(
        DeliveryStreamName="demo-stream",
        Record={"Data": (json.dumps({"hello": "world"}, separators=(",", ":")) + "\n").encode()},
    )
    assert "record-123" in capsys.readouterr().out
