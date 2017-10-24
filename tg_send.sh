#!/bin/bash
SCRIPT=$(readlink -f $0)
SCRIPTPATH=`dirname $SCRIPT`
${SCRIPTPATH}/zbxtg_send.py --username "$1" --message "$2" --subject "$3" --debug
