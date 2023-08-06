from collections import OrderedDict
import json
import logging
import os
try:
    import urllib.parse as urlparse
except ImportError:
    import urlparse

from humanfriendly import format_size, parse_size
import requests


MAX_FILE_DEFAULT = parse_size('128m')
OH_BASE_URL = os.getenv('OHAPI_OH_BASE_URL', 'https://www.openhumans.org/')


class SettingsError(Exception):
    pass


def oauth2_auth_url(redirect_uri=None, client_id=None, base_url=OH_BASE_URL):
    """
    Returns an OAuth2 authorization URL for a project, given Client ID. This
    function constructs an authorization URL for a user to follow.
    The user will be redirected to Authorize Open Humans data for our external
    application. An OAuth2 project on Open Humans is required for this to
    properly work. To learn more about Open Humans OAuth2 projects, go to:
    https://www.openhumans.org/direct-sharing/oauth2-features/

    :param redirect_uri: This field is set to `None` by default. However, if
        provided, it appends it in the URL returned.
    :param client_id: This field is also set to `None` by default however,
        is a mandatory field for the final URL to work. It uniquely identifies
        a given OAuth2 project.
    :param base_url: It is this URL `https://www.openhumans.org`.
    """
    if not client_id:
        client_id = os.getenv('OHAPI_CLIENT_ID')
        if not client_id:
            raise SettingsError(
                "Client ID not provided! Provide client_id as a parameter, "
                "or set OHAPI_CLIENT_ID in your environment.")
    params = OrderedDict([
        ('client_id', client_id),
        ('response_type', 'code'),
    ])
    if redirect_uri:
        params['redirect_uri'] = redirect_uri

    auth_url = urlparse.urljoin(
        base_url, '/direct-sharing/projects/oauth2/authorize/?{}'.format(
            urlparse.urlencode(params)))

    return auth_url


def oauth2_token_exchange(client_id, client_secret, redirect_uri,
                          base_url=OH_BASE_URL, code=None, refresh_token=None):
    """
    Exchange code or refresh token for a new token and refresh token. For the
    first time when a project is created, code is required to generate refresh
    token. Once the refresh token is obtained, it can be used later on for
    obtaining new access token and refresh token. The user must store the
    refresh token to obtain the new access token. For more details visit:
    https://www.openhumans.org/direct-sharing/oauth2-setup/#setup-oauth2-authorization

    :param client_id: This field is the client id of user.
    :param client_secret: This field is the client secret of user.
    :param redirect_uri: This is the user redirect uri.
    :param base_url: It is this URL `https://www.openhumans.org`
    :param code: This field is used to obtain access_token for the first time.
        It's default value is none.
    :param refresh_token: This field is used to obtain a new access_token when
        the token expires.
    """
    if not (code or refresh_token) or (code and refresh_token):
        raise ValueError("Either code or refresh_token must be specified.")
    if code:
        data = {
            'grant_type': 'authorization_code',
            'redirect_uri': redirect_uri,
            'code': code,
        }
    elif refresh_token:
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
        }
    token_url = urlparse.urljoin(base_url, '/oauth2/token/')
    req = requests.post(
        token_url, data=data,
        auth=requests.auth.HTTPBasicAuth(client_id, client_secret))
    handle_error(req, 200)
    data = req.json()
    return data


def get_page(url):
    """
    Get a single page of results.

    :param url: This field is the url from which data will be requested.
    """
    response = requests.get(url)
    handle_error(response, 200)
    data = response.json()
    return data


def get_all_results(starting_page):
    """
    Given starting API query for Open Humans, iterate to get all results.

    :param starting page: This field is the first page, starting from which
        results will be obtained.
    """
    logging.info('Retrieving all results for {}'.format(starting_page))
    page = starting_page
    results = []

    while True:
        logging.debug('Getting data from: {}'.format(page))
        data = get_page(page)
        logging.debug('JSON data: {}'.format(data))
        results = results + data['results']

        if data['next']:
            page = data['next']
        else:
            break

    return results


