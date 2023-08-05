# Hypy by Example


### Important Classes and Methods

- HDatabase
    Represents the overall data store containing the index.  **Key
    Methods**: `db.open(filename, mode)`, `db.close()`,
    `db.putDoc(document)`, `db.search(condition)`

- HDocument
    Represents a single document/location which will be indexed and
    stored. **Key Methods**: `doc.addText(text)`,
    `doc.addHiddenText(text)`, `doc.encode(encoding)`

    In addition, HDocument acts like a dictionary, where the keys are the
    attributes (metadata) of the document.  For example, `doc[u'@uri']`
    returns a document's @uri attribute.  Dictionary methods work too.

- HHit
    A subclass of HDocument which represents one hit returned from a
    search.  It has the capabilities of HDocument, plus one more.  **Key
    Methods**: `result.teaser(wordList)`

- HResults
    A collection of HHit returned from a search.  **Key Methods**:
    `results.hitWords()`, `results.pluck(attr)`

    In addition, HResults acts like a list, so you can iterate results.

- HCondition
    A query object which is used to perform a search.  Construct one of
    these with the parameters of the search, such as the phrase to search
    for and maximum number of hits, or metadata attributes.  **Key
    Methods**: `cond.addAttr(attributeExpression)`,
    `cond.setOrder(orderExpression)`


### Examples

Most of these examples will build on each other in order.  If you want to run
all of them, it's probably best to type them in one after the other.  If
you're only reading them, you can always just scroll back up to see the
assumptions of the example you're interested in.

#### Open a Database

An index, or database, has to be created before it can be used.  It creates a
disk directory at the spot you tell it.  When re-opened, you must give it the
location of the same directory.

Create flags are like the builtin Python function open(), with similar
semantics:

- 'r' : flag
    Open read-only
- 'w' : flag
    Clobber/delete if it exists, and open it for writing
- 'a' : flag
    Open for writing, creating if necessary.  (The most common way to open an index.)

Example:

```
from hypy import *   # don't do this in real life....
                     # import * is bad medicine.

INDEX = 'breakfast/'
db = HDocument()
db.open(INDEX, 'w') # create it, destroying old one if it exists
db.close()
db.open(INDEX, 'a')
```


#### Spidering

Hypy is not *itself* a web spider, but since it depends on Hyper Estraier, you
**already have one**.  Lucky you!  Here's how you use Hyper Estraier's spider,
which is called `estwaver`.  More [details on estwaver]() can be found on the
Internet.

(Bash syntax) example:

```
$ cd ~/projects/
$ estwaver init hypysite
2009-02-21T23:18:45Z    INFO    the root directory created
```

estwaver `init` does the same thing as `db.open(INDEX, 'w')` in the
example above, except that it also creates a boilerplate config file.

There will now be a file called `hypy/_conf`.  Edit this file.  Change the seeds
at the top to the site you want to spider.  If you want to restrict the URL,
there is a place to change the regular expression of links it is allowed
to visit.

```
# ORIGINAL
seed: 1.5|http://hyperestraier.sourceforge.net/uguide-en.html
seed: 1.0|http://hyperestraier.sourceforge.net/pguide-en.html
seed: 1.0|http://hyperestraier.sourceforge.net/nguide-en.html
seed: 0.0|http://qdbm.sourceforge.net/
...
# allowing regular expressions of URLs to be visited
allowrx: ^http://
```

I changed these to the following, and added some rules to avoid re-indexing
builtin wiki stuff

```
# MY CHANGES
seed: 1.0|http://mysite.goonmill.org/
...
allowrx: ^http://(|[a-zA-Z0-9_]*\.)goonmill\.org
denyrx: ^http://wiki\.goonmill\.org/Help
denyrx: ^http://wiki\.goonmill\.org/.*Wiki
denyrx: ^http://wiki\.goonmill\.org/.*\?action=
denyrx: ^http://wiki\.goonmill\.org/SystemPages

# leave the rest of denyrx in place.
```

