from datetime import datetime
import getpass
from atlassian import Confluence
import pandas as pd


def acquire_conf_connection(url, username=None, password=None):
    username = username if username is not None else getpass.getuser()
    password = password if password is not None else getpass.getpass(
        "Please insert your password >> "
    )
    return Confluence(
        url=url,
        username=username,
        password=password
    )


def get_information_from_content(source, knot, child):
    for k, v in source.items():
        if k == knot:
            return get_information_from_content(v, knot, child)
        if k == child:
            return v


def get_conf_pages_ids(confluence, space, start=0, limit=500):
    pages = confluence.get_all_pages_from_space(space, start=start, limit=limit)
    return [
        [page['id'], page['title']] for page in pages
    ] if pages is not None else []


def get_key_for_value_in_list(check_val, d):
    for k, v in d.items():
        if type(v) == 'list':
            for value in v:
                if value == check_val:
                    return k
        if v == check_val:
            return k
    return None


def get_conf_update_information(confluence, space, theme, category_tag_map):
    names = []
    lastUpdates = []
    cat_lists = {}

    for page in get_conf_pages_ids(confluence, space):
        cat_check = {}
        for category in category_tag_map.keys():
            cat_check[category] = False
            cat_lists[category] = []
        name = None
        last_updated = -1
        if confluence.page_exists(space, page[1]):
            labels = confluence.get_page_labels(
                page[0], prefix=None, start=None, limit=None
            )
            for label in labels['results']:
                if label['name'] == theme:
                    name = page[1]
                    last_updated = (datetime.now() - datetime.strptime(
                        get_information_from_content(
                            confluence.get_page_by_id(
                                page[0],
                                expand='version'
                            ),
                            'version',
                            'when'
                        ),
                        '%Y-%m-%dT%H:%M:%S.%f%z'
                        ).replace(tzinfo=None)).days
                    last_updated = 0 if last_updated < 0 else last_updated
                cat_match = get_key_for_value_in_list(label['name'], category_tag_map)
                if cat_match is not None:
                    cat_check[cat_match] = True
            if name is not None:
                names.append(name)
                lastUpdates.append(last_updated)
                for category in category_tag_map.keys():
                    cat_lists[category].append(cat_check[category])
    return pd.DataFrame(data=cat_lists)
