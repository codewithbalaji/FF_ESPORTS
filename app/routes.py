from flask import Blueprint
from app.views import (index, winner, submit_team_data, search_team, second, 
                       get_group_teams, third, round_selection, generate_vs, 
                       submit_winners, view_eliminated_teams, retrieve_teams, 
                       register, login, logout, success)

bp = Blueprint('main', __name__)

bp.route('/')(index)
bp.route('/winner')(winner)
bp.route('/submit', methods=['POST'])(submit_team_data)
bp.route('/search_team', methods=['GET'])(search_team)
bp.route('/second')(second)
bp.route('/group_teams', methods=['GET'])(get_group_teams)
bp.route('/third')(third)
bp.route('/round')(round_selection)
bp.route('/generate_vs', methods=['POST'])(generate_vs)
bp.route('/submit_winners', methods=['POST'])(submit_winners)
bp.route('/eliminated_teams')(view_eliminated_teams)
bp.route('/retrieve_teams', methods=['POST'])(retrieve_teams)
bp.route('/register', methods=['GET', 'POST'])(register)
bp.route('/login', methods=['GET', 'POST'])(login)
bp.route('/logout')(logout)
bp.route('/success')(success)