import time
import threading

from pypresence import Presence as PyPresence

from . import pygpen as pp

from .const import Difficulties

CLIENT_ID = '1289414646029357088'

class Presence(pp.ElementSingleton):
    def __init__(self):
        super().__init__()

        self.start = time.time()
        self.last_state = None
        self.rpc = None
        self.valid = False
        
        threading.Thread(target=self.init_task, daemon=True).start()

    def init_task(self):
        try:
            self.rpc = PyPresence(client_id=CLIENT_ID)
            self.rpc.connect()
            self.valid = True
        except Exception as e:
            print('RPC Init Failed:', e)
        
    def update_task(self, **kwargs):
        self.rpc.update(**kwargs)

    def update(self):
        if self.valid:
            try:
                state = self.e['State'].season
                if self.e['State'].title:
                    state = 'home'
                
                if state != self.last_state:
                    if (self.last_state == 'home') or (state == 'home'):
                        self.start = time.time()
                    self.last_state = state

                    difficulty_name = Difficulties.info(self.e['State'].difficulty_set)['name']

                    if state == 'home':
                        location = 'Main Menu'
                        details = None
                    else:
                        location = f'{state[0].upper()}{state[1:]}'
                        details = f'Wave {self.e["State"].wave} | {difficulty_name}'

                    info = {
                        'start': int(self.start),
                        'state': location,
                        'large_image': f'{state}_icon',
                        'buttons': [{'label': 'Steam', 'url': 'https://store.steampowered.com/app/2824730/Yawnoc'}],
                        'small_image': 'base_icon' if (state == 'home') else f'difficulty_{self.e["State"].difficulty_set}',
                    }

                    if details:
                        info['details'] = details

                    threading.Thread(target=self.update_task, daemon=True, kwargs=info).start()

            except Exception as e:
                pass