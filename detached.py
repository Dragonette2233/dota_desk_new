import requests

def get_public_matches():
    url = "https://api.opendota.com/api/publicMatches"
    response = requests.get(url)
    return response.json()

def get_match_details(match_id):
    url = f"https://api.opendota.com/api/matches/{match_id}"
    response = requests.get(url)
    return response.json()

def rank_tier_to_mmr(rank_tier):
    tier = rank_tier // 10
    sub_tier = rank_tier % 10
    if tier == 0:
        return (0 + 144 * sub_tier + 144 * (sub_tier + 1)) / 2
    elif tier == 1:
        return (720 + 168 * (sub_tier - 1) + 168 * sub_tier) / 2
    elif tier == 2:
        return (1560 + 168 * (sub_tier - 1) + 168 * sub_tier) / 2
    elif tier == 3:
        return (2400 + 168 * (sub_tier - 1) + 168 * sub_tier) / 2
    elif tier == 4:
        return (3240 + 168 * (sub_tier - 1) + 168 * sub_tier) / 2
    elif tier == 5:
        return (4080 + 168 * (sub_tier - 1) + 168 * sub_tier) / 2
    elif tier == 6:
        return (4920 + 168 * (sub_tier - 1) + 168 * sub_tier) / 2
    elif tier == 7:
        return 5760
    return None

def calculate_avg_mmr_from_rank_tier(match_details):
    players = match_details.get("players", [])
    mmrs = [rank_tier_to_mmr(player.get("rank_tier")) for player in players if player.get("rank_tier") is not None]
    mmrs = [mmr for mmr in mmrs if mmr is not None]
    if not mmrs:
        return None
    return sum(mmrs) / len(mmrs)



print(rank_tier_to_mmr(55))

