# CPLOY

[![Build Status](https://travis-ci.org/deadc0de6/cploy.svg?branch=master)](https://travis-ci.org/deadc0de6/cploy)
[![PyPI version](https://badge.fury.io/py/cploy.svg)](https://badge.fury.io/py/cploy)
[![Python](https://img.shields.io/pypi/pyversions/cploy.svg)](https://pypi.python.org/pypi/cploy)
[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](http://www.gnu.org/licenses/gpl-3.0)

*The ad hoc continuous deployment solution for developers*

I sometimes have to code stuff that needs to be deployed and run on remote hosts.
Since I don't have all my prefs/settings/dotfiles/etc on the remote, I usually code
on local and have a small one-liner lying around that allows me to quickly deploy
the code (with `scp` or similar) and run some command on the other side (with `ssh` for example).
This is not optimal and that's the reason I created *cploy*.

*Cploy* allows to mirror changes performed on a local directory to a remote
host through SSH. A specific command (bash one-liner for example) can be run
after any change, for example to trigger a build or execute a script.

Features:

  * handle multiple syncs in parallel
  * secure sync through SSH
  * run in the background
  * execute command on each local change
  * ability to exclude some files from sync
  * save and resume tasks
  * load tasks from file

Quick start:
```bash
# install cploy
sudo pip3 install cploy
# start the daemon
cploy daemon start
# add a directory to sync
cploy sync /tmp/local someuser@somehost /tmp/remote
```

see [usage](#usage) for more info

---

**Table of Contents**

* [Installation](#installation)
* [Usage](#usage)

  * [Adding a task](#adding-a-task)
  * [Talking with the daemon](#talking-with-the-daemon)
  * [File exclusion](#file-exclusion)
  * [Sync events](#sync-events)
  * [Run a command on change](#run-a-command-on-change)
  * [Save and resume tasks](#save-and-resume-tasks)

* [Contribution](#contribution)

# Installation

To install run:
```bash
$ sudo pip3 install cploy
$ cploy --help
```

Or from github directly
```bash
$ cd /tmp; git clone https://github.com/deadc0de6/cploy && cd cploy
$ sudo python3 setup.py install
$ cploy --help
```

To work with *cploy* without installing it, you can do the following
```bash
$ cd /tmp; git clone https://github.com/deadc0de6/cploy && cd cploy
$ sudo pip3 install -r requirements.txt
$ python3 -m cploy.cploy --help
```

or install it in a virtualenv
```bash
$ cd /tmp; git clone https://github.com/deadc0de6/cploy && cd cploy
$ virtualenv -p python3 env
$ source env/bin/activate
$ python setup.py install
$ cploy --help
```

# Usage

The usual way of using *cploy* is by starting the daemon. A task will
continuously synchronize any change made to a specific local directory
on a remote path. All synchronizations are done through SSH.

Start the daemon
```bash
$ cploy daemon start --debug
```

The daemon's logs are in `/tmp/cploy/cploy.log`.

Add a task to it:
```bash
# sync local dir /tmp/local
# on host "somehost" under /tmp/remote
$ cploy sync /tmp/local/ somehost /tmp/remote
```

Usage:
```
cploy

Usage:
    cploy sync [-dfF] [-p <port>] [-u <user>] [-P <pass>]
        [-k <key>] [-K <pass>] [-c <cmd>] [-e <pattern>...]
        <local_path> <hostname> <remote_path>
    cploy daemon [-d] (start | stop | restart)
    cploy daemon [-d] (info | ping | debug)
    cploy daemon [-d] unsync <id>
    cploy daemon [-d] resync <id>
    cploy daemon [-d] resume <path>
    cploy --help
    cploy --version

Options:
    -p --port=<port>          SSH port to use [default: 22].
    -u --user=<user>          username for SSH [default: $USER].
    -k --key=<key>            Path of SSH private key to use.
    -P --pass=<pass>          SSH password to use.
    -K --keypass=<pass>       SSH private key passphrase.
    -e --exclude=<pattern>    Pattern to exclude using fnmatch.
    -c --command=<cmd>        Command to execute on changes.
    -F --front                Do not daemonize.
    -f --force                Force overwrite on remote [default: False].
    -d --debug                Enable debug [default: False].
    -v --version              Show version.
    -h --help                 Show this screen.
```

## Adding a task

Tasks can be added by using the `sync` command.

After adding a task, make sure to check the daemon to see if the task has
been added successfully with `cploy daemon info`. In case it wasn't, checking
the logs in `/tmp/cploy/cploy.log` usually allows to identify the issue.

Connections to a remote hosts is done using SFTP (SSH). Multiple
connection options can be applied: connection with password, with SSH keys, using
the SSH agent, different port, different username, etc.

Besides using the above switches, The *<hostname>* argument can also be
provided using a compact format similar to what the SSH client provides:
```
<username>@<hostname>:<port>
```

The `<remote_path>` is normalized based on the default user's directory
on the remote (usually `$HOME`). For example `../../tmp/test` would
result in `/tmp/test` if the remote user's default directory is `/home/user`.
Note that shell expansions are not performed on remote paths (like `~` for example)
neither are environment variables (like `$HOME`).

Once a new task is added, *cploy* will start by copying any local existing files to
the remote directory to initiate the remote directory. Then, any change to the local directory
is automatically applied on the remote.

Connection Requirements:

* SSH access is working (obviously)
* remote host key is trusted
* local directory exists (`<local_path>`)
* remote directory does not exist (`<remote_path>`) unless `--force` is used

## Talking with the daemon

A few commands are available to talk to the daemon with the
`daemon` command:

* **start**: start the daemon
* **stop**: stop the daemon
* **restart**: stop and then start the daemon
* **info**: get a list of current tasks
* **ping**: ping the daemon
* **debug**: toggle debug flag
* **unsync**: stop syncing a specific task
* **resync**: force a full sync of the local directory to the remote one
* **resume**: resume sync from a file

If you prefer not to use the daemon, *cploy* can also be entirely run in the foreground
by using the `--front` switch. However only a single task can be added to it then.

Getting information from the daemon allows to see the different task
running and their id:

```bash
$ cploy daemon info
```

## File exclusion

Files can be excluded from the sync in the monitored directory by using
the `--exclude` switch.
Matching is done using [fnmatch](https://docs.python.org/3.4/library/fnmatch.html).

Example: exclude any hidden files
```
--exclude '*/.*'
```

Example: exclude any files containing *test*
```
--exclude '*/test*'
```

## Sync events

Here is a list of changes that are synchronized on the remote:

* File creation
* File deletion
* File attribute change
* File content modification
* File move

## Run a command on change

A command can be added to a task using the `--command` switch.
The provided command will be run on the remote anytime a change
is applied on the local monitored directory.

*Cploy* uses paramiko channel's
[exec\_command](http://docs.paramiko.org/en/2.4/api/channel.html#paramiko.channel.Channel)
to execute the command which will be run from the default directory of the remote user
(usually `$HOME`).

For example if the remote directory is `/tmp/remote` and the script to
run remotely is located in `/tmp/remote/test.sh`, the command argument
will be `--command="/tmp/remote/test.sh"`.

Currently the specified command is run on any change with no control
over the granularity.

# Save and resume tasks

Each time *cploy*'s daemon is stopped, it will append its running tasks
to `/tmp/cploy/cploy.save`. This file can easily be edited or saved for backup.

*Cploy* can resume tasks from a saved file by calling the `resume` daemon's command
and providing it with a valid saved file.

Here's an example of a saved file's content describing two tasks:
```
sync /tmp/first host1 /tmp/remote --debug --force
sync /tmp/second host2 /tmp/remote --debug --force
```

This also allows to describe tasks in a file directly instead of
calling the command line for each task.
Issuing the following command will load the tasks from `/tmp/sometasks`

```bash
$ cploy daemon resume /tmp/sometasks
```

# Contribution

If you are having trouble installing or using *cploy*, open an issue.

If you want to contribute, feel free to do a PR (please follow PEP8).

Have a look at the *design* directory.

# License

This project is licensed under the terms of the GPLv3 license.
