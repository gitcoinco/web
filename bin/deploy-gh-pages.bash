#!/bin/bash
set -e

# Establish base configuration variables.
CI_SKIP_MSG=${CI_SKIP_MSG:-'[CI SKIP]'}
REMOTE_ORIGIN_URL=$(git config remote.origin.url)

DOCS_BRANCH=${DOCS_BRANCH:-'gh-pages'}
DOCS_BUILD_DIR=${DOCS_BUILD_DIR:-'_build/site'}
DOCS_DIR_PREFIX=${DOCS_DIR_PREFIX:-'tmp-dir'}
DOCS_ORIGIN_DESIGNATOR=${DOCS_ORIGIN_DESIGNATOR:-'origin'}
DOCS_TMP_DIR=$DOCS_BRANCH-$DOCS_DIR_PREFIX
GH_COMMIT_MSG=${GH_COMMIT_MSG:-'Deploy Github Pages'}

echo "Deploying Documentation to Github Pages!"
echo "Remote Origin URL: ($REMOTE_ORIGIN_URL)"
echo "Documentation Build Directory: ($DOCS_BUILD_DIR)"
echo "Documentation Branch: ($DOCS_BRANCH)"
echo "Documentation Temporary Directory: ($DOCS_TMP_DIR)"

# Verify the Github email and name have been specified.
: "${GH_EMAIL:?You must set the GH_EMAIL environment variable}"
: "${GH_NAME:?You must set the GH_NAME environment variable}"

# Make the intermediate directory.
echo "Creating the temporary documentation directory: $DOCS_TMP_DIR"
mkdir "$DOCS_TMP_DIR"
cd "$DOCS_TMP_DIR" || exit 1

# Git configuration and initialization.
git config --global user.email "$GH_EMAIL" > /dev/null 2>&1
git config --global user.name "$GH_NAME" > /dev/null 2>&1
git init
git remote add --fetch "$DOCS_ORIGIN_DESIGNATOR" "$REMOTE_ORIGIN_URL"

# Check for revisions - if none don't do this since git rm bombs otherwise.
if git rev-parse --verify "$DOCS_ORIGIN_DESIGNATOR"/"$DOCS_BRANCH" > /dev/null 2>&1; then
    # Switch into the $DOCS_BRANCH branch.
    git checkout "$DOCS_BRANCH"
    # Delete any old site as we are going to replace it.
    git rm -rf .
else
    git checkout --orphan "$DOCS_BRANCH"
fi

# Copy the documentation page assets into the root project directory.
cp -a "../${DOCS_BUILD_DIR}/." .

# Stage all changes.
git add -A

# Commit updated documentation assets and instruct to skip CI.
git commit --allow-empty -m "$GH_COMMIT_MSG - $CI_SKIP_MSG"

# Force push documentation changes overtop of the $DOCS_BRANCH branch and ignore output.
git push --force --quiet "$DOCS_ORIGIN_DESIGNATOR" "$DOCS_BRANCH" > /dev/null 2>&1
echo "Documentation update pushed to $DOCS_BRANCH!"

# Cleanup temporary assets.
cd .. || exit 1
rm -rf "$DOCS_TMP_DIR"
echo "Github Pages Deployed!"
