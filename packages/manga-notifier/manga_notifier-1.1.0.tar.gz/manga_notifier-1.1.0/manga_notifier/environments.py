import os

HOME = os.environ.get('HOME')
FAVORITE_LOCATION = "{0}/.local/mangastream/favorite.json".format(HOME)
DOWNLOAD_LOCATION = "{0}/.local/mangastream/library".format(HOME)

# To see what's really happen under the hood
MANGASTREAM_DEBUG = bool(os.environ.get('MANGASTREAM_DEBUG'))

# Specify a favorite file location
MANGASTREAM_FAVORITE_FILE = os.environ.get('MANGASTREAM_FAVORITE_FILE',
                                           FAVORITE_LOCATION)

# Specify a custom download directory
MANGASTREAM_DOWNLOAD_DIR = os.environ.get('MANGASTREAM_DOWNLOAD_DIR',
                                          DOWNLOAD_LOCATION)
