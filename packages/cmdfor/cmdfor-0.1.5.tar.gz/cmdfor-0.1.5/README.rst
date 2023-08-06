===============================
cmdfor
===============================

.. image:: https://img.shields.io/travis/jwgalley/cmdfor.svg
        :target: https://travis-ci.org/jwgalley/cmdfor

.. image:: https://img.shields.io/pypi/v/cmdfor.svg
        :target: https://pypi.python.org/pypi/cmdfor


nd for every line of input

* Free software: MIT license
* Documentation: (COMING SOON!) https://cmdfor.readthedocs.org.

Features
--------

A shell utility (and package) which runs a command for every line of input.

It allows for spawning an arbitrary number of concurrent threads, and control
over where to keep each commands output.

In my daily work, I have to run all manner of commands on huge batches of
items. These things are usually not CPU bound, so it makes sense to
multithread these tasks.

Thus, I find myself doing bash commands such as the following, which takes an
input file of items, splits it into equal(ish) parts, and then spawns a worker
for each part, all the while keeping granular logs and return codes::

    lines=`wc -l domains.txt | awk '{print $1}'`; threads=10; split=$(((lines/threads)+1)); mkdir -p in out; split -d -l ${split} domains.txt in/part. ; ls in/ | while read -r f; do cat in/${f} | while read -r d; do host -t a "${d}" > out/${d} 2>&1; echo -e "${d}\t$?"; done > log.${f} & echo ${!}; done > pids

That gets pretty tiring to type all the time. Why not use ``xargs -P`` you say?
Well that works perfectly fine for cases where I don't need to make very
complicated commands, and don't need to log all return codes. Maybe I can do
all of that with ``xargs``, but I wanted to make this anyway as a learning
experience.

How-To
------

The program can take input from STDIN or from a file passed with the -i option.

All arguments that aren't options are considered the subcommand to run. All
wildcards ``{}`` are replaced with the corresponding positional field from the
input data.

To delete a list of files, basically the same behaviour as xargs::

    cat files.txt | cmdfor rm {}

To run the fictional command ``imaplogin`` for every line of a csv that
contains <email>,<password> fields, logging each individual command's output
to an file in the directory ./out::

    cat email_users.csv | cmdfor -d, -o ./out -- imaplogin -u {} -p {}

To look up the IP addresses of a huge amount of hostnames, using 10 concurrent
threads, and storing each individual commands stdout and stderr in seperate
files in the directory ./results, with each file being named after the hostname
on which the query was performed::

    cat hostnames.txt | cmdfor -t 10 -Eo ./results -l 1 -- host -t a {}


To-Do
-----

1. Come up with a real test case. Since this is a shell utility and really only
deals with shell subcommands, I don't know what will work and what won't on
travis.ci (can I run a shell command there?)
2. By default, it suppresses all output from subprocesses, and writes a message
to STDOUT for each process spawn and reap. This output is too verbose for the
default behaviour, and so it should be toggled with -v. The default should be
quitier and simpler. Perhaps just the returncodes of each task.
3. Refactoring some stuff to be a little less messy. The function signatures
are huge, and there are messages generated in odd places. I think it would be
better to pass a context object.


