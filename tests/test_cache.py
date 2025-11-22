from backend.cache import LRUCacheTTL

def test_set_get():
    c = LRUCacheTTL(capacity=2, default_ttl=2)
    c.set("a", 1)
    assert c.get("a") == 1

def test_ttl_expiry():
    c = LRUCacheTTL(capacity=2, default_ttl=1)
    c.set("b", 2)
    import time; time.sleep(1.2)
    assert c.get("b") is None
