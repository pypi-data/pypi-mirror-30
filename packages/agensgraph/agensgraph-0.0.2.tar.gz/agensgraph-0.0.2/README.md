# Agensgraph python driver

A psycopg2 extension to use [AgensGraph][1] with Python.

### Documentation

Go to [Psycopg's documentation][2] for documentation about the Python interface and to [AgensGraph][1] documentation for AgensSQL. If you want to learn more about Cypher, I recommend you to go to [Neo4j's][3] documentation.


### How to 
```python
import agensgraph

conn = agensgraph.connect("dbname=iomed")  # Equivalent to psycopg2.connect
cur = conn.cursor()
cur.execute("SET graph_path=snomed;")

cur.execute("MATCH (a)-[r]->(b) RETURN a,r,b LIMIT 10;")
result = cur.fetchall()

```


**Copyright © 2017, IOMED Medical Solutions S.L.**

[1]: http://bitnine.net/wp-content/uploads/2017/06/html5/main.html
[2]: http://initd.org/psycopg/docs/index.html 
[3]: https://neo4j.com/docs/developer-manual/current/cypher/



