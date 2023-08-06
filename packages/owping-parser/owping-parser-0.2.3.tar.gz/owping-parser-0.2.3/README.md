# owping-parser

This module is just parsing the output of owping from https://github.com/perfsonar/owamp/tree/master/owping

# How to use #

```python
parser = owping.Parser(result)
owping_result =parser.parse_owping()
```

where result is the output string of the owping command

parse_owping is returning a OWPingResult

# OWPingResult #
has a from_client and a from_server for the query:
* from_client / from_server
    * sid
    * first
    * last
    * sent
    * lost
    * duplicates
    * jitter
    * hops
    * delay
        * min
        * median
        * max