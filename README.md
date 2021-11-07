# Minecraft Analytics

This repo contains tools and configurations for analytics used in the Minecraft
Utopia research project. 

## Installation

First, ensure you have ffmpeg and ffprobe installed. 

This repository has a submodule, the [data repo](https://github.com/cproctor/minecraft-utopia-data). 
When you clone this repo, use `--recurse-submodules` to also check out the
submodule. If you already have this repo cloned, you can initialize and fetch
the submodule with the following commands:

```
$ cd data
$ git submodule init
$ git submodule update
```

*Minecraft Analytics* uses [poetry](https://python-poetry.org/) for dependency
management. After installing poetry, run `poetry install` to install
dependencies and then run `poetry shell` to enter a shell with
a properly-configured path able to access these dependencies. `exit` from the
shell back to your prior shell when finished. 

You will need to update some settings in `invoke.yaml` for your local
environment.

## Running tasks

*Minecraft Analytics* uses [invoke](https://www.pyinvoke.org/) to define and run
tasks. Run `inv --list` to see available tasks and `inv --help <taskname>` for
help on a specific task.

### Getting started

Here's an example of basic usage. In the example below, we sync log files to the
local machine, then resample events by grouping all events per minute, and then
find the player's mean location for each minute. (`NaN` stands for "not a
number"; these values are for periods in which there were no logged events and
it was therefore impossible to calculate a mean.)

```
$ inv sync --world logtest --interact
>>> df
...
>>> loc_cols = [c for c in df.columns if c.startswith('location')]
>>> df[loc_cols].resample('min').mean()
                     location_x  location_y  location_z
timestamp                                              
2021-06-26 19:28:00    5.567797   65.677966  211.813559
2021-06-26 19:29:00         NaN         NaN         NaN
2021-06-26 19:30:00         NaN         NaN         NaN
...                         ...         ...         ...
2021-06-26 20:33:00   40.317972   68.631336  203.539171
2021-06-26 20:34:00   34.492823   67.470494  202.722488
2021-06-26 20:35:00   49.631313   65.315657  218.717172
```

## Architecture

The top-level directories in this repo are:

- **analysis**: Code for producing specific analyses. Most of the work should be
  done by code imported from `lib`.
- **data**: The [Minecraft Utopia submodule](https://github.com/cproctor/minecraft-utopia-data). 
  All personally-identifiable information (including downstream analysis
  products which have not been de-identified) must be contained within this
  repo.
- **export**: Location to store reproducible results of analysis, such as
  figures and tables. Not part of the repo, but will be created as needed.
- **participants**: Documents meant for participants, such as set-up instructions
- **lib**: All generalizable source code lives here. 
- **server**: Code meant for deployment on the server, such as configuration files
- **tasks**: Definitions of [invoke](http://www.pyinvoke.org/) tasks, this package's
  high-level API.
- **tutorial**: Space for stuff meant for team members' learning.

## Next steps

- Select collaboration segments to analyze
  - Specify metadata format
- See if I can find any additional audio resources
- Write joint visual attention code

### The big question

How would we conceptualize and validate high-quality collaboration? 

- Need to read recent ICLS papers on this
