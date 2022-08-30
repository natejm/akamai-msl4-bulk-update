# akamai-msl4-bulk-update

This Project is to be used to BULK update Advanced Ingest Metdata Tags for
MSLV4 Streams.

First Please ensure all required Libraries/Dependencies are installed 

```
pip3 install -r dependencies.txt
```

## Other Pre-requisites:

* Provision/Download Akamai API Credentials 
* Configure ~/.edgerc credential file
* Install python3

This script takes four (4) arguments

|Arguments | Description |  Optional / Mandatory |
|-----------|------------|-----------------------|
| --switchKey  | Account SwitchKey to Update (eg. I-6JHGS) |  REQUIRED
| --streamIds  | STREAM_ID list. Space delimited (Eg. 1234 9876 6634) | REQUIRED |
| --edgercFile  | NAME of EdgeRC File (default: ~/.edgerc) | optional |
| --edgercSection  | SECTION of EdgeRC File (default: 'default') | optional |


### Example (only required arguments)
```
python3 stream-update.py --switchKey 1-6JHGX --streamIds 2043270 2033705
```
### Example (all arguments)
```
python3 stream-update.py --switchKey 1-6JHGX --streamIds 2043270 2033705 --edgercFile /User/Joe/.edgerc --edgercSection mslv4
```

