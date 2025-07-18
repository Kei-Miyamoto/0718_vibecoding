import pyxel
import math
import random

class GameState:
    START_SCREEN = 0
    RUNNING = 1
    GAME_OVER = 2
    GAME_WON = 3

class Launcher:

    def __init__(self, x, y, style="Classic"):
        self.x = x
        self.y = y
        self.angle = -45
        self.power = 5
        self.style = style

    def update(self):
        if pyxel.btn(pyxel.KEY_LEFT):
            self.angle -= 1
        if pyxel.btn(pyxel.KEY_RIGHT):
            self.angle += 1
        self.angle = max(-90, min(0, self.angle))

        if pyxel.btn(pyxel.KEY_UP):
            self.power += 0.1
        if pyxel.btn(pyxel.KEY_DOWN):
            self.power -= 0.1
        self.power = max(1, min(10, self.power))

    def draw(self):
        angle_rad = math.radians(self.angle)
        end_x = self.x + math.cos(angle_rad) * (self.power * 3)
        end_y = self.y + math.sin(angle_rad) * (self.power * 3)

        if self.style == "Classic":
            pyxel.rect(self.x - 6, self.y, 12, 5, 1) # Shadow
            pyxel.rect(self.x - 5, self.y - 1, 10, 5, 13) # Body
            pyxel.line(self.x, self.y, end_x, end_y, 1) # Barrel Shadow
            pyxel.line(self.x, self.y-1, end_x, end_y-1, 7) # Barrel
        elif self.style == "Triangle":
            pyxel.rect(self.x - 8, self.y + 2, 16, 4, 1)
            pyxel.rect(self.x - 7, self.y+1, 14, 2, 13)
            pyxel.circ(self.x, self.y + 2, 3, 1)
            barrel_length = self.power * 2.5
            barrel_width = 3
            p_rad = angle_rad + math.pi / 2
            dx, dy = math.cos(p_rad) * barrel_width, math.sin(p_rad) * barrel_width
            x1, y1 = self.x + dx, self.y + dy
            x2, y2 = self.x - dx, self.y - dy
            tip_x = self.x + math.cos(angle_rad) * (barrel_length + 2)
            tip_y = self.y + math.sin(angle_rad) * (barrel_length + 2)
            pyxel.tri(x1, y1, x2, y2, tip_x, tip_y, 7)
        elif self.style == "Pistol":
            cos_a = math.cos(angle_rad)
            sin_a = math.sin(angle_rad)

            # Points for body and grip, relative to pivot
            body = [(-6, -3), (12, -3), (12, 3), (-6, 3)]
            grip = [(-4, 3), (2, 3), (2, 8), (-4, 8)]
            
            # Rotate body points
            r_body = []
            for x, y in body:
                r_body.append((self.x + x * cos_a - y * sin_a, self.y + x * sin_a + y * cos_a))

            # Rotate grip points
            r_grip = []
            for x, y in grip:
                r_grip.append((self.x + x * cos_a - y * sin_a, self.y + x * sin_a + y * cos_a))

            # Draw Body
            pyxel.tri(r_body[0][0], r_body[0][1], r_body[1][0], r_body[1][1], r_body[2][0], r_body[2][1], 13)
            pyxel.tri(r_body[0][0], r_body[0][1], r_body[2][0], r_body[2][1], r_body[3][0], r_body[3][1], 13)
            
            # Draw Grip
            pyxel.tri(r_grip[0][0], r_grip[0][1], r_grip[1][0], r_grip[1][1], r_grip[2][0], r_grip[2][1], 1)
            pyxel.tri(r_grip[0][0], r_grip[0][1], r_grip[2][0], r_grip[2][1], r_grip[3][0], r_grip[3][1], 1)

        elif self.style == "Crossbow":
            cos_a = math.cos(angle_rad)
            sin_a = math.sin(angle_rad)

            # Define relative points for the crossbow components
            # Bow (relative to launcher pivot)
            bow_left_rel = (-15, 0)
            bow_right_rel = (15, 0)
            
            # Stock (relative to launcher pivot)
            stock_points_rel = [
                (0, -3),  # Top-left of stock
                (4, -3),  # Top-right of stock
                (4, 5),   # Bottom-right of stock
                (0, 5)    # Bottom-left of stock
            ]

            # Function to rotate and translate a point
            def get_rotated_point(px_rel, py_rel):
                rotated_x = self.x + (px_rel * cos_a - py_rel * sin_a)
                rotated_y = self.y + (px_rel * sin_a + py_rel * cos_a)
                return rotated_x, rotated_y

            # Get rotated points for bow
            bl_x, bl_y = get_rotated_point(bow_left_rel[0], bow_left_rel[1])
            br_x, br_y = get_rotated_point(bow_right_rel[0], bow_right_rel[1])

            # Get rotated points for stock
            rotated_stock_points = [get_rotated_point(p[0], p[1]) for p in stock_points_rel]

            # Draw Bow
            pyxel.line(bl_x, bl_y, br_x, br_y, 4) # Bow line

            # Draw Stock
            pyxel.tri(rotated_stock_points[0][0], rotated_stock_points[0][1],
                      rotated_stock_points[1][0], rotated_stock_points[1][1],
                      rotated_stock_points[2][0], rotated_stock_points[2][1], 4)
            pyxel.tri(rotated_stock_points[0][0], rotated_stock_points[0][1],
                      rotated_stock_points[2][0], rotated_stock_points[2][1],
                      rotated_stock_points[3][0], rotated_stock_points[3][1], 4)

            # Main barrel/arrow (still from launcher pivot to end_x, end_y)
            pyxel.line(self.x, self.y, end_x, end_y, 7)

            # Crossbow string (perpendicular to barrel)
            string_offset_from_pivot = -5 # How far back the string is from the pivot
            string_center_x = self.x + math.cos(angle_rad) * string_offset_from_pivot
            string_center_y = self.y + math.sin(angle_rad) * string_offset_from_pivot

            # Perpendicular direction
            perp_angle_rad = angle_rad + math.pi / 2
            string_half_width = 15 # Half of the bow width (30 / 2)

            string_start_x = string_center_x + math.cos(perp_angle_rad) * string_half_width
            string_start_y = string_center_y + math.sin(perp_angle_rad) * string_half_width
            string_end_x = string_center_x - math.cos(perp_angle_rad) * string_half_width
            string_end_y = string_center_y - math.sin(perp_angle_rad) * string_half_width

            pyxel.line(string_start_x, string_start_y, string_end_x, string_end_y, 0) # Black string

        pyxel.text(self.x - 10, self.y - 12, f"P:{int(self.power)}", 7)

