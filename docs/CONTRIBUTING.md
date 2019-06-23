# Contributing to Gitcoin

Contributions to gitcoin could come in different forms. Some contribute code
changes, others contribute docs, others help answer questions from users, help
keep the infrastructure running,

We welcome all contributions from folks who are willing to work in good faith
with the community. No contribution is too small and all contributions are
valued.

* [Monetization Policy](#monetization-policy)
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
* [Python](#python)
  * [Docstrings](#docstrings)
    * [Classes](#classes)
    * [Methods](#methods)
    * [Example](#example)
  * [VSCode Remote Debugger](#vscode-remote-debugger)
    * [VSCode Prerequisites](#vscode-prerequisites)
    * [Add Launch Configuration](#add-launch-configuration)
    * [VSCode Additional Resources](#additional-vscode-resources)
  * [Additional Resources](#additional-resources)
* [FAQ](#faq)
  * [Contributing Static Assets](#contributing-static-assets)

## Monetization Policy

This repo uses [Gitcoin](https://gitcoin.co) to incentivize contributions from contributors all around the world.

We believe that properly incentivizing Open Source Software means providing funding to support contributors, but we also recognize the dangerous precedent that is set when contributors who have been contributing for intrinsic reasons begin to expect extrinsic rewards for their contributions.

Gitcoin has written about this, in the abstract, [here](https://medium.com/gitcoin/building-a-platform-that-maximizes-freedom-1149968a7b05). Tangibly, our *monetary policy* is:

1. Our mission is to "Grow Open Source".  [Read More about our Mission here](https://gitcoin.co/mission).
2. We believe that contributors should contribute for intrinsic reasons first (see mission statement above), and we hereby provide notice that we will not be able to fund all contributions.  Appreciate it if and when a Tip comes!
3. Scope that is explicitly funded upfront will be posted to the Github Issue by [@gitcoinbot](https://github.com/gitcoinbot), and will also be posted to the [Gitcoin Issue Explorer](https://gitcoin.co/explorer).


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
discuss, and provide a fix if needed.

Before opening an issue, check to see if there are any current issues with similar key words. This helps us cut down on duplicate tickets.

When you [open an issue](https://github.com/gitcoinco/web), you'll notice four templates (bug, custom, discussion, feature) with the user-story format we like for our issue reports. When starting a new issue, please do your best to be as detailed and specific as possible.

1. Bug report - use this to create a bug report to help us improve Gitcoin
2. Discussion - use this template to start a discussion
3. Feature request - use this to suggest a project idea
4. Custom report - use this to report an issue that doesn't fall under any other category

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

In order to make use of the `pre-commit` hooks used for this repository, you should have a valid installation of `node`/`npm`, `isort` (`pip install isort`), `yapf` (`pip install yapf`), `stylelint` (`npm install -g stylelint`), and `eslint` (`npm install -g eslint`).

User facing copy / text should be run through [Django Translation Framework](https://docs.djangoproject.com/en/2.0/topics/i18n/translation/). For example,

1. HTML user-facing pieces of copy are in `{% blocktrans %}` or `{% trans %}` fields.
2. javascript user-facing pieces of copy are in `gettext` fields.
3. each of the `views.py` user-facing pieces of copy are in `gettext_lazy` fields
4. each of the models `help_text`s are internationalized
5. as are all the emails in `marketing/mails.py`
6. run `make autotranslate` or a combination of the necessary `./manage.py makemessages` and `./manage.py compilemessages` commands.

If you are contributing user-facing assets, interface components or other relevant visuals,
then please add them to our UI Inventory page.

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
* Add relevant unit tests for all new Python logic and update existing tests to accommodate new logic.  You can run tests via: `make pytest`
* If you introduce new backend methods or classes, you must include docstrings that conform to PEP-257 and follow the existing patterns throughout the codebase.  See `app/avatar/(models|views|utils).py`  - If you introduce a new django module, like: `avatar` or `marketing`, you must update `pydocmd.yaml` to include relevant python modules from the newly introduced app.

### Step 4: Commit

1. Ensure your code changes adhere to our styling and linting standards: `npm run eslint:fix; npm run stylelint:fix; isort -rc --atomic .`
2. List all your changes as a list if needed else simply give a brief description on what the changes are.
3. All lines at 100 columns.
4. If your PR fixed an issue, Use the `Fixes:` prefix and the full issue URL. For other references use `Refs:`.

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
* The PR passes all CI checks, to include: Stickler, and Travis CI.
* If tests are failing or coverage is decreased while adding logic to any backend code, you will be asked to include relevant tests and your PR will not be merged until all checks pass.

## Python

### Docstrings

Gitcoin attempts to adhere to [PEP-257](https://www.python.org/dev/peps/pep-0257/) while employing the [Google Python Style Guide](https://github.com/google/styleguide/blob/gh-pages/pyguide.md#38-comments-and-docstrings) approach to docstring formatting.

#### Classes

```python
class Gitcoin:
    """Define the overall Gitcoin object.

    Attributes:
        repo (str): The Gitcoin repository.

    """

    repo = 'gitcoinco/web'

```

#### Methods

```python
def foo(bar='bar'):
    """Handle string concatenation of the provided suffix.

    Args:
      bar (str): The foo suffix. Defaults to: bar.

    Attributes:
      foobar (str): The foo string concatentated with the provided bar variable.

    Returns:
      str: The concatenated string.

    """
    foobar = f'foo{bar}'
    return foobar
```

#### Example

```python
from __future__ import braces


class Example:
    """Define the overall Example object."""

    # Class attributes.
    repo = 'gitcoinco/web'
    known_dances = ['tango']

    def example(self):
        """Some Example.example class method docstring.

        Returns:
            bool: Whether or not the Example performs the specified dance.

        """
        return 'example'

    def example2(self):
        """Some Example.example2 class method docstring.

        Attributes:
            var (str): The example2 variable.

        """
        var = 'example2'

def can_dance(example, dance='tango'):
    """Handle determining whether or not Example can perform the provided dance.

    Args:
        dingo (dashboard.Example): The Example object.
        dance (str): The dance type.  Defaults to: tango.

    Returns:
        bool: Whether or not the Example performs the specified dance.

    """
    return dance in example.known_dances


def example3(self):
    """Some example3 method docstring.

    Attributes:
        var (str): The example3 variable.

    Returns:
        str: The example var text.

    """
    var = 'example3'
    return var
```

### VSCode Remote Debugger

One benefit of using VSCode is the built-in debugger and you can use the vscode debugger with Gitcoin!

You must complete all prerequisite steps, add the `launch.json` configuration snippet, and ensure the Gitcoin `web` docker container is running.

If this is your first time using the debugger, it's advised that you stop your existing docker-compose services: `docker-compose down`, add the necessary environment variable to `.env`, and rebuild the `web` image via: `docker-compose build web` or `docker-compose up -d --build` to additionally start the services following the build.

Once you have completed all of the below outlined steps, you should be able to start debugging!

#### VSCode Prerequisites

* [VSCode Python support extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python) is installed.
* [Gitcoin Docker Setup](https://docs.gitcoin.co/mk_setup/) has been completed.
* Add `VSCODE_DEBUGGER_ENABLED=on` to your `.env` file. (This envvar *must* be added before downing/starting the compose services in order for the necessary `ptvsd` req to be installed)

*Please note: Completely restart the docker-compose services (`docker-compose down; docker-compose up -d`) following successful completion of all steps.*

#### Add Launch Configuration

In order to use the vscode remote debugger for the Gitcoin Django app, you must add the below snippet to your Python debugger `launch.json` configuration.
You can do this by:

* Switch to the Debugging tab (`⇧⌘D`)
* Select `Add Configuration...` from the dropdown menu
* Add the following json snippet to the `configurations` array and save the file:

```json
{
    "name": "Gitcoin Remote Debugger",
    "type": "python",
    "request": "attach",
    "localRoot": "${workspaceRoot}",
    "remoteRoot": "/code",
    "port": 3030,
    "host": "localhost"
}
```

#### Additional VSCode Resources

* [VSCode Debugging Overview](https://code.visualstudio.com/docs/editor/debugging)
* [VSCode Debugging Intro Video](https://code.visualstudio.com/docs/introvideos/debugging)

### Additional Resources

We either strongly employ or encourage the review and implementation of the following resources:

* [Python Style Guide: PEP-8](https://www.python.org/dev/peps/pep-0008/)
* [The Zen of Python: PEP-20](https://www.python.org/dev/peps/pep-0020/)
* [Docstrings: PEP-257](https://www.python.org/dev/peps/pep-0257/)
* [Docutils: PEP-258](https://www.python.org/dev/peps/pep-0258/)
* [f-strings: PEP-498](https://www.python.org/dev/peps/pep-0498/)
* [Google Python Style Guide](https://github.com/google/styleguide/blob/gh-pages/pyguide.md)
* [Hitchhiker's Guide to Python](http://docs.python-guide.org/)
* [Django Documentation](https://docs.djangoproject.com/)

## FAQ

### Contributing Static Assets

Note: Please remember to optimize/compress your image assets via: `make compress-images` (Requires: jpeq-recompress, optipng, and svgo in `PATH`)
You can install the necessary binaries via:

* `npm install -g jpeg-recompress-bin pngquant-bin svgo`
* `brew install optipng`

Q: `I need to add static assets...  Where to I put them?`

All assets that will be used as static resources must be placed into their appropriate place in the `app/assets` directory.

Q: `I've added the new assets to the appropriate directory, but can't seem to use them. How do I make Django recognize my newly added assets?`

Run: `make collect-static` if using Docker or `cd app; python3 manage.py collectstatic -i other` for virtualenv/local setup.

Additionally, you can check out the [Django Managing Static Files Documentation](https://docs.djangoproject.com/en/2.0/howto/static-files/)

<img src='https://d3vv6lp55qjaqc.cloudfront.net/items/263e3q1M2Y2r3L1X3c2y/helmet.png'/>
Welcome to the gitcoin community. Lets Grow Open Source Software.