Now crawl the site using `estwaver crawl`, telling it the index
directory to index into

```
$ estwaver crawl hypysite
2009-02-21T23:44:43Z    INFO    DB-EVENT: status: name=hypysite/_index ...
2009-02-21T23:44:43Z    INFO    crawling started (continue)
2009-02-21T23:44:43Z    INFO    fetching: 0: http://goonmill.org/
2009-02-21T23:44:44Z    INFO    seeding: 1.000: http://goonmill.org/
2009-02-21T23:44:45Z    INFO    [1]: fetching: 0: http://goonmill.org/
2009-02-21T23:44:45Z    INFO    [2]: fetching: 1: http://goonmill.org/cory

...

2009-02-21T23:47:02Z    INFO    DB-EVENT: closing: name=hypysite/_index ...
2009-02-21T23:47:02Z    INFO    finished successfully
```

.. _details on estwaver: http://hyperestraier.sourceforge.net/cguide-en.html#introduction


#### CRUD (Create/Read/Update/Delete) Documents

If you aren't spidering, or need to add documents using Python code, we'll
provide some examples for directly operating on documents.

Simple:

```
doc = HDocument(uri=u'http://estraier.gov/example.txt')
doc.addText(u"Hello there, this is my text.")
db.putDoc(doc)
```

I just added a single document to the index, with the URI
`http://estraier.gov/example.txt`.  **Note that both the text and uri are
unicode strings.  Hypy requires Unicode strings everywhere you would give it
text.**

This document is available for search only when the index has been flushed.
This happens each time:

* the index is closed with close()
* you call flush() on the index
* or you call putDoc, *if autoflush is turned on*

You can turn on autoflush when you open the index, or do it right now.

```
# db = HDatabase(autoflush=True)  ## or ...
db.autoflush = True
# turning on autoflush does not immediately flush, so do that.
db.flush()
```

### Tip

    Autoflush increases disk IO significantly, so it is recommended that you not
    autoflush if you are indexing in bulk; instead, flush() every n documents, where
    n is large enough to reduce disk IO but small enough that you won't fill up
    memory.

All documents must have a @uri attribute, so that gets specified in the
initializer of HDocument().  However, any other named attribute may also be
added to a document.

```
doc2 = HDocument(uri=u'http://estraier.gov/pricelist.txt')
doc2.addText(u"""Coffee: $2.00
Toast: $1.00
Eggs (2, any style): $3.00          Eggs (9, any style): $13.50
Eggs (3, any style): $4.50          Eggs (10, any style): $15.00
Eggs (4, any style): $6.00          Eggs (11, any style): $16.50
Eggs (5, any style): $7.50          Eggs (12, any style): $18.00
Eggs (6, any style): $9.00          Eggs (13, any style): $19.50
Eggs (7, any style): $10.50         Eggs (14, any style): $21.00
Eggs (8, any style): $12.00         Eggs (15, any style): $22.50
...
with apologies to the New Yorker for this joke""")
doc2[u'maxprice'] = u'22.50'
doc2[u'minprice'] = u'1.00'
db.putDoc(doc2)
```

Some attributes are automatically available

```
print doc[u'@id']
## prints 1
print doc[u'@uri']
## prints http://estraier.gov/example.txt
```

You can directly remove a document from the index, by reference or by either of
the builtin attributes.

```
db.remove(id=1)
db.putDoc(doc) # put it back so we can remove it again :)
db.remove(doc)
db.putDoc(doc) # and again..
db.remove(uri=u'http://estraier.gov/example.txt')
# n.b. the document gets a NEW ID each time we put it in..
print doc[u'@id']
## prints 4
```

Since you can remove and re-put documents, you now know how to update them.

So, uh, how many documents are in the index any more?  ``len()`` is how you
find out, and we can verify that we now have 1 document left:

```
print len(db)
## prints 1
```

You've probably guessed by now that you can also fetch a document from the
index by uri, using dict-like getitem syntax

