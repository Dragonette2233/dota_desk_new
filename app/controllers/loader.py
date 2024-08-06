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

# @kw:
def rank_tier_to_mmr(rank_tier):
    base_mmr = None
    for rank_range, base in RANKTIERS.items():
        if rank_tier in rank_range:
            base_mmr = base
            break
        
    sub_tier = rank_tier % 10 # Класс тира
    mmr_step = 168  # Шаг между уровнями
    
    # Рассчитываем ммр с шагом
    mmr = base_mmr + (sub_tier - 1) * mmr_step + mmr_step / 2
    return mmr

def match_fits_conditions(match) -> bool:
    """Checks all match conditions"""
    
    if isinstance(match, dict):
    
        return all(
                [
                    match["avg_rank_tier"] is not None,
                    match["avg_rank_tier"] >= Static.AVG_RANK_REQUIRE,
                    match["game_mode"] == 22,
                    not Match.query.filter_by(id=match["match_id"]).first()
                ]
            )

def loader():
    
    if Static.DEBUG_MODE:
        while True:
            app.logger.info("Debugging mode | [loader] disabled")
            time.sleep(1200)

    app.app_context().push()
    info = Info.query.first()
    min_match_id = info.min_match_id
    max_match_id = info.max_match_id
    # print(min_match_id, type(max_match_id), info.reached_2020)

    # If it`s first execution
    if not min_match_id and not max_match_id:
        min_match_id = 10e12
        max_match_id = 0

        info.min_match_id = min_match_id
        info.max_match_id = max_match_id
        info.reached_2020 = False
        db.session.flush()

        url = "https://api.opendota.com/api/publicMatches"
        matches: list | dict = requests.get(url).json()

        try:
            app.logger.error(matches['error'])
            raise SystemExit()
        except (AttributeError, KeyError, TypeError):
            ...
        
        # print(matches)
        
        max_match_id = matches[0]["match_id"]  # Set up top id
        info.max_match_id = max_match_id
        db.session.commit()
        
        # First 100 matches
        for match in matches:
            if match_fits_conditions(match):
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
                    # print(f"Exception while parse match {match['match_id']}\n\n{e}")
                    pass
        
        # Decrease min_match_id
        time.sleep(Static.API_REQUEST_DELAY)
        min_match_id = match['match_id']
        info.min_match_id = min_match_id
        db.session.commit()

        min_match_start_time = match['start_time']
        while min_match_start_time >= Static.UNIX_TIME_2024:  # Iterates since date 01.08.2024
            url = f"https://api.opendota.com/api/publicMatches?less_than_match_id={min_match_id}"
            matches: list = requests.get(url).json()
            
            for match in matches:
                if match_fits_conditions(match) and not Match.query.filter_by(id=match["match_id"]).first():
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
                        # print(f"Exception while parse match {match['match_id']}\n\n{e}")
                        pass
            
            app.logger.info(f'First loop {min_match_id}')
            time.sleep(Static.API_REQUEST_DELAY)
            
            if isinstance(match, dict):
                min_match_id = match["match_id"]
                info.min_match_id = min_match_id
                db.session.commit()
            
                min_match_start_time = match["start_time"]
        # Toggle variable when reaches end
        info.reached_2020 = True
        db.session.commit()
        
        # Infinite loop. 01.01.2021 has been already reached.
        while True:
            # Go up
            min_match_id = max_match_id
            max_match_id += 100
            info.min_match_id = min_match_id
            info.max_match_id = max_match_id
            db.session.commit()
            
            url = f"https://api.opendota.com/api/publicMatches?less_than_match_id={max_match_id}"
            matches: list[dict] = requests.get(url).json()
            
            for match in matches:
                if match_fits_conditions(match) and not Match.query.filter_by(id=match["match_id"]).first():
                    print(f'First fn: {match["radiant_team"]}')
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
                        # print(f"Exception while safe match {match['match_id']}\n\n{e}")
                        pass
            
            app.logger.info(f'Second loop {min_match_id}')

            # Задержка между запросами
            time.sleep(Static.API_REQUEST_DELAY)
            
    # Elif script was terminated
    else:
        reached_2020 = info.reached_2020

        if not reached_2020:
            url = f"https://api.opendota.com/api/publicMatches?less_than_match_id={min_match_id}"
            matches: list = requests.get(url).json()
            
            for match in matches:
                if match_fits_conditions(match) and not Match.query.filter_by(id=match["match_id"]).first():
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
                        # print(f"Exception while parse match {match['match_id']}\n\n{e}")
                        pass
            
            
            # Decrease min_match_id
            if isinstance(match, dict):
                min_match_id = match['match_id']
                info.min_match_id = min_match_id
                db.session.commit()
                
                min_match_start_time = match['start_time']
            
            # Задержка между запросами
            time.sleep(Static.API_REQUEST_DELAY)
            
            app.logger.info(f'Reached 2024 loop_2 {min_match_id}')
            while min_match_start_time >= Static.UNIX_TIME_2024:  # Iterates since date 01.01.2024
                url = f"https://api.opendota.com/api/publicMatches?less_than_match_id={min_match_id}"
                matches: list = requests.get(url).json()
                
                for match in matches:
                    if match_fits_conditions(match) and not Match.query.filter_by(id=match["match_id"]).first():
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
                            # print(f"Exception while parse match {match['match_id']}\n\n{e}")
                            pass
                
                
                
                if isinstance(match, dict):
                    min_match_id = match["match_id"]
                    info.min_match_id = min_match_id
                    db.session.commit()
                
                    min_match_start_time = match["start_time"]
                
                # Задержка между запросами
                time.sleep(Static.API_REQUEST_DELAY)
           
            info.reached_2020 = True
            db.session.commit()
        
        # Infinite loop. 01.01.2024 has been already reached.
        app.logger.info(f'Reached 2024 loop_3 {min_match_id}')
        while True:
            # Go up
            min_match_id = max_match_id
            max_match_id += 100
            info.min_match_id = min_match_id
            info.max_match_id = max_match_id
            db.session.commit()
            
            url = f"https://api.opendota.com/api/publicMatches?less_than_match_id={max_match_id}"
            matches: list = requests.get(url).json()
            
            for match in matches:
                if match_fits_conditions(match):
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
                        # print(f"Exception while safe match {match['match_id']}\n\n{e}")
                        pass
            app.logger.info(f'Reached 2024 loop_3 {min_match_id}')
            # Задержка между запросами
            time.sleep(Static.API_REQUEST_DELAY)
            # app.logger.warning('In infinite loop')
