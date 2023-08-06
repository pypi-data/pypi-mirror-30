.. image:: https://img.shields.io/badge/language-Unix%20Shell-blue.svg
    :target: none

|

Install
```````


.. code:: bash

    `[sudo] pip install gitmsg`

Examples
````````


.. code:: bash

    $ cd /path/to/repo/
    $ touch new_file
    $ rm deleted_file
    $ echo "new" > modified_file
    $ git add -A
    $ gitmsg
    '+new_file; -deleted_file; ^modified_file'



Feedback



.. image:: https://img.shields.io/github/issues/looking-for-a-job/gitmsg.sh.cli.svg
    :target: https://github.com/looking-for-a-job

.. image:: https://img.shields.io/github/stars/looking-for-a-job/gitmsg.sh.cli.svg?style=social&label=Stars
    :target: https://github.com/looking-for-a-job/gitmsg.sh.cli

.. image:: https://img.shields.io/github/issues/looking-for-a-job/gitmsg.sh.cli.svg
    :target: https://github.com/looking-for-a-job/gitmsg.sh.cli/issues
