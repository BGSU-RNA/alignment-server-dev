#!/usr/bin/env python

import os
import json
import hashlib
import argparse
import requests
import urlparse as ul


def main(nts):
    if nts.startswith('http:'):
        url = ul.urlparse(nts)
        query = ul.parse_qs(url.query)
        nts = query['units'][0]

    params = {'units': nts}
    headers = {'Accept': 'application/json'}
    response = requests.get("http://rna.bgsu.edu/variations", headers=headers,
                            params=params)
    response.raise_for_status()
    data = response.json()

    if not os.path.exists("examples"):
        os.mkdir("examples")

    filename = os.path.join("examples", hashlib.md5(nts).hexdigest() + '.json')
    with open(filename, 'wb') as out:
        json.dump(data, out)


if __name__ == '__main__':
    parser = argparse.ArgumentParser("Get and store data for an example")
    parser.add_argument("range", help="Range to get data for")
    args = parser.parse_args()
    main(args.range)