def exchange_oauth2_member(access_token, base_url=OH_BASE_URL):
    """
    Returns data for a specific user, including shared data files.

    :param access_token: This field is the user specific access_token.
    :param base_url: It is this URL `https://www.openhumans.org`.
    """
    url = urlparse.urljoin(
        base_url,
        '/api/direct-sharing/project/exchange-member/?{}'.format(
            urlparse.urlencode({'access_token': access_token})))
    member_data = get_page(url)
    logging.debug('JSON data: {}'.format(member_data))
    return member_data


def upload_file(target_filepath, metadata, access_token, base_url=OH_BASE_URL,
                remote_file_info=None, project_member_id=None,
                max_bytes=MAX_FILE_DEFAULT):
    """
    Upload a file.To learn more about Open Humans OAuth2 projects, go to:
    https://www.openhumans.org/direct-sharing/oauth2-features/.

    :param target_filepath: This field is the filepath of the file to be
        uploaded
    :param metadata: This field is the metadata associated with the file.
        Description and tags are compulsory fields of metadata.
    :param access_token: This is user specific access token/master token.
    :param base_url: It is this URL `https://www.openhumans.org`.
    :param remote_file_info: This field is for for checking if a file with
        matching name and file size already exists. Its default value is none.
    :param project_member_id: This field is the list of project member id of
        all members of a project. Its default value is None.
    :param max_bytes: This field is the maximum file size a user can upload.
        It's default value is 128m.
    """
    filesize = os.stat(target_filepath).st_size
    if filesize > max_bytes:
        logging.info('Skipping {}, {} > {}'.format(
            target_filepath, format_size(filesize), format_size(max_bytes)))
        raise ValueError("Maximum file size exceeded")

    if remote_file_info:
        if process_info(remote_file_info, filesize, target_filepath) is False:
            return

    url = urlparse.urljoin(
        base_url, '/api/direct-sharing/project/files/upload/?{}'.format(
            urlparse.urlencode({'access_token': access_token})))

    logging.info('Uploading {} ({})'.format(
        target_filepath, format_size(filesize)))

    if not(project_member_id):
        response = exchange_oauth2_member(access_token)
        project_member_id = response['project_member_id']
    r = requests.post(url, files={'data_file': open(target_filepath, 'rb')},
                      data={'project_member_id': project_member_id,
                            'metadata': json.dumps(metadata)})
    handle_error(r, 201)
    logging.info('Upload complete: {}'.format(target_filepath))
    return r


def delete_file(access_token, project_member_id, base_url=OH_BASE_URL,
                file_basename=None, file_id=None, all_files=False):
    """
    Delete project member files by file_basename, file_id, or all_files. To
        learn more about Open Humans OAuth2 projects, go to:
        https://www.openhumans.org/direct-sharing/oauth2-features/.

    :param access_token: This field is user specific access_token.
    :param project_member_id: This field is the project member id of user.
    :param base_url: It is this URL `https://www.openhumans.org`.
    :param file_basename: This field is the name of the file to delete for the
        particular user for the particular project.
    :param file_id: This field is the id of the file to delete for the
        particular user for the particular project.
    :param all_files: This is a boolean field to delete all files for the
        particular user for the particular project.
    """
    url = urlparse.urljoin(
        base_url, '/api/direct-sharing/project/files/delete/?{}'.format(
            urlparse.urlencode({'access_token': access_token})))
    data = {'project_member_id': project_member_id}
    if file_basename and not (file_id or all_files):
        data['file_basename'] = file_basename
    elif file_id and not (file_basename or all_files):
        data['file_id'] = file_id
    elif all_files and not (file_id or file_basename):
        data['all_files'] = True
    else:
        raise ValueError(
            "One (and only one) of the following must be specified: "
            "file_basename, file_id, or all_files is set to True.")
    response = requests.post(url, data=data)
    handle_error(response, 200)
    return response


