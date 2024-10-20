from flask import render_template, request, jsonify, redirect, url_for, session, flash
from werkzeug.security import check_password_hash, generate_password_hash
from pymongo import errors
from app.utils import update_team_data
from flask import current_app as app

def index():
    if 'username' not in session:
        return redirect(url_for('main.login'))
    else:
        return render_template('index.html')

def winner():
    if 'role' in session and session['role'] == 'admin':
        winning_team = app.db.teams.find_one()
        if winning_team and 'team_name' in winning_team:
            winner_name = winning_team['team_name']
        else:
            winner_name = 'No team found or missing team_name field'
        return render_template('winner.html', winner_name=winner_name)
    else:
        return redirect(url_for('main.login'))

def submit_team_data():
    team_name = request.json.get('team_name')
    group = request.json.get('group')
    won = request.json.get('won')
    kills = request.json.get('kills', 0)

    if not team_name or not won:
        return jsonify({"error": "Missing team name or win/loss information"}), 400

    update_team_data(team_name, group, won, kills)
    updated_team = app.db.teams.find_one({"team_name": team_name}, {"_id": 0})
    return jsonify(updated_team)

def search_team():
    team_name = request.args.get('team_name')

    if not team_name:
        return jsonify({"error": "Team name is required"}), 400

    team = app.db.teams.find_one({"team_name": team_name}, {"_id": 0})

    if not team:
        return jsonify({"error": "Team name does not exist"}), 404

    return jsonify(team)

def second():
    return render_template('second.html')

def get_group_teams():
    group = request.args.get('group')

    if not group:
        return jsonify({"error": "Group is required"}), 400

    teams = list(app.db.teams.find({"group": group}, {"_id": 0}))
    teams.sort(key=lambda x: (-x['points'], -x.get('kills', 0)))

    return jsonify(teams)

def third():
    return render_template('third.html')

def round_selection():
    if 'username' not in session:
        return redirect(url_for('main.login'))
    else:
        return render_template('round.html')

def generate_vs():
    selected_round = request.form.get('rounds')

    if selected_round == "round1-league":
        group_a_teams = list(app.db.teams.find({"group": "Group A"}))
        group_a_teams.sort(key=lambda team: team['points'], reverse=True)

        group_b_teams = list(app.db.teams.find({"group": "Group B"}))
        group_b_teams.sort(key=lambda team: team['points'], reverse=True)

        matchups_a = []
        for i in range(len(group_a_teams)):
            for j in range(i + 1, len(group_a_teams)):
                team1 = group_a_teams[i]
                team2 = group_a_teams[j]
                matchups_a.append(f"{team1['team_name']} vs {team2['team_name']}")

        matchups_b = []
        for i in range(len(group_b_teams)):
            for j in range(i + 1, len(group_b_teams)):
                team1 = group_b_teams[i]
                team2 = group_b_teams[j]
                matchups_b.append(f"{team1['team_name']} vs {team2['team_name']}")

        return render_template('matchups.html', matchups_a=matchups_a, matchups_b=matchups_b)

    elif selected_round == "round2-knockouts":
        group_a_teams = list(app.db.teams.find({"group": "Group A"}))
        group_a_teams.sort(key=lambda team: team['points'], reverse=True)

        if len(group_a_teams) < 2:
            return "Not enough teams to generate matchups", 400

        eliminated_team_a = group_a_teams.pop()

        knockout_matches_a = []
        for i in range(0, len(group_a_teams), 2):
            if i + 1 < len(group_a_teams):
                team1 = group_a_teams[i]
                team2 = group_a_teams[i + 1]
                knockout_matches_a.append((team1['team_name'], team2['team_name']))

        group_b_teams = list(app.db.teams.find({"group": "Group B"}))
        group_b_teams.sort(key=lambda team: team['points'], reverse=True)

        if len(group_b_teams) < 2:
            return "Not enough teams to generate matchups", 400

        eliminated_team_b = group_b_teams.pop()

        knockout_matches_b = []
        for i in range(0, len(group_b_teams), 2):
            if i + 1 < len(group_b_teams):
                team1 = group_b_teams[i]
                team2 = group_b_teams[i + 1]
                knockout_matches_b.append((team1['team_name'], team2['team_name']))

        return render_template('round2.html',
                               knockout_matches_a=knockout_matches_a,
                               knockout_matches_b=knockout_matches_b,
                               eliminated_team_a=eliminated_team_a['team_name'],
                               eliminated_team_b=eliminated_team_b['team_name'],
                               teams_a=group_a_teams,
                               teams_b=group_b_teams)

    elif selected_round == "round3-climax-clash":
        remaining_teams_a = list(app.db.teams.find({"group": "Group A"}))
        remaining_teams_b = list(app.db.teams.find({"group": "Group B"}))

        matchups = []
        for team_a in remaining_teams_a:
            for team_b in remaining_teams_b:
                matchups.append(f"{team_a['team_name']} vs {team_b['team_name']}")

        return render_template('matchups_round3.html', matchups=matchups)

    return f"Selected round: {selected_round}"

