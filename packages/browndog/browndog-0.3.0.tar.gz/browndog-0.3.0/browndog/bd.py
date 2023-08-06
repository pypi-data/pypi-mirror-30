import json
import sys
import urllib
import requests
import os
import time
import mimetypes
import docker
import numpy
from shutil import move
from os.path import basename

# Global constants
API_VERSION_STR = "/v1"

# Error messages
connection_error_msg = "Failed to establish connection with Brown Dog API Gateway. Please try again later."
timeout_error_msg = "The request timed out. Please try again later."
http_error_msg = "An HTTP error occurred. Please try again later."
invalid_json_error_msg = "Server responded with invalid JSON in response body. Please try again later."
generic_error_msg = "An unknown error occurred. Please try again later."


def get_extracted_metadata(metadata_json_ld, extractor_name):
    """
    Return a block of metadata by extractor name
    @param metadata_json_ld: it's a returned value from extract method
    @param extractor_name: name of extractor. for example,"ncsa.image.ocr"
    @return a dictionary of the block with the extractor name. it contains content, @context, agent, etc. If it can't
    find one with the name, it will return None
    """
    for m in metadata_json_ld['metadata.jsonld']:
        # full uri of the name
        fullname = m['agent']['name']
        if fullname.endswith(extractor_name):
            return m
    return None


def __split_url(url):
    """
    Split URL into BrownDog Fence URL, username, and password
    @param url: URL of the BD API gateway with username and password
    @return Tuple of bds, username, and password
    """
    if '@' in url:
        parts = url.rsplit('@', 1)
        url = parts[1]
        parts = parts[0].split(':')
        username = parts[1].split('//')[1]
        password = parts[2]
        bds = parts[0] + '://' + url
        return bds, username, password
    else:
        return url, '', ''


def get_key(url):
    """
    Get a key from the BD API gateway to access BD services
    @param url: URL of the BD API gateway with username and password
    @return: Tuple of BD API key, HTTP response status code, and HTTP response status reason
    """
    key = status_code = reason = response = None
    # noinspection PyBroadException
    try:
        (bds, username, password) = __split_url(url)
        api_call = bds + API_VERSION_STR + '/keys'
        response = requests.post(api_call, auth=(username, password), headers={'Accept': 'application/json'})
        response.raise_for_status()

        # Get key if response status is ok
        if response.status_code == requests.codes.ok:
            json_result = json.loads(response.text)
            if 'api-key' in json_result:
                key = json_result['api-key']
    except requests.ConnectionError:
        print connection_error_msg
    except requests.Timeout:
        print timeout_error_msg
    except requests.HTTPError:
        print http_error_msg
    except Exception:
        print generic_error_msg
    finally:
        if response is not None:
            status_code = response.status_code
            reason = response.reason
        return key, status_code, reason


def get_token(bds, key):
    """
    Get a token for a specific key from the BD API gateway to access BD services.
    @param bds: The URL to the Brown Dog server to use.
    @param key: BD API key
    @return: Tuple of BD API token, HTTP response status code, and HTTP response status reason
    """
    token = status_code = reason = response = None
    # noinspection PyBroadException
    try:
        api_call = bds + API_VERSION_STR + '/keys/' + key + '/tokens'
        response = requests.post(api_call, headers={'Accept': 'application/json'})
        response.raise_for_status()

        # Get token if response status is ok
        if response.status_code == requests.codes.ok:
            json_result = json.loads(response.text)
            if 'token' in json_result:
                token = json_result['token']
    except requests.ConnectionError:
        print connection_error_msg
    except requests.Timeout:
        print timeout_error_msg
    except requests.HTTPError:
        print http_error_msg
    except Exception as e:
        print generic_error_msg + " " + e.message
    finally:
        if response is not None:
            status_code = response.status_code
            reason = response.reason
        return token, status_code, reason


