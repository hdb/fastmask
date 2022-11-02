# Fastmask

Python library and CLI for Fastmail's Masked Email

## Install

`pip install fastmask`

## Usage

```text
fastmask [OPTIONS] COMMAND [ARGS]...

  Manage Fastmail masked email from the command line

Options:
  --username TEXT  [default: (FM_USERNAME)]
  --token TEXT     [default: (FM_ME_TOKEN)]
  --help           Show this message and exit.

Commands:
  activate  Set state of masked email to Active
  block     Set state of masked email to Blocked
  delete    Delete masked email
  edit      Edit information associated with a masked email
  list      List masked emails associated with account
  new       Create a new masked email
  search    Search for masked emails
```
