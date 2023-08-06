This command-line tool tries to connect to specified url until it
receives successful http status code.

## Installation

```
pip install urlwait2
```

## Usage
To wait before starting celery worker:

```bash
urlwait2 myhost && celery -A myapp.app worker
```
