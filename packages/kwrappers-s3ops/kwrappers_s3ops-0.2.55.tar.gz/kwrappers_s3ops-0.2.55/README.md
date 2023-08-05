# Kwrappers

A central repository for high level wrappers of AWS tasks.  It is intended to be used as a python library.  It should include any operations that:

- a) consolidates a number of low level automation operations; and
- b) has a clearly defined purpose.

It is foreseeable that this library becomes quite large and as such no noob user front end will be provided however it should be useful for informed users either, wishing to perform complex AWS automation or, writing CLI applications for their noobs to use.

## Installation

```
pip install kwrappers
```

## Usage

### Ex 1: List your buckets

```python
from kwrappers.util import Session

session = Session()
s3 = session.client('s3')
[b['Name'] for b in s3.list_buckets()['Buckets']]

```

### Ex 2: Perform a highly customised S3 transfer using an assumed rol

```python
from kwrappers.util import Session
from kwrappers.s3ops.general import TransferConfig, Transfer, ProgressPercentage

# 1.    Get a session
# Get TOKEN ASSUMED_ROLE and MFA_SERIAL
role = "arn:aws:iam::167464700695:role/Demo-StackCreator"
mfa_serial = "arn:aws:iam::623551153426:mfa/IAM-T.Elson"
session = Session('ap-southeast-2', role=role, mfa_serial=mfa_serial, mfa_token='111222')
s3 = session.client('s3', 'ap-southeast-2')

# 2.    Define to file for upload
file_name = '~/Downloads/Slack-2.8.2-macOS.zip'
bucket_name = 'khasha'
target_file_name = 'foo'

# 3.    Define the setting for the transfer
config = TransferConfig(
    multipart_threshold=8 * 1024 * 1024,
    max_request_concurrency=4,
    num_download_attempts=10,
    max_bandwidth=15 * 1024,  # Bytes/s
)

# 4.    Carry out the transfer
transfer = Transfer(s3, config)
transfer.upload_file(
    file_name,
    bucket_name,
    target_file_name,
    callback=ProgressPercentage(file_name)
)

```

## Develop

1. Clone the repo
2. Install the packages locally in a confined python environment

```bash
./dev_install.sh
```

3. Install test requirements

```bash
pip install -r requirements_test.txt
```

### Testing and Linting

Lint and test before committing code. The build system will fail if either of these steps fail:

```bash
pytest
flake8 --ignore=E501
```

To build a new version and upload to PyPi ensure these steps pass.

Write tests for new code.  See current tests for examples. Use `pytest` to run all tests.
