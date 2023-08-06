# Simple program to connect to servers from a list.

This is a simple program to load servers from a file, list them, then allow you to login, SSH mount, etc.

Features provided by a terse command line syntax:

* Login using a terminal instance on the command line via SSH.
* Invoke an xterm on a configured host.
* Mount and unmount a [SSH Fuse] directory.
* Invoke a [Emacs] session via SSH.
* Print environment in a [bash] `export` format for scripting.

Other commands are easily configurable in [cli.py](python/zensols/hostcon/cli.py).


## Obtaining

The easist way to install the command line program is via the `pip` installer:
```bash
pip install zensols.hostcon
```


## Usage

First, create a configuration file.  Examples used by the test cases are
given [here](test-resources).  Below is a simple example that declares an SSH
host `jove` on the (default) port 22 with [SSH Fuse] mount options convenient for
a MacOS client.

```ini
[default]
host_name=jove
ssh_port=22
ssh_switches=-X -Y
mount_options=reconnect,sshfs_sync,no_readahead,sync_read,cache=no,noreadahead,noubc,noappledouble,noapplexattr
```

Save this example to `~/.hostconrc` or anywhere else specified in environment
variable `HOSTCONRC`.  Now we can get include this as environment:

```bash
$ hostcon env
export DOMAIN=None
export HOST_NAME=jove
export SSH_PORT=22
export USER_NAME=someuser
```

Start an XTerm on the host:

```bash
$ hostcon
invoking ssh -X -Y -f -p 22 someuser@jove /usr/bin/xterm
```

See the [test cases](test/python/tests.py) for more examples of how to
configure and *alias* host information.


### Help

The usage is given with `-h`:

```sql
$ hostcon
Usage: hostcon <list|...> [options]

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -s, --short           short output for list
  -w NUMBER, --whine=NUMBER
                        add verbosity to logging
  -n HOST_NAME, --hostname=HOST_NAME
                        the host to connect to
  -d, --dryrun          dry run to not actually connect, but act like it
```


## Changelog

An extensive changelog is available [here](CHANGELOG.md).


## License

Copyright © 2018 Paul Landes

Apache License version 2.0

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

[http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0)

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.


<!-- links -->
[SSH Fuse]: https://github.com/libfuse/sshfs
[Emacs]: https://www.gnu.org/software/emacs/
[bash]: https://www.gnu.org/software/bash/
