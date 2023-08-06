#!/bin/sh

echo "Post install"

# --------------------------------------------------------------------
# Scenario:
# In this example, a kernel was installed.  Set the trigger files and
# reboot later.  The watch dog service should be running and clean
# things up.
# --------------------------------------------------------------------
# write trigger files
snapshot_util.py -t
exit $ret 