def check_token_validity(bds, token):
    """
    Check token validity using BD API and return the result in JSON format.
    @param bds: The URL to the Brown Dog server to use.
    @param token: BD API token
    @return: Tuple of JSON formatted result of checking token validity (e.g. {"found": "true", "ttl": 63858}), if the request
    succeeds (None, in all other cases), HTTP response status code, and HTTP response status reason
    """
    status_code = reason = response = json_content = None
    # noinspection PyBroadException
    try:
        api_call = bds + API_VERSION_STR + '/tokens/' + token
        response = requests.get(api_call, headers={'Accept': 'application/json'})

        # Get JSON response if status is ok
        if response.status_code == requests.codes.ok:
            json_content = response.json()
    except requests.ConnectionError:
        print connection_error_msg
    except requests.Timeout:
        print timeout_error_msg
    except requests.HTTPError:
        print http_error_msg
    except ValueError:
        print invalid_json_error_msg
    except Exception as e:
        print generic_error_msg + " " + e.message
    finally:
        if response is not None:
            status_code = response.status_code
            reason = response.reason
        return json_content, status_code, reason


def outputs(bds, input_format, token):
    """
    Check Brown Dog Service for available output formats for the given input format.
    @param bds: The URL to the Brown Dog server to use.
    @param input_format: The format of the input file.
    @param token: Brown Dog access token
    @return: Tuple of string array of reachable output format extensions, HTTP response status code, and HTTP response
    status reason
    """
    status_code = reason = response = None
    output_array = []

    # noinspection PyBroadException
    try:
        api_call = bds + API_VERSION_STR + '/conversions/inputs/' + input_format
        response = requests.get(api_call, headers={'Accept': 'text/plain', 'Authorization': token})

        # Get string array of reachable output format extensions if response status is ok
        if response.status_code == requests.codes.ok:
            output_array = response.text.strip().split()
    except requests.ConnectionError:
        print connection_error_msg
    except requests.Timeout:
        print timeout_error_msg
    except requests.HTTPError:
        print http_error_msg
    except Exception as e:
        print generic_error_msg + " " + e.message
    finally:
        if response is not None:
            status_code = response.status_code
            reason = response.reason
        return output_array, status_code, reason


def convert(bds, input_filename, output, output_path, token, wait=60, verbose=False, download=True):
    """
    Convert file using Brown Dog Service.
    @param bds: The URL to the Brown Dog Server to use.
    @param input_filename: The input filename.
    @param output: The output format extension.
    @param output_path: The path for the created output file.  May contain a different filename here as well.
    @param token: Brown Dog access token
    @param wait: The amount of time to wait for the DAP service to respond.  Default is 60 seconds.
    @param verbose: Set to true if verbose output should be generated.  Default is False.
    @param download: Set to true if download the converted file to local
    @return: Tuple of output filename if download is set to True (converted file URL if download is set to
    False), HTTP response status code, and HTTP response status reason
    """
    output_filename = None
    result = None
    boundary = 'browndog-fence-header'
    status_code = reason = response = None

    # Check for authentication
    (bds, username, password) = __split_url(bds)

    # noinspection PyBroadException
    try:
        if input_filename.startswith('http://') or input_filename.startswith('https://'):
            api_call = bds + API_VERSION_STR + '/conversions/' + output + '/' + urllib.quote_plus(input_filename)
            response = requests.get(api_call,
                                    headers={'Accept': 'text/plain', 'Authorization': token}, allow_redirects=False)

            # Handling temporary redirect
            if response.status_code == requests.codes.temporary_redirect:
                response = requests.get(response.headers['Location'], headers=response.request.headers)

            if response.status_code == requests.codes.ok:
                result = response.text
        else:
            api_call = bds + API_VERSION_STR + '/conversions/' + output + '/'
            files = [('file', (input_filename, mimetypes.guess_type(input_filename)[0] or 'application/octet-stream'))]
            response = requests.post(api_call, headers={'Accept': 'text/plain', 'Authorization': token,
                                                        'Content-Type': 'multipart/form-data; boundary=' + boundary},
                                     data=multipart([], files, boundary, 5 * 1024 * 1024), allow_redirects=False)
            # Handling temporary redirect
            if response.status_code == requests.codes.temporary_redirect:
                response = requests.post(response.headers['Location'], headers=response.request.headers,
                                         data=multipart([], files, boundary, 5 * 1024 * 1024))

            if response.status_code == requests.codes.ok:
                result = response.text

        if result is not None:
            if basename(output_path):
                output_filename = output_path
            else:
                output_filename = output_path + basename(result)

            if verbose:
                print output_filename

            if download:
                download_file(result, output_filename, token, wait)
    except requests.ConnectionError:
        print connection_error_msg
    except requests.Timeout:
        print timeout_error_msg
    except requests.HTTPError:
        print http_error_msg
    except Exception as e:
        print generic_error_msg + " " + e.message
    finally:
        if response is not None:
            status_code = response.status_code
            reason = response.reason
        if download:
            return output_filename, status_code, reason
        else:
            return result, status_code, reason


