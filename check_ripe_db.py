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
            expected.append((elements[0].replace("(", "").lstrip(" "), values, elements[len(elements)-1].replace(")", "")))
    return source, objecttype, key, expected


def get_attributes(expect):
    attribs = []
    for tup in expect:
        attribs.append(tup[0].upper())
    return attribs


def get_values(current_dict, attributes, val):
    for item in current_dict.items():
        if type(item[1]) == str:
            if item[0] == "name" and item[1].upper() in attributes:
                if item[1] in val.keys():
                    val[item[1]].append(current_dict["value"])
                else:
                    val[item[1]] = [current_dict["value"]]
        else:
            if type(item[1]) == dict:
                get_values(item[1], attributes, val)
            elif type(item[1]) == list:
                for obj in item[1]:
                    if type(obj) == dict:
                        get_values(obj, attributes, val)


def check_values(res, attrs):
    values = {}
    get_values(res, attrs, values)
    # TODO Checks
    return values


def main():
    src, objtype, key, exp = parse_cli()
    url = f"https://rest.db.ripe.net/{src}/{objtype}/{key}"
    resp = requests.get(url, headers={"Accept": "application/json"})
    resp_dict = json.loads(resp.text)
    attrs = get_attributes(exp)
    check_values(resp_dict, attrs)


if __name__ == "__main__":
    main()
