import argparse
import json
import re
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

    # parse expected values
    matches = re.findall("\([^)(]+\)", expected_string)
    if not matches:
        print("UNKNOWN - The expected results format is wrong")
        exit(3)

    expected = []
    for g in matches:
        m = re.search("\(([^,]+),\s+(SINGLEVALUE|EXACTLIST),\s+([^)]+)", g)
        if not m:
            raise Exception("icinga service variable does not match regex, service cannot be updated")

        if m.group(2) == "SINGLEVALUE":
            values = [m.group(3)]
        else:
            values = m.group(3).strip("[]").split(", ")

        expected.append((m.group(1), [x.strip("\"") for x in values], m.group(2)))

    return source, objecttype, key, expected


def check_single_value(expected, actual, attribute):
    if len(actual) > 1:
        print(
            f"CRITICAL - The DB returned more than one value for \"{attribute}\" => \"SINGLEVALUE\" match mode failed")
        exit(2)
    elif len(expected) > 1:
        print(f"CRITICAL - The expected value for \"{attribute}\" was a list => \"SINGLEVALUE\" match mode failed")
        exit(2)
    elif expected[0].upper() != actual[0].upper():
        print(
            f"CRITICAL - The DB returned a different value for \"{attribute}\" => Expected: {expected}, Actual: {actual}")
        exit(2)


def check_exact_list(expected, actual, attribute):
    if len(expected) != len(actual):
        print(
            f"CRITICAL - The DB returned different values for attribute \"{attribute}\" => Expected: {expected}, Actual: {actual}")
        exit(2)
    expected.sort()
    actual.sort()
    for i in range(len(expected)):
        if expected[i].upper() != actual[i].upper():
            print(
                f"CRITICAL - The DB returned different values for attribute \"{attribute}\" => Expected: {expected}, Actual: {actual}")
            exit(2)


def get_values(current_dict):
    attributes = current_dict["objects"]["object"][0]["attributes"]["attribute"]
    res = {}
    for attr in attributes:
        if attr["name"] not in res:
            res[attr["name"]] = []
        res[attr["name"]].append(attr["value"])
    return res


def check_values(res, expected):
    result = get_values(res)
    for i in range(len(expected)):
        if "EXACTLIST" in expected[i][2]:
            check_exact_list(expected[i][1], result[expected[i][0]], expected[i][0])
        else:
            check_single_value(expected[i][1], result[expected[i][0]], expected[i][0])


def main():
    src, objtype, key, exp = parse_cli()
    url = f"https://rest.db.ripe.net/{src}/{objtype}/{key}"
    resp = requests.get(url, headers={"Accept": "application/json"})
    resp_dict = json.loads(resp.text)
    check_values(resp_dict, exp)
    print("OK - All values from the DB were as expected")
    exit(0)


if __name__ == "__main__":
    main()