def convert_local(bds, input_filename, output, output_path, token, docker_machine, wait=60, verbose=False):
    """
    Convert file using Brown Dog Service.
    @param bds: The URL to the Brown Dog Server to use.
    @param input_filename: The input filename.
    @param output: The output format extension.
    @param output_path: The path for the created output file.  May contain a different filename here as well.
    @param token: Brown Dog access token
    @param wait: The amount of time to wait for the DAP service to respond.  Default is 60 seconds.
    @param verbose: Set to true if verbose output should be generated.  Default is False.
    @return: Tuple of output file path, HTTP response status code, and HTTP response status reason
    """
    result = ''
    docker_base_name = 'ncsapolyglot/'
    conversion_path = []
    intermediate_files = []
    local_dir = None
    intermediate_output_filename = ""
    status_code = reason = response = output_filepath = None

    # Check for authentication
    (bds, username, password) = __split_url(bds)

    # Get input format
    input_format = os.path.splitext(input_filename)[1].split('.')[1]

    # noinspection PyBroadException
    try:

        api_call = bds + API_VERSION_STR + '/conversions/path/' + output + '/' + input_format
        response = requests.get(api_call, headers={'Accept': 'text/plain', 'Authorization': token})

        if response.status_code == requests.codes.ok:
            conversion_path = json.loads(response.text)

        # Get docker client
        docker_client = docker.Client(version='auto', **docker_machine.config(machine='default'))

        mount_dir = "/home/polyglot/data"

        # Setting intermediate input file name for chained conversions
        chain_count = 0

        # Get local directory and filename
        (local_dir, local_filename) = os.path.split(os.path.abspath(input_filename))

        for converter_info in conversion_path:

            # Read details about converter
            application = str(converter_info["application"])
            intermediate_output = str(converter_info["output"])
            docker_image_name = docker_base_name + "converters-" + application.lower()

            # Pull docker image if not existing locally
            status_messages = docker_client.pull(docker_image_name, tag="latest")
            if verbose:
                print status_messages

            # From second iteration onwards use output filename of the previous step as input filename of the next step
            if chain_count > 0:
                local_filename = intermediate_output_filename

            # Intermediate output filename
            intermediate_output_filename = os.path.splitext(local_filename)[0] + "." + intermediate_output

            # Create container
            docker_container = docker_client.create_container(
                user="root",
                image=docker_image_name,
                stdin_open=True,
                tty=True,
                environment={
                    "LOCAL_PROCESSING": "True",
                    "INPUT_FILE_PATH": os.path.join(mount_dir, local_filename),
                    "OUTPUT_FORMAT": intermediate_output,
                    "OPERATION": "convert",
                    "APPLICATION": application
                },
                volumes=[mount_dir],
                host_config=docker_client.create_host_config(binds=[local_dir + ":" + mount_dir])
            )

            # Store docker container ID
            docker_container_id = docker_container.get("Id")

            # Start docker container
            response = docker_client.start(container=docker_container_id)

            # Get Logs
            logs = docker_client.logs(container=docker_container_id, stdout=True, timestamps=True, stream=True)
            if verbose:
                for character in logs:
                    sys.stdout.write(character)

            # Wait for container to stop
            docker_client.wait(container=docker_container_id)

            # Remove docker container
            docker_client.remove_container(container=docker_container_id)

            # Save intermediate file names for later use
            if os.path.isfile(os.path.join(local_dir, intermediate_output_filename)):
                intermediate_files.append(intermediate_output_filename)

            chain_count += 1

        # move all intermediate files and output files to current working directory
        for file_name in intermediate_files:
            move(os.path.join(local_dir, file_name), os.path.join(os.getcwd(), file_name))

        if os.path.isfile(intermediate_output_filename):
            if basename(output_path):
                output_filename = output_path
            else:
                output_filename = output_path + basename(result)

            if verbose:
                print output_filename

    except requests.ConnectionError:
        print connection_error_msg
    except requests.Timeout:
        print timeout_error_msg
    except requests.HTTPError:
        print http_error_msg
    except Exception as e:
        print generic_error_msg + " " + e.message
    finally:
        if response is not None:
            status_code = response.status_code
            reason = response.reason

        if local_dir is not None and intermediate_output_filename is not None:
            output_filepath = os.path.join(local_dir, intermediate_output_filename)

        return output_filepath, status_code, reason


