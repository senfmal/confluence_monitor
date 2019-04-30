
from pprint import pprint
import sys
from conf_last_updated import acquire_conf_connection, get_conf_update_information


if __name__ == '__main__':
    try:
        url, space, theme = sys.argv[1:]
    except ValueError as err:
        print("You need to specify three parameters:\n\t1. url e.g. 'http://localhost:8080/'\n\t2. space\n\t3. theme i.e. basic label")
        sys.exit()

    pprint(get_conf_update_information(acquire_conf_connection(url), space, theme))
