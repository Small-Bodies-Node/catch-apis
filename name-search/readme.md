# Word Search Service Setup

## What's This?

This dir houses scripts for getting the names of objects from MPC website and loading them into the postgresql DB.

These scripts are part of a mini-pipeline launched from the script `_build_word_search`.

Chances are, only dwd need run this script once on each db.

## Note on Indexes

The approach for querying word search goes as follows. We have three columns: numid (integer), unaccented (string) and accented (string). We want to combine the unaccented and numid into one searchable text column. Example:

`1456 | Van Gaal -> "1456 van gaal"`

This way, we can let the user submit a query for either a number or word, and match to a row to find the object name. We perform this combination by means of a user-edinfed function `getSearchText`.

We're using the similarity operator to map (i) each such string, and (ii) a search term, to the range [0,1], and then returning up to the top 10 best matches.

I tried to index this query but, unfortunately, on the approach being taken here, we'd need the index to be effective on the ORDER BY command, and this is only possible in postgres with btree indexes. So, as far as I can tell at the moment, this approach is not indexable, and we'll have to be concerned if we push this list much beyond its current ~50k entries.
