from config import Static
from app import db, app
from app.models.info import Info
from app.models.match import Match
import time
import requests

# Диапазоны рангов эквивалентные примерному ммр с шагом 168
RANKTIERS = {
    range(10, 16): 0,
    range(20, 26): 720,
    range(30, 36): 1560,
    range(40, 46): 2400,
    range(50, 56): 3240,
    range(60, 66): 4080,
    range(70, 76): 4920,
    range(80, 86): 5760
}

def rank_tier_to_mmr(rank_tier):
    for rank_range, base in RANKTIERS.items():
        if rank_tier in rank_range:
            sub_tier = rank_tier % 10
            mmr_step = 168
            return base + (sub_tier - 1) * mmr_step + mmr_step / 2
    return None

def match_fits_conditions(match) -> bool:
    if isinstance(match, dict):
        return all([
            match["avg_rank_tier"] is not None,
            match["avg_rank_tier"] >= Static.AVG_RANK_REQUIRE,
            match["game_mode"] == 22,
            not Match.query.filter_by(id=match["match_id"]).first()
        ])
    return False

def add_match_to_db(match):
    m = Match(
        id=match["match_id"],
        radiant_win=match["radiant_win"],
        start_time=match["start_time"],
        avg_mmr=rank_tier_to_mmr(match["avg_rank_tier"]),
        radiant_team=" ".join(str(i) for i in match["radiant_team"]),
        dire_team=" ".join(str(i) for i in match["dire_team"])
    )
    try:
        db.session.add(m)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        app.logger.warning(f"Exception in parsing | {e}")

def fetch_matches(url) -> dict:
    while True:
        result = requests.get(url).json()
        
        # Устанавливаем задержку если в запросе ошибка (например израсходован лимит)
        try:
            app.logger.error(result['error'] + " cooldown 5min")
            time.sleep(360)
        except (AttributeError, KeyError, TypeError):
            return result
        
        
    
def update_match_ids(info, matches):
    info.max_match_id = matches[0]["match_id"]
    db.session.commit()

def main_loop(info, min_match_start_time, min_match_id):
    while min_match_start_time >= Static.UNIX_TIME_2024:
        url = f"https://api.opendota.com/api/publicMatches?less_than_match_id={min_match_id}"
        matches = fetch_matches(url)
        for match in matches:
            if match_fits_conditions(match):
                add_match_to_db(match)
        if matches:
            min_match_id = matches[-1]["match_id"]
            info.min_match_id = min_match_id
            min_match_start_time = matches[-1]["start_time"]
            db.session.commit()
        time.sleep(Static.API_REQUEST_DELAY)
    info.reached_2020 = True
    db.session.commit()

def infinite_loop(info, max_match_id):
    while True:
        min_match_id = max_match_id
        max_match_id += 100
        info.min_match_id = min_match_id
        info.max_match_id = max_match_id
        db.session.commit()
        url = f"https://api.opendota.com/api/publicMatches?less_than_match_id={max_match_id}"
        matches = fetch_matches(url)
        for match in matches:
            if match_fits_conditions(match):
                add_match_to_db(match)
        time.sleep(Static.API_REQUEST_DELAY)

def loader():
    if Static.DEBUG_MODE:
        while True:
            app.logger.info("Debugging mode | [loader] disabled")
            time.sleep(1200)

    app.app_context().push()
    info = Info.query.first()
    min_match_id = info.min_match_id or 10e12
    max_match_id = info.max_match_id or 0
    info.min_match_id = min_match_id
    info.max_match_id = max_match_id
    info.reached_2020 = False
    db.session.flush()

    if not info.min_match_id and not info.max_match_id:
        url = "https://api.opendota.com/api/publicMatches"
        matches = fetch_matches(url)
        update_match_ids(info, matches)
        for match in matches[:100]:
            if match_fits_conditions(match):
                add_match_to_db(match)
        min_match_id = matches[-1]['match_id']
        info.min_match_id = min_match_id
        min_match_start_time = matches[-1]['start_time']
        main_loop(info, min_match_start_time, min_match_id)
    else:
        if not info.reached_2020:
            url = f"https://api.opendota.com/api/publicMatches?less_than_match_id={min_match_id}"
            matches = fetch_matches(url)
            for match in matches:
                if match_fits_conditions(match):
                    add_match_to_db(match)
            min_match_id = matches[-1]['match_id']
            info.min_match_id = min_match_id
            min_match_start_time = matches[-1]['start_time']
            main_loop(info, min_match_start_time, min_match_id)
        infinite_loop(info, max_match_id)
