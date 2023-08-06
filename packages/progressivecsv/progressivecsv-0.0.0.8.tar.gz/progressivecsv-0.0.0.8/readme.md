Progressive CSV
===============

Used to write CSV files progressively, whereby later rows may contain more or less headers than earlier ones. When the file is closed, the file will be rewritten (if necessary) to accommodate the new data.

See the class documentation for further usage details.

Example
-------

```
from progressivecsv import ProgressiveCsvWriter

w = ProgressiveCsvWriter( "example.csv" )
        
w.write_row( { "name": "alice" } )
w.write_row( { "name": "bob"    , "address": "home" } )
w.write_row( { "name": "charlie", "spam"   : "eggs" } )

w.close( )
```


Meta
----

```ini
author      = Martin Rusilowicz
language    = Python3
type        = library
created     = September 2017
host        = bitbucket,pypi
```