class Ball:
    def __init__(self, x, y, angle, power, ball_type="normal", radius=3, style="Normal"):
        self.x = x
        self.y = y
        self.vx = math.cos(math.radians(angle)) * power
        self.vy = math.sin(math.radians(angle)) * power
        self.radius = radius
        self.is_active = True
        self.ball_type = ball_type
        self.style = style
        self.pierce_count = 0

    def update(self):
        if not self.is_active:
            return
        self.vy += 0.15
        self.x += self.vx
        self.y += self.vy
        if self.x < -self.radius or self.x > pyxel.width + self.radius or self.y > pyxel.height + self.radius:
            self.is_active = False

    def draw(self):
        if not self.is_active:
            return

        if self.style == "Normal":
            color = 10
            if self.ball_type == "bomb": color = 8
            elif self.ball_type == "pierce": color = 6
            pyxel.circ(self.x, self.y, self.radius, 1) # Shadow
            pyxel.circ(self.x, self.y - 1, self.radius, color)
            pyxel.circ(self.x, self.y - 2, 1, 7) # Highlight
        elif self.style == "Baseball":
            pyxel.circ(self.x, self.y, self.radius, 1) # Shadow
            pyxel.circ(self.x, self.y - 1, self.radius, 7)
            for i in range(-2, 3):
                pyxel.pset(self.x + i, self.y + (1-abs(i)), 8)
                pyxel.pset(self.x + i, self.y - (3-abs(i)), 8)
        elif self.style == "Billiard":
            pyxel.circ(self.x, self.y, self.radius, 1) # Shadow
            pyxel.circ(self.x, self.y - 1, self.radius, 10)
            pyxel.circ(self.x, self.y - 1, self.radius - 1, 7)
            pyxel.text(self.x - 1, self.y - 3, "8", 1)
        elif self.style == "Slipper":
            # Calculate rotation for slipper
            angle_rad = math.atan2(self.vy, self.vx) # Angle based on ball's velocity
            cos_a = math.cos(angle_rad)
            sin_a = math.sin(angle_rad)

            # Define relative points for slipper components (sole and strap)
            # Sole points relative to ball center
            sole_points_rel = [
                (-4, -2), (4, -2), (4, 3), (-4, 3) # x, y relative to ball center
            ]
            # Strap points relative to ball center
            strap_points_rel = [
                (-4, -4), (1, -4), (1, -2), (-4, -2) # x, y relative to ball center
            ]

            # Function to rotate and translate a point
            def get_rotated_point(px_rel, py_rel):
                rotated_x = self.x + (px_rel * cos_a - py_rel * sin_a)
                rotated_y = self.y + (px_rel * sin_a + py_rel * cos_a)
                return rotated_x, rotated_y

            # Get rotated points for sole
            rotated_sole_points = [get_rotated_point(p[0], p[1]) for p in sole_points_rel]

            # Get rotated points for strap
            rotated_strap_points = [get_rotated_point(p[0], p[1]) for p in strap_points_rel]

            # Draw Sole (Shadow)
            pyxel.tri(rotated_sole_points[0][0]+1, rotated_sole_points[0][1]+1,
                      rotated_sole_points[1][0]+1, rotated_sole_points[1][1]+1,
                      rotated_sole_points[2][0]+1, rotated_sole_points[2][1]+1, 1)
            pyxel.tri(rotated_sole_points[0][0]+1, rotated_sole_points[0][1]+1,
                      rotated_sole_points[2][0]+1, rotated_sole_points[2][1]+1,
                      rotated_sole_points[3][0]+1, rotated_sole_points[3][1]+1, 1)

            # Draw Sole (Main)
            pyxel.tri(rotated_sole_points[0][0], rotated_sole_points[0][1],
                      rotated_sole_points[1][0], rotated_sole_points[1][1],
                      rotated_sole_points[2][0], rotated_sole_points[2][1], 0)
            pyxel.tri(rotated_sole_points[0][0], rotated_sole_points[0][1],
                      rotated_sole_points[2][0], rotated_sole_points[2][1],
                      rotated_sole_points[3][0], rotated_sole_points[3][1], 0)

            # Draw Strap (Shadow)
            pyxel.tri(rotated_strap_points[0][0]+1, rotated_strap_points[0][1]+1,
                      rotated_strap_points[1][0]+1, rotated_strap_points[1][1]+1,
                      rotated_strap_points[2][0]+1, rotated_strap_points[2][1]+1, 1)
            pyxel.tri(rotated_strap_points[0][0]+1, rotated_strap_points[0][1]+1,
                      rotated_strap_points[2][0]+1, rotated_strap_points[2][1]+1,
                      rotated_strap_points[3][0]+1, rotated_strap_points[3][1]+1, 1)

            # Draw Strap (Main)
            pyxel.tri(rotated_strap_points[0][0], rotated_strap_points[0][1],
                      rotated_strap_points[1][0], rotated_strap_points[1][1],
                      rotated_strap_points[2][0], rotated_strap_points[2][1], 0)
            pyxel.tri(rotated_strap_points[0][0], rotated_strap_points[0][1],
                      rotated_strap_points[2][0], rotated_strap_points[2][1],
                      rotated_strap_points[3][0], rotated_strap_points[3][1], 0)

