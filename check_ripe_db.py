import argparse
import json

import requests


def parse_cli():
    parser = argparse.ArgumentParser(
        description="Monitoring check plugin to query the RIPE database and check if the values match the expectations")
    parser.add_argument("-s", "--source", type=str, help="RIPE database source", default="ripe")
    parser.add_argument("-o", "--objecttype", type=str, help="RIPE database objecttype")
    parser.add_argument("-k", "--key", type=str, help="RIPE database objecttype")
    parser.add_argument("-e", "--expected", type=str, help="Expected values to check")
    args = parser.parse_args()
    args = args.__dict__
    if "objecttype" not in args.keys():
        print("UNKNOWN - The DB objecttype (-o/--objecttype) is required, but was not given")
        exit(3)
    if "key" not in args.keys():
        print("UNKNOWN - The DB key (-k/--key) is required, but was not given")
        exit(3)
    if "expected" not in args.keys():
        print("UNKNOWN - The expected values (-e/--expected) are required, but were not given")
        exit(3)
    source, objecttype, key = args["source"], args["objecttype"], args["key"]
    expected_string = args["expected"]
    expected = []
    for value in expected_string.split("),"):
        elements = value.split(",")
        if len(elements) < 3:
            print("UNKNOWN - The expected results format is wrong, please use the following format:"
                  "<(attribute, [value, ...], match_mode), ...>")
            exit(3)
        else:
            values = []
            for val in elements[1:len(elements)-1]:
                values.append(val.replace("[", "").replace("]", "").lstrip(" "))
            expected.append((elements[0].replace("(", ""), values, elements[len(elements)-1].replace(")", "")))
    return source, objecttype, key, expected


def check_values(res):
    pass


def main():
    src, objtype, key, exp = parse_cli()
    url = f"https://rest.db.ripe.net/{src}/{objtype}/{key}"
    resp = requests.get(url, headers={"Accept": "application/json"})
    resp_dict = json.loads(resp.text)
    check_values(resp_dict)


if __name__ == "__main__":
    main()
