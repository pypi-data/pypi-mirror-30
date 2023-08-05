BUILD = 'python setup.py sdist'
TAG_GIT = "git tag {version}"
PUSH_TAG_TO_GIT = 'git push --follow-tags'
PUBLISH_TO_PYPI = 'twine upload dist/{project_name}-{version}.tar.gz'
