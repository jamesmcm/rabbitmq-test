from pickle import load
from time import sleep
import sys

INPUT_FILE = '.raw_data.pickle'
events = load(open(INPUT_FILE, 'rb'))

OUTPUT_FILE = '../input/finding.csv'
open(OUTPUT_FILE, 'w').close()

SECS_PER_DAY = 1

if(len(sys.argv) > 1):
    try:
        SECS_PER_DAY = float(sys.argv[1])
    except:
        print('Run with \"python start_findings_stream.py <INT|FLOAT>\" - Using default values')

time = 0
print('Streaming data to ' + OUTPUT_FILE)
for event in events:
    event_time = float(event[2])
    del event[2]
    sleep(SECS_PER_DAY * (event_time - time))
    time = event_time
    with open(OUTPUT_FILE, 'a') as file:
        file.write(','.join(event) + '\n')
