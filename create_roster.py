roster = """
Status,Curtis,Chris,Matt,Aaron,Jim,Kyle,Tim
Active,Niklas Anttila [91249],James Conrad [17295],Eagle McMahon [37817],Ricky Wysocki [38008],Isaac Robinson [50670],Anthony Barela [44382],Calvin Heimburg [45971]
Active,Jakub Semerád [91925],Paul Oman [34344],Ezra Aderhold [121715],Joel Freeman [69509],Luke Humphries [69424],Kyle Klein [85132],Chandler Kramer [139228]
Active,Eric Oakley [53565],Adam Hammes [57365],Kevin Jones [41760],Alden Harris [98091],Corey Ellis [44512],Kevin Kiefer III [97115],Thomas Gilbert [85850]
Active,Aaron Gossage [35449],Jake Monn [98722],Matthew Orum [18330],Väinö Mäkelä [59635],James Proctor [34250],Greg Barsby [15857],Chris Dickerson [62467]
Active,Ben Callaway [39015],Chris Clemons [50401],Bradley Williams [31644],Evan Smith [101574],Ezra Robinson [50671],Brodie Smith [128378],Robert Burridge [96512]
Active,Knut Valen Haland [35070],Cole Redalen [79748],Matt Bell [48950],Albert Tamm [76669],Nate Sexton [18824],Paul Ulibarri [27171],Mauri Villmann [107197]
AutoSub,Emerson Keith [47472],Andrew Presnell [63765],Tristan Tanner [99053],Jason Hebenheimer [43762],Casey White [81739],Lauri Lehtinen [82297],Austin Turner [54049]
Inactive,Mason Ford [72844],Austin Hannum [68835],Zach Melton [38631],Parker Welck [39491],Jeremy Koling [33705],Garrett Gurthie [13864],Andrew Marwede [75590]
Inactive,Gannon Buhr [75412],Nikko Locastro [11534],Gavin Rathbun [60436],Zach Arlinghaus [65266],Gavin Babcock [80331],Scott Stokely [3140],Aidan Scott [99246]
Inactive,Cale Leiviska [24341],Paul McBeth [27523],Michael Johansen [20300],Linus Carlsson [82098],Simon Lizotte [8332],Kyle Honeyager [84173],Drew Gibson [48346]
"""

import json
event_roster = {}
competitors = {}
for line in roster.split('\n'):
    if 'Status,' in line:
        for index, competitor in enumerate(line.split(',')):
            if competitor != 'Status':
                competitors[index] = competitor
                event_roster[competitor] = []
    else:
        players = line.split(',')
        if players == ['']:
            continue
        status = players[0].lower()
        for index, competitor in competitors.items():
            player_name = players[index].split(' [')[0]
            pdga_num = players[index].split('[')[1][:-1]
            event_roster[competitor].append({
                'name': player_name,
                'pdga': int(pdga_num),
                'status': status
                })
        
    #print(line)
with open('event_roster.json', 'w') as f:
    json.dump(event_roster, f, indent=4)
print(json.dumps(event_roster, indent=4))