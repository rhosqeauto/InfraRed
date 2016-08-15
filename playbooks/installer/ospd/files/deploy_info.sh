#!/bin/bash

if ! options=$(getopt -o h -l help -- "$@")
then
    # parse error
    display_help
    exit 1
fi

eval set -- $options

function display_help()
{
        echo "$0 [option..]"
	echo "This command supposed to help to debug openstack overcloud deployment issues."
	echo "The undercloud credentials has to be available as an environment variable, and will be used by the openstack command."
        echo "-h|--help Display help"
}

while [ $# -gt 0 ]
do
    case "$1" in
    -h|--help) display_help; exit 0 ;;
    (--) shift; break ;;
    (-*) echo "$0: error - unrecognized option $1" >&2; display_help; exit 1 ;;
    (*)  echo "$0: error - unexpected argument $1" >&2; display_help; exit 1 ;;
    esac
    shift
done


echo "Server info"
set -x
openstack server list |  awk 'BEGIN {a=0}; /\|/{ if (a>2) print $2} {a=a+1}' | xargs -n 1 openstack server show

echo "Deployment issues"
DEPLOYMENTS=`openstack software deployment list --long`
echo "$DEPLOYMENTS"

for a in `echo "$DEPLOYMENTS" | grep -v 'COMPLETE' | awk 'BEGIN {a=0}; /\|/{ if (a>2) print $2} {a=a+1}'`; do
	echo "Inspecting: $a"
	openstack software deployment output show "$a" --all
done
