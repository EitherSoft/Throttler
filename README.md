Request Throttler
=================

Uses Redis for data store.

Create settings for domain:
-------
``` shell
$ curl -X POST http://server.tld:port/delay -d '{"domain": "google.com", "duration": 60, "limit": 100}'
```
Parameters:
```
domain:     domain name
duration:   time interval in seconds
limit:      max request count for `duration` period
```

Get delay for domain
-------
``` shell
$ curl -X GET "http://server.tld:port/delay?domain=google.com&request_time=2.54"
```
Parameters:
```
domain:         domain name
request_time:   last page generation time in seconds
```

Clear domain data
------
``` shell
$ curl -X DELETE "http://server.tld:port/delay?domain=google.com"
```
Parameters:
```
domain:         domain name
```
