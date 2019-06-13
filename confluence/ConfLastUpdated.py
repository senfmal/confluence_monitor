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
        api_root='wiki/rest/api',
        username=username,
        password=password
    )


def get_conf_pages_ids(confluence, space, start=0, limit=500):
    pages = confluence.get_all_pages_from_space(space, start=start, limit=limit)
    return [
        [page['id'], page['title']] for page in pages
    ] if pages is not None else []


def get_key_for_value_in_list(check_val, d):
    for k, v in d.items():
        if isinstance(v['tags'], typing.List) or isinstance(v['tags'], typing.Tuple):
            for value in v['tags']:
                if value == check_val:
                    return k
        elif v['tags'] == check_val:
            return k
    return None


def get_conf_update_information(confluence, space, theme, category_tag_map):
    cat_lists = {}
    cat_check = {}
    cat_lists['name'] = []
    cat_lists['last_updated'] = []
    cat_lists['url'] = []
    for category in category_tag_map.keys():
        cat_check[category] = False
        cat_lists[category] = []
    for page in get_conf_pages_ids(confluence, space):
        cat_match_count = 0
        name = None
        last_updated = -1
        url = ""
        for category in category_tag_map.keys():
            cat_check[category] = False
        if confluence.page_exists(space, page[1]):
            labels = confluence.get_page_labels(
                page[0], prefix=None, start=None, limit=None
            )
            for label in labels['results']:
                if label['name'] == theme:
                    last_updated_date = None
                    name = page[1]
                    content = confluence.get_page_by_id(page[0], expand='history')
                    last_updated_date = content['history']['_expandable']['lastUpdated']
                    url = content['_links']['base'] + '/pages/viewpage.action?pageId=' + page[0]
                    if content is None or len(last_updated_date) == 0:
                        content = confluence.get_page_by_id(page[0], expand='version')
                        last_updated_date = content['version']['when']
                    if last_updated_date is not None:
                        last_updated = (datetime.now() - datetime.strptime(
                            last_updated_date,
                            '%Y-%m-%dT%H:%M:%S.%f%z'
                            ).replace(tzinfo=None)).days
                    else:
                        last_updated = 0
                    last_updated = 0 if last_updated < 0 else last_updated
                cat_match = get_key_for_value_in_list(label['name'], category_tag_map)
                if cat_match is not None:
                    cat_match_count += 1
                    cat_check[cat_match] = True
                    cat_match = None
            if name is not None:
                if cat_match_count == 0:
                    cat_check["untagged"] = True
                cat_lists['name'].append(name)
                cat_lists['last_updated'].append(last_updated)
                cat_lists['url'].append(url)
                for category in category_tag_map.keys():
                    cat_lists[category].append(cat_check[category])
    return pd.DataFrame(data=cat_lists)
