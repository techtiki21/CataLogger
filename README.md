![1780823969374](images/logo.png)

# CataLogger: *AI-Powered Cat Metric Logger*

### Table of Contents

* [Overview](#overview)
* [How it Works](#how-it-works)
* [Features](#features)
* [Usage](#usage)

## Overview

Keeping track of your cat's health can be difficult, especially when changes happen gradually over time. CataLogger is a CLI tool that lets you log daily metrics like weight, activity, appetite, water intake, and litter habits for each of your cats. When you want to check in on how they're doing, the built-in AI analyzes the logged data and provides a clear health overview, highlighting trends and flagging anything that might need a vet visit.

*(Built for the HacktheKitty hackathon)*

## How it Works

The CLI is built with *Python* and *SQLite3.* It uses the third-party library `Click` to allow the user to interact with the script via a command line along with supporting user inputs as arguments. The user runs the main `.exe`  by using it in the Windows Terminal or using the `main.py` script in other supported operating systems. There are 3 Python scripts found in the source code;

* `main.py`: The link between the user (front-end) and the other scripts (back-end).
* `sql.py`: Handles all connections with the database. (stored locally as `cat-a-log.db`)
* `analyze.py`: Contains all the AI connections. (uses `groq` as the main endpoint, `llama-3.3-70b-versatile` as the AI model)

When the user uses the app for the first time, they would probably think to add their cat as an entry to the database first before logging. When they use the `add-entry` command, this is what happens on the backend;

1. The arguments the user passed in (*name, birth date, breed*) will be received by `main.py`.
2. It then passes the arguments to `sql.py`, and runs the `addEntry` function.
3. The function executes a SQL command `INSERT` with `cursor.execute`. Using the '?' placeholders is good practice as it prevents [SQL Injection.](https://en.wikipedia.org/wiki/SQL_injection)
4. The code block runs, but if the cat already exists inside the database, a `sqlite3.IntegrityError` is returned, indicating the cat's name is already recorded. (better hope you don't have multiple cats with the same name!)
5. It prints a confirmation statement, informing the user that the cat has been added to the database.

So in short: `command is run -> passed into SQL INSERT command -> checks for existing entries -> prints confirmation`

When the user wants to log their cat's daily metrics using the `log` command:

`command is run → input validated → user confirms → INSERT into log table → prints confirmation`

When the user wants an AI-generated health overview using the `overview` command:

`command is run → fetches logs from SQLite → sends to llama-3.3-70b via Groq → streams health overview to terminal`

## Features

* Contains a `log` command, which takes in arguments directly from the terminal, or prompts the user for them if some values are not given.
* An `overview` can be provided of a specific cat, using Llama 3.3 to analyze the `.db`.

## Usage

### `add-entry`

Add one of your feline companions to your local database.


| Arguments | Explanation                                            | Required |
| :-------: | ------------------------------------------------------ | -------- |
| `--name` | Name of the cat you want to add                        | YES      |
| `--birth` | When your cat was born (Best formatted as`YYYY-MM-DD`) | NO       |
| `--breed` | Breed of your cat                                      | NO       |

### `log`

Log health metrics of a specific cat.

*(If an argument is not provided when the command is initially run, the CLI will prompt you to insert it via an `input` box.)*


| Arguments    | Explanation                                                                           | Required |
| ------------ | ------------------------------------------------------------------------------------- | -------- |
| `--cat`      | Name of the cat you want to log (case-sensitive)                                      | NO       |
| `--weight`   | Current weight of the cat in kilograms                                                | NO       |
| `--activity` | How active the cat is on a scale of 1-5                                               | NO       |
| `--appetite` | How hungry is the cat:`None, (N)ormal, (L)ow, (H)igh`                                | NO       |
| `--water`    | How much water does the cat drink:`None, (N)ormal, (L)ow, (H)igh`                    | NO       |
| `--litter`   | Litter of the cat:`(N)ormal, (S)training, (D)iarrhea, (C)onstipated`                 | NO       |
| `--notes`    | Extra notes the AI can use to better its understanding of the cat's current situation | NO       |

### `list-cats`

Prints out all cats currently stored in the database alongside their birth dates and breeds.

### `overview`

Uses AI to create a health overview by checking the logged metrics of the cat you selected.

*(The AI can make mistakes, so contact a certified veterinarian before acting upon things the AI has said to do)*


| Arguments | Explanation                                       | Required |
| --------- | ------------------------------------------------- | -------- |
| `--cat`   | The cat you want the AI to provide an overview on | NO       |
