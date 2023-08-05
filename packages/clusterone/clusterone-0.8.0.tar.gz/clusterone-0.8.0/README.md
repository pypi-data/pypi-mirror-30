# Clusterone CLI Readme

## Development

### Installation

0. Clone repository

```sh
    git clone [github_link] 
```

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
    pip3 install -e .[dev]
```

### Working

0. Run work script, this will:
- activate the virtualenv
- set PYTHONPATH
- alias `just` as the package under dev

```sh
    source workon.sh
```

### Testing

- Units
```sh
    pytest
```

- E2E
```sh
    python clusterone/functional_check.py
```

### Connecting to local main app

```
    export JUST_LOCAL=True
```

- This will change the API target to http://localhost:8000 (default for main app in dev mode) and enable verbose log messages on every request.
- Works for "true" in any case, so "TRUE", "true", "True", "TrUe" are all valid values
- Any other values are considered falsy

### Caution

#### Adding new commands

Whenever new command is added please make sure that your it's propperly imported all the way up to `commands` module. We have a test for that, so no worries, just keep that in mind.

Example:
`commands/__init__.py` import `create`, which in it's own `__init__.py` import `project`, which imports `command` from `cmd.py`

#### Dependency hell

Clusterone projects depend on `get_data_path()` and `get_logs_path()` from the `clusterone_client` package. We have a test for that, so no worries, just keep that in mind. 

#### Passwords in plaintext

ONE. DOES. NOT. SIMPLY. STORE. PASSWORDS. IN. PLAINTEXT. NO. NEVER.

### Versioning

We follow [semantic versioning](https://semver.org/).

### Linting and style

#### EditorConfig

Please make sure that your editor supports editor config.
Visit [EditorConfig webiste](editorconfig.org/) for details.

#### Pylint

Please make sure that you have installed `pylint` on your system 

When to run? TBD
Config? TBD

### Additional naming conventions and note about folder structure

Virtualenv for Python 2.7 shall it be needed is to be named `env27`

All commands shall have a coresponding `cmd.py` file located in `Clusterone/commands/([subcommand]/)*/command/`
If additional code [more than few lines and a tport client call] is needed for implementing given functionality than a `helper.py` should be utilised and the client call moved to it

`cmd.py` must  contain `command` function that is a click command
If `helper.py` exists it must contain `main` function that is to be called by `command` from `cmd.py`

#### Example

`tport create project [args]` has a `cmd.py` located in `Clusterone/commands/create/project/`
Additional code is needed for ensuring that tport git remote is created for a project, therefore `helper.py` exists in the same location