class Block:
    def __init__(self, x, y, width, height, block_type="wood"):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.block_type = block_type
        self.is_active = True
        if block_type == "wood":
            self.hp = 1
            self.base_color = 4
            self.highlight_color = 10
            self.shadow_color = 2
            self.explosion_color = 5
            self.destruction_sound_id = 1
        elif block_type == "stone":
            self.hp = 1
            self.base_color = 13
            self.highlight_color = 7
            self.shadow_color = 6
            self.explosion_color = 0
            self.destruction_sound_id = 2
        elif block_type == "glass":
            self.hp = 1
            self.base_color = 12
            self.highlight_color = 7
            self.shadow_color = 5
            self.explosion_color = 7
            self.destruction_sound_id = 1
        else: # Fallback
            self.hp = 1
            self.base_color = 3
            self.highlight_color = 7
            self.shadow_color = 2
            self.explosion_color = 5
            self.destruction_sound_id = 1
        self.max_hp = self.hp

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.is_active = False
            return True
        return False

    def draw(self):
        if not self.is_active:
            return

        # Draw main body
        pyxel.rect(self.x, self.y, self.width, self.height, self.base_color)

        # Draw 3D effect
        if self.block_type == "wood":
            pyxel.rect(self.x, self.y, self.width, 1, self.highlight_color)
            pyxel.rect(self.x, self.y + self.height -1, self.width, 1, self.shadow_color)
            pyxel.rect(self.x + self.width -1, self.y, 1, self.height, self.shadow_color)
        elif self.block_type == "stone":
            pyxel.rect(self.x, self.y, self.width, 1, self.highlight_color)
            pyxel.rect(self.x, self.y + self.height -1, self.width, 1, self.shadow_color)
            pyxel.rect(self.x + self.width -1, self.y, 1, self.height, self.shadow_color)
            for _ in range(5):
                pyxel.pset(self.x + random.randint(1, self.width-2), self.y + random.randint(1, self.height-2), self.shadow_color)
        elif self.block_type == "glass":
            pyxel.rectb(self.x, self.y, self.width, self.height, self.shadow_color)
            pyxel.rect(self.x+1, self.y+1, self.width-2, self.height-2, self.base_color)
            pyxel.pset(self.x + 1, self.y + 1, self.highlight_color)
        else:
            pyxel.rectb(self.x, self.y, self.width, self.height, 0)

