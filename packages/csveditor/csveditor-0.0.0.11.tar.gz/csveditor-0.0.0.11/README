CSV Editor
==========

Lightweight command-line editor for CSVs too large for tools such as Excel.

Edit operations are pipeline-backed, meaning you can create your pipeline using a "preview" portion of the table and defer modifying the underlying data until the table is actually saved.

CꜱᴠEᴅɪᴛᴏʀ uses the [Iɴᴛᴇʀᴍᴀᴋᴇ](intermake.html) library, and therefore supports multiple modes of operation: command-line, command-line-interactive, python-interactive-shell, python-scripting, Jupyter, basic GUI, etc. 

Supported operations
--------------------

* change dialect
* replace text
* join tables
* lookup values
* filter by column
* filter to unique values
* sort by column
* rearrange columns
* drop rows

Installation
------------

Please install using pip:

```bash
(sudo) pip install csveditor
```

Getting started
---------------

* `csveditor` to launch the program in CLI mode.
* Use the `cmdlist` command to get an idea of what you can do.
* Extensive help is built in and is not provided in this readme.
* For how to start CꜱᴠEᴅɪᴛᴏʀ in other modes or to pass arguments from the command line, please see the [Iɴᴛᴇʀᴍᴀᴋᴇ](intermake.html) documentation. 

General help - specifying columns
---------------------------------

* To identify columns by name, just use the name, e.g. `sequence`
* To identify columns by index, use the prefix `#`, e.g. `#2`
* To specify the table, use by the prefix `:`, e.g. `data:#2` for column 2 of the `data` table.
* If no table is specified, the current working table is assumed.
* Rows are always identified by their index in the working table, e.g. `5` for row 5 of the current table.
* All indices are zero based.

Example
-------

Our aim in this example is to join two bioinformatics tables together based on a common column, _family_:
* Left table columns: _id_, _family_, _eccentricity_
* Right table columns: _sequence_, _family_
* Join on column: _family_
* Output table columns: _id_, _family_, _eccentricity_, _sequence_


First we open up our _left_ table
```bash
$ open /Users/martinrusilowicz/examples/left.csv
```

We take a peek to make sure the data loaded okay:
```bash
$ head

    -------------------- 0 --------------------
    0  id                         [11532]
    1  family                     [F11532]
    2  eccentricity               [6]
    ...
```

It loaded fine, so we load our _right_ table. It has a longer filename, so we provide an abbreviation - "right".
```
$ open /Users/martinrusilowicz/examples/the-right-table.csv right
```

We take another peek:
```bash
$ head

    -------------------- 0 --------------------
    0 sequence [ NZ_JQAK01000007|gi|692233712]
    1 family   [ F0]
```

We see some some unwanted space, e.g. `" F0"` instead of `"F0"`. We can fix that by being more specific about the CSV dialect we are using:

```bash
$ dialect +trim
```

Now we've fixed the dialect we can check again:
```bash
$ head

    -------------------- 0 --------------------
    0 sequence [NZ_JQAK01000007|gi|692233712]
    1 family   [F0]
```

Notice how we don't need to reload our table to change the dialect.

Now we can _join_ our tables together. When we loaded the _right_ table that table became active, use the `switch` command to go back to the _left_ table:

```bash
$ switch left
```

And add the _join_ operation to our pipeline:
```bash
$ join family right:family
```

Take a peek to see if it worked:
```bash
$ summary

    Initial: 5787 rows
    Initial: 23 columns
    Final: 45484 rows
    Final: 24 columns
```

We see that our new table has a lot more rows, so the `join` probably worked, we could do some more in depth exploration using `head` or `view`, but for now let's just save the table:

```
$ save /Users/martinrusilowicz/examples/leftright.csv
```

That's it.

Meta
----

```ini
author  = Martin Rusilowicz
licence = https://www.gnu.org/licenses/agpl-3.0.html
date    = 2017
keywords= csv, tsv, editor, viewer, command-line, cli
language= python3
type    = cli
os      = independent
host    = bitbucket,pypi
type    = arg,cli
```
