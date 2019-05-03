from flask_caching import Cache

CACHE_CONFIG = {
    'CACHE_TYPE': 'simple'
}

cache = Cache(config=CACHE_CONFIG)
