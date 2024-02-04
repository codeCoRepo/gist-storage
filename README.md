# gist-storage

[![Build Status](https://github.com/psychonaute/gist-storage/workflows/test/badge.svg?branch=master&event=push)](https://github.com/psychonaute/gist-storage/actions?query=workflow%3Atest)
[![codecov](https://codecov.io/gh/psychonaute/gist-storage/branch/master/graph/badge.svg)](https://codecov.io/gh/psychonaute/gist-storage)
[![Python Version](https://img.shields.io/pypi/pyversions/gist-storage.svg)](https://pypi.org/project/gist-storage/)
[![wemake-python-styleguide](https://img.shields.io/badge/style-wemake-000000.svg)](https://github.com/wemake-services/wemake-python-styleguide)

A versatile tool designed to store and share data via gists, ideal for synchronizing information across devices. Since gists are publicly available, it includes an option for encryption to ensure security.

## Features

- Fully typed with annotations and checked with mypy, [PEP561 compatible](https://www.python.org/dev/peps/pep-0561/)
- Fernet Encryption for sensitive data

## Installation

```bash
poetry add git+git@github.com:psychonaute/gist-storage.git
```

if you need encryption

```bash
poetry add git+git@github.com:psychonaute/gist-storage.git#master --optional -E encryption
poetry install
```

## Usage

### `GITHUB_GIST_TOKEN` environement variable

It needs to hold your githun token, to get the token:  
*your avatar* > *settings* > *developper settings* (bottom) > *Personal access tokens* > [tick Gist]  
The key starts with `ghp_...`

### load into env var

you can:

- load the env var from *keepass*, using triggers
- hard code the key in `.env` file

```env
GITHUB_GIST_TOKEN=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
```

`your-gist-hash`: *avatar* > Gist > [create Gist] > copy from gist url ie:
<https://gist.github.com/username/P809QZO0ZWgS8CzQmeyC4AOqwukolr1h>  
`your-filename`: create a new file > copy the name `info.json`

```python
manager = GistManager('your-gist-hash', 'your-filename.json')

my_data = {
    "ip": "192.168.4.104"
}

manager.push_json(my_data)

update_data = {
    "ip2": "192.168.1.202"
}
manager.update_json(update_data)

print(manager.fetch_json())

# => 
# {
#     "ip": "192.168.4.104"
#     "ip2": "192.168.1.202"
# }
```

### Use Encryption

Encryption activates when `GIST_ENCRYPT_SECRET_KEY` is present in env variables.

It Needs hold a 32 chars long string  

You can generate one and add it into your `.env` file like so:  

```python
import base64
from dotenv import set_key

# Generate the key
key = base64.urlsafe_b64encode(os.urandom(32)).decode()

# Save the key to .env file
set_key('.env', 'GIST_ENCRYPT_SECRET_KEY', key)
```

## License

[MIT](https://github.com/psychonaute/gist-storage/blob/master/LICENSE)

## Credits

This project was generated with [`wemake-python-package`](https://github.com/wemake-services/wemake-python-package). Current template version is: [de5779cdb74d1f42b95f55e9ce6b80ebc5fe7c01](https://github.com/wemake-services/wemake-python-package/tree/de5779cdb74d1f42b95f55e9ce6b80ebc5fe7c01). See what is [updated](https://github.com/wemake-services/wemake-python-package/compare/de5779cdb74d1f42b95f55e9ce6b80ebc5fe7c01...master) since then.
