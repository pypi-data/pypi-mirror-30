PY Have I Been PWNED
====================

What is this repository for?
----------------------------

The API allows the list of pwned accounts (email addresses and
usernames) to be quickly searched via a RESTful service.

How do I get set up?
--------------------

-  Install this script with:

   -  pip3 py\_pwned --upgrade (or pip py\_pwned --upgrade )
   -  or
   -  sudo -H pip3 py\_pwned --upgrade

-  ready to use it!

What packages does this script uses
-----------------------------------

-  tableprint
-  progress
-  cfscrape

You can also install them by hand

-  pip install progress
-  pip install tableprint
-  pip install cfscrape

OR

-  pip3 install tableprint
-  pip3 install progress
-  pip3 install cfscrape

How to use
----------

start with

``pwned = PwNed()``

For Password check

``data = pwned.searchpwd('YOURPASSWORD') print(data)``

For email check

``data = pwned.searchemail('YOUREMAIL) print(data)``

Who do I talk to?
-----------------

-  Theodorus van der Sluijs (friends call me Theo)
-  theodorus@vandersluijs.nl

License
-------

Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)

You are free to:
~~~~~~~~~~~~~~~~

-  Share — copy and redistribute the material in any medium or format
-  Adapt — remix, transform, and build upon the material

-The licensor cannot revoke these freedoms as long as you follow the
license terms.-

Under the following terms:
~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Attribution — You must give appropriate credit, provide a link to the
   license, and indicate if changes were made. You may do so in any
   reasonable manner, but not in any way that suggests the licensor
   endorses you or your use.
-  NonCommercial — You may not use the material for commercial purposes.
-  ShareAlike — If you remix, transform, or build upon the material, you
   must distribute your contributions under the same license as the
   original.