def download_file(url, filename, token, wait=60):
    """
    Download file at given URL.
    @param url: The URL of the file to download.
    @param filename: An optional new filename for the downloaded file.  Set to '' if the current filename on the URL is
    to be used.
    @param token: Brown Dog access token
    @param wait: The amount of time in seconds to wait for the file to download.  Default is 60 seconds.
    @return: Tuple of the downloaded filename, HTTP response status code, and HTTP response status reason
    """
    status_code = reason = response = None

    if not filename:
        filename = url.split('/')[-1]

    # noinspection PyBroadException
    try:
        response = requests.get(url, headers={'Authorization': token}, stream=True)

        while wait > 0 and response.status_code == requests.codes.not_found:
            time.sleep(1)
            wait -= 1
            response = requests.get(url, headers={'Authorization': token}, stream=True)

        if response.status_code == requests.codes.ok:
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:  # Filter out keep-alive new chunks
                        f.write(chunk)
                        f.flush()
    except requests.ConnectionError:
        print connection_error_msg
    except requests.Timeout:
        print timeout_error_msg
    except requests.HTTPError:
        print http_error_msg
    except Exception as e:
        print generic_error_msg + " " + e.message
    finally:
        if response is not None:
            status_code = response.status_code
            reason = response.reason

        return filename, status_code, reason


def extractors(bds, input_format, token):
    """
    Check Brown Dog Service for available extractions for the given input format.
    @param bds: The URL to the Brown Dog server to use.
    @param input_format: The format of the input file (not currently used!).
    @param token: Brown Dog access token
    @return: Tuple of the comma-separated string of available extractions, HTTP response status code, and HTTP response
    status reason.
    """
    output_string = status_code = reason = response = None

    (bds, username, password) = __split_url(bds)

    # noinspection PyBroadException
    try:

        # Get list of extractors
        api_call = bds + API_VERSION_STR + '/extractors/running'
        response = requests.get(api_call, headers={'Accept': 'application/json', 'Authorization': token})

        # Get string of extractions if response status is ok
        if response.status_code == requests.codes.ok:
            output_string = ', '.join(response.json()['Extractors'])
    except requests.ConnectionError:
        print connection_error_msg
    except requests.Timeout:
        print timeout_error_msg
    except requests.HTTPError:
        print http_error_msg
    except Exception as e:
        print generic_error_msg + " " + e.message
    finally:
        if response is not None:
            status_code = response.status_code
            reason = response.reason

        return output_string, status_code, reason


