from django import template
from django.conf import settings
from django.core.cache import cache

from ..apps.users.models import LeagueRating

import re
import requests

register = template.Library()

API_BASE = 'https://psyonix-rl.appspot.com'
API_VERSION = '105'
CACHE_KEY = 'API_SESSION_ID'
CACHE_TIMEOUT = 60 * 60 * 4  # 14,400 seconds = 4 hours

try:
    from ..settings.secrets import api_login
except ImportError:
    print("You are missing the `api_login` function in your settings. This script cannot run without it.")
    exit()


def get_league_data(steam_ids):
    """
    Season 1:
    Playlist=0&Mu=20.6591&Sigma=4.11915&RankPoints=100
    Playlist=10&Mu=27.0242&Sigma=2.96727&RankPoints=292
    Playlist=11&Mu=37.0857&Sigma=2.5&RankPoints=618
    Playlist=12&Mu=35.8244&Sigma=2.5&RankPoints=500
    Playlist=13&Mu=33.5018&Sigma=2.5&RankPoints=468
    """

    """
    Season 2:
    Playlist=0&Mu=20.6134&Sigma=3.2206&Tier=
    Playlist=10&Mu=24.9755&Sigma=2.5&Tier=
    Playlist=11&Mu=29.3782&Sigma=2.5&Tier=
    Playlist=12&Mu=34.4383&Sigma=2.5&Tier=
    Playlist=13&Mu=34.5306&Sigma=2.5&Tier=
    """

    """
    Season 2, Patch 1.13:
    Playlist=0&Mu=25.6939&Sigma=2.5&Tier=&Division=&MatchesPlayed=&MMR=
    Playlist=10&Mu=31.8213&Sigma=4.88486&Tier=5&Division=0&MatchesPlayed=11&MMR=17.1667
    Playlist=11&Mu=25.0579&Sigma=2.5&Tier=5&Division=0&MatchesPlayed=31&MMR=17.5579
    Playlist=12&Mu=29.5139&Sigma=3.75288&Tier=0&Division=0&MatchesPlayed=7&MMR=18.2552
    Playlist=13&Mu=27.0215&Sigma=2.5&Tier=5&Division=0&MatchesPlayed=27&MMR=19.5215
    """

    all_steam_ids = list(steam_ids)

    for steam_ids in chunks(all_steam_ids, 10):
        data = {
            'Proc[]': [
                'GetPlayerSkillSteam'
            ] * len(steam_ids),
        }

        for index, steam_id in enumerate(steam_ids):
            data['P{}P[]'.format(index)] = [str(steam_id)]

        headers = api_login()
        r = requests.post(
            API_BASE + '/callproc{}/'.format(API_VERSION),
            headers=headers,
            data=data
        )

        if r.text.strip() == 'SCRIPT ERROR SessionNotActive:':
            print('Hit SessionNotActive')
            cache.delete(CACHE_KEY)
            continue

        # Split the response into individual chunks.
        response_chunks = r.text.strip().split('\r\n\r\n')

        for index, response in enumerate(response_chunks):
            print('Getting rating data for', steam_ids[index])
            matches = re.findall(r'Playlist=(\d{1,2})&Mu=([0-9\.]+)&Sigma=([0-9\.]+)&Tier=(\d*)&Division=(\d?)&MatchesPlayed=(\d*)&MMR=([0-9\.]*)', response)

            if not matches:
                print('no matches')
                continue

            has_tiers = False
            matches_dict = {}

            for match in matches:
                playlist, mu, sigma, tier, division, matches_played, mmr = match

                if tier != '' and tier != '0':
                    has_tiers = True

                    matches_dict[playlist] = {
                        'mu': mu,
                        'sigma': sigma,
                        'tier': tier,
                        'division': division,
                        'matches_played': matches_played,
                        'mmr': mmr,
                    }

            if not has_tiers:
                print('No tiers')
                continue

            object_data = {}

            if str(settings.PLAYLISTS['RankedDuels']) in matches_dict:
                object_data['duels'] = matches_dict[str(settings.PLAYLISTS['RankedDuels'])]['tier']
                object_data['duels_division'] = matches_dict[str(settings.PLAYLISTS['RankedDuels'])]['division']
                object_data['duels_matches_played'] = matches_dict[str(settings.PLAYLISTS['RankedDuels'])]['matches_played']

                if matches_dict[str(settings.PLAYLISTS['RankedDuels'])]['mmr'] != '':
                    object_data['duels_mmr'] = matches_dict[str(settings.PLAYLISTS['RankedDuels'])]['mmr']
            else:
                object_data['duels'] = 0

            if str(settings.PLAYLISTS['RankedDoubles']) in matches_dict:
                object_data['doubles'] = matches_dict[str(settings.PLAYLISTS['RankedDoubles'])]['tier']
                object_data['doubles_division'] = matches_dict[str(settings.PLAYLISTS['RankedDoubles'])]['division']
                object_data['doubles_matches_played'] = matches_dict[str(settings.PLAYLISTS['RankedDoubles'])]['matches_played']

                if matches_dict[str(settings.PLAYLISTS['RankedDoubles'])]['mmr'] != '':
                    object_data['doubles_mmr'] = matches_dict[str(settings.PLAYLISTS['RankedDoubles'])]['mmr']
            else:
                object_data['doubles'] = 0

            if str(settings.PLAYLISTS['RankedSoloStandard']) in matches_dict:
                object_data['solo_standard'] = matches_dict[str(settings.PLAYLISTS['RankedSoloStandard'])]['tier']
                object_data['solo_standard_division'] = matches_dict[str(settings.PLAYLISTS['RankedSoloStandard'])]['division']
                object_data['solo_standard_matches_played'] = matches_dict[str(settings.PLAYLISTS['RankedSoloStandard'])]['matches_played']

                if matches_dict[str(settings.PLAYLISTS['RankedSoloStandard'])]['mmr'] != '':
                    object_data['solo_standard_mmr'] = matches_dict[str(settings.PLAYLISTS['RankedSoloStandard'])]['mmr']
            else:
                object_data['solo_standard'] = 0

            if str(settings.PLAYLISTS['RankedStandard']) in matches_dict:
                object_data['standard'] = matches_dict[str(settings.PLAYLISTS['RankedStandard'])]['tier']
                object_data['standard_division'] = matches_dict[str(settings.PLAYLISTS['RankedStandard'])]['division']
                object_data['standard_matches_played'] = matches_dict[str(settings.PLAYLISTS['RankedStandard'])]['matches_played']

                if matches_dict[str(settings.PLAYLISTS['RankedStandard'])]['mmr'] != '':
                    object_data['standard_mmr'] = matches_dict[str(settings.PLAYLISTS['RankedStandard'])]['mmr']
            else:
                object_data['standard'] = 0

            print(object_data)

            # Store this rating.
            LeagueRating.objects.create(
                steamid=steam_ids[index],
                **object_data
            )


def chunks(input_list, chunk_length):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(input_list), chunk_length):
        yield input_list[i:i+chunk_length]
