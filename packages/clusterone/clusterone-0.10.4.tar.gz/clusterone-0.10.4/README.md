# Clusterone CLI

![](https://drone.shared.tools.clusterone.com/api/badges/clusterone/cli/status.svg)

## Installation

0. Clone repository

```sh
    git clone git@github.com:clusterone/cli.git
```

If this step does not work for you than please [connect to Github with SSH](https://help.github.com/articles/connecting-to-github-with-ssh/). 

1. Change directory to CLI folder 
```sh
    cd cli
```

2. Create a virtualenv

```sh
   virtualenv env 
```

3. Activate the virtualenv
```sh
    . env/bin/activate
```

4. Install project dependencies and dev dependencies

```sh
    pip install -e .[dev]
```

Or for zshell users:

```sh
    echo "pip install -e .[dev]" | bash
```


## Working

0. Run work script, this will:
- activate the virtualenv
- set PYTHONPATH
- alias `just` as the package under dev

```sh
    source workon.sh
```

## Testing

- Units
```sh
    pytest
```

- E2E
```sh
    python clusterone/functional_check.py
```

### Mocks

Long mocking literals are stored in `clusterone/mocks`

## Connecting to local main app

```
    just config endpoint http://localhost:8000
```

- Bare in mind this is persistent

## Verbose logging 

```
    export JUST_DEBUG=True
```

- Enable verbose print messages for every request made
- Works for "true" in any case, so "TRUE", "true", "True", "TrUe" are all valid values
- Any other values are considered falsy

## Caution

### Adding new commands

Whenever new command is added please make sure that your it's propperly imported all the way up to `commands` module. We have a test for that, so no worries, just keep that in mind.

Example:
`commands/__init__.py` import `create`, which in it's own `__init__.py` import `project`, which imports `command` from `cmd.py`

### Dependency hell

Clusterone projects depend on `get_data_path()` and `get_logs_path()` from the `clusterone_client` package. We have a test for that, so no worries, just keep that in mind. 

### Passwords in plaintext

ONE. DOES. NOT. SIMPLY. STORE. PASSWORDS. IN. PLAINTEXT. NO. NEVER.

### Global instances

There are global instances used across the CLI of:
- Clusterone client
- Config (persistent between session)
- Session (persistent between invocation)

### Versioning

We follow [semantic versioning](https://semver.org/).
Before new version release please upgrade version number in `__init__.py` 

### Files utilized

- `session.json` in `~/.config/clusterone`
- `justrc.json` in `~/.config/clusterone` (or equivalent on platform other than GNU/Linux)

## Linting and style

### EditorConfig

Please make sure that your editor supports editor config.
Visit [EditorConfig webiste](editorconfig.org/) for details.

### Pylint

Please make sure that you have installed `pylint` on your system 

When to run? TBD
Config? TBD

## Additional naming conventions and note about folder structure

Virtualenv for Python 3 shall is to be named `env`  
Virtualenv for Python 2.7 shall it be needed is to be named `env27`

All commands shall have a coresponding `cmd.py` file located in `Clusterone/commands/([subcommand]/)*/command/`
If additional code [more than few lines and a just client call] is needed for implementing given functionality than a `helper.py` should be utilised and the client call moved to it

`cmd.py` must  contain `command` function that is a click command   
If `helper.py` exists it must contain `main` function that is to be called by `command` from `cmd.py`

### Example

`just create project [args]` has a `cmd.py` located in `clusterone/commands/create/project/`
Additional code is needed for ensuring that tport git remote is created for a project, therefore `helper.py` exists in the same location

