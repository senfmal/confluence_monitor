from datetime import datetime
import getpass
from atlassian import Confluence


def acquire_conf_connection(url, username=None):
    username = username if username is not None else getpass.getuser()
    return Confluence(
        url=url,
        username=username,
        password=getpass.getpass("Please insert your password >> ")
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


def get_conf_update_information(confluence, space, theme):
    update_stats = {}
    for page in get_conf_pages_ids(confluence, space):
        if confluence.page_exists(space, page[1]):
            labels = confluence.get_page_labels(
                page[0], prefix=None, start=None, limit=None
            )
            vals = {}
            vals['name'] = page[1]
            for label in labels['results']:
                if label['name'] == theme:
                    vals['lastUpdated'] = (datetime.now() - datetime.strptime(
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
                if label['name'] == "block":
                    vals['is_block'] = True
                if label['name'] in (
                    "vorhaben", "projekt", "maßnahme", "project", "massnahme"
                ):
                    vals['is_vorhaben'] = True
                if label['name'] in (
                    "status", "statusbericht", "bericht", "statusreport", "report"
                ):
                    vals['is_status'] = True
            if 'lastUpdated' in vals:
                update_stats[page[0]] = vals
    return update_stats