class Explosion:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.life = 20
        self.particles = []
        for _ in range(8):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(0.5, 2)
            self.particles.append({
                'x': x, 'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'color': color
            })

    def update(self):
        self.life -= 1
        for p in self.particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vy'] += 0.05

    def draw(self):
        if self.life > 0:
            for p in self.particles:
                pyxel.pset(p['x'], p['y'], p['color'])

class Item:
    def __init__(self, x, y, item_type):
        self.x = x
        self.y = y
        self.item_type = item_type
        self.is_active = True
        self.vy = 0.5

    def update(self):
        self.y += self.vy
        if self.y > pyxel.height:
            self.is_active = False

    def draw(self):
        if self.is_active:
            if self.item_type == "multi_ball":
                pyxel.circ(self.x, self.y, 4, 11)
            elif self.item_type == "big_ball":
                pyxel.rect(self.x - 2, self.y - 2, 5, 5, 14)
            elif self.item_type == "laser_beam":
                pyxel.tri(self.x, self.y - 2, self.x - 3, self.y + 2, self.x + 3, self.y + 2, 8)

class Laser:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle
        self.is_active = True
        self.length = 0

    def update(self):
        self.length += 10
        if self.length > pyxel.width:
            self.is_active = False

    def draw(self):
        if self.is_active:
            end_x = self.x + math.cos(math.radians(self.angle)) * self.length
            end_y = self.y + math.sin(math.radians(self.angle)) * self.length
            pyxel.line(self.x, self.y, end_x, end_y, 8)

