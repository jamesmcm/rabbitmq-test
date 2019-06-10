#!/bin/sh
set -e;
echo "SECS_PER_DAY: $SECS_PER_DAY";
echo "DELAY: $DELAY";
fifo=$(mktemp -u);
mkfifo "$fifo";
sleep "$DELAY";
./waitForMySQL.sh &&
echo "Starting event processing..." &&
trap 'kill %1; kill %2; kill %3' INT
cat "$fifo" &
python aggregate_karma_updater.py mysql &
python redis_receive.py redis &
python cassandra_receive.py cassandra &
touch ../../../input/finding.csv &&
tail -f ../../../input/finding.csv | tee "$fifo"  | python event_generator.py &
(cd ../../../log_gen; python ./start_finding_stream.py "$SECS_PER_DAY" > /dev/null 2>&1) &&
echo "Finished generating events";
sleep 10;
