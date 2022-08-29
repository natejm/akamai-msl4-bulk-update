#!/usr/bin/python3

# Author: Nate Whittaker (nwhittak)
"""
Copyright 2020 Akamai Technologies, Inc. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.

You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

This script assumes you have python3 installed on your machine.  If
you don't have it installed on your Mac, it is easily available by
installing it with Brew.  https://brew.sh
"""

### Obtain library from https://github.com/akamai-open/AkamaiOPEN-edgegrid-python
### For remainder libraries, use pip install <module_name>
from akamai.edgegrid import EdgeGridAuth, EdgeRc


### Initialize Requiests (HTTP) object
import requests
### We use this for creating URLs easily
### https://docs.python.org/2/library/urlparse.html
import urllib.parse 
### Import JSON Module --- only used for writing JSON Object into text. http.request contains its own parser
### https://docs.python.org/2/library/json.html
import json
#import jsonpatch
### Import Regular Expression module
### https://docs.python.org/2/library/re.html
import re

import time
from datetime import datetime
import os
### Import csv module
### https://docs.python.org/3/library/csv.html
import csv
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

import ipaddress

import logging
import zipfile
from io import BytesIO
from boto3 import resource
import gzip
import io




##################### DO NOT EDIT BEYOND THIS POINT! ###############################################
def update_stream(ACCOUNT_ID, PATH, SECTION, STREAM_BATCH ):
    ### Base URL obtained after API setup
    print(ACCOUNT_ID, PATH, SECTION, STREAM_BATCH )
    try:
        EDGERC_PATH = (PATH)
        EDGERC = EdgeRc(EDGERC_PATH)
        http_session = requests.Session()
        http_session.auth = EdgeGridAuth.from_edgerc(EDGERC, SECTION)
        baseurl = 'https://{}/'.format(EDGERC.get(SECTION, 'host'))
        headers = { "Accept": "application/json", "Content-Type": "application/json" }

    except Exception as e:
        print(e)
    # recursively goes thru list of STREAM_IDs
    for stream in STREAM_BATCH:
       
        #retrieve STREAM JSON Metadata
        result = http_session.get(urllib.parse.urljoin(baseurl, '/config-media-live/v2/msl-origin/streams/{}?accountSwitchKey={}'.format(stream, ACCOUNT_ID)))
        if result.status_code != 200:
                print("UNABLE to FETCH STREAM",stream,"\n", result.status_code, result.text,"\n")
                
        else:
            stream_config = result.json()
            stream_config_pretty = json.dumps(stream_config, indent=2)
            #print(stream_config_pretty)
            
            #Store relevant Stream config parameters
            ingestOptions = stream_config['ingestOptions']
            format = stream_config['format']
            ingestOverrides = ''
    
            #Define the ingest-override metadata based on type of stream (HLS/CMAF, etc...)
            if format == "HLS":
                ingestOverrides =  json.loads('{"ingestOverrides": "<overrides>\\n<http>\\n<allowed-exts>\\n<hls-meta-exts>m3u8 key</hls-meta-exts>\\n<hls-zip-exts>ts aac adts vtt webvtt ac3 ec3 jpg jpeg</hls-zip-exts>\\n</allowed-exts>\\n</http>\\n</overrides>"}')
            if format == "CMAF":
                ingestOverrides = json.loads('{"ingestOverrides": "<overrides>\\n<http>\\n<allowed-exts>\\n<cmaf-meta-exts>m3u8     mpd</cmaf-meta-exts>\\n<cmaf-zip-exts>cmfv m4s m4v mp4 cmfa m4s m4a mp4 webvtt vtt cmft jpg jpeg</cmaf-zip-exts>\\n</allowed-exts>\\n</http>\\n</overrides>"}')
    
            #print out the existing ingest-override metadata if there's any
            #if 'ingestOverrides' in stream_config['ingestOptions']:
               # print("OLD INGEST: ",ingestOptions,format)
    
            #UPDATE the ingest-override metadata based on type of stream (HLS/CMAF, etc...)
            stream_config['ingestOptions'].update(ingestOverrides)
    
            #Only update the stream config if we matched the proper STREAM Format (HLS/CMAF, etc...)
            if ingestOverrides != '':
                update_result = http_session.put(urllib.parse.urljoin(baseurl, '/config-media-live/v2/msl-origin/streams/{}?accountSwitchKey={}'.format(stream, ACCOUNT_ID)), json=stream_config, headers=headers)
                if update_result.status_code != 202:
                    print("UPDATE ERROR!!! ",update_result.status_code,update_result.text)
                if update_result.status_code == 202:
                    print('{} ({}) Updated Successfully!'.format(stream_config['name'], stream_config['id']))

            else:
                print("No Ingest Metadata Updated")
####################################################################

if __name__ == "__main__" :
    

    try:
        argument = ArgumentParser(prog='stream-create.py', description="This script is to be used to BULK update Advanced Ingest Metdata Tags for MSLV4 Streams.")
        
        argument.add_argument('--switchKey', required=True, help="Account SwitchKey to Update (eg. I-6JHGS")
        
        argument.add_argument('--edgercFile',  default=os.path.expanduser('~')+'/.edgerc', help="NAME of EdgeRC File (default: ~/.edgerc)")
        argument.add_argument('--edgercSection', default='default', help="SECTION of EdgeRC File (default: 'default')")
        argument.add_argument('--streamIds', nargs='+',  required=True, help="STREAM_ID list. Space delimited (Eg. 1234 9876 6634)")
        
        ARGS = argument.parse_args()

  

        update_stream(ARGS.switchKey, ARGS.edgercFile, ARGS.edgercSection, ARGS.streamIds )
    
    except Exception as e:
        print(e)
        exit()
