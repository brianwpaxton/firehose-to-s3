import argparse
import json
from pathlib import Path
from typing import Sequence

import boto3


def load_record(file_path: Path) -> dict[str, object]:
    with file_path.open(encoding="utf-8") as file:
        record = json.load(file)
    if not isinstance(record, dict):
        raise ValueError("The input JSON must be an object.")
    return record


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Send a JSON object to an Amazon Data Firehose stream."
    )
    parser.add_argument("--stream-name", required=True, help="Firehose delivery stream name")
    parser.add_argument("--region", required=True, help="AWS Region, such as us-east-1")
    parser.add_argument("--file", required=True, type=Path, help="Path to a JSON object")
    args = parser.parse_args(argv)

    record = load_record(args.file)
    response = boto3.client("firehose", region_name=args.region).put_record(
        DeliveryStreamName=args.stream_name,
        Record={"Data": (json.dumps(record, separators=(",", ":")) + "\n").encode("utf-8")},
    )
    print(f"Accepted record: {response['RecordId']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
