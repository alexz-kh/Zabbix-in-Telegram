#!/bin/bash

echo "HUI`date`" >> /dev/fd/2
echo "$@" >> /dev/fd/2

echo "HUI`date`" >> /tmp/zabbix_log
echo "$@" >> /tmp/zabbix_log 