def submit_winners():
    winning_teams = request.form.getlist('winners')

    if 'round3-climax-clash' in request.form:
        for team_name in winning_teams:
            app.db.teams.update_one(
                {"team_name": team_name},
                {"$inc": {"points": 2, "matches_played": 1, "matches_won": 1}}
            )

        all_teams = list(app.db.teams.find({"group": {"$in": ["Group A", "Group B"]}}))
        losing_teams = [team for team in all_teams if team['team_name'] not in winning_teams]

        for losing_team in losing_teams:
            try:
                app.db.eliminated_teams.insert_one({
                    'team_name': losing_team['team_name'],
                    'group': losing_team['group'],
                    'points': losing_team['points'],
                    'matches_played': losing_team['matches_played'],
                    'matches_won': losing_team['matches_won'],
                    'matches_lost': losing_team['matches_lost'],
                    'kills': losing_team['kills']
                })
            except errors.DuplicateKeyError:
                print(f"Team {losing_team['team_name']} is already eliminated.")

            app.db.teams.delete_one({"team_name": losing_team['team_name']})

        return "Winners submitted for Round 3, and losing teams moved to eliminated collection!"

    else:
        for team_name in winning_teams:
            app.db.teams.update_one(
                {"team_name": team_name},
                {"$inc": {"points": 2, "matches_played": 1, "matches_won": 1}}
            )

        all_teams = list(app.db.teams.find({"group": "Group A"}))
        losing_teams = [team for team in all_teams if team['team_name'] not in winning_teams]

        for losing_team in losing_teams:
            try:
                app.db.eliminated_teams.insert_one({
                    'team_name': losing_team['team_name'],
                    'group': losing_team['group'],
                    'points': losing_team['points'],
                    'matches_played': losing_team['matches_played'],
                    'matches_won': losing_team['matches_won'],
                    'matches_lost': losing_team['matches_lost'],
                    'kills': losing_team['kills']
                })
            except errors.DuplicateKeyError:
                print(f"Team {losing_team['team_name']} is already eliminated.")

            app.db.teams.delete_one({"team_name": losing_team['team_name']})

        all_teams_b = list(app.db.teams.find({"group": "Group B"}))
        losing_teams_b = [team for team in all_teams_b if team['team_name'] not in winning_teams]

        for losing_team in losing_teams_b:
            try:
                app.db.eliminated_teams.insert_one({
                    'team_name': losing_team['team_name'],
                    'group': losing_team['group'],
                    'points': losing_team['points'],
                    'matches_played': losing_team['matches_played'],
                    'matches_won': losing_team['matches_won'],
                    'matches_lost': losing_team['matches_lost'],
                    'kills': losing_team['kills']
                })
            except errors.DuplicateKeyError:
                print(f"Team {losing_team['team_name']} is already eliminated.")

            app.db.teams.delete_one({"team_name": losing_team['team_name']})

        return "Winners submitted, and losing teams moved to eliminated collection!"

def view_eliminated_teams():
    if 'role' in session and session['role'] == 'admin':
        eliminated_teams = list(app.db.eliminated_teams.find({}, {"_id": 0}))
        return render_template('eliminated_teams.html', eliminated_teams=eliminated_teams)
    else: 
        return "Access denied: Admins only.", 403

def retrieve_teams():
    selected_teams = request.form.getlist('team_names')

    for team_name in selected_teams:
        team = app.db.eliminated_teams.find_one({"team_name": team_name})
        if team:
            try:
                app.db.teams.insert_one({
                    'team_name': team['team_name'],
                    'group': team.get('group', 'Unknown'),
                    'points': team['points'],
                    'matches_played': team['matches_played'],
                    'matches_won': team['matches_won'],
                    'matches_lost': team['matches_lost'],
                    'kills': team['kills']
                })
                
                app.db.eliminated_teams.delete_one({"team_name": team_name})
            except errors.DuplicateKeyError:
                print(f"Team {team_name} already exists in the active teams collection.")

    return "Selected teams have been retrieved!"

def register():
    if 'role' in session and session['role'] == 'admin':
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            role = request.form['role']

            hashed_password = generate_password_hash(password)

            user_data = {
                'username': username,
                'password': hashed_password,
                'role': role
            }
            app.db.users.insert_one(user_data)

            return redirect(url_for('main.success'))

        return render_template('register.html')
    else:
        return redirect(url_for('main.login'))

def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = app.db.users.find_one({'username': username})
        if user and check_password_hash(user['password'], password):
            session['username'] = username
            session['role'] = user['role']
            return redirect(url_for('main.index'))

        flash('Invalid username or password', 'error')

    return render_template('login.html')

def logout():
    session.clear()
    return redirect(url_for('main.login'))

def success():
    return "Registration successful!"