from . import pygpen as pp

class Tutorial(pp.ElementSingleton):
    def __init__(self):
        super().__init__()

    @property
    def state(self):
        if self.e['Game'].controller_mode:
            return self.e['State'].tutorial_progress[1]
        return self.e['State'].tutorial_progress[0]
    
    def advance(self):
        if self.e['Game'].controller_mode:
            self.e['State'].tutorial_progress[1] += 1
        else:
            self.e['State'].tutorial_progress[0] += 1
        self.e['State'].save()
    
    def update(self):
        pass
    
    def render(self):
        if not self.e['State'].ui_busy:
            base_pos = (self.e['Game'].player.center[0] - self.e['Game'].camera[0] + 1, self.e['Game'].player.pos[1] - self.e['Game'].camera[1] - 26 - (1 if self.e['Window'].time % 1 < 0.75 else 0))
            if self.e['Game'].controller_mode:
                if self.state in {0, 3, 5}:
                    input_name = ['move_x', 'primary', 'secondary', 'dodge', 'swap', 'swap'][self.state]
                    if self.state == 5:
                        if not self.e['Game'].player.alt_weapon:
                            return
                    img = self.e['InputTips'].lookup_controller_binding(self.e['Controllers'].inv_name_mapping[input_name])
                    self.e['InputTips'].render_icon(img, (base_pos[0] - img.get_width() / 2, base_pos[1] - img.get_height() / 2))
                if self.state in {1, 2}:
                    input_name = ['move_x', 'primary', 'secondary', 'dodge'][self.state]
                    aim_img = self.e['InputTips'].lookup_controller_binding(self.e['Controllers'].inv_name_mapping['aim_x'])
                    action_img = self.e['InputTips'].lookup_controller_binding(self.e['Controllers'].inv_name_mapping[input_name])
                    self.e['InputTips'].render_icon(aim_img, (base_pos[0] - aim_img.get_width() - 2, base_pos[1] - aim_img.get_height() / 2))
                    self.e['InputTips'].render_icon(action_img, (base_pos[0] + 2, base_pos[1] - action_img.get_height() / 2))
            else:
                if self.state == 0:
                    up_img = self.e['InputTips'].lookup_binding(self.e['Input'].config['up'])
                    down_img = self.e['InputTips'].lookup_binding(self.e['Input'].config['down'])
                    right_img = self.e['InputTips'].lookup_binding(self.e['Input'].config['right'])
                    left_img = self.e['InputTips'].lookup_binding(self.e['Input'].config['left'])

                    self.e['InputTips'].render_icon(down_img, (base_pos[0] - down_img.get_width() / 2, base_pos[1] - down_img.get_height() / 2))
                    self.e['InputTips'].render_icon(left_img, (base_pos[0] - down_img.get_width() / 2 - left_img.get_width() - 3, base_pos[1] - left_img.get_height() / 2))
                    self.e['InputTips'].render_icon(right_img, (base_pos[0] + down_img.get_width() / 2 + 3, base_pos[1] - right_img.get_height() / 2))
                    self.e['InputTips'].render_icon(up_img, (base_pos[0] - up_img.get_width() / 2, base_pos[1] - down_img.get_height() / 2 - up_img.get_height() - 3))
                
                if self.state == 1:
                    shoot_img = self.e['InputTips'].lookup_binding(self.e['Input'].config['shoot'], large=True)
                    self.e['InputTips'].render_icon(shoot_img, (base_pos[0] - shoot_img.get_width() / 2, base_pos[1] - shoot_img.get_height() / 2))
                
                if self.state == 2:
                    secondary_img = self.e['InputTips'].lookup_binding(self.e['Input'].config['secondary'], large=True)
                    self.e['InputTips'].render_icon(secondary_img, (base_pos[0] - secondary_img.get_width() / 2, base_pos[1] - secondary_img.get_height() / 2))
                
                if self.state == 3:
                    roll_img = self.e['InputTips'].lookup_binding(self.e['Input'].config['dodge'], large=True)
                    self.e['InputTips'].render_icon(roll_img, (base_pos[0] - roll_img.get_width() / 2, base_pos[1] - roll_img.get_height() / 2))

                if self.state == 5:
                    if self.e['Game'].player.alt_weapon:
                        swap_img = self.e['InputTips'].lookup_binding(self.e['Input'].config['swap_weapon'], large=True)
                        self.e['InputTips'].render_icon(swap_img, (base_pos[0] - swap_img.get_width() / 2, base_pos[1] - swap_img.get_height() / 2))


                