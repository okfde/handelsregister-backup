Handelsregister Backup
======================

Public, important data is safest when it's distributed over
many storage devices. So let's create backups of the company
and association register at handelsregister.de.

## What it does - in a nutshell

This script performs searches for register numbers on
handelsregister.de and stores the very basic data for each
entry in a local SQLite database.

Since there are register numbers almost as high as 500.000,
we test for each and every number between 1 and 500.000.
Note: This takes a lot of time.

## Install

1. Clone this repository:

```
$ git clone https://github.com/okfde/handelsregister-backup.git
```

2. Change into the new directory

```
$ cd handelsregister-backup
```

3. Create and start a virtual python environment:

```
$ virtualenv venv
$ source venv/bin/activate
```

4. Install the required Python modules

```
$ pip install -r requirements.txt
```

That's it.


## Basic Usage

For basic use, simply run the script this way:

    $ python scrape.py -v

The -v switch ensures that you see what's happening.

You should see an output like this:

    Creating 500000 jobs...
    Register number: 198387
    1 entry found
    Register number: 447721
    ...
    Register number: 381187
    2 entries found
    Resolved 10 jobs in 53 seconds. 499991 jobs, 30.8 days remaining


Note that you can kill the script any time (Ctrl+C). If you restart it using the same
command as above, it will resume the work until done.

After you started the script for the first time, you have an SQLite3 database file
named `orgdata.db` in your current directory.

## Advanced Usage

### Start over

Once you ran the script, you usually have a job queue and the gathered organization
data in your database.

If you want to start over from scratch, simply delete the database file in your
working directory. It will be re-created once you start the script again.

If you only want to kill the job queue, without losing the organizations data,
you can start the script using the `-j` switch. This deletes all entries from the
job queue and creates jobs for the entire register number range. Note that there
is no way to undo this, so be careful.

    $ python scrape.py -j

or

    $ python scrape.py --resetjobs

Note that organization entries are never removed from the database. A subsequent run
will simply overwrite existing records. See section "Data" below on how to identify
outdated records.

### Limited register number range

If you want to limit the number range to search for, e.g. only 1 to 1000,
change the configuration settings MIN_REGISTER_NUMBER and MAX_REGISTER_NUMBER
accordingly:

```python
MIN_REGISTER_NUMBER = 1
MAX_REGISTER_NUMBER = 1000
```

If you started the script before with a different number range configured, you will
have to reset the job queue in order for these changes to take effect. Read the
"Start over" section above, especially the part about the -j switch.

Hint: This might be a good way to distribute the entire number range over several
machines and prevent duplicate work at the same time.


### Use via SOCKS proxy

You can use a SOCKS (SOCKS5, to be exact) proxy server for all network traffic.
This might be a good idea if you are behind a firewall or if you need additional
features, like the anonymity provided by the Tor network.

Say, for example, you have the Tor Browser Bundle running, which automatically
provides a SOCKS5 proxy on your local machine, port 9150. Run the script with the
additional switches `-s` (for "s"ocks) and `-p` (for "p"ort) like this:

    $ python scrape.py -v -s 127.0.0.1 -p 9150


### Error 1: No form found on initial page

If you see this output, chances are that your IP address has been blocked by the server.
You can double check by visiting www.handelsregister.de.

There is a config variable ERROR_1_LIMIT which defines how often this error
may occur before the script automatically quits.

## Data

The database created by the script contains a table called `organizations` which will
hold the organization entries after they have been retrieved.

Since this is an SQLite3 database, there are many tools out there to export the data,
to a SQL or CSV file, for example.

The table schema is as follows:


### `state`

The federal state owning this entry, e. g. `Baden-Württemberg`.


### `court`

The name of the city where the court ("Registergericht") owning the record resides, e. g. `Stuttgart`.


### `register_type`

The register type of this entry. The following types are possible:

* `HRA`: Handelsregister category A (everything except "Kapitalgesellschaften")
* `HRB`: Handelsregister category B (only "Kapitalgesellschaften")
* `GnR`: Genossenschaftsregister
* `PR`: Personenregister
* `VR`: Vereinsregister


### `idnum`

The register number. This is generally, but not always, simply an integer.

Sometimes, the idnum field has a text extension. Examples:

    120620 früher Amtsgericht Buxtehude
    9873 HL


### `name`

Name of the organization


### `location`

A city or locality string, indicating the city of residence of the organization.


### `last_seen`

The date when this entry has been last found and written to our database. This is
useful when you want to update your database. After several complete runs, this field
helps you to identify outdated entries.
