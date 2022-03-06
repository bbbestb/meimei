#!/bin/bash
# The official documentation doesn't have any word on this,
# but this seems to be a common practice
PROCESSOR_COUNT=$(nproc)
THREAD_COUNT=2

uwsgi --http :8300 --plugin python2 --wsgi-file app.py --processes "$PROCESSOR_COUNT" --threads "$THREAD_COUNT" --disable-logging
