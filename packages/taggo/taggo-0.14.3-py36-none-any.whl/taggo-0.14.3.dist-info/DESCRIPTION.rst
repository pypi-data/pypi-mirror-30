taggo
=====

.. image:: https://img.shields.io/pypi/v/taggo.svg
        :target: https://pypi.python.org/pypi/taggo

.. image:: https://img.shields.io/travis/xeor/taggo.svg
        :target: https://travis-ci.org/xeor/taggo

.. image:: https://img.shields.io/coveralls/xeor/taggo.svg
        :target: https://coveralls.io/github/xeor/taggo?branch=master

.. image:: https://readthedocs.org/projects/taggo/badge/?version=latest
        :target: https://taggo.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://pyup.io/repos/github/xeor/taggo/shield.svg
     :target: https://pyup.io/repos/github/xeor/taggo/
     :alt: Updates

Tag organizer that uses names of files and folders to create symlinks.
Tags are defined by using #hashtags in the name. They can also be as many sub levels as you want, like #sub-hash-tag

**note**
This version is a completey different version than the old (https://github.com/xeor/taggo/tree/0.2).
The old version works for python 2 (but not 3). It also had config-file instead of parameters. Check out the
repo if you want it..

* Free software: MIT license
* Documentation: https://taggo.readthedocs.io
* Source: https://github.com/xeor/taggo
* Issues: https://github.com/xeor/taggo/issues

Introduction
------------

This project is in beta stage, please report bugs :)

Any questions, thoughts, bugs are very welcome!


Requirements
------------

* 3.6+


Docker
------

Start the container with environment variables like `CRON_TAGGO_0` with the format `* * * * *|run ....`

* CRON_TAGGO_n where n is a number, start at 0, have as many as you want.
* We take care automaticly that only 1 of each number is running at a time. Example, if one of your job is running every minute and it takes more than a minute to finish. It wont start the 2nd time.
* The environment variable is split in 2 by a `|`. The first param is a cron, the 2nd is the parameters sent to the `taggo` command.

FAQ
---

* Why the name taggo?

  * It's a tagging tool. It does stuff with tags. What do you suggest? Tagging, taggs, tags, tag2fold... no.. Taggo!

* Why do you want to create tags with symlinks?

  * Because everyone have underestimated the power of tagging data.
  * Photo filenames are just wasted, what does DCIM1234.jpg tell you?
  * You know you miss one folder that contains all your dog pictures.
  * You sould not depend on a 3rd party program/database to manage
    your files/photos.


=======
History
=======

0.13.0 (2018-03-04)
-------------------

* Dropping python 2.x support... Some things might end up being problematic to support. Like symlinks for directories in windows.
  So instead of making a bunch of hacks around functionality. It is now dropped.

0.12.0 (2018-03-03)
-------------------

* Making symlink name template configurable
* Symlink collision handling
* Logs to stdout/stderr depending on message severety
* Option to output log as json
* Option to prompt/wait after each symlink. Usefull for debugging
* Lots of things around symlink-name-templates, it's now completly configurable.
* Possible to have extrainfo (used in symlink-name) from a tag parameter. Like #tag(info)
* Using powerful filters to not symlink certain files, or only symlink some files.
* Metadata-addons to use special file-info as in the symlink-name, like md5, stat, exif-data, ...
* Output data as json, if you want a logparser to use it. Single-lines..
* Configurable collision handling. If symlink already exist and points to a different file.
* Making `pip install taggo[all]` to get all metadata-addon required libs
* --auto-cleanup option in `run`
* Log different messages to stdout or stderr


0.11.0 (2018-02-20)
-------------------

* Fixing up docker image


0.10.0 (2017-11-04)
-------------------

* Basic docker image

0.9.0 (2017-10-21)
------------------

* Python 2.7 support

0.8.0 (2017-10-21)
------------------

* Good test coverage
* Things are mostly working
* Rename functionality
* List/info
* Much more

0.4.0 (2017-10-08)
------------------

* Started a complete rewrite, mainly focusing on using python 3.6
* Test on PyPI.. Non working version.

0.2 (2017-10-07)
------------------

* Checkpoint of the old version working only with 2.x. This checkpoint contains code from many years ago.


