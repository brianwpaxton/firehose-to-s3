# JSON to S3 with Amazon Data Firehose

A small Python example that sends one JSON object to an Amazon Data Firehose
delivery stream. The CloudFormation template provisions the stream, its S3
destination, and the least-privilege IAM role Firehose needs to write there.

## Prerequisites

- Python 3.12 or newer
- AWS CLI v2 configured with credentials allowed to create CloudFormation
  stacks, IAM roles, S3 buckets, and Firehose delivery streams

The application uses boto3 1.x. Dependencies are declared in `requirements.txt`.

## Deploy

Choose an AWS Region that supports Amazon Data Firehose, then deploy the stack:

```bash
aws cloudformation deploy \
  --template-file template.yaml \
  --stack-name firehose-s3-demo \
  --capabilities CAPABILITY_IAM \
  --region eu-west-2
```

Get the delivery stream name from the stack outputs:

```bash
aws cloudformation describe-stacks \
  --stack-name firehose-s3-demo \
  --query "Stacks[0].Outputs" \
  --output table \
  --region eu-west-2
```

## Send a JSON record

Install the application dependency and submit the included sample:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python firehose_s3.py \
  --stream-name firehouse-s3-demo-DeliveryStream-YdM9djwewW3i \
  --region eu-west-2 \
  --file sample.json
```

The command prints the Firehose record ID when the service accepts the record.
Firehose buffers records before delivering them to S3, so the object may take
a short time to appear. The bucket name is included in the CloudFormation stack
outputs; delivered objects are written under the `records/` prefix, partitioned
by delivery date.

## Test

```bash
python -m pip install -r requirements.txt -r requirements-dev.txt
python -m pytest
```

Tests use a mocked Firehose client and do not require AWS credentials.

## Clean up

Empty the destination bucket first (use the bucket name from the stack outputs),
then delete the stack:

```bash
aws s3 rm s3://<DestinationBucketName> --recursive --region eu-west-2
aws cloudformation delete-stack \
  --stack-name firehose-s3-demo \
  --region eu-west-2
```
