from backend.cache import LRUCacheTTL

# default: keep 512 answers cached for 2 hours
cache = LRUCacheTTL(capacity=512, default_ttl=2 * 60 * 60)