```
print db[u'http://extraier.gov/pricelist.txt']
## prints @digest=caacaefddcc1fd244de251723b0814be
##        @id=2
##        @uri=http://estraier.gov/pricelist.txt
##        ...
```

What it prints is known as the "draft" format, and is an internal
representation of the document.  It's also what you get when you use `str()`
on a document, but this is not the recommended way to get the text.  To get
the document text encoded in a representation of your choice, use `encode()`

```
print doc2.encode('utf-16')
## prints ÿþC^@o^@f^@f^@e^@e^@:...
```

#### Create Documents, Weighted

Hypy does not provide a way to directly influence a document's scoring weight
during searches, but you can easily influence it during indexing.  If you are
using `estwaver` to spider, alter the value in your `seed:` lines to weight
different URLs differently in the index.  If you are inserting documents
directly, `doc.addHiddenText(text)` is one method you can use to change the
weight of terms in your documents.

A document's weight is calculated primarily by the number of times a word in
the phrase matched a document in the index.  If you want to weight certain
words more heavily, simply insert them--hidden--into the document text.

```
doc5 = HDocument(u'http://estraier.gov/weighted.txt')
doc5.addText(u"This is my boom-stick.")
doc5.addHiddenText(u"eggs " * 30)
db.putDoc(doc5)
```

The third document will now score *higher* than doc2 when searching for "eggs"
because of the hidden text.  But if you print it, you will not see the hidden
text.

```
print doc5.encode('utf-8')
# prints This is my boom-stick.
```


#### Search, and Read Results

Say, now that we now how to weight documents for search, how do you search,
anyway?  Simple: construct a condition, and use ``db.search(condition)``.
Results are list-like.

```
cond = HCondition(u'eggs')
results = db.search(cond)
for doc in results:
    print doc[u'@id']
# prints 5 then 2

# you can also do this another way, using pluck to get an attribute off of
# every result document:

print results.pluck(u'@id')
# prints [u'5', u'2']
```

Search using wildcards is also supported:

```
cond = HCondition(u'egg*')
results = db.search(cond)
print len(results)
# prints 2
print results[0][u'@uri']
# prints .../weighted.txt
```

There are also other modes.  By default, "simple" intersection matching is
done on the search phrase.  But unions are also possible, either by specifying
'matching' on the condition, or using elements of search syntax within the
phrase.  Search syntax is preferred because it gives you better control over
the results:

```
doc6 = HDocument(uri=u'http://estraier.gov/spam.txt')
doc6.addText(u'spam and eggs')
db.putDoc(doc6)  # document @id is 6

# simple, intersection:
print db.search(HCondition(u'spam* eggs*')).pluck(u'@id')
# prints [u'6']

# union
print db.search(HCondition(u'eggs spam', matching='union')).pluck(u'@id')
# prints [u'5', u'2', u'6']

# unions with simple matching - you cannot use wildcard matches with
# matching='union' but you can do so with '|' syntax
print db.search(HCondition(u'egg* | spam')).pluck(u'@id')
# prints [u'5', u'2', u'6']
```