def extract(bds, input_filepath, token, wait=60):
    """
    Extract derived data from the given input file's contents via Brown Dog Service (BDS).
    @param bds: The URL to the Brown Dog Service to use.
    @param input_filepath: The input file.
    @param token: Brown Dog Service access token
    @param wait: The amount of time to wait for the DTS to respond.  Default is 60 seconds.
    @return: Tuple of the filename of the JSON file containing the extracted data, HTTP response status code, and HTTP
    response status reason
    """
    metadata = file_id = status_code = reason = response = None
    boundary = 'browndog-fence-header'

    # Check for authentication
    (bds, username, password) = __split_url(bds)

    # noinspection PyBroadException
    try:

        # If the filepath is a URL
        if input_filepath.startswith('http://') or input_filepath.startswith('https://'):
            data = json.dumps({"fileurl": input_filepath})
            api_call = bds + API_VERSION_STR + '/extractions/url'
            response = requests.post(api_call,
                                     headers={
                                         'Content-Type': 'application/json',
                                         'Accept': 'application/json',
                                         'Authorization': token},
                                     data=data, allow_redirects=False)
            # Handling temporary redirect
            if response.status_code == requests.codes.temporary_redirect:
                response = requests.post(response.headers['Location'], headers=response.request.headers, data=data)

            if response.status_code == requests.codes.ok:
                file_id = response.json()['id']
        else:
            files = [('File', (input_filepath, mimetypes.guess_type(input_filepath)[0] or 'application/octet-stream'))]
            api_call = bds + API_VERSION_STR + '/extractions/file'
            response = requests.post(api_call,
                                     headers={'Accept': 'application/json',
                                              'Authorization': token,
                                              'Content-Type': 'multipart/form-data; boundary=' + boundary},
                                     data=multipart([], files, boundary, 5 * 1024 * 1024), allow_redirects=False)
            # Handling temporary redirect
            if response.status_code == requests.codes.temporary_redirect:
                response = requests.post(response.headers['Location'], headers=response.request.headers,
                                         data=multipart([], files, boundary, 5 * 1024 * 1024))

            if response.status_code == requests.codes.ok:
                file_id = response.json()['id']

        # Poll until output is ready
        if file_id:
            while wait > 0:
                api_call = bds + API_VERSION_STR + '/extractions/' + file_id + '/status'
                status = requests.get(api_call, headers={'Accept': 'application/json', 'Authorization': token}).json()
                if status['Status'] == 'Done':
                    break
                time.sleep(1)
                wait -= 1

            # Get extracted content (TODO: needs to be one endpoint!!!)
            # TODO: At present only the deprecated endpoint is supported via Fence. Need to investigate about this.
            api_call = bds + '/dts/api/files/' + file_id + '/tags'
            tag_response = requests.get(api_call, headers={'Accept': 'application/json', 'Authorization': token})
            if tag_response.status_code == requests.codes.ok:
                metadata = tag_response.json()

            api_call = bds + API_VERSION_STR + '/extractions/files/' + file_id + '/metadata.jsonld'
            jsonld_metadata_response = requests.get(api_call,
                                                    headers={'Accept': 'application/json', 'Authorization': token})
            if jsonld_metadata_response.status_code == requests.codes.ok:
                metadata['metadata.jsonld'] = jsonld_metadata_response.json()

            # TODO: At present only the deprecated endpoint is supported via Fence. Need to investigate about this.
            api_call = bds + '/dts/api/files/' + file_id + '/versus_metadata'
            versus_metadata_response = requests.get(api_call,
                                                    headers={'Accept': 'application/json', 'Authorization': token})
            if versus_metadata_response.status_code == requests.codes.ok:
                metadata['versusmetadata'] = versus_metadata_response.json()

    except requests.ConnectionError:
        print connection_error_msg
    except requests.Timeout:
        print timeout_error_msg
    except requests.HTTPError:
        print http_error_msg
    except Exception as e:
        print generic_error_msg + " " + e.message
    finally:
        if response is not None:
            status_code = response.status_code
            reason = response.reason

        return metadata, status_code, reason


