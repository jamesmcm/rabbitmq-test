#!/bin/sh
# wait until MySQL is really available
# https://cweiske.de/tagebuch/docker-mysql-available.htm

maxcounter=180
 
counter=1
while ! mysql -h db --protocol TCP -u"root" -p"groot" -e "show databases;" > /dev/null 2>&1; do
    sleep 1
    counter=$($counter + 1)
    if [ "$counter" -gt "$maxcounter" ]; then
        >&2 echo "We have been waiting for MySQL too long already; failing."
        exit 1
    fi;
done
