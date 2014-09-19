# encoding: utf8

# The path/file name of our local SQLite database.
# If it doesn't exist, the database file will be
# generated upon startup.
#
DB_PATH = 'orgdata.db'

# The number range to be searched
#
MIN_REGISTER_NUMBER = 1
MAX_REGISTER_NUMBER = 500000

# minimum and maximum time to wait between requests
#
WAIT_MIN = 0.3
WAIT_MAX = 2.0

# The base url for register searches
#
HANDELSREGISTER_URL = "https://www.handelsregister.de/rp_web/mask.do?Typ=e"

# The number of search results we'd like
#
ITEMS_PER_PAGE = 100

# If you use a proxy server, this port
# is used if you don't set a specific port
# via the -p / --proxyport command line option.
#
DEFAULT_PROXY_PORT = 9150

# How often can error one (no form found)
# occur before we quit?
#
ERROR_1_LIMIT = 5

# A selection of user agents strings
# to identify with
#
USER_AGENTS = [
	'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.78.2 (KHTML, like Gecko) Version/7.0.6 Safari/537.78.2',
	'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.143 Safari/537.36',
	'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.94 Safari/537.36',
	'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:31.0) Gecko/20100101 Firefox/31.0',
	'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.143 Safari/537.36',
	'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36',
	'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.103 Safari/537.36',
	'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36',
	'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:31.0) Gecko/20100101 Firefox/31.0',
	'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.143 Safari/537.36',
	'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:32.0) Gecko/20100101 Firefox/32.0',
	'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
	'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:31.0) Gecko/20100101 Firefox/31.0',
	'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; MRA 4.6 (build 01425))',
    'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Chrome/10.0.648.204 Safari/534.16',
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.2.16) Gecko/20110319 Firefox/3.6.16 (.NET CLR 3.5.30729)',
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.2.16) Gecko/20110319 Firefox/3.6.16',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.2; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
    'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; de; rv:1.9.2.15) Gecko/20110303 Firefox/3.6.15',
    'Mozilla/5.0 (X11; Linux x86_64; rv:2.0) Gecko/20100101 Firefox/4.0'
]