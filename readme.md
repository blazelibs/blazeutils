# BlazeUtils

[![nox](https://github.com/blazelibs/blazeutils/actions/workflows/nox.yaml/badge.svg)](https://github.com/blazelibs/blazeutils/actions/workflows/nox.yaml)
[![codecov](https://codecov.io/gh/blazelibs/blazeutils/branch/master/graph/badge.svg)](https://codecov.io/gh/blazelibs/blazeutils)


## Introduction

BlazeUtils was originally developed as a library to hold common tools for the
[Blaze library family](https://github.com/blazelibs/).

Over the years it has expanded to be a catch-all for tools commonly used by the
[Level 12](https://level12.io/) development team.


## Questions and comments

Please visit the
[Blaze libraries discussion group](http://groups.google.com/group/blazelibs).


## Current status

The code and API stay fairly stable.

Source code and the issue tracker are on
[GitHub](https://github.com/blazelibs/blazeutils/).


## Development


### Copier Template

Project structure and tooling mostly derives from
[Coppy](https://github.com/level12/coppy). See its documentation for context and
additional instructions.

This project can be updated from the upstream repo, see
[Updating a Project](https://github.com/level12/coppy?tab=readme-ov-file#template-updates).


### Project Setup

From zero to hero (passing tests that is):

1. Ensure [host dependencies](https://github.com/level12/coppy/wiki/Mise) are installed

2. Start docker service dependencies (if applicable):

   `docker compose up -d`

3. Sync [project](https://docs.astral.sh/uv/concepts/projects/) virtualenv w/ lock file:

   `uv sync`

4. Configure prek:

   `prek install`

5. Run tests:

   `nox`


### Versions

Versions are date based. A `version` task shows and bumps versions:

```shell

  # Show current version
  mise run version show

  # Bump version based on date, tag, and push:
  mise run version bump

  # See other options
  mise run version -- --help
```
