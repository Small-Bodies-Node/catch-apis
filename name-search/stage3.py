"""
STAGE 2 of Pipeline
Build indexes, test uploads, etc.
"""

import time
from stage2 import session


# Create gist index (gin doesn't work for the desired query; see: https://www.postgresql.org/docs/9.1/pgtrgm.html)
# Requires running `CREATE EXTENSION pg_trgm;`
q = session.execute(
    """
        CREATE INDEX IF NOT EXISTS search_text_idx2 ON name_search USING gist(comparison_text gist_trgm_ops);
    """
)
session.commit()


# Test retrieval efficacy of search word
# Number of retrievals
retrievals: int = 1
# Mark start time
t1: float = time.time()
# Retrieve results multiple times for benchmarking
for i in list(range(0, retrievals)):
    q = session.execute(
        """
            SELECT *, comparison_text <-> 'gunn' AS dist from name_search
            -- WHERE search_text % 'van gall'
            -- WHERE similarity(search_text, 'van gall') > 0.35
            ORDER BY (comparison_text <-> 'gunn')
            -- WHERE search_text ILIKE '%van gaal%' -- Run this only when similarity is unavailable
            LIMIT 10;
        """
    )

    # Print out retrieved data
    print("")
    for p in q:
        print(p)


print(f"time taken for {retrievals} retrievals:")
print(time.time() - t1)
