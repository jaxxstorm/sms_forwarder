# SMS Forwarder

Receives a Flask-compatible request and forwards its `From` and `Body` fields
using the Twilio REST client. The function entry point is `main.receive_sms`.

## Runtime and installation

This dependency set targets **Python 3.12**, replacing the original Python 3.6
Pipfile target. Confirm the deployed function's runtime and hosting framework
support Python 3.12 before adopting this update. This repository does not define
or change the deployed runtime, and the local tests do not deploy or send SMS.

```sh
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install --require-hashes -r requirements.txt
python -m pip check
python -m unittest discover -s tests -v
```

Set `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_NUMBER`, and
`DESTINATION_NUMBER` in the hosting environment. Do not commit credentials.
Tests use dummy values and intercept the HTTP transport while exercising the
real Twilio SDK, including form serialization and API error propagation.

## Dependency maintenance

`Pipfile` pins the direct dependencies. `Pipfile.lock` records the resolved tree
and artifact hashes; `requirements.txt` is the hash-bearing Pipenv export used
for installation. With Pipenv installed separately from the application:

```sh
pipenv lock --python 3.12
pipenv verify
pipenv requirements --hash > requirements.txt
```

Install the exported requirements into a fresh Python 3.12 environment and run
the tests above. With `pip-audit` installed separately, audit the entire pinned
export after successful installation and `pip check`:

```sh
pip-audit -r requirements.txt --no-deps --disable-pip
```

The audit flags avoid another resolver environment; they do not omit transitive
packages because every locked dependency is explicitly present in the export.
An audit reports known package advisories, not an application security review.
The existing response format and missing-field behavior are unchanged.