def extract_local(bds, input_filename, token, docker_machine, wait=60, verbose=False):
    """
    Extract derived data from the given input file's contents via Brown Dog Service (BDS).
    @param bds: The URL to the Brown Dog Service to use.
    @param input_filename: The input file.
    @param token: Brown Dog Service access token
    @param wait: The amount of time to wait for the DTS to respond.  Default is 60 seconds.
    @return: Tuple of extracted metadata array, HTTP response status code, and HTTP response status reason
    """
    metadata = []
    docker_images = []
    status_code = reason = response = None

    # Check for authentication
    (bds, username, password) = __split_url(bds)

    # noinspection PyBroadException
    try:

        # Get MIME type of file
        mime_type, encoding = mimetypes.guess_type(input_filename)

        # MIME type could not be obtained
        if mime_type is None:
            print "Mime type of local file could not be decoded"
        # MIME type has been obtained
        else:
            # Get details about extractors running at that moment
            api_call = bds + API_VERSION_STR + '/extractors?file_type=' + mime_type
            running_extractors = requests.get(api_call,
                                              headers={'Accept': 'application/json', 'Authorization': token}).json()

            # Iterate through the available extractors
            for extractor in running_extractors:

                # Get the docker image name for the extractor in consideration
                docker_image_name = extractor['docker_repo']

                # Continue only if docker image name is set
                if docker_image_name is not None and docker_image_name is not "":

                    docker_images.append(docker_image_name)

                    # Get docker client
                    docker_client = docker.Client(version='auto', **docker_machine.config(machine='default'))

                    # Pull docker image
                    status_messages = docker_client.pull(docker_image_name, tag="latest")
                    if verbose:
                        print status_messages

                    # Get local directory and filename
                    (local_dir, local_filename) = os.path.split(os.path.abspath(input_filename))
                    ext = os.path.splitext(local_filename)[1]

                    # Output filename
                    output_filename = os.path.splitext(local_filename)[0] + "." + extractor['extractor_name'] + ".json"

                    # Create container
                    mount_dir = "/home/clowder/data"
                    docker_container = docker_client.create_container(
                        user="root",
                        image=docker_image_name,
                        stdin_open=True,
                        tty=True,
                        environment={
                            "LOCAL_PROCESSING": "True",
                            "INPUT_FILE_PATH": os.path.join(mount_dir, local_filename),
                            "OUTPUT_FILE_PATH": os.path.join(mount_dir, output_filename)},
                        volumes=[mount_dir],
                        host_config=docker_client.create_host_config(binds=[local_dir + ":" + mount_dir])
                    )
                    docker_container_id = docker_container.get("Id")

                    # Start docker container
                    response = docker_client.start(container=docker_container_id)

                    # Get Logs
                    logs = docker_client.logs(container=docker_container_id, stdout=True, timestamps=True, stream=True)
                    if verbose:
                        for character in logs:
                            sys.stdout.write(character)

                    # Kill container
                    docker_client.stop(container=docker_container_id)

                    # Remove docker container
                    docker_client.remove_container(container=docker_container_id)

                    # Read JSON metadata content for the extractor, add it to metadata array, and remove extractor
                    # metadata file
                    output_filepath = os.path.join(local_dir, output_filename)
                    if os.path.isfile(output_filepath):
                        with open(output_filepath, 'r') as json_file:
                            metadata.append(json.load(json_file))
                        os.remove(output_filepath)
    except requests.ConnectionError:
        print connection_error_msg
    except requests.Timeout:
        print timeout_error_msg
    except requests.HTTPError:
        print http_error_msg
    except Exception as e:
        print generic_error_msg + " " + e.message
    finally:
        if response is not None:
            status_code = response.status_code
            reason = response.reason

        return metadata, status_code, reason


def index(bds, directory, token, wait=60, verbose=False):
    """
    Extract signatures/tags from files via the Brown Dog Service in order to index their contents.
    @param bds: The URL to the Data Tilling Service to use.
    @param directory: The directory of files to index.
    @param token: Brown Dog Service access token
    @param wait: The amount of time per file to wait for the DTS to respond. Default is 60 seconds.
    @param verbose: Set to true if verbose output should be generated.  Default is False.
    @return: Tuple of the output filename containing the indexed data, HTTP response status code, and HTTP response
    status reason
    """
    output_filename = status_code = reason = None

    # noinspection PyBroadException
    try:

        if not directory.endswith('/'):
            directory += '/'

        output_filename = directory + '.index.tsv'

        with open(output_filename, 'w') as f:
            for filename in os.listdir(directory):
                if not filename[0] == '.':
                    if verbose:
                        print filename

                    metadata, status_code, reason = extract(bds, directory + filename, token, wait)

                    # Write to index file
                    line = filename

                    for i in range(len(metadata['versusmetadata'])):
                        line += '\t' + str(metadata['versusmetadata'][i]['descriptor'])

                    for i in range(len(metadata['tags'])):
                        line += '\t["' + str(metadata['tags'][i]) + '"]'

                    f.write(line + '\n')

    except Exception as e:
        print generic_error_msg + " " + e.message
    finally:
        return output_filename, status_code, reason


