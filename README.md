# fantasy-disc
Script to calculate disc golf fantasy scores

## Usage
### Prerequisites
Install python3. Install pip libraries in requirements.txt.

### Create roster
I am pretty lazy. I export the google sheet with the roster to a CSV and copy paste into the create_roster.py file for each event. Then, run create_roster.py to create a roster.json which will be read by the main script.

This is pretty clunky but takes me like 3 minutes to go from export to a roster.json.

### Run event
There are a couple of inputs to change on each run. They are these variables at the top of main.py:
```python
_event_id = 67202
_event_modifier = 1.25
_latest_round = '4'
```

* event_id is the event ID used by PDGA scoring application/API. If you go to the main page for the event on the PDGA website you will find it easily in the URL: https://www.pdga.com/tour/event/67202
* event_modifier is some pre-agreed number we set out at the beginning (1 for ES, 1.25 for Major, 1.5 for Worlds)
* latest_round lets you run tournaments before the final round. You should put a string number here for the round you want to score through.

Once you do that, run main.py to produce scoring outputs. There are two files created in events folder. One is a detailed output and one is a top level summary.

## Code Structure
I'm not going to write a lot about how the project is structured right now because the script is pretty bad and needs a big refactor.

## Scoring
General rules are:
* Tournament finish points awarded for final placing of 6 activated players
* Tournament ace worth 25 points
* Each hot round worth 10 points
* Birdie streaks start at 3, points increase as streak continues
* All event points are multiplied by event modifier (essentially DGPT point modifiers)

Tournament Finish	Points
1	100
2	66
3	60
4	53
5	46
6	40
7	33
8	30
9	26
10	23
11-15	20
16-20	16
21-25	13
26-30	10
31-40	6
41-50	3

Consecutive Under Par	Points
3	1
4	2
5	4
6	6
7	10
8	14
9	18
10	24
11	30
12	38
13	46
14	55
15	65
16	77
17	89
18	103
