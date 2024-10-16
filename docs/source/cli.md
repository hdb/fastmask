# fastmask CLI

Command line interface for managing Fastmail masked emails

```text
fastmask [OPTIONS] COMMAND [ARGS]...

  Manage Fastmail masked email from the command line

Options:
  --version        Show the version and exit.
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

## Authentication

You will need to provide an API token for fastmask to authenticate calls to the Fastmail API:

1. In the Fastmail web client, go to `Settings` > `Account` > `Password & Security` > `API Tokens` > `Manage` > `New API token`
2. Set name to "fastmask" or whatever you'd like, check only the `Masked Email` scope and hit `Generate API token`
3. Copy the API token. You can authenticate either by providing your credentials as arguments, or by using the `FM_ME_TOKEN` and `FM_USERNAME` environment variables / providing these variables via `.env` file:

You can skip parsing `.env` with `python-dotenv` by setting the environment variable `SKIP_PYTHONDOTENV=1`.

Example:

```bash
export FM_ME_TOKEN='YOUR-TOKEN-HERE'
export FM_USERNAME='username@fastmail.com'

fastmask list --limit 5

# alternatively, you can provide your credentials as arguments
fastmask --username username@fastmail.com --token 'YOUR-TOKEN-HERE' \
  list --limit 5
```

## Create a masked email

Use `fastmask new` to create a new masked email address. Optionally specifiy the description, URL or domain.

Example:

```bash
fastmask new twitter --url twitter.com

> Successfully added email fake.email1234@fastmail.com (id: masked-12345678)
```

## List

`fastmask list` will return a Rich table, json, or csv of masked emails, optionally filtering results by active/blocked state, recent, used/unused status, etc.

Usage:

```text
fastmask list [OPTIONS]

  List masked emails associated with account

Options:
  --limit INTEGER                 Limit number of results
  --active                        Show only active addresses
  --blocked                       Show only blocked addresses
  --unused                        Show only active + unused addresses
  --used                          Show only used addresses
  --deleted                       Show only deleted addresses
  --sort                          Field to sort by
  --desc / --asc                  Sort order
  --recent INTEGER                Only show items from the past X days
  -j, --json                      Print to json instead of table
  -o, --out TEXT                  Output to csv or json file
  --help                          Show this message and exit.
```

Examples:

```bash
fastmask list --unused
```

```bash
fastmask list --blocked --limit 20 --json
```

```bash
fastmask list --sort lastMessageAt --desc --active
```

## Activate / Block / Delete

You can change the state of a masked email with `fastmask activate`, `fastmask block` or `fastmask delete`. Email IDs accepted are:
  
- email address
- description (case-insensitive)
- the id of the address, with or without the "masked-" prefix

Examples:

```bash
fastmask activate new.mail0412@fastmail.com
```

```bash
fastmask block masked-12312345
```

```bash
fastmask delete facebook.com
```

## Edit

`fastmask edit` can be used to change the description, url or domain associated with masked email address.

Example:

```bash
fastmask edit some.user1231@fastmail.com --description x.com --url x.com
```

## Search

`fastmask search` is a case-insensitive search defaulting to matching email addresses and descriptions. You can set the fields searches using the `--field` flag.

Examples:

```bash
fastmask search reddit
```

```bash
fastmask search --field email fastmail.com
```

```bash
fastmask search --field createdAt 2022-10-31
```

```bash
fastmask search --field createdBy fastmask -o out.csv
```
