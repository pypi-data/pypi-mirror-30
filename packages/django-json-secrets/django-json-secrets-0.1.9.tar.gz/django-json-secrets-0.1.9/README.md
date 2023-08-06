# django-json-secrets

**django-json-secrets** is a package that helps you import the secret values managed by JSON file into Django.

## Requirements

- Python (3.6)
- Django (>2.0)

## Installation

Install using `pip`

```
pip install django-json-secrets
```

## Example usage

Specify the folder that contains the JSON secret files, and name the JSON file as the module name to assign the value to.

If the folder where the JSON secret files are gathered is `.secrets` and the `settings` module is packaged, it has the following structure.

```
# settings module
settings/
	__init__.py
	base.py
	local.py

# Secrets DIR
.secrets/
	base.json
	local.json
```

**`settings/base.py`**

```python
from djs import import_secrets

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SECRETS_DIR = os.path.join(BASE_DIR, '.secrets')
import_secrets()
```

**`settings/local.py`**

```python
from .base import *

import_secrets()
```
