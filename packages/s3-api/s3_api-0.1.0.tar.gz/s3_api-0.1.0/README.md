# Amazon S3 API

Simple Python based API client for Amazon S3.

## Configuration

* `S3_BASE_URL` (`str`) - The base URL to be used for the API calls (defaults to `https://s3.amazonaws.com/`)
* `S3_ACCESS_KEY` (`str`) - Secret key to be used to authenticate API request (defaults to `None`)
* `S3_SECRET` (`str`) - String value to be kept secret and used in the request signing process as the secret key (defaults to `None`)
* `S3_REGION` (`str`) - The name of the region where the request are going to be sent by default (defaults to `None`)

## License

Amazon S3 API is currently licensed under the [Apache License, Version 2.0](http://www.apache.org/licenses/).

## Build Automation

[![Build Status](https://travis-ci.org/hivesolutions/s3_api.svg?branch=master)](https://travis-ci.org/hivesolutions/s3_api)
[![Coverage Status](https://coveralls.io/repos/hivesolutions/s3_api/badge.svg?branch=master)](https://coveralls.io/r/hivesolutions/s3_api?branch=master)
[![PyPi Status](https://img.shields.io/pypi/v/s3_api.svg)](https://pypi.python.org/pypi/s3_api)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://www.apache.org/licenses/)
