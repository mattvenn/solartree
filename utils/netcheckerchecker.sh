#!/bin/bash
d=$(date)
log=~/solartree/utils/netcheckerchecker.log
net=$(ps ax | grep 'python.*netchecker' | grep -v grep)

echo $d $net  >> $log
vmstat >> $log
