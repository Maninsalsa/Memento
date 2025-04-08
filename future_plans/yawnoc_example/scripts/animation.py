from . import pygpen as pp

class Animation(pp.Entity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        try:
            self.z = 4 + self.pos[1] / self.e['Tilemap'].tile_size
        except KeyError:
            pass
        
    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        
        if self.animation.finished:
            return True