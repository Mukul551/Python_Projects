SEARCH_KEY = "AIzaSyBHFsp0pPmgHgPPFV3hCXLgAfXFmq7XuUI"
SEARCH_ID = "6417ae5a351c14e6a"
COUNTRY = "us"
SEARCH_URL = "https://www.googleapis.com/customsearch/v1?key={key}&cx={cx}&q={query}&start={start}&num=10&gl=" + COUNTRY
RESULT_COUNT = 10

import os
if os.path.exists("private.py"):
    from private import *