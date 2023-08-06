from __future__ import unicode_literals, print_function

import logging

from qordoba.project import ProjectAPI, PageStatus
from qordoba.languages import get_source_language, init_language_storage, get_destination_languages

log = logging.getLogger('qordoba')


"""
The add feature enables developers to upload single keys to project files

"""


def filelist(curdir, config,file_name):
    api = ProjectAPI (config)
    project = api.get_project ()
    lang = next(get_destination_languages(project))
    remote_file_pages = list (api.page_search(language_id=lang.id, search_string=file_name))
    list_of_remote_files = list()

    for remote_file in remote_file_pages:
        file_name_ = remote_file['url']
        version_tag = remote_file["version_tag"]
        page_id = remote_file['page_id']
        list_of_remote_files.append([file_name_, version_tag, page_id])

    from tabulate import tabulate
    log.info(tabulate(list_of_remote_files, headers=['filename', 'version', 'page_id']))


def addkey_command(curdir, config, key, value, file_id):
    api = ProjectAPI(config)
    status_response = api.status_single_key(file_id, key)

    if not status_response['success']:
        log.info("The key `{}` already exists".format(key))
        log.info("Or you may not use the correct key format".format(key))
    else:
        print("key is added {}".format(status_response['success']))
        api.upload_single_key(file_id, key, value)