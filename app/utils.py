from flask import current_app as app

def update_team_data(team_name, group, won, kills):
    team = app.db.teams.find_one({"team_name": team_name})

    if not team:
        new_team = {
            'team_name': team_name,
            'group': group,
            'points': 0,
            'matches_played': 0,
            'matches_won': 0,
            'matches_lost': 0,
            'kills': int(kills)
        }
        app.db.teams.insert_one(new_team)
    else:
        update_increments = {
            'matches_played': 1,
            'kills': int(kills)
        }

        if won == "Yes":
            update_increments['points'] = 2
            update_increments['matches_won'] = 1
        else:
            update_increments['matches_lost'] = 1

        app.db.teams.update_one(
            {"team_name": team_name},
            {"$inc": update_increments}
        )