You can also refer to the [Hyper Estraier User's Guide](http://hyperestraier.sourceforge.net/uguide-en.html#searchcond) for a complete
reference on the search syntax.

Finally, you can get an abstract of the documents, called the "teaser", using
a method called, hey, `teaser()`.  This method currently has two supported
formats, html and [rst](http://docutils.sourceforge.net/docs/user/rst/quickref.html).  You must provide it with the words to highlight, as a
list.

```
words = [u'toast']
results = db.search(HCondition(u' '.join(words)))
hit = results[0]
print hit.teaser(words) # default is 'html'
# prints Coffee: $2.00 <strong>Toast</strong>: $1.00 Eggs (2, ...

# another way to get the original search words:
words = results.hintWords()

print hit.teaser(words, format='rst')
# prints Coffee: $2.00 **Toast**: $1.00 Eggs (2, ...
```




#### Attribute Search

There is also a robust syntax for searching for attributes.

```
cond = HCondition()
cond.addAttr(u'@id STREQ 5')

print db.search(cond)[0][u'@id']
# prints 5
```

Let's set up a little for the rest of the examples:

```
# for clarity in the rest of these examples, I'll use this function:
def attrSx(expr):
    cond = HCondition()
    cond.addAttr(expr)
    return u' '.join(db.search(cond).pluck(u'@id'))

# give another document some interesting attributes
doc6[u'maxprice'] = u'100'
doc6[u'minprice'] = u'0'
doc5[u'date'] = u'2009-01-01'
doc6[u'date'] = u'2009-02-02'

# commit the documents again, so they can be searched.  Note that this has
# nothing to do with flush() - these changes only exist in memory until
# you commit them with putDoc() and flush() too.  In this case, we are
# still using autoflush.
db.putDoc(doc6)
db.putDoc(doc5)
```

Numeric searches:

```
print attrSx(u'maxprice NUMGE 50')
# prints 6

# NOTE: documents that don't have an attribute are treated as having it
# set to "0" when doing a numeric comparison. therefore all the documents
# match this one:
print attrSx(u'minprice NUMLE 50')
# prints 2 6 5

# and two documents match this one:
print attrSx(u'minprice NUMLE 0.99')
# prints 2 5
```


Date comparisons are numeric comparisons:

```
print attrSx(u'date NUMGE 2008-12-31')
# prints 6 5

print attrSx(u'date NUMGE 2009-01-30')
# prints 6
```

Regular expressions, why not:

```
print attrSx(u'@uri STRRX (pricelist.txt|spam.txt)')
# prints 2 6
```

You can invert any attribute expression, too, to get only documents *not*
matching:

```
print attrSx(u'@uri !STRRX (pricelist.txt|spam.txt)')
# prints 5
```

And of course, you can use attribute searches in the same condition with
phrase searches.  They combine as using the matching rule of the condition
(i.e. usually intersection, i.e. "match spam AND minprice<=50")

```
cond = HCondition(u'spam')
cond.addAttr(u'minprice NUMLE 50')
print db.search(cond)[0][u'@id']
# prints 6
```


#### Other Search Options

Phew!  Lots of attribute search options and stuff.  Well, that's not all.  You
can also limit the number of hits and change the order of hits.

```
print db.search(HCondition(u'e*')).pluck(u'@id')
# prints [u'5', u'2', u'6']
print db.search(HCondition(u'e*', max=2)).pluck(u'@id')
# prints [u'5', u'2'] .. what did you expect?
```

If you use `max` you probably also want `skip`.

```
print db.search(HCondition(u'e*', skip=2)).pluck(u'@id')
# prints [u'6']
```


To change the order, call `setOrder(order)` on the condition.  The [Hyper
Estraier User's Guide]() has a complete reference on order expressions.  This
one changes the result order by the @id attribute.

```
cond = HCondition(u'e*')

# natural (scored) order
print db.search(cond).pluck(u'@id')
# prints [u'5', u'2', u'6']

# numeric ascending
cond.setOrder(u'@id NUMA')
print db.search(cond).pluck(u'@id')
# prints [u'2', u'5', u'6']

# numeric descending
cond.setOrder(u'@id NUMD')
print db.search(cond).pluck(u'@id')
# prints [u'6', u'5', u'2']
```


### Other Reference Docs

Well, that sure was a lot.  If you still didn't find what you want, well, dig
deeper:

1. Try the [API docs](api/), which are delicious.

1. The [Hyper Estraier User's Guide](http://hyperestraier.sourceforge.net/uguide-en.html#searchcond) describes the search syntax, as well as
   the syntaxes for attribute search and ordering.  As we've mentioned several
   times before.

1. The [Hypy unit tests](https://github.com/corydodt/Hypy/blob/master/hypy/test_lib.py) contain a wealth of examples of search syntax,
   particularly in `TestDatabase.test_queries` and
   `TestDatabase.test_condExtras`.  The tests cover 100% of the code in
   lib.py.  They have docstrings and comments; obscure things like skip and
   max searches and various attribute comparisons are covered.

