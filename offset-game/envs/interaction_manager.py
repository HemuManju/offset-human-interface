from .utils.interaction import check_perimeter, findkeys
from .utils import magicattr


class InteractionManager(object):
    def __init__(self, config):
        self.config = config
        return None

    def get_team_position(self, blue_team, red_team):
        # Get the attributes
        blue_team_attr = blue_team.get_attributes(['centroid_pos'])
        red_team_attr = red_team.get_attributes(['centroid_pos'])

        # Extract the position from dictionary
        blue_team_pos = list(findkeys(blue_team_attr, 'centroid_pos'))
        red_team_pos = list(findkeys(red_team_attr, 'centroid_pos'))
        return blue_team_pos, red_team_pos

    def change_action(self, team, action):
        magicattr.set(team, action, 'shooting')
        return None

    def action_lookup_string(self, key, attr):
        vehicle_type = key.split('_')[0]
        action = 'action_manager.' + vehicle_type + '_platoons' + str(
            [key]) + '.action' + str([attr])
        return action

    def update_actions(self, blue_team, red_team):
        # Check the closeness (this function might change)
        blue_team_pos, red_team_pos = self.get_team_position(
            blue_team, red_team)
        with_in_perimeter = check_perimeter(blue_team_pos, red_team_pos,
                                            self.config)

        # Perform actions accordingly
        for blue_key, red_key in with_in_perimeter.items():

            # Get the action (str) from blue and red team
            blue_action = self.action_lookup_string(blue_key, 'primitive')
            red_action = self.action_lookup_string(red_key, 'primitive')

            # Change the attribute
            self.change_action(blue_team, blue_action)
            self.change_action(red_team, red_action)
