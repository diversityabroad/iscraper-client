from djsmartsearch.engine import  *
e = load_engines()
se = e['google']
se.search(query='joe')




SMARTSEARCH_AVAILABLE_ENGINES = [
    {'NAME':'google',
     'CLASS':'djsmartsearch.engine.google.SearchEngine',
     'GOOGLE_SITE_SEARCH_API_KEY':'',
     'GOOGLE_SITE_SEARCH_SEID':'',
     },
]


SMARTSEARCH_LOGGER="smartsearch"


SMARTSEARCH_LOCAL_SITE="www.osfsaintfrancis.org"
