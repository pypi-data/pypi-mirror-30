Cluster Searcher
================

A searcher, for David's clusters

Installation
------------

### Prerequisites ###

* Python 3.6

### Installation ###

```bash
$    (sudo) pip install cluster_searcher
```

Usage
-----

Launch cluster searcher from the command line

```bash
cluster_searcher
```

Type `cmdlist` to list the available commands.

Please see [Iɴᴛᴇʀᴍᴀᴋᴇ](https://bitbucket.org/mjr129/intermake) for how to use the application. 


Troubleshooting
---------------

* `Not found` error in KEGG - You're probably pasting the output into a different pathway.
* ***False negatives*** - KEGG wildcards (e.g. `Slk1/2` or `Slk1_2`) and differences in naming (e.g. `Slk-beta` vs `Slkβ`). Please check manually.
* ***Missing values*** - Check the pathway (e.g. `hsa12345.xml`) and the gene name prefix (e.g. `hsa`) matches.
* Slow loading files - copy the files locally

Meta
----

```ini
language= python3
type    = arg,cli
host    = bitbucket,pypi
licence = https://www.gnu.org/licenses/agpl-3.0.html
```
