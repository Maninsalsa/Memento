import os

from . import pygpen as pp

from steamworks import STEAMWORKS
from steamworks.exceptions import SteamNotRunningException
from .const import CWD

class Steamworks(pp.ElementSingleton):
    def __init__(self):
        super().__init__()

        self.steamworks = None

        try:
            #os.add_dll_directory(f'{CWD}/steamworks')

            self.steamworks = STEAMWORKS()
            self.steamworks.initialize()
            self.steamworks.UserStats.RequestCurrentStats()
            self.steamworks.run_callbacks()
        except Exception as e:
            print('steamworks error', e)

    def grant_achievement(self, achievement_id):
        try:
            if not self.steamworks.UserStats.GetAchievement(bytes(achievement_id, 'utf-8')):
                print('giving achievement', achievement_id)
                success = self.steamworks.UserStats.SetAchievement(bytes(achievement_id, 'utf-8'))
                if success:
                    print('success')
                self.store_stats()
        except Exception as e:
            print('steamworks achievement error', achievement_id, e)
    
    def increment_stat(self, stat_id, amount):
        try:
            value = self.steamworks.UserStats.GetStatInt(bytes(stat_id, 'utf-8'))
            self.steamworks.UserStats.SetStat(bytes(stat_id, 'utf-8'), value + amount)
            return value + 1
        except Exception as e:
            print('steamworks stat increment error', stat_id, amount, e)
        return 0

    def store_stats(self):
        try:
            self.steamworks.UserStats.StoreStats()
            self.steamworks.run_callbacks()
        except Exception as e:
            print('steamworks achievement store error', e)

    def open_store_page(self):
        if self.steamworks:
            self.steamworks.Friends.ActivateGameOverlayToStore(int(self.steamworks.app_id))

