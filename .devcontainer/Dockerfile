FROM mcr.microsoft.com/devcontainers/python:1-3.12-bookworm

# The base image ships a Yarn apt source whose signing key rotated upstream,
# which makes `apt-get update` fail and breaks every feature that installs
# via apt (exit code 100). We don't use yarn, so drop the source.
# https://github.com/devcontainers/images/issues/1797
USER root
RUN rm -f /etc/apt/sources.list.d/yarn.list \
 && grep -rl 'dl.yarnpkg.com' /etc/apt/sources.list.d/ 2>/dev/null | xargs -r rm -f \
 && apt-get update \
 && rm -rf /var/lib/apt/lists/*
