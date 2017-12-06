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
general discussions are made. An contributor is allowed to create an issue,
discuss and provide a fix if needed.

## Discussions And General Help
As Gitcoin is still at it's early stages, drop by [gitcoin.co/slack](gitcoin.co/slack)
and say hi to know what's next / to get your answers
cleared up.

## Pull Requests
Pull Requests are the way in which concrete changes are made to the code and
documentation.

### Step 1: Fork

Fork the project [on GitHub](https://github.com/gitcoinco/web) and clone your
fork locally.

```text
$ git clone git@github.com:username/web.git
$ cd web
$ git remote add upstream https://github.com/gitcoinco/web.git
$ git fetch upstream
```

### Step 2: Branch

It's always better to create local branches to work on a specific issue. Makes
life easier for you if you are the kind who enjoys multiple things parallely.
These should also be created directly off of the `master` branch.

```text
$ git checkout -b my-branch -t upstream/master
```

### Step 3: Code

As of now, we don't have any sort of design style / lint to validate things.
So we ask you to ensure all these are met before you shoot out a PR.
- Avoid trailing whitespace & un-necessary white lines
- Indentation is as follows
  - 1 tab = 2 spaces for `.html` files
  - 1 tab = 4 spaces for everything else

### Step 4: Commit

1. The first line should:
   - contain a short description of the change (preferably 50 characters or less
     and no more than 72 characters)
   - be prefixed with the name of the changed subsystem and start with an
   imperative verb.
   - If your commit can be explained in one line, then you can skip whats below

   __Examples:__
   - `doc: updated README.md`
   - `ui: added design for testimonial page`

2. Keep the second line blank.
3. Wrap all other lines at 72 columns.
4. If your PR fixed an issue, Use the `Fixes:` prefix and the full issue URL.
  For other references use `Refs:`.

   __Examples:__
   - `Fixes: https://github.com/gitcoinco/web/issues/87`
   - `Refs: https://github.com/gitcoinco/web/issues/91`

5. Sample commit
   ```txt
   subsystem: explain the commit in one line

   - list out your changes as points if there are many changes
   - if needed you can also send it across as

   Fixes: https://github.com/gitcoinco/web/issues/87
   Refs: https://github.com/gitcoinco/web/issues/91
   ```
6. Ensure your squash your commit to make our history neater and reviewing
   easier.

### Step 5: Rebase

Ensure you neat lil description on what your PR is for, so that it's
easier for folks to understand the gist of it without before jumping to the
the code / doc.

As a best practice, once you have committed your changes, it is a good idea
to use `git rebase` (not `git merge`) to ensure your changes are placed at the
top. Plus merge conflicts can be resolved

```text
$ git fetch upstream
$ git rebase upstream/master
```

<img src='https://d3vv6lp55qjaqc.cloudfront.net/items/263e3q1M2Y2r3L1X3c2y/helmet.png'/>
Welcome to the gitcoin community. Lets push Open Source Forward.
