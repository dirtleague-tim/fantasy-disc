


class Competitor:
    def __init__(self, name, player_pdga_numbers, autosub_pdga, player_pdga_numbers_inactive):

        self.name = name
        self.pdga_numbers_active = [int(i) for i in player_pdga_numbers]
        self.pdga_number_autosub = autosub_pdga
        self.pdga_numbers_inactive = [int(i) for i in player_pdga_numbers_inactive]
        self.points_total = 0
        self.events_scores = {}

    def add_points(self, competitor_event_scores, player_results, pdga_number, event_modifier, player_type):
        if pdga_number not in list(player_results.keys()):
            points = 0
            status = 'DNP'
        else:
            points = player_results[pdga_number].points
            status = 'Played'
        competitor_event_scores.append({
            'player_name': self.name,
            'pdga_number': pdga_number,
            'points': points * event_modifier,
            'status': status,
            'type': player_type
        })

    def get_round_total(self, player_results, event_modifier, event_id):
        competitor_event_scores = []
        round_total = 0
        activate_autosub = False

        for pdga_number in self.pdga_numbers_active:
            self.add_points(competitor_event_scores, player_results, pdga_number, event_modifier, 'Active')

        for competitor in competitor_event_scores:
            if competitor['status'] == 'DNP':
                activate_autosub = True
                break
    
        for pdga_number in self.pdga_numbers_inactive:
            self.add_points(competitor_event_scores, player_results, pdga_number, event_modifier, 'Inactive')
        
        self.add_points(competitor_event_scores, player_results, self.pdga_number_autosub, event_modifier, 'Autosub (Activated)' if activate_autosub else 'Autosub (Inactive)')

        for competitor in competitor_event_scores:
            if competitor['type'] in ['Active', 'Autosub (Activated)']:
                round_total += competitor['points']

        self.points_total += round_total
        self.events_scores[event_id] = round_total
        return round_total, competitor_event_scores
