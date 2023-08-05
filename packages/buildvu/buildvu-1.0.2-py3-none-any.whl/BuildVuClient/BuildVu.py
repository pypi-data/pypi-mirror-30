"""
Copyright 2018 IDRsolutions

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.

You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Main class used to interact with the buildvu web app
For detailed usage instructions, see the GitHub repository:
    https://github.com/idrsolutions/buildvu-python-client
"""
import json
import os
import sys
import time

try:
    import requests
except ImportError:
    sys.exit("Missing dependency: 'requests'. Install it using 'pip install requests'.")

base_endpoint = None
endpoint = None
request_timeout = None
convert_timeout = None


def setup(url, timeout_length=(10, 30), conversion_timeout=30):
    """
    Initialise the converter

        Args:
            url (str): The URL of the converter
            timeout_length (int, int): A tuple of ints representing the request and
                response timeouts in seconds respectively
            conversion_timeout (int): The maximum length of time (in seconds) to wait for the file to
                convert before aborting
    """
    global base_endpoint
    global endpoint
    global request_timeout
    global convert_timeout
    base_endpoint = url
    endpoint = url + '/buildvu'
    request_timeout = timeout_length
    convert_timeout = conversion_timeout


def convert(input_file_path, output_file_path):
    """
    Convert a PDF file to html

    Args:
        input_file_path (str): Location of the PDF to convert, i.e 'path/to/input.pdf'
        output_file_path (str): The directory the output will be saved in, i.e
            'path/to/output/dir'

    Returns:
        boolean, true if conversion was successful, false otherwise
    """
    if not base_endpoint:
        print('Converter has not been setup')
        return False

    # Upload the file
    try:
        uuid = __upload(input_file_path)
    except requests.exceptions.RequestException as error:
        print(error)
        return False

    # Check the conversion status once every second until complete or timeout
    count = 0
    while True:
        count += 1
        time.sleep(1)

        try:
            r = __poll_status(uuid)
        except requests.exceptions.RequestException as error:
            print(error)
            return False

        response = json.loads(r.text)

        if response['state'] == 'processed' or response['state'] == 'error':
            break

        if count > convert_timeout:
            print('Failed: File took longer than ' + str(convert_timeout) + ' seconds to convert')
            return False

    # Download the conversion output
    download_url = base_endpoint + '/' + response['downloadPath']
    output_file_path += '/' + os.path.basename(input_file_path[:-3]) + 'zip'

    try:
        success = __download(download_url, output_file_path)
    except requests.exceptions.RequestException as error:
        print(error)
        return False

    return success


def __upload(input_file_path):
    # Private method for internal use
    # Upload the given file to be converted
    # Return the UUID string associated with conversion
    input_file = open(input_file_path, 'rb')

    try:
        r = requests.post(endpoint, files={'file': input_file}, timeout=request_timeout)
        r.raise_for_status()
    except requests.exceptions.RequestException as error:
        print(error)
        raise

    response = json.loads(r.text)

    return response['uuid']


def __poll_status(uuid):
    # Private method for internal use
    # Poll converter for status of conversion with given UUID
    # Returns response object
    try:
        r = requests.get(endpoint, params={'uuid': uuid}, timeout=request_timeout)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(e)
        raise

    return r


def __download(download_url, output_file_path):
    # Private method for internal use
    # Download the given resource to the given location
    # Return true if successful, otherwise false
    try:
        r = requests.get(download_url, timeout=request_timeout)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(e)
        return False

    if not r.ok:
        print('Failed: Status code ' + str(r.status_code) + ' for ' + download_url)
        return False

    with open(output_file_path, 'wb') as output_file:
        for chunk in r.iter_content(chunk_size=1024):
            output_file.write(chunk)
    return True
