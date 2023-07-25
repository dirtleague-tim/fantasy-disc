import requests
import json
import os
import urllib.parse
import requests
requests.packages.urllib3.disable_warnings() 


class Scoring:
    def __init__(self):

        self.points = [100, 66, 60, 53, 46, 40, 33, 30, 26, 23] + [20] * 5 + [16] * 5 + [13] * 5 + [10] * 5 + [6] * 10 + [3] * 10
        self.number_of_finishers_at_place = [0] * len(self.points)
        self.hot_round_points = 5
        self.ace_points = 25
        self.birdie_streak_points = [1, 2, 4, 6, 10, 14, 18, 24, 30, 38, 46, 55, 65, 77, 89, 103]

    def add_finisher(self, finish_place):
        if finish_place < len(self.points):
            self.number_of_finishers_at_place[finish_place - 1] += 1

    def add_round_finish_points(self, finish):
        if finish > len(self.points) - 1:
            return 0
        total_points = 0
        for points in range(finish-1, finish-1+self.number_of_finishers_at_place[finish-1]):
            total_points += self.points[points] if points < len(self.points) else 0
        return total_points / (1 if self.number_of_finishers_at_place[finish-1] == 0 else self.number_of_finishers_at_place[finish-1])

    def add_hot_round_points(self):
        return self.hot_round_points

    def add_ace_points(self):
        return self.ace_points

    def add_birdie_streak_points(self, streak_length):
        # consecutive bridies -2:
        # 3 in a row = 1
        # 4 in a row = 2
        # etc.
        return self.birdie_streak_points[streak_length - 3]

scores = Scoring()


class PlayerResult():
    def __init__(self, pdga_number, player_name):
        self.pdga_number = pdga_number
        self.player_name = player_name
        self.status = 'DNP'
        self.finish_place = -1
        self.finish_place_points = 0
        self.points = 0
        self.hot_rounds = 0
        self.hot_round_points = 0
        self.ace_count = 0
        self.ace_points = 0
        self.birdie_streak_lengths = []
        self.birdie_streak_points = 0
        self.running_place = 10000

    def set_running_place(self, running_place):
        self.running_place = running_place

    def add_round_based_points(self, round_scores, round_pars):
        round_scores = round_scores.split(',')
        round_pars = round_pars.split(',')

        running_birdie_count = 0

        for hole_number, hole_score in enumerate(round_scores):

            # If bad hole data, call it a scratch and close out birdie streak
            scratch = False
            try:
                hole_score = int(hole_score)
            except:
                scratch = True

            try:
                round_par = int(round_pars[hole_number])
            except:
                scratch = True

            if not scratch and int(hole_score) == 1:
                self.ace_count = self.ace_count + 1
                self.ace_points = self.ace_points + scores.add_ace_points()

            if not scratch and int(hole_score) < int(round_pars[hole_number]):
                running_birdie_count += 1
            else:
                if running_birdie_count >= 3:
                    self.birdie_streak_lengths.append(running_birdie_count)
                    self.birdie_streak_points += scores.add_birdie_streak_points(running_birdie_count)
                running_birdie_count = 0

            # If birdie streak goes into last hole
            if hole_number == len(round_scores) - 1:
                if running_birdie_count >= 3:
                    self.birdie_streak_lengths.append(running_birdie_count)
                    self.birdie_streak_points += scores.add_birdie_streak_points(running_birdie_count)

    def set_birdie_streak_points(self):
        self.points += self.birdie_streak_points

    def add_hot_round_points(self):
        self.hot_rounds += 1
        self.hot_round_points += scores.add_hot_round_points()

    def set_hot_round_points(self):
        self.points += self.hot_round_points

    def set_finish_place(self):
        self.finish_place = self.running_place
        scores.add_finisher(self.finish_place)

    def set_finish_place_points(self):
        #print(f'{self.player_name} - {self.running_place} - {scores.add_round_finish_points(self.finish_place)}')
        self.finish_place_points += scores.add_round_finish_points(self.finish_place)
        self.points += self.ace_points
        self.points += self.finish_place_points

    def print(self):
        return json.dumps({
            'pdga_number': self.pdga_number,
            'player_name': self.player_name,
            'finish_place': self.finish_place,
            'points': self.points
        })


