import os
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import shutil
from tools.cache_manager import CacheManager

def test_cache_save_and_load():
    test_hash = "test123hash"
    style = "default"
    test_data = {
        "summary": "This is a test summary.",
        "style": style,
        "source": "compressed",
        "chunks": 1,
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30
        },
        "cost": 0.0002
    }

    # Ensure cache dir is fresh
    if os.path.exists("cache"):
        shutil.rmtree("cache")

    CacheManager.save_summary(test_hash, style, test_data)
    assert CacheManager.is_cached(test_hash, style)

    loaded = CacheManager.load_cached_summary(test_hash, style)
    assert loaded == test_data
