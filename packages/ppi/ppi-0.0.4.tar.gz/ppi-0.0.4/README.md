# PPI -- publisher for pypi

A command line tool help you to publish your python project on github and pypi.

## Usage

```
$ ppi --help

Usage: ppi [OPTIONS] COMMAND [ARGS]...

Options:
  --debug / --no-debug
  --help                Show this message and exit.

Commands:
  build
  config   Config ppi.json
  init     Initialize a ppi.json file
  publish  Publish to github, pypi
  update   Update a new version
```


### Step by Step

```bash

you can do this three command to publish a new version

# update to a new version
$ ppi update

# build the file
$ ppi build

# push dist/{version}.tar.gz file to pypi
$ ppi publish

or you can do three command above in one command

# do all steps in one command
$ ppi one

# do the aborted one command
$ ppi contiue
```

## LICENSE

MIT Copyright (c) 2018 jeremaihloo