class App:
    def __init__(self):
        pyxel.init(200, 150, title="Pyxel Demolisher")
        # Sounds
        pyxel.sounds[0].set('c2', 't', '7', 's', 3)
        pyxel.sounds[1].set('c1', 'n', '7', 's', 7)
        pyxel.sounds[2].set('c2', 't', '7', 's', 10)
        pyxel.sounds[3].set('c1e1g1', 't', '7', 's', 5)
        pyxel.sounds[4].set('c3', 'p', '7', 's', 10)
        pyxel.sounds[5].set('c3e3g3', 'p', '6', 's', 8)
        pyxel.sounds[6].set('c4', 's', '7', 'v', 15)
        pyxel.sounds[7].set('c4', 't', '7', 's', 10)
        pyxel.sounds[8].set("c4g4c4", "t", "7", "s", 10)

        # Music
        pyxel.musics[0].set([10], [11])
        pyxel.sounds[10].set("g2c3e3g3c3g3e3c3", "p", "6", "s", 15)
        pyxel.sounds[11].set("c1g1c2g2c1g1c2g2", "t", "7", "s", 15)
        pyxel.musics[1].set([12])
        pyxel.sounds[12].set("c4e4g4c4", "t", "7", "s", 10)
        pyxel.musics[2].set([13])
        pyxel.sounds[13].set("g3e3c3a2", "t", "7", "f", 12)
        pyxel.musics[3].set([14])
        pyxel.sounds[14].set("c3g3c4g4 c3g3c4g4", "p", "6", "s", 12)

        self.game_state = GameState.START_SCREEN
        self.launcher_styles = ["Classic", "Triangle", "Pistol", "Crossbow"]
        self.ball_styles = ["Normal", "Baseball", "Billiard", "Slipper"]
        self.selected_launcher_index = 0
        self.selected_ball_index = 0
        self.selected_option = 0

        self.current_stage = 0
        self.highscore = 0
        self.load_highscore()
        self.reset_game()
        pyxel.run(self.update, self.draw)

    def load_highscore(self):
        try:
            with open("highscore.txt", "r") as f:
                self.highscore = int(f.read())
        except FileNotFoundError:
            self.highscore = 0
        except ValueError:
            self.highscore = 0 # Handle corrupted file

    def save_highscore(self):
        with open("highscore.txt", "w") as f:
            f.write(str(self.highscore))

    def reset_game(self):
        pyxel.stop()
        selected_launcher_style = self.launcher_styles[self.selected_launcher_index]
        self.launcher = Launcher(20, pyxel.height - 10, style=selected_launcher_style)
        self.balls = []
        self.blocks = []
        self.explosions = []
        self.items = []
        self.lasers = []
        self.score = 0
        self.balls_left = 5
        self.current_ball_type = "normal"
        self.shake_intensity = 0
        self.combo_count = 0
        self.combo_timer = 0
        self.multi_ball_timer = 0
        self.big_ball_timer = 0
        self.laser_beam_timer = 0
        self.fever_mode = False
        self.fever_timer = 0
        self.fever_shot_timer = 0
        self.fantastic_display_timer = 0
        self.was_power_max = False
        self.ground_y = pyxel.height - 5
        self.generate_random_blocks()
        if self.current_stage % 3 == 1: self.current_ball_type = "bomb"
        elif self.current_stage % 3 == 2: self.current_ball_type = "pierce"
        else: self.current_ball_type = "normal"
        
        if self.game_state == GameState.RUNNING:
            pyxel.playm(0, loop=True)

    def update(self):
        if self.game_state == GameState.START_SCREEN:
            self.update_start_screen()
        elif self.game_state == GameState.RUNNING:
            self.update_game()
        elif self.game_state == GameState.GAME_OVER:
            if pyxel.btnp(pyxel.KEY_RETURN):
                self.game_state = GameState.START_SCREEN
        elif self.game_state == GameState.GAME_WON:
            if pyxel.btnp(pyxel.KEY_RETURN):
                self.current_stage += 1
                self.game_state = GameState.RUNNING
                self.reset_game()

    def draw(self):
        pyxel.cls(12)
        if self.game_state == GameState.START_SCREEN:
            self.draw_start_screen()
        else:
            self.draw_game()

    def update_start_screen(self):
        if pyxel.btnp(pyxel.KEY_UP): self.selected_option = 0
        if pyxel.btnp(pyxel.KEY_DOWN): self.selected_option = 1

        if self.selected_option == 0:
            if pyxel.btnp(pyxel.KEY_LEFT): self.selected_launcher_index = (self.selected_launcher_index - 1 + len(self.launcher_styles)) % len(self.launcher_styles)
            if pyxel.btnp(pyxel.KEY_RIGHT): self.selected_launcher_index = (self.selected_launcher_index + 1) % len(self.launcher_styles)
        else:
            if pyxel.btnp(pyxel.KEY_LEFT): self.selected_ball_index = (self.selected_ball_index - 1 + len(self.ball_styles)) % len(self.ball_styles)
            if pyxel.btnp(pyxel.KEY_RIGHT): self.selected_ball_index = (self.selected_ball_index + 1) % len(self.ball_styles)

        if pyxel.btnp(pyxel.KEY_RETURN):
            self.game_state = GameState.RUNNING
            self.current_stage = 0
            self.reset_game()

    def draw_start_screen(self):
        pyxel.cls(1)
        pyxel.text(70, 20, "Pyxel Demolisher", pyxel.frame_count % 16)
        
        launcher_text = f"Launcher: < {self.launcher_styles[self.selected_launcher_index]} >"
        pyxel.text(50, 60, launcher_text, 10 if self.selected_option == 0 else 7)

        ball_text = f"Ball Style: < {self.ball_styles[self.selected_ball_index]} >"
        pyxel.text(50, 80, ball_text, 10 if self.selected_option == 1 else 7)

        pyxel.text(55, 120, "Press Enter to Start", 7)
        pyxel.text(5, 140, f"HIGH SCORE: {self.highscore}", 7)

    def update_game(self):
        if self.shake_intensity > 0:
            self.shake_intensity *= 0.9
            if self.shake_intensity < 0.1: self.shake_intensity = 0

        if self.combo_timer > 0: self.combo_timer -= 1
        else:
            if self.combo_count > 1: self.score += self.combo_count * 50
            self.combo_count = 0

        if self.multi_ball_timer > 0: self.multi_ball_timer -= 1
        if self.big_ball_timer > 0:
            self.big_ball_timer -= 1
            if self.big_ball_timer == 0:
                for ball in self.balls: ball.radius = 3
        if self.laser_beam_timer > 0: self.laser_beam_timer -= 1

        if self.fever_mode:
            self.fever_timer -= 1
            if self.fever_timer == 0:
                self.fever_mode = False
                pyxel.stop()
                pyxel.playm(0, loop=True)
            if self.fever_shot_timer > 0: self.fever_shot_timer -= 1

        self.launcher.update()

        if self.launcher.power == 10 and not self.was_power_max:
            self.fantastic_display_timer = 60
            pyxel.play(0, 8)
        self.was_power_max = (self.launcher.power == 10)

        if self.fantastic_display_timer > 0: self.fantastic_display_timer -= 1

        selected_ball_style = self.ball_styles[self.selected_ball_index]
        if self.fever_mode:
            if pyxel.btn(pyxel.KEY_SPACE) and self.fever_shot_timer == 0:
                power = self.launcher.power * 1.5
                self.balls.append(Ball(self.launcher.x, self.launcher.y, self.launcher.angle, power, ball_type="normal", style=selected_ball_style))
                pyxel.play(0, 3)
                self.fever_shot_timer = 5
        elif pyxel.btnp(pyxel.KEY_SPACE) and self.balls_left > 0:
            radius = 6 if self.big_ball_timer > 0 else 3
            self.balls.append(Ball(self.launcher.x, self.launcher.y, self.launcher.angle, self.launcher.power, self.current_ball_type, radius, selected_ball_style))
            if not self.fever_mode: self.balls_left -= 1
            pyxel.play(0, 3)
            if self.multi_ball_timer > 0:
                for i in range(2):
                    angle = self.launcher.angle + random.uniform(-10, 10)
                    self.balls.append(Ball(self.launcher.x, self.launcher.y, angle, self.launcher.power, self.current_ball_type, radius, selected_ball_style))

        if self.laser_beam_timer > 0 and pyxel.btnp(pyxel.KEY_F):
            self.lasers.append(Laser(self.launcher.x, self.launcher.y, self.launcher.angle))
            pyxel.play(0, 6)

        for laser in self.lasers:
            laser.update()
            for block in self.blocks:
                if block.is_active and self.check_laser_collision(laser, block):
                    if block.take_damage(1):
                        self.score += 100
                        self.explosions.append(Explosion(block.x + block.width / 2, block.y + block.height / 2, block.explosion_color))
                        pyxel.play(0, block.destruction_sound_id)
                        self.trigger_shake(1)

        for ball in self.balls:
            ball.update()
            for block in self.blocks:
                if block.is_active and self.check_collision(ball, block):
                    if ball.ball_type == "normal":
                        overlap_x = (ball.radius + block.width / 2) - abs(ball.x - (block.x + block.width / 2))
                        overlap_y = (ball.radius + block.height / 2) - abs(ball.y - (block.y + block.height / 2))
                        if overlap_x < overlap_y:
                            ball.vx *= -1
                            ball.x += math.copysign(overlap_x, -ball.vx)
                        else:
                            ball.vy *= -1
                            ball.y += math.copysign(overlap_y, -ball.vy)
                    elif ball.ball_type == "bomb":
                        ball.is_active = False
                        for other_block in self.blocks:
                            if other_block.is_active and abs(block.x - other_block.x) < 20 and abs(block.y - other_block.y) < 20:
                                if other_block.take_damage(1):
                                    self.score += 100
                                    self.explosions.append(Explosion(other_block.x + other_block.width / 2, other_block.y + other_block.height / 2, other_block.explosion_color))
                                    pyxel.play(0, 1)
                                    self.trigger_shake(4)
                                    if random.random() < 0.1: self.items.append(Item(other_block.x, other_block.y, random.choice(["multi_ball", "big_ball", "laser_beam"])))
                    elif ball.ball_type == "pierce":
                        ball.pierce_count += 1
                        if ball.pierce_count >= 3: ball.is_active = False
                    pyxel.play(0, 0)
                    if block.take_damage(1):
                        self.score += 100
                        self.explosions.append(Explosion(block.x + block.width / 2, block.y + block.height / 2, block.explosion_color))
                        pyxel.play(0, block.destruction_sound_id)
                        self.trigger_shake(2)
                        self.combo_count += 1
                        self.combo_timer = 30
                        if self.combo_count >= 10 and not self.fever_mode:
                            self.fever_mode = True
                            self.fever_timer = 600
                            pyxel.stop()
                            pyxel.playm(3, loop=True)
                            pyxel.play(0, 7)
                        if self.combo_count > 1: pyxel.play(0, 5)
                        if random.random() < 0.1: self.items.append(Item(block.x, block.y, random.choice(["multi_ball", "big_ball", "laser_beam"])))

        for item in self.items:
            item.update()
            if item.is_active and self.check_item_collision(item):
                item.is_active = False
                pyxel.play(0, 4)
                if item.item_type == "multi_ball": self.multi_ball_timer = 300
                elif item.item_type == "big_ball":
                    self.big_ball_timer = 300
                    for ball in self.balls: ball.radius = 6
                elif item.item_type == "laser_beam": self.laser_beam_timer = 120

        self.explosions = [exp for exp in self.explosions if exp.life > 0]
        self.balls = [b for b in self.balls if b.is_active]
        self.blocks = [b for b in self.blocks if b.is_active]
        self.items = [i for i in self.items if i.is_active]
        self.lasers = [l for l in self.lasers if l.is_active]

        if not any(b.is_active for b in self.blocks):
            self.game_state = GameState.GAME_WON
            self.balls = []
            self.balls_left = 0
            pyxel.stop()
            pyxel.playm(1, loop=False)

        if self.balls_left == 0 and not any(b.is_active for b in self.balls) and any(b.is_active for b in self.blocks):
            self.game_state = GameState.GAME_OVER
            pyxel.stop()
            pyxel.playm(2, loop=False)
            if self.score > self.highscore:
                self.highscore = self.score
                self.save_highscore()

    def draw_game(self):
        offset_x, offset_y = (0, 0)
        if self.shake_intensity > 0:
            offset_x = random.uniform(-self.shake_intensity, self.shake_intensity)
            offset_y = random.uniform(-self.shake_intensity, self.shake_intensity)
        
        pyxel.camera(offset_x, offset_y)

        # Draw background based on stage
        stage_bg_color = 12 # Default sky blue
        if self.current_stage == 0: # Grassland
            pyxel.cls(12) # Sky
            pyxel.rect(0, self.ground_y - 20, pyxel.width, 20, 3) # Green grass
            pyxel.rect(0, self.ground_y, pyxel.width, pyxel.height - self.ground_y, 1) # Dirt
            for i in range(0, pyxel.width, 8):
                pyxel.tri(i+4, self.ground_y - 20, i, self.ground_y - 30, i+8, self.ground_y - 30, 3) # Hills
        elif self.current_stage == 1: # Volcano
            pyxel.cls(0) # Dark sky
            pyxel.tri(pyxel.width/2, self.ground_y, pyxel.width/2 - 50, self.ground_y - 50, pyxel.width/2 + 50, self.ground_y - 50, 8) # Volcano mountain
            pyxel.circ(pyxel.width/2, self.ground_y - 50, 5, 10) # Lava
            pyxel.rect(0, self.ground_y, pyxel.width, pyxel.height - self.ground_y, 1) # Ground
        elif self.current_stage == 2: # Ocean
            pyxel.cls(6) # Deep blue ocean
            pyxel.rect(0, self.ground_y - 10, pyxel.width, 10, 12) # Lighter blue surface
            for i in range(0, pyxel.width, 10):
                pyxel.circ(i + random.randint(-2,2), self.ground_y - 5 + random.randint(-2,2), 2, 7) # Bubbles
            pyxel.rect(0, self.ground_y, pyxel.width, pyxel.height - self.ground_y, 1) # Seabed
        elif self.current_stage == 3: # Sky
            pyxel.cls(12) # Bright sky
            for i in range(0, pyxel.width, 15):
                pyxel.circ(i + random.randint(-5,5), 30 + random.randint(-5,5), 10, 7) # Clouds
                pyxel.circ(i + random.randint(-5,5), 50 + random.randint(-5,5), 8, 7) # Clouds
            pyxel.rect(0, self.ground_y, pyxel.width, pyxel.height - self.ground_y, 3) # Ground
        elif self.current_stage == 4: # Space
            pyxel.cls(0) # Black space
            for _ in range(50): # Stars
                pyxel.pset(random.randint(0, pyxel.width), random.randint(0, pyxel.height), 7)
            pyxel.circ(pyxel.width - 20, 20, 10, 10) # Moon/Planet
            pyxel.rect(0, self.ground_y, pyxel.width, pyxel.height - self.ground_y, 1) # Ground
        else: # Default background for stages beyond 4
            pyxel.cls(12)
            pyxel.rect(0, self.ground_y, pyxel.width, pyxel.height - self.ground_y, 3)

        self.launcher.draw()
        for ball in self.balls: ball.draw()
        for block in self.blocks: block.draw()
        for exp in self.explosions: exp.draw()
        for item in self.items: item.draw()
        for laser in self.lasers: laser.draw()
        pyxel.camera(0, 0)

        pyxel.text(5, 5, f"SCORE: {self.score}", 7)
        pyxel.text(5, 15, f"BALLS: {self.balls_left}", 7)
        pyxel.text(5, 25, f"STAGE: {self.current_stage + 1}", 7)
        if self.combo_count > 0: pyxel.text(5, 35, f"COMBO: {self.combo_count}", 8)
        if self.multi_ball_timer > 0: pyxel.text(5, 45, f"MULTI-BALL: {self.multi_ball_timer // 60}", 11)
        if self.big_ball_timer > 0: pyxel.text(5, 55, f"BIG-BALL: {self.big_ball_timer // 60}", 14)
        if self.laser_beam_timer > 0: pyxel.text(5, 65, f"LASER: {self.laser_beam_timer // 60}", 8)
        if self.fever_mode: pyxel.text(pyxel.width / 2 - 20, 5, f"FEVER MODE: {self.fever_timer // 60}", 8)
        if self.fantastic_display_timer > 0: pyxel.text(pyxel.width / 2 - 30, pyxel.height / 2 - 10, "FANTASTIC!!", 10)

        if self.game_state == GameState.GAME_OVER:
            pyxel.text(pyxel.width / 2 - 20, pyxel.height / 2 - 4, "GAME OVER", 8)
            pyxel.text(pyxel.width / 2 - 45, pyxel.height / 2 + 4, "Press ENTER to return to Title", 7)
        elif self.game_state == GameState.GAME_WON:
            pyxel.text(pyxel.width / 2 - 25, pyxel.height / 2 - 4, "STAGE CLEAR!", 14)
            pyxel.text(pyxel.width / 2 - 40, pyxel.height / 2 + 4, "Press ENTER for next stage", 7)

    def check_collision(self, ball, block):
        return (ball.x - ball.radius < block.x + block.width and
                ball.x + ball.radius > block.x and
                ball.y - ball.radius < block.y + block.height and
                ball.y + ball.radius > block.y)

    def check_item_collision(self, item):
        return (item.x > self.launcher.x - 5 and item.x < self.launcher.x + 10 and
                item.y > self.launcher.y and item.y < self.launcher.y + 5)

    def check_laser_collision(self, laser, block):
        end_x = laser.x + math.cos(math.radians(laser.angle)) * laser.length
        end_y = laser.y + math.sin(math.radians(laser.angle)) * laser.length
        return (max(laser.x, end_x) >= block.x and
                min(laser.x, end_x) <= block.x + block.width and
                max(laser.y, end_y) >= block.y and
                min(laser.y, end_y) <= block.y + block.height)

    def generate_random_blocks(self):
        self.blocks = []
        num_blocks = 5 + self.current_stage * 2
        for _ in range(num_blocks):
            block_type = random.choice(["wood", "stone", "glass"])
            x = random.randint(pyxel.width // 2, pyxel.width - 20)
            y_offset = random.randint(10, pyxel.height // 2)
            self.blocks.append(Block(x, self.ground_y - y_offset, 10, 10, block_type=block_type))

    def trigger_shake(self, intensity):
        self.shake_intensity = max(self.shake_intensity, intensity)

App()
