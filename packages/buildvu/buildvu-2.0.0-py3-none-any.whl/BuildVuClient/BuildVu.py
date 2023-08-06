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
import time

try:
    import requests
except ImportError:
    raise Exception("Missing dependency: 'requests'. Install it using 'pip install requests'.")


class BuildVu:

    def __init__(self, url, timeout_length=(10, 30), conversion_timeout=30):
        """
        Constructor, setup the converter details

            Args:
                url (str): The URL of the converter
                timeout_length (int, int): (Optional) A tuple of ints representing the request and
                    response timeouts in seconds respectively
                conversion_timeout (int): (Optional) The maximum length of time (in seconds) to
                    wait for the file to convert before aborting
        """
        self.base_endpoint = url
        self.endpoint = url + '/buildvu'
        self.request_timeout = timeout_length
        self.convert_timeout = conversion_timeout

    def convert(self, input_file_path, output_file_path=None):
        """
        Converts the given file and returns the URL where the output can be previewed online. If the
        output_file_path parameter is also passed in, a copy of the output will be downloaded to the
        specified location.

        Args:
            input_file_path (str): Location of the PDF to convert, i.e 'path/to/input.pdf'
            output_file_path (str): (Optional) The directory the output will be saved in, i.e
                'path/to/output/dir'

        Returns:
            string, the URL where the HTML output can be previewed online
        """
        if not self.base_endpoint:
            raise Exception('Error: Converter has not been setup. Please call setup() before trying to '
                            'convert a file.')

        try:
            uuid = self.__upload(input_file_path)
        except requests.exceptions.RequestException as error:
            raise Exception('Error uploading file: ' + str(error))

        # Check the conversion status once every second until complete or error / timeout
        count = 0
        while True:
            time.sleep(1)

            try:
                r = self.__poll_status(uuid)
            except requests.exceptions.RequestException as error:
                raise Exception('Error checking conversion status: ' + str(error))

            response = json.loads(r.text)

            if response['state'] == 'processed':
                break

            if response['state'] == 'error':
                raise Exception('The server ran into an error converting file, see server logs for '
                                'details.')

            if count > self.convert_timeout:
                raise Exception('Failed: File took longer than ' + str(self.convert_timeout) +
                                'seconds to convert')

            count += 1

        # Download the conversion output
        if output_file_path is not None:
            download_url = self.base_endpoint + '/' + response['downloadPath']
            output_file_path += '/' + os.path.basename(input_file_path[:-3]) + 'zip'

            try:
                self.__download(download_url, output_file_path)
            except requests.exceptions.RequestException as error:
                raise Exception('Error downloading conversion output: ' + str(error))

        return self.base_endpoint + '/' + response['previewPath']

    def __upload(self, input_file_path):
        # Private method for internal use
        # Upload the given file to be converted
        # Return the UUID string associated with conversion
        input_file = open(input_file_path, 'rb')

        try:
            r = requests.post(self.endpoint, files={'file': input_file},
                              timeout=self.request_timeout)
            r.raise_for_status()
        except requests.exceptions.RequestException as error:
            raise Exception(error)

        response = json.loads(r.text)

        if response['uuid'] is None:
            raise Exception('The server ran into an error uploading file, see server logs for details')

        return response['uuid']

    def __poll_status(self, uuid):
        # Private method for internal use
        # Poll converter for status of conversion with given UUID
        # Returns response object
        try:
            r = requests.get(self.endpoint, params={'uuid': uuid}, timeout=self.request_timeout)
            r.raise_for_status()
        except requests.exceptions.RequestException as error:
            raise Exception(error)

        return r

    def __download(self, download_url, output_file_path):
        # Private method for internal use
        # Download the given resource to the given location
        try:
            r = requests.get(download_url, timeout=self.request_timeout)
            r.raise_for_status()
        except requests.exceptions.RequestException as error:
            raise Exception(error)

        if not r.ok:
            raise Exception('Failed: Status code ' + str(r.status_code) + ' for ' + download_url)

        with open(output_file_path, 'wb') as output_file:
            for chunk in r.iter_content(chunk_size=1024):
                output_file.write(chunk)
