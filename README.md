# whatsup - Simple daily task tracker (WIP)

[![pdm-managed](https://img.shields.io/badge/pdm-managed-blueviolet)](https://pdm.fming.dev)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)


## Philosophy (WIP)
- Every day you have no more than **3 tasks**
- Default deadline for a task - **24 hours**
- Priority of daily tasks is set of **{1, 2, 3}**, so you have clear order of tasks
- Program is running in **shell**. No registration, no internet, no javascript

### What problem does this tool solve
<img src="./img/whatsup.png" width="400"/>

## Installation

1. A good way - install using pipx as a global package in an isolated environment. command: `pipx install link_to_github??`
2. Rye is also capable of installing isolated global packages, but I haven't tried it
3. ...

## Features

List of current tasks (wup is a shortcut):
```commandline
wup
whatsup show
```
Add a task:
```commandline
whatsup add 'task description' --priority 3
```
Mark the task as done:
```commandline
whatsup done task_num
```
Remove the task:
```commandline
whatsup rm task_num
```
Show archived tasks:
```commandline
whatsup arc
```

## Development
1. `cd` into a folder and make a virtualenv: `virtualenv .venv` or `python3 -m venv .venv`
2. Activate virtualenv: `. .venv/bin/activate`
3. [Install PDM](https://pdm.fming.dev/latest/#recommended-installation-method)
4. `pdm install`
5. `pre-commit install`
6. `pipx install --editable .` to actually use this tool while editing source code
7. **Merge with main branch using PR**

## Demo

I know, there's a bug in column ts_archived displaying UTC time, I fixed that

https://github.com/pyrogn/whatsup/assets/60060559/ee3ae3aa-0a67-44da-a899-c6d6f343a960

## TODO
- [x] Add basic tests
- [ ] Add daily stats on (in)completed tasks
- [ ] Make all tasks functionality available in CLI
- [ ] Make location of db stable and cross-platform
- [x] Add better string formatting
- [ ] Add constraints (a number of tasks, average priority, deadline)

## Experiments
- [x] Learn how to juggle multiple PRs and how issues are linked to PR
- [ ] Make this library available as package (not necessary PyPI)

## The Why
- To build with Python something useful and practical
- To use this tool for personal productivity
- To learn intricacies of managing a DB (although a very simple one)

## What's next? (possibilities)
- Add repeating tasks
- A tool for managing long-term plans
- A tool with hierarchical structure for big tasks
- Rewrite this to another language