# Alternate names for the same functions.
def delete_files(*args, **kwargs):
    """
    Alternate name for the :func:`delete_file<ohapi.api.delete_file>`.
    """
    return delete_file(*args, **kwargs)


def message(subject, message, access_token, all_members=False,
            project_member_ids=None, base_url=OH_BASE_URL):
    """
    Send an email to individual users or in bulk. To learn more about Open
    Humans OAuth2 projects, go to:
    https://www.openhumans.org/direct-sharing/oauth2-features/

    :param subject: This field is the subject of the email.
    :param message: This field is the body of the email.
    :param access_token: This is user specific access token/master token.
    :param all_members: This is a boolean field to send email to all members of
        the project.
    :param project_member_ids: This field is the list of project_member_id.
    :param base_url: It is this URL `https://www.openhumans.org`.
    """
    url = urlparse.urljoin(
        base_url, '/api/direct-sharing/project/message/?{}'.format(
            urlparse.urlencode({'access_token': access_token})))
    if not(all_members) and not(project_member_ids):
        response = requests.post(url, data={'subject': subject,
                                            'message': message})
        handle_error(response, 200)
        return response
    elif all_members and project_member_ids:
        raise ValueError(
            "One (and only one) of the following must be specified: "
            "project_members_id or all_members is set to True.")
    else:
        r = requests.post(url, data={'all_members': all_members,
                                     'project_member_ids': project_member_ids,
                                     'subject': subject,
                                     'message': message})
        handle_error(r, 200)
        return r



def exceeds_size(filesize, max_bytes, target_filepath):
    if filesize > max_bytes:
        logging.info('Skipping {}, {} > {}'.format(
            target_filepath, format_size(filesize), format_size(max_bytes)))
        return True
    return False


def process_info(remote_file_info, filesize, target_filepath):
    """
    Helper function for checking if a file with matching name and file_size
    exists.

    :param remote_file_info: This field is for for checking if a file with
        matching name and file size already exists.
    :param filesize: This field is the size of file.
    :param target_filepath: This field is the filepath of the file to be
        checked.
    """
    response = requests.get(remote_file_info['download_url'], stream=True)
    remote_size = int(response.headers['Content-Length'])
    if remote_size == filesize:
        logging.info('Skipping {}, remote exists with matching name and '
                     'file size'.format(target_filepath))
        return False
    return True


def handle_error(r, expected_code):
    """
    Helper function to match reponse of a request to the expected status
    code

    :param r: This field is the response of request.
    :param expected_code: This field is the expected status code for the
        function.
    """
    code = r.status_code
    if code != expected_code:
        info = 'API response status code {}'.format(code)
        if 'detail' in r.json():
            info = info + ": {}".format(r.json()['detail'])
        raise Exception(info)


def upload_aws(target_filepath, metadata, access_token, base_url=OH_BASE_URL,
               remote_file_info=None, project_member_id=None,
               max_bytes=MAX_FILE_DEFAULT):
    if remote_file_info:
        filesize = os.stat(target_filepath).st_size
        if process_info(remote_file_info, filesize, target_filepath) is False:
            return

    url = urlparse.urljoin(
        base_url,
        '/api/direct-sharing/project/files/upload/direct/?{}'.format(
            urlparse.urlencode({'access_token': access_token})))

    if not(project_member_id):
        response = exchange_oauth2_member(access_token)
        project_member_id = response['project_member_id']

    filename = target_filepath.split("/")[-1]

    r = requests.post(url, data={'project_member_id': project_member_id,
                                 'metadata': json.dumps(metadata),
                                 'filename': filename})
    requests.put(url=r.json()['url'],
                 data=open(target_filepath, 'rb'))
    done = urlparse.urljoin(
        base_url,
        '/api/direct-sharing/project/files/upload/complete/?{}'.format(
            urlparse.urlencode({'access_token': access_token})))

    r1 = requests.post(done, data={'project_member_id': project_member_id,
                                   'file_id': r.json()['id']})
    handle_error(r1, 200)
    logging.info('Upload complete: {}'.format(target_filepath))
    return r1
