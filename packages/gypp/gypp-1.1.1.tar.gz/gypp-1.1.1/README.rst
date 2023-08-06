gypp - readonly access to GPG YAML files
========================================

``gypp`` provides convenience methods for accessing entries in a GPG encrypted YAML file.

The YAML file has a structure like::

    # Comments start with a "#"
    DESCRIPTION: |
      This is a human readable description of this file.

    RECIPIENTS:
      - list of
      - recipients of
      - the encrypted file

    some_key:
      user: name of account (required)
      password: the password or phrase (required)
      name: human readable name of entry (optional)
      note: |
        optional note. The pipe char indicates that
        line breaks will be preserved, but the
        preceding space on each line will not.
      other: Other properties may be added as needed.

    another_key:
      user: some user
      password: password with a quote " in it
      name: another test entry
      note: |
        Same old stuff


Installation
------------

::

  pip install -U gypp


Use
---

List entries available::

  $ gypp my_passwords.gpg

  Source: junk.txt
  Description: This is a human readable description of this file.

  Keys available:
    some_key          : human readable name of entry (optional)
    another_key       : another test entry

Show a specific entry on the commandline::

  $ gypp -s -k some_key my_passwords.gpg

  user     : name of account (required)
  password :
  name     : human readable name of entry (optional)
  note
    optional note. The pipe char indicates that
    line breaks will be preserved, but the
    preceding space on each line will not.

  other    : Other properties may be added as needed.

Place password for entry on the clipboard::

  $ gypp -k some_key my_passwords.gpg


New in version 1.1: ``gypp`` will read a list of sources from a configuration file that
by default is located at ``$HOME/.config/gypp/gypp.yaml``. The config file is a yaml
file structured like::

  sources:
    source_name_1: path/to/encrypted/file
    source_name_2: path/to/another/encryped/file

``gypp`` can then be run using a key under ``sources`` to specify the gpg file to read. e.g.::

  $ gypp source_name_2


Development
-----------

Repository: https://github.com/datadavev/gypp

Development install::

  $ git clone https://github.com/datadavev/gypp.git
  $ cd gypp
  $ pip install -U -e .

Deploy to pypi::

  $ python setup.py sdist
  $ twine upload dist/*

