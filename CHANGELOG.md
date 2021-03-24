# Changelog

## 1.0.8
- Build system improvements, reuse makefile commands in circle ci

## 1.0.7
- Remove `selected: true` by default from the catalog [#8](https://github.com/singer-io/tap-nikabot/pull/8)

## 1.0.6
-  Remove cutoff days feature [#2](https://github.com/singer-io/tap-nikabot/pull/2)
    * feat: Adding version command line argument
    * feat: Removing cutoff days feature as it's confusing and unused
    * test: Fix test and linting errors
    * feat: Raise error when unsupported replication method selected
    * docs: Update README to remove cutoff days, bump version to 1.0.3
    * chore: Update default catalog.json to use FULL_TABLE for records
    * ci: Revert use of Makefile in ci, fix dev dependency versions
    * style: Implementing isort to tidy up imports
    * fix: Fix date issue in python 3.6.2. Add clean task to Makefile

## 1.0.5
- Fix setup.py to not specify drescription to avoid issues with deploy script
- Incorporate make lint and make test into circle

## 1.0.4
- Preparing for alpha release

## 1.0.2

- Applying `Transformer().transform` to record before writing to the stream, changes RFC date format slightly from `2019-08-20T00:00:00+00:00` to `2019-08-20T00:00:00Z`.

## 1.0.1

- Initial release
