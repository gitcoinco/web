# Contributing to Gitcoin

Contributions to gitcoin could come in different forms. Some contribute code
changes, others contribute docs, others help answer questions from users, help
keep the infrastructure running,

We welcome all contributions from folks who are willing to work in good faith
with the community. No contribution is too small and all contributions are
valued.

* [Code of Conduct](#code-of-conduct)
* [Issues](#issues)
* [Discussions And General Help](#discussions-and-general-help)
* [Pull Requests](#pull-requests)
  * [Step 1: Fork](#step-1-fork)
  * [Step 2: Branch](#step-2-branch)
  * [Step 3: Code](#step-3-code)
  * [Step 4: Commit](#step-4-commit)
  * [Step 5: Rebase](#step-5-rebase)
  * [Step 6: PRs](#step-6-prs)

## Code of Conduct

Contributions to Gitcoin are governed by the [Contributor Covenant version 1.4](https://www.contributor-covenant.org/version/1/4/code-of-conduct.html).
All contributors and participants agree to abide by its terms. To report
violations, shoot out an email to founders@gitcoin.co

The Code of Conduct is designed and intended, above all else, to help establish
a culture within the project that allows anyone and everyone who wants to
contribute to feel safe doing so.

Open, diverse, and inclusive communities live and die on the basis of trust.
Contributors can disagree with one another so long as they are done in good
faith and everyone is working towards a common goal.

## Issues

Issues in `gitcoin/web` are the primary means by which bug reports and
general discussions are made. A contributor is allowed to create an issue,
discuss and provide a fix if needed.

## Discussions And General Help

As Gitcoin is still at its early stages, drop by
[gitcoin.co/slack](gitcoin.co/slack) and say hi to know what's next / to get
your answers cleared up.

## Pull Requests

Pull Requests are the way in which concrete changes are made to the code and
documentation.

## Prerequisites

You must install [pre-commit](https://pre-commit.com/#install) in order to enable our
precommit hooks and `pre-commit install` from your `gitcoinco/web` root directory.

In order to make use of the `pre-commit` hooks used for this repository, you should have a valid installation of `node`/`npm`, `isort` (`pip install isort`), `stylelint` (`npm install -g stylelint`), and `eslint` (`npm install -g eslint`).

User facing copy / text should be run through [Django Translation Framework](https://docs.djangoproject.com/en/2.0/topics/i18n/translation/). For example,

1. HTML user-facing pieces of copy are in `{% blocktrans %}` or `{% trans %}` fields.
2. javascript user-facing pieces of copy are in `ngettext` fields.
3. each of the `views.py` user-facing pieces of copy are in `gettext_lazy` fields
4. each of the models `help_text`s are internationalized
5. as are all the emails in `marketing/mails.py`

### Step 1: Fork

Fork the project [on GitHub](https://github.com/gitcoinco/web) and clone your
fork locally.

```shell
git clone git@github.com:username/web.git
cd web
git remote add upstream https://github.com/gitcoinco/web.git
git fetch upstream
```

### Step 2: Branch

It's always better to create local branches to work on a specific issue. Makes
life easier for you if you are the kind who enjoys multiple things parallely.
These should also be created directly off of the `master` branch.

```shell
git checkout -b my-branch -t upstream/master
```

### Step 3: Code

To keep the style of the Javascript code consistent we have a basic linting configured. To check your contributed code for errors run `npm run eslint`. To make life easy use the automatic fixing by running `npm run eslint:fix` before your commit.

* Use the pre-configured eslint for Javascript
* Avoid trailing whitespace & un-necessary white lines
* Indentation is as follows
  * 1 tab = 2 spaces for `.html` and `.js` files
  * 1 tab = 4 spaces for everything else
* Use `rem` for CSS when applicable
* Add relevant unit tests for all new Python logic and update existing tests to accommodate new logic.

### Step 4: Commit

1. Ensure your code changes adhere to our styling and linting standards: `npm run eslint:fix; npm run stylelint:fix; isort -rc --atomic .`
2. List all your changes as a list if needed else simply give a brief
  description on what the changes are.
3. All lines at 100 columns.
4. If your PR fixed an issue, Use the `Fixes:` prefix and the full issue URL.
  For other references use `Refs:`.

    _Examples:_
    * `Fixes: https://github.com/gitcoinco/web/issues/87`
    * `Refs: https://github.com/gitcoinco/web/issues/91`

5. _Sample commit A_
    ```txt
    if you can write down the changes explaining it in a paragraph which each
    line wrapped within 100 lines.

    Fixes: https://github.com/gitcoinco/web/issues/87
    Refs: https://github.com/gitcoinco/web/issues/91
    ```

    _Sample commit B_
    ```txt
    - list out your changes as points if there are many changes
    - if needed you can also send it across as
    - all wrapped within 100 lines

    Fixes: https://github.com/gitcoinco/web/issues/87
    Refs: https://github.com/gitcoinco/web/issues/91
    ```
6. [Squashing](https://git-scm.com/book/en/v2/Git-Tools-Rewriting-History) and [Merging](https://git-scm.com/docs/git-merge) your commits to make our history neater is always welcomed, but squashing can be handled during the merge process.

### Step 5: Rebase

Ensure you neat description on what your PR is for, so that it's
easier for folks to understand the gist of it before jumping to the
the code / doc.

As a best practice, once you have committed your changes, it is a good idea
to use `git rebase` (not `git merge`) to ensure your changes are placed at the
top. Plus merge conflicts can be resolved

```shell
git fetch upstream
git rebase upstream/master
```

### Step 6: PRs

Please ensure that your pull request follows all of the community guidelines to include:

* Title is descriptive and generally focused on what the PR addresses (If your PR is a work in progress, include `WIP` in the title. Once the PR is ready for review, please remove `WIP`)
* Description explains what the PR achieves or addresses
* If the PR modifies the frontend in any way, please attach screenshots and/or GIFs of all purposeful changes (before and after screens are recommended)
* The PR passes all CI checks, to include Stickler, codecov, and Travis.

## FAQ

### Contributing Static Assets

Note: Please remember to optimize/compress your image assets via: `make compress-images` (Requires: jpeq-recompress, optipng, and svgo in `PATH`)
You can install the necessary binaries via:

- `npm install -g jpeg-recompress-bin pngquant-bin svgo`
- `brew install optipng`

Q: `I need to add static assets...  Where to I put them?`

All assets that will be used as static resources must be placed into their appropriate place in the `app/assets` directory.

Q: `I've added the new assets to the appropriate directory, but can't seem to use them. How do I make Django recognize my newly added assets?`

Run: `make collect-static` if using Docker or `cd app; python3 manage.py collectstatic -i other` for virtualenv/local setup.

Additionally, you can check out the [Django Managing Static Files Documentation](https://docs.djangoproject.com/en/2.0/howto/static-files/)

<img src='https://d3vv6lp55qjaqc.cloudfront.net/items/263e3q1M2Y2r3L1X3c2y/helmet.png'/>
Welcome to the gitcoin community. Lets Grow Open Source Software.
