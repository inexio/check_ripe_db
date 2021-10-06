# check_ripe_db
Monitoring check plugin that queries the RIPE database and checks whether its results match the expectations.

### Usage
Possible options:  

|                          Option                                 |         Description        |      required?      |            
|-----------------------------------------------------------------|----------------------------|---------------------|
| -h                                                              | Help                       | no                  |
| -s/--source <DB source>:                                        | The DB source to query     | no (default: ripe)  |
| -o/--objecttype <DB objecttype>                                 | The DB objecttype to query | yes                 |
| -k/--key <DB search key>                                        | The DB key to query        | yes                 |
| -e/--expected "<(attribute, match_mode, [value, value2]), ...>" | The expected attributes    | yes                 |

There are three different match modes for the expected values:
    
    1. SINGLEVALUE: The expected value has to match the resulting value
    2. EXACTLIST:   The expacted values must exactly match the resulting values list

A possible usage could look like this:

```shell
python check_ripe_db.py -s "ripe" -o "aut-num" -k "as27856" -e "(status, SINGLEVALUE, Assigned), (source, EXACTLIST, [Filtered, Assigned])"
```

### Dependencies

The plugin only needs the requests library to run. The library can be installed by running:

```shell
python -m pip install requests
```
