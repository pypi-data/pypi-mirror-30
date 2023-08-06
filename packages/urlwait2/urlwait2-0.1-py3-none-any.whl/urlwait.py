#!/usr/bin/env python3
import time

import click
from requests import get


@click.command()
@click.argument('url')
def main(url):
    if not url.startswith('http'):
        url = 'http://' + url
    print(f'urlwait: waiting for {url}')

    attempt = 1
    while True:
        try:
            get(url, allow_redirects=True).raise_for_status()
        except Exception as e:
            print(f'{e} Attempt {attempt} failed, retrying in 2 seconds')
            attempt += 1
            time.sleep(2)
        else:
            print(f'urlwait: successfully connected to {url}')
            break


if __name__ == '__main__':
    main()
