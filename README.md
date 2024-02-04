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
poetry add gist-storage
```

if you need encryption

```bash
poetry add gist-storage[encryption]
```

## Usage

`your-github-token`: *avatar* > *settings* > *developper settings* (bottom) > *Personal access tokens* > [tick Gist]  
`your-gist-hash`: *avater* > Gist > [create Gist] > copy from url:
<https://gist.github.com/psychonaute/5df4f367d185e866235dc6e012761c3f>  
`your-filename`: create a new file > copy the name `info.json`

```python
manager = GistManager('your-github-token', 'your-gist-hash', 'your-filename.json')

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

Needs `GIST_ENCRYPT_SECRET_KEY` env variable to hold the key

you can load the env var from *keepass*, using triggers or if the repo using this utility is private you can hard code the key in `.env` file

```python
import base64
import os

# Generate the key
key = base64.urlsafe_b64encode(os.urandom(32)).decode()

# Save the key to .env file
with open(".env", "w") as file:
    file.write(f"GIST_ENCRYPT_SECRET_KEY={key}\n")
```

With the `.env` file inplace the `GIST_ENCRYPT_SECRET_KEY` env var will be define and encryption active.

## License

[MIT](https://github.com/psychonaute/gist-storage/blob/master/LICENSE)

## Credits

This project was generated with [`wemake-python-package`](https://github.com/wemake-services/wemake-python-package). Current template version is: [de5779cdb74d1f42b95f55e9ce6b80ebc5fe7c01](https://github.com/wemake-services/wemake-python-package/tree/de5779cdb74d1f42b95f55e9ce6b80ebc5fe7c01). See what is [updated](https://github.com/wemake-services/wemake-python-package/compare/de5779cdb74d1f42b95f55e9ce6b80ebc5fe7c01...master) since then.