class ScoringRound:
    def __init__(self, event_id, event_modifier=1, latest_round='final'):

        self.event_id = event_id
        self.event_modifier = event_modifier
        self.competitors = []

        response = requests.get(f'https://www.pdga.com/apps/tournament/live-api/live_results_fetch_event.php?TournID={event_id}'.replace(' ', '%20'), verify=False)

        if response.status_code != 200:
            raise Exception('Cannot get scoring info')

        tournament_info = response.json()
        self.event_name = tournament_info['data']['Name']
        self.event_date = tournament_info['data']['EndDate']
        self.number_of_rounds = len(tournament_info['data']['RoundsList'].keys())
        self.final_round_info = tournament_info['data']['RoundsList'][str(tournament_info['data']['FinalRound'])]

        self.competitor_players_in_event = []
        self.competitor_event_scores = {}

        self.player_results = {}

        if latest_round == 'final':
            last_round_number = self.number_of_rounds
        else:
            last_round_number = int(latest_round)
        round_count = 0

        for round_number, round in tournament_info['data']['RoundsList'].items():

            round_count += 1

            response = requests.get(f'https://www.pdga.com/apps/tournament/live-api/live_results_fetch_round.php?TournID={event_id}&Division=MPO&Round={round["Label"]}'.replace(' ', '%20'), verify=False)
            round_scores = response.json()

            #print(f'https://www.pdga.com/apps/tournament/live-api/live_results_fetch_round.php?TournID={event_id}&Division=MPO&Round={round["Label"]}'.replace(' ', '%20'))
            hot_round = 10000
            hot_round_players = []

            final_round = round['Number'] == tournament_info['data']['FinalRound']
            round_score_data = []
            if 'scores' in round_scores['data']:
                round_score_data += round_scores['data']['scores']
            else:
                for data in round_scores['data']:
                    round_score_data += data['scores']

            for player in round_score_data:
                if player['PDGANum'] not in self.player_results:
                    self.player_results[player['PDGANum']] = PlayerResult(player['PDGANum'], player['Name'])

                self.player_results[player['PDGANum']].add_round_based_points(player['Scores'], player['Pars'])

                if player['Holes'] == player['Played']:
                    if int(player['RoundScore']) < hot_round:
                        hot_round = int(player['RoundScore'])
                        hot_round_players = [player['PDGANum']]

                    elif player['RoundScore'] == hot_round:
                        hot_round_players.append(player['PDGANum'])

                self.player_results[player['PDGANum']].set_running_place(player['RunningPlace'])

            print(f'hot round {round_count} ({hot_round}) players: {json.dumps(hot_round_players)}')
            for pdga_num in hot_round_players:
                self.player_results[pdga_num].add_hot_round_points()

            if round_count == last_round_number:
                break

        for pdga_num in self.player_results.keys():
            self.player_results[pdga_num].set_finish_place()

        for pdga_num in self.player_results.keys():
            self.player_results[pdga_num].set_hot_round_points()
            self.player_results[pdga_num].set_finish_place_points()
            self.player_results[pdga_num].set_birdie_streak_points()

    def competitor_results(self, competitor):
        self.competitors.append(competitor)
        competitor_score, player_event_scores = competitor.get_round_total(self.player_results, self.event_modifier, self.event_id)
        self.competitor_players_in_event += player_event_scores
        self.competitor_event_scores[competitor.name] = competitor_score
        return competitor_score

    def print_event_details(self):

        if not os.path.exists('./events'):
            os.makedirs('./events')

        if not os.path.exists('./events/details'):
            os.makedirs('./events/details')

        filename = f'./events/details/{self.event_date}-{self.event_name}.csv'
        with open(filename, 'w+') as f:
            f.write('Finish Place,Player,PDGA Number,Event Modifier,Competitor,Player Tournament Status,Player Roster Status,Finish Place Points,Hot Rounds,Hot Round Points,Ace Points,Birdie Streaks,Birdie Streak Points,Total Points,\n')
            self.competitor_players_in_event.sort(key=lambda x: x['points'], reverse=True)
            for competitor in self.competitor_players_in_event:
                if competitor['pdga_number'] not in list(self.player_results.keys()):
                    continue
                competitor_info = self.player_results[competitor['pdga_number']]
                f.write(','.join([str(x) for x in [
                    competitor_info.finish_place,
                    competitor_info.player_name,
                    competitor_info.pdga_number,
                    self.event_modifier,
                    competitor['player_name'],
                    competitor['status'],
                    competitor['type'],
                    competitor_info.finish_place_points,
                    competitor_info.hot_rounds,
                    competitor_info.hot_round_points,
                    competitor_info.ace_points,
                    json.dumps(competitor_info.birdie_streak_lengths).replace(',', '|'),
                    competitor_info.birdie_streak_points,
                    competitor['points'],
                    '\n'
                ]]))

        print(f'Wrote: {filename}')

    def print_event_summary(self):

        if not os.path.exists('./events'):
            os.makedirs('./events')

        competitor_list = {}

        for player in self.competitor_players_in_event:
            if player['type'] == 'Active':
                if player['player_name'] not in competitor_list:
                    competitor_list[player['player_name']] = 0
                competitor_list[player['player_name']] += player['points']

        competitor_list = [{'name': k, 'points_total': v} for k, v in competitor_list.items()]

        filename = f'./events/{self.event_date}-{self.event_name}.csv'
        with open(filename, 'w+') as f:
            f.write('Rank,Competitor,Event Modifier,Points\n')

            competitor_list.sort(key=lambda x: x['points_total'], reverse=True)
            for rank, competitor in enumerate(competitor_list):
                f.write(f'{rank+1},{competitor["name"]},{self.event_modifier},{competitor["points_total"]}\n')

        print(f'Wrote: {filename}')