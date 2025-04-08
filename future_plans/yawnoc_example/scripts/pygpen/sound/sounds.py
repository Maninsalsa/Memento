import pygame

from threading import Timer

from ..misc.errors import InvalidAsset
from ..utils.elements import ElementSingleton
from ..utils.io import recursive_file_op

class Sounds(ElementSingleton):
    def __init__(self, path=None, filetype='wav'):
        super().__init__()
        pygame.mixer.init()
        pygame.mixer.set_num_channels(64)
        self.path = path
        self.filetype = filetype
        self.pan_vol = True
        if path:
            self.load(path)

        self.frame_sounds_played = {}

    def update(self):
        self.frame_sounds_played = {}
    
    def load(self, path):
        self.path = path
        self.sounds = recursive_file_op(self.path, lambda x: pygame.mixer.Sound(x), filetype=self.filetype)

    def play(self, sound_id, volume=1.0, angle=0, distance=0, times=0):
        if sound_id not in self.frame_sounds_played:
            self.frame_sounds_played[sound_id] = 1
        else:
            self.frame_sounds_played[sound_id] += 1

        if (distance and self.frame_sounds_played[sound_id] < 4) or (self.frame_sounds_played[sound_id] < 2):
            volume *= self.e['Settings'].sfx_volume
            
            sound_id_split = sound_id.split('/')
            s = self.sounds
            while len(sound_id_split):
                next_id = sound_id_split.pop(0)
                if (type(s) == dict) and (next_id in s):
                    s = s[next_id]
                else:
                    raise InvalidAsset(sound_id)
            if type(s) != pygame.mixer.Sound:
                raise InvalidAsset(sound_id)

            channel = s.play(times)
            if channel:
                if distance:
                    channel.set_volume(volume)
                    channel.set_source_location(angle, max(0, min(255, distance)))
                else:
                    channel.set_volume(volume)
        