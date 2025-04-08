import math

import pygame

from . import pygpen as pp

from .pause import PauseMenu
from .tutorial import Tutorial
from .util import format_time
from .const import DEMO

class HUD(pp.ElementSingleton):
    def __init__(self):
        super().__init__()

        self.scrap_spin = 0
        self.flash = 0

        self.swap_offset = 0

        self.team_alert = -1
        self.team_alert_target = None
        self.team_alert_offsets = [-100, -100]

        self.boss = None

        self.hide_ui = False

        self.guide_target = None

        self.pause_menu = PauseMenu()
        self.tutorial = Tutorial()

    def new_team_alert(self, member):
        self.team_alert = 2.5
        self.team_alert_offsets = [self.e['Game'].display.get_width() + 100] * 2
        self.team_alert_target = member
        self.e['Sounds'].play('ding', volume=0.2)

    def update(self):
        if self.e['Input'].pressed('hide_ui'):
            self.hide_ui = not self.hide_ui
        self.pause_menu.update()
        self.tutorial.update()

    def render(self):
        if not self.hide_ui:
            self.tutorial.render()

            if self.guide_target:
                start_pos = self.e['Game'].player.center
                distance = pp.game_math.distance(self.guide_target, start_pos)
                if distance > 30:
                    angle = math.atan2(self.guide_target[1] - start_pos[1], self.guide_target[0] - start_pos[0])
                    arrow_base = pp.utils.game_math.advance(list(start_pos), angle, 20 + math.sin(self.e['Window'].time * 9) * 2.5)
                    arrow_points = [
                        pp.utils.game_math.advance(list(arrow_base), angle, 8),
                        pp.utils.game_math.advance(list(arrow_base), angle + math.pi / 2, 3),
                        pp.utils.game_math.advance(list(arrow_base), angle - math.pi / 2, 3),
                    ]
                    for offset in [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1)]:
                        color = (38, 27, 46)
                        z = 9980
                        if offset == (0, 0):
                            color = (254, 252, 211)
                            z = 9981
                        render_points = [(p[0] + offset[0] - self.e['Game'].camera[0], p[1] + offset[1] - self.e['Game'].camera[1]) for p in arrow_points]
                        self.e['Renderer'].renderf(pygame.draw.polygon, color, render_points, z=z, group='ui')
                self.guide_target = None

            score_text = f'Wave: {self.e["State"].wave}'
            if DEMO:
                score_text = f'Wave: {self.e["State"].wave} / 10'
                if self.e['State'].season != 'summer':
                    score_text = f'Wave: 0 / 10'

            self.swap_offset += -self.swap_offset * self.e['Window'].dt * 10
            if self.swap_offset < 0.5:
                self.swap_offset = 0

            if self.team_alert > -1:
                member_anim = self.team_alert_target.animations['run']
                anim_img = member_anim.images[int(self.e['Window'].time * 10) % len(member_anim.images)]
                self.e['Renderer'].blit(anim_img, (self.e['Game'].display.get_width() - (self.team_alert_offsets[0] + self.team_alert_offsets[1]) / 2 - anim_img.get_width() / 2, 90 - anim_img.get_height()), z=10002, group='ui')
                alert_text = f'{self.team_alert_target.name} is now tagging along!'
                progress = [max(0, int((2 - self.team_alert) * 50)), int(max(0, -self.team_alert * 80))]
                self.team_alert = max(-1, self.team_alert - self.e['Window'].dt)
                self.e['Text']['small_font'].renderzb(alert_text[:progress[0]], (self.e['Game'].display.get_width() / 2 - self.e['Text']['small_font'].width(alert_text[:progress[0]]) / 2, 92), color=(254, 252, 211), bgcolor=(38, 27, 46), hide_chars=progress[1], z=10002, group='ui')
            if self.team_alert > 0:
                self.team_alert_offsets[0] += (self.e['Game'].display.get_width() / 2 - 80 - self.team_alert_offsets[0]) * self.e['Window'].dt * 5
                self.team_alert_offsets[1] += (self.e['Game'].display.get_width() / 2 + 80 - self.team_alert_offsets[1]) * self.e['Window'].dt * 5
            else:
                self.team_alert_offsets[0] += (-100 - self.team_alert_offsets[0]) * self.e['Window'].dt * 5
                self.team_alert_offsets[1] += (-100 - self.team_alert_offsets[1]) * self.e['Window'].dt * 5

            if self.team_alert_offsets[1] > -50:
                self.e['Renderer'].renderf(pygame.draw.line, (254, 252, 211), (self.e['Game'].display.get_width() - self.team_alert_offsets[0], 101), (self.e['Game'].display.get_width() - self.team_alert_offsets[1], 101), z=10003, group='ui')
                self.e['Renderer'].renderf(pygame.draw.line, (38, 27, 46), (self.e['Game'].display.get_width() - self.team_alert_offsets[0] + 1, 102), (self.e['Game'].display.get_width() - self.team_alert_offsets[1] - 1, 102), z=10001, group='ui')

            if self.e['Game'].player.dead:
                if (not self.e['PauseMenu'].paused) or (self.e['PauseMenu'].mode != 'dead'):
                    if not self.e['PauseMenu'].death_consumed:
                        self.e['PauseMenu'].pause(mode='dead')

            elif not self.e['State'].title:
                self.e['Game'].minimap.render()

                health_surf = pygame.Surface((self.e['Game'].player.health / self.e['Game'].player.max_health * 94, 10))
                health_surf.blit(self.e['Assets'].images['misc']['health'], (health_surf.get_width() - 94, 0))
                shield_surf = pygame.Surface((min(1, self.e['Game'].player.total_shield / self.e['Game'].player.max_health) * 94, 4))
                shield_surf.blit(self.e['Assets'].images['misc']['shield'], (shield_surf.get_width() - 94, 0))
                if self.e['Game'].player.hurt > 0.99:
                    health_surf.fill((254, 252, 211))
                    shield_surf.fill((254, 252, 211))
                self.e['Renderer'].blit(self.e['Assets'].images['misc']['health_bar'], (4 - self.e['State'].left_inv_offset, 4), z=9998, group='ui')
                self.e['Renderer'].blit(health_surf, (9 - self.e['State'].left_inv_offset, 12), z=9997, group='ui')
                self.e['Renderer'].blit(shield_surf, (9 - self.e['State'].left_inv_offset, 16), z=9997.5, group='ui')

                tl_hud_offset = 0
                if self.e['Game'].player.partner[0]:
                    partner = self.e['Game'].player.partner[0]
                    self.e['Renderer'].blit(self.e['Assets'].images['misc']['partner_health_bar'], (7 - self.e['State'].left_inv_offset, 23), z=9998, group='ui')
                    health_surf = pygame.Surface((partner.health / partner.max_health * 70, 5))
                    health_surf.blit(self.e['Assets'].images['misc']['health'], (health_surf.get_width() - 94, -2))
                    if partner.hurt > 0.2:
                        health_surf.fill((254, 252, 211))
                    self.e['Renderer'].blit(health_surf, (25 - self.e['State'].left_inv_offset, 23), z=9997, group='ui')
                    self.e['Renderer'].blit(self.e['Assets'].images['partner_icons'][partner.type], (12 - self.e['State'].left_inv_offset, 23), z=9998.5, group='ui')
                    tl_hud_offset = 12

                primary_img = self.e['Assets'].images['weapons'][f'{self.e["Game"].player.weapon.type}_icon']
                self.e['Renderer'].blit(primary_img, (4 + self.swap_offset - self.e['State'].left_inv_offset, 31 - primary_img.get_height() / 2 + tl_hud_offset), z=9998, group='ui')
                self.e['Game'].player.weapon.render_stars((4 + self.swap_offset - self.e['State'].left_inv_offset, 31 - primary_img.get_height() / 2 + tl_hud_offset + primary_img.get_height() - 3), group='ui', z=9999)
                if self.e['Game'].player.alt_weapon:
                    secondary_img = self.e['Assets'].images['weapons'][f'{self.e["Game"].player.alt_weapon.type}_flat']
                    self.e['Renderer'].blit(secondary_img, (20 - self.swap_offset - self.e['State'].left_inv_offset, 35 - secondary_img.get_height() / 2 + tl_hud_offset), z=9997, group='ui')

                self.scrap_spin += -self.scrap_spin * 10 * self.e['Window'].dt
                if abs(self.scrap_spin) < 6:
                    self.scrap_spin = 0
                scrap_img = pygame.transform.rotate(self.e['Assets'].images['misc']['scrap'], self.scrap_spin)
                scrap_img.set_colorkey((0, 0, 0))
                self.e['Renderer'].blit(scrap_img, (7 - scrap_img.get_width() / 2 - self.e['State'].left_inv_offset, 49 - scrap_img.get_height() / 2 + tl_hud_offset), z=9997, group='ui')
                self.e['Text']['small_font'].renderzb(f'{self.e["State"].scrap:,}', (13 - self.e['State'].left_inv_offset, 45 + tl_hud_offset), color=(254, 252, 211), bgcolor=(38, 27, 46), offset=(0, 0), group='ui', z=9997)

                self.e['Text']['small_font'].renderzb(score_text, (5 - self.e['State'].left_inv_offset, 56 + tl_hud_offset), color=(254, 252, 211), bgcolor=(38, 27, 46), offset=(0, 0), group='ui', z=9998)

                timer_text = format_time(int(self.e['State'].difficulty))
                difficulty_color = [(254, 252, 211), (238, 209, 108), (228, 103, 71), (191, 60, 96), (125, 43, 88)][min(4, int(self.e['State'].difficulty // (60 * 6)))]
                self.e['Text']['small_font'].renderzb(timer_text, (5 - self.e['State'].left_inv_offset, 67 + tl_hud_offset), color=difficulty_color, bgcolor=(38, 27, 46), offset=(0, 0), group='ui', z=9998)

                if self.e['State'].upgrade_stat('potato_farmer'):
                    potato_img = self.e['Assets'].images['misc']['potato']
                    self.e['Renderer'].blit(potato_img, (7 - potato_img.get_width() / 2 - self.e['State'].left_inv_offset, 83 - potato_img.get_height() / 2 + tl_hud_offset), z=9997, group='ui')
                    self.e['Text']['small_font'].renderzb(f'{self.e["State"].potatoes:,}', (13 - self.e['State'].left_inv_offset, 78 + tl_hud_offset), color=(254, 252, 211), bgcolor=(38, 27, 46), offset=(0, 0), group='ui', z=9997)

                if self.e['Game'].player.hurt:
                    hurt_fill = pygame.Surface(self.e['Game'].display.get_size()).convert_alpha()
                    hurt_fill.fill((191, 60, 96))
                    hurt_fill.set_alpha(max(0, min(255, self.e['Game'].player.hurt * 80)))
                    self.e['Renderer'].blit(hurt_fill, (0, 0), z=9990, group='ui')
                    hurt_img = self.e['Assets'].images['misc']['hurt']
                    hurt_img.set_alpha(max(0, min(255, self.e['Game'].player.hurt * 200)))
                    self.e['Renderer'].blit(hurt_img, (0, 0), z=9990, group='ui')

                if self.e['Machines'].beacon or self.boss:
                    if self.e['Machines'].beacon:
                        boss_health = self.e['Machines'].beacon.health
                        boss_max_health = self.e['Machines'].beacon.max_health
                        hurt = self.e['Machines'].beacon.hurt
                        boss_name = 'Beacon'
                    else:
                        boss_health = self.boss.health
                        boss_max_health = self.boss.max_health
                        hurt = self.boss.hurt
                        boss_name = '???'
                        if self.boss.type == 'eye':
                            boss_name = 'World\'s Eye'
                        if self.boss.type == 'eye_small':
                            boss_name = 'Satellite Eye'
                    beacon_health_border = self.e['Assets'].images['misc']['boss_health']
                    self.e['Renderer'].blit(beacon_health_border, (self.e['Game'].display.get_width() / 2 - beacon_health_border.get_width() / 2, self.e['Game'].display.get_height() - 13), z=9998, group='ui')
                    health_surf = pygame.Surface((boss_health / boss_max_health * 122, 5))
                    health_surf.blit(self.e['Assets'].images['misc']['boss_health_bg'], (health_surf.get_width() - 122, -2))
                    if hurt > 0.25:
                        health_surf.fill((254, 252, 211))
                    self.e['Renderer'].blit(health_surf, (self.e['Game'].display.get_width() / 2 - beacon_health_border.get_width() / 2 + 2, self.e['Game'].display.get_height() - 11), z=9997, group='ui')
                    self.e['Text']['small_font'].renderzb(boss_name, (self.e['Game'].display.get_width() / 2 - self.e['Text']['small_font'].width(boss_name) / 2, self.e['Game'].display.get_height() - 22), color=(254, 252, 211), bgcolor=(38, 27, 46), group='ui', z=9998)

            self.flash = max(0, self.flash - self.e['Window'].dt * 4)
            if self.flash:
                white = pygame.Surface(self.e['Game'].display.get_size())
                white.fill((254, 252, 211))
                white.set_alpha(int(min(1, self.flash) * 255))
                self.e['Renderer'].blit(white, (0, 0), z=10011, group='ui')

            self.boss = None

        self.pause_menu.render()

        render_cursor = True
        if self.e['Game'].controller_mode:
            if self.e['State'].ui_busy:
                render_cursor = False
            if not any(self.e['Controllers'].read_stick('aim_x', 'aim_y')):
                render_cursor = False
        if self.hide_ui:
            render_cursor = False
        if render_cursor:
            z_offset = 0
            if self.e['Game'].player.dead or (self.e['PauseMenu'].mode == 'victory'):
                z_offset = 1000
            self.e['Renderer'].blit(self.e['Assets'].images['misc']['cursor'], (self.e['Game'].mpos[0] - 4, self.e['Game'].mpos[1] - 4), z=10002 + z_offset, group='ui')