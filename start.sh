#!/bin/bash
ps -ef|grep 5100.py|grep -v grep|awk '{print $2}'|xargs kill -9
echo 'kill done'
sudo python 5100.py > 3&
echo 'start over'
