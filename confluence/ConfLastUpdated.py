from datetime import datetime
import getpass
from atlassian import Confluence
import pandas as pd
import typing


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
    try:
        for k, v in source.items():
            if k == knot:
                return get_information_from_content(v, knot, child)
            if k == child:
                return v
    except AttributeError as ae:
        print("Error in get_information_from_content: {}".format([source, knot, child]))
        return None


def get_conf_pages_ids(confluence, space, start=0, limit=500):
    pages = confluence.get_all_pages_from_space(space, start=start, limit=limit)
    return [
        [page['id'], page['title']] for page in pages
    ] if pages is not None else []


def get_key_for_value_in_list(check_val, d):
    for k, v in d.items():
        if isinstance(v, typing.List) or isinstance(v, typing.Tuple):
            for value in v:
                if value == check_val:
                    return k
        elif v == check_val:
            return k
    return None


def get_conf_update_information(confluence, space, theme, category_tag_map):
    cat_lists = {}
    cat_check = {}
    cat_lists['name'] = []
    cat_lists['last_updated'] = []
    for category in category_tag_map.keys():
        cat_check[category] = False
        cat_lists[category] = []
    for page in get_conf_pages_ids(confluence, space):
        name = None
        last_updated = -1
        for category in category_tag_map.keys():
            cat_check[category] = False
        if confluence.page_exists(space, page[1]):
            labels = confluence.get_page_labels(
                page[0], prefix=None, start=None, limit=None
            )
            for label in labels['results']:
                if label['name'] == theme:
                    name = page[1]
                    try:
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
                    except TypeError as te:
                        # fresh page without history
                        # TODO: Creation date of the initial page needs to be used in such cases
                        # TODO: Other scenario is a problem with the REST API history display, investigation needed
                        last_updated = 0
                    finally:
                        last_updated = 0 if last_updated < 0 else last_updated
                cat_match = get_key_for_value_in_list(label['name'], category_tag_map)
                if cat_match is not None:
                    cat_check[cat_match] = True
                    cat_match = None
            if name is not None:
                cat_lists['name'].append(name)
                cat_lists['last_updated'].append(last_updated)
                for category in category_tag_map.keys():
                    cat_lists[category].append(cat_check[category])
    return pd.DataFrame(data=cat_lists)
