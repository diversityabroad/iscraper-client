from djsmartsearch.engine import  *
e = load_engines()
se = e['google']
se.search(query='joe')