def find(bds, query_filename, token, wait=60):
    """
    Search a directory for similar files to the query. Directory must be indexed already and a '.index.tsv' present.
    @param bds: The URL to the Brown Dog Service to use.
    @param query_filename: The query file.
    @param token: Brown Dog Service access token
    @param wait: The amount of time per file to wait for the DTS to respond. Default is 60 seconds.
    @return: Tuple of the search results with similarity scores, HTTP response status code, and HTTP response status
    reason
    """
    ranking = {}
    status_code = reason = None

    # noinspection PyBroadException
    try:

        # Extract signature from query file
        metadata, status_code, reason = extract(bds, query_filename, token, wait)

        query_descriptors = []

        for i in range(len(metadata['versusmetadata'])):
            query_descriptors.append(metadata['versusmetadata'][i]['descriptor'])

        for i in range(len(metadata['tags'])):
            tmp = [metadata['tags'][i]]
            query_descriptors.append(tmp)

            # Search index
        with open('.index.tsv') as index_file:
            for line in index_file.readlines():
                parts = line.split('\t')
                filename = parts[0].strip()
                descriptors = []

                for descriptor in parts[1:]:
                    descriptors.append(json.loads(descriptor.strip()))

                distance = descriptor_set_distance(query_descriptors, descriptors)

                ranking[filename] = distance

    except Exception as e:
        print generic_error_msg + " " + e.message
    finally:
        return ranking, status_code, reason


def descriptor_set_distance(descriptor_set1, descriptor_set2):
    """
    Calculate the closest distance between the two sets of descriptors.
    @param descriptor_set1: A set of descriptors for a file
    @param descriptor_set2: A set of descriptors for another file
    @return: The distance between the closest two descriptors in each set.
    """
    d = numpy.float('inf')

    for i in range(len(descriptor_set1)):
        for j in range(len(descriptor_set2)):
            dij = descriptor_distance(descriptor_set1[i], descriptor_set2[j])

            if dij < d:
                d = dij

    return d


def descriptor_distance(descriptor1, descriptor2):
    """
    Return the distance between the two descriptors.
    @param descriptor1: A content descriptor for a file.
    @param descriptor2: A content descriptor for another file.
    @return: The distance between the two descriptors.
    """
    # Check if exactly the same
    if json.dumps(descriptor1) == json.dumps(descriptor2):
        return 0

        # Compare lists of stuff
    if isinstance(descriptor1, list) and isinstance(descriptor2, list):
        descriptor1 = numpy.array(descriptor1)
        descriptor2 = numpy.array(descriptor2)
        dimensions = len(descriptor1.shape)

        # Get distance between arrays of numbers
        if dimensions == 1 and not isinstance(descriptor1[0], numpy.basestring) and not isinstance(descriptor2[0],
                                                                                                   numpy.basestring):
            return numpy.linalg.norm(descriptor1 - descriptor2)
        elif dimensions == 2 and descriptor1.shape[0] == descriptor2.shape[0]:
            n = descriptor1.shape[0]
            d = 0

            for i in range(n):
                d += numpy.linalg.norm(descriptor1[i] - descriptor2[i])

            d /= n

            return d
        else:
            return numpy.float('inf')
    else:
        return numpy.float('inf')


def multipart(data, files, boundary, blocksize=1024 * 1024):
    """Creates appropriate body to send with requests.

    The body that is generated will be transferred as chunked data. This assumes the
    following is added to headers: 'Content-Type': 'multipart/form-data; boundary=' + boundary

    Only the actual filedata is chunked, the values in the data is send as is.

    :param data: (key, val) pairs that are send as form data
    :param files:  (key, file) or (key, (file, content-type)) pairs that will be send
    :param boundary: the boundary marker
    :param blocksize: the size of the chunks to send (1MB by default)
    :return:
    """

    # send actual form data
    for tup in data:
        tup_key, tup_value = tup
        yield '--%s\r\n' \
              'Content-Disposition: form-data; name="%s"\r\n\r\n' % (boundary, tup_key)
        yield tup_value
        yield '\r\n'

    # send the files
    for tup in files:
        (tup_key, tup_value) = tup
        if isinstance(tup_value, tuple):
            real_file, content_type = tup_value
            filename = os.path.basename(real_file)
        else:
            real_file = tup_value
            filename = os.path.basename(real_file)
            content_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        with open(real_file, 'rb') as fd:
            yield '--%s\r\n' \
                  'Content-Disposition: form-data; name="%s"; filename="%s"\r\n' \
                  'Content-Type: %s\r\n\r\n' % (boundary, tup_key, filename, content_type)
            while True:
                data = fd.read(blocksize)
                if not data:
                    break
                yield data
        yield '\r\n'
    yield '--%s--\r\n' % boundary
