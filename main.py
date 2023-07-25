
import competitor
import scoring_round
import json

_event_id = 67202
_event_modifier = 1.25
_latest_round = '4'

def main(scoring_rounds, competitor_list):

    for scoring_round_event in scoring_rounds:

        scoring_round_results = scoring_round.ScoringRound(scoring_round_event['event_id'], scoring_round_event['event_modifier'], _latest_round)

        for event_competitor in competitor_list:
            scoring_round_results.competitor_results(event_competitor)

        scoring_round_results.print_event_details()
        scoring_round_results.print_event_summary()


if __name__ == '__main__':

    scoring_rounds = [
        {'event_id': _event_id, 'event_modifier': _event_modifier}
    ]

    competitor_list = [
    ]

    with open('event_roster.json', 'r') as f:
        roster = json.load(f)
        for competitor_name, players in roster.items():
            active = []
            autosub = []
            inactive = []
            for player in players:
                if player['status'] == 'active':
                    active.append(player['pdga'])
                elif player['status'] == 'autosub':
                    autosub = player['pdga']
                else:
                    inactive.append(player['pdga'])
            
            competitor_list.append(competitor.Competitor(competitor_name, active, autosub, inactive))

    main(scoring_rounds, competitor_list)