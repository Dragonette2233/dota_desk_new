from app import app, db
from flask import render_template, url_for, redirect, request

import json
import requests
from datetime import datetime, timedelta

from app.models.hero import Hero
from app.models.match import Match


@app.route('/', methods=["GET"])
def index():
    matches_count = db.session.query(Match).count()
    
    # All inputs in form
    inputs = {f'A{i}': '' for i in range(1, 6)}
    inputs.update({f'B{i}': '' for i in range(1, 6)})

    if request.args:
        args = dict(request.args)
                
        # Collected stats
        stats = {
            'matches': 0,
            'wins': 0  # Team A wins
        }
        
        team_a, team_b = set(), set()
        for k, v in args.items():
            if v.isdigit():  # Hero id
                hero = Hero.query.filter_by(id=int(v)).first()
            else:  # Hero name
                hero = Hero.query.filter_by(name=v).first()

            if hero:  # If hero exists
                if k.startswith('A'):
                    team_a.add(str(hero.id))
                else:
                    team_b.add(str(hero.id))
                inputs[k] = v  # Fill into inputs
        
        month_ago_time = datetime.now() - timedelta(days=30)
        month_ago_time = int(month_ago_time.timestamp())
        
        matches = Match.query.filter(Match.start_time > month_ago_time).all()

        for match in matches:
            radiant_team = set(match.radiant_team.split())
            dire_team = set(match.dire_team.split())
            
            if team_a == radiant_team and team_b == dire_team:
                if match.radiant_win:
                    stats["wins"] += 1
                stats["matches"] += 1
            elif team_a == dire_team and team_b == radiant_team:
                if not match.radiant_win:
                    stats["wins"] += 1
                stats["matches"] += 1
            
        if stats["matches"]:
            return render_template(
                "home/index.html",
                inputs=inputs,
                matches_exist=True,
                wins_a=stats["wins"],
                wins_a_perc=f"{round(100 * (stats['wins'] / stats['matches']), 2)}",
                wins_b=stats["matches"] - stats["wins"],
                wins_b_perc=f"{round(100 * (1 - stats['wins'] / stats['matches']), 2)}",
                matches=stats["matches"],
                matches_count=matches_count
            )
        return render_template(
            "home/index.html",
            matches_exist=False,
            inputs=inputs,
            matches_count=matches_count
        )
    
    return render_template(
        "home/index.html",
        inputs=inputs,
        matches_count=matches_count
    )


@app.route('/test/<int:start_time>')
def test(start_time):
    
    date_time = datetime.fromtimestamp(start_time)
    print(date_time)
    
    return redirect(url_for('index'))


@app.route('/t')
def test_2():
    # import random
    # random_match = random.choice(Match.query.all())
    # print(random_match)
    
    # month_ago_time = datetime.now() - timedelta(days=30)  # Дата месяц назад
    # month_ago_time = month_ago_time.timestamp()
    # for match in Match.query.filter(Match.id > month_ago_time).all():
    #     print(match)
    
    a = {'12'}
    b = ['120']
    
    print(a.issubset(b))
    
    return redirect(url_for('index'))
