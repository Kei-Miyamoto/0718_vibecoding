import pyxel
import math
import random

class Launcher:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = -45
        self.power = 5

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
        pyxel.rect(self.x - 5, self.y, 10, 5, 13)
        end_x = self.x + math.cos(math.radians(self.angle)) * (self.power * 3)
        end_y = self.y + math.sin(math.radians(self.angle)) * (self.power * 3)
        pyxel.line(self.x, self.y, end_x, end_y, 7)
        pyxel.text(self.x - 10, self.y - 10, f"P:{int(self.power)}", 7)

class Ball:
    def __init__(self, x, y, angle, power, ball_type="normal", radius=3):
        self.x = x
        self.y = y
        self.vx = math.cos(math.radians(angle)) * power
        self.vy = math.sin(math.radians(angle)) * power
        self.radius = radius
        self.is_active = True
        self.ball_type = ball_type
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
        if self.is_active:
            color = 10
            if self.ball_type == "bomb":
                color = 8
            elif self.ball_type == "pierce":
                color = 6
            pyxel.circ(self.x, self.y, self.radius, color)

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
            self.color = 3
            self.explosion_color = 5
            self.destruction_sound_id = 1
        elif block_type == "stone":
            self.hp = 1
            self.color = 1
            self.explosion_color = 0
            self.destruction_sound_id = 2
        elif block_type == "glass":
            self.hp = 1
            self.color = 12
            self.explosion_color = 7
            self.destruction_sound_id = 1
        else:
            self.hp = 1
            self.color = 3
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
        if self.is_active:
            pyxel.rect(self.x, self.y, self.width, self.height, self.color)
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
        pyxel.sounds[1].set('c1', 'n', '777', 's', 8)
        pyxel.sounds[2].set('c2', 't', '7', 's', 10)
        pyxel.sounds[3].set('c1e1g1', 't', '7', 's', 5)
        pyxel.sounds[4].set('c3', 'p', '8', 's', 10)
        pyxel.sounds[5].set('c3e3g3', 'p', '6', 's', 8)
        pyxel.sounds[6].set('c4', 's', '8', 'v', 15)
        pyxel.sounds[7].set('c5', 't', '7', 's', 10) # Fever mode start
        pyxel.sounds[8].set("c5g5c6", "t", "7", "s", 10) # Fantastic!

        # Music
        pyxel.musics[0].set([10], [11], loop=True)
        pyxel.sounds[10].set("c2e2g2c3 g2e2c2-", "t", "7", "s", 15)
        pyxel.sounds[11].set("c1g1c2g2", "t", "7", "s", 15)
        pyxel.musics[1].set([12], loop=False)
        pyxel.sounds[12].set("c4e4g4c5", "t", "7", "s", 10)
        pyxel.musics[2].set([13], loop=False)
        pyxel.sounds[13].set("g3e3c3a2", "t", "7", "f", 12)
        pyxel.musics[3].set([14], loop=True)
        pyxel.sounds[14].set("c3g3c4g4 c3g3c4g4", "p", "6", "s", 12)

        self.current_stage = 0
        self.reset_game()
        pyxel.run(self.update, self.draw)

    def reset_game(self):
        pyxel.stop()
        self.launcher = Launcher(20, pyxel.height - 10)
        self.balls = []
        self.blocks = []
        self.explosions = []
        self.items = []
        self.lasers = []
        self.score = 0
        self.game_over = False
        self.balls_left = 5
        self.current_ball_type = "normal"
        self.shake_intensity = 0
        self.game_won = False
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
        if self.current_stage % 3 == 0:
            self.current_ball_type = "normal"
        elif self.current_stage % 3 == 1:
            self.current_ball_type = "bomb"
        elif self.current_stage % 3 == 2:
            self.current_ball_type = "pierce"
        pyxel.playm(0, loop=True)

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

    def update(self):
        if self.game_over:
            if pyxel.btnp(pyxel.KEY_RETURN):
                self.reset_game()
            return

        if self.game_won:
            if pyxel.btnp(pyxel.KEY_RETURN):
                self.current_stage += 1
                self.reset_game()
            return

        if self.shake_intensity > 0:
            self.shake_intensity *= 0.9
            if self.shake_intensity < 0.1:
                self.shake_intensity = 0

        if self.combo_timer > 0:
            self.combo_timer -= 1
        else:
            if self.combo_count > 1:
                self.score += self.combo_count * 50
            self.combo_count = 0

        if self.multi_ball_timer > 0:
            self.multi_ball_timer -= 1
        if self.big_ball_timer > 0:
            self.big_ball_timer -= 1
            if self.big_ball_timer == 0:
                for ball in self.balls:
                    ball.radius = 3
        if self.laser_beam_timer > 0:
            self.laser_beam_timer -= 1

        if self.fever_mode:
            self.fever_timer -= 1
            if self.fever_timer == 0:
                self.fever_mode = False
                pyxel.stop()
                pyxel.playm(0, loop=True)
            if self.fever_shot_timer > 0:
                self.fever_shot_timer -= 1

        self.launcher.update()

        # Check for FANTASTIC!! trigger
        if self.launcher.power == 10 and not self.was_power_max:
            self.fantastic_display_timer = 60 # Display for 1 second
            pyxel.play(8, 0)
        self.was_power_max = (self.launcher.power == 10)

        if self.fantastic_display_timer > 0:
            self.fantastic_display_timer -= 1

        if self.fever_mode:
            if pyxel.btn(pyxel.KEY_SPACE) and self.fever_shot_timer == 0:
                power = self.launcher.power * 1.5
                self.balls.append(Ball(self.launcher.x, self.launcher.y, self.launcher.angle, power, ball_type="normal"))
                pyxel.play(3, 0)
                self.fever_shot_timer = 5 # 5 frames between shots
        elif pyxel.btnp(pyxel.KEY_SPACE) and self.balls_left > 0:
            radius = 6 if self.big_ball_timer > 0 else 3
            self.balls.append(Ball(self.launcher.x, self.launcher.y, self.launcher.angle, self.launcher.power, ball_type=self.current_ball_type, radius=radius))
            if not self.fever_mode:
                self.balls_left -= 1
            pyxel.play(3, 0)
            if self.multi_ball_timer > 0:
                for i in range(2):
                    angle = self.launcher.angle + random.uniform(-10, 10)
                    self.balls.append(Ball(self.launcher.x, self.launcher.y, angle, self.launcher.power, ball_type=self.current_ball_type, radius=radius))

        if self.laser_beam_timer > 0 and pyxel.btnp(pyxel.KEY_F):
            self.lasers.append(Laser(self.launcher.x, self.launcher.y, self.launcher.angle))
            pyxel.play(6, 0)

        for laser in self.lasers:
            laser.update()
            for block in self.blocks:
                if block.is_active and self.check_laser_collision(laser, block):
                    if block.take_damage(1):
                        self.score += 100
                        self.explosions.append(Explosion(block.x + block.width / 2, block.y + block.height / 2, block.explosion_color))
                        pyxel.play(block.destruction_sound_id, 0)
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
                                    pyxel.play(1, 0)
                                    self.trigger_shake(4)
                                    if random.random() < 0.1:
                                        self.items.append(Item(other_block.x, other_block.y, random.choice(["multi_ball", "big_ball", "laser_beam"])))
                    elif ball.ball_type == "pierce":
                        ball.pierce_count += 1
                        if ball.pierce_count >= 3:
                            ball.is_active = False
                    pyxel.play(0, 0)
                    if block.take_damage(1):
                        self.score += 100
                        self.explosions.append(Explosion(block.x + block.width / 2, block.y + block.height / 2, block.explosion_color))
                        pyxel.play(block.destruction_sound_id, 0)
                        self.trigger_shake(2)
                        self.combo_count += 1
                        self.combo_timer = 30
                        if self.combo_count >= 10 and not self.fever_mode:
                            self.fever_mode = True
                            self.fever_timer = 600 # 10 seconds
                            pyxel.stop()
                            pyxel.playm(3, loop=True)
                            pyxel.play(7, 0)
                        if self.combo_count > 1:
                            pyxel.play(5, 0)
                        if random.random() < 0.1:
                            self.items.append(Item(block.x, block.y, random.choice(["multi_ball", "big_ball", "laser_beam"])))

        for item in self.items:
            item.update()
            if item.is_active and self.check_item_collision(item):
                item.is_active = False
                pyxel.play(4, 0)
                if item.item_type == "multi_ball":
                    self.multi_ball_timer = 300
                elif item.item_type == "big_ball":
                    self.big_ball_timer = 300
                    for ball in self.balls:
                        ball.radius = 6
                elif item.item_type == "laser_beam":
                    self.laser_beam_timer = 120

        for exp in self.explosions:
            exp.update()
        self.explosions = [exp for exp in self.explosions if exp.life > 0]
        self.balls = [b for b in self.balls if b.is_active]
        self.blocks = [b for b in self.blocks if b.is_active]
        self.items = [i for i in self.items if i.is_active]
        self.lasers = [l for l in self.lasers if l.is_active]

        if not any(b.is_active for b in self.blocks) and not self.game_won:
            self.game_won = True
            self.balls = []
            self.balls_left = 0
            pyxel.stop()
            pyxel.playm(1, loop=False)

        if not self.game_won and self.balls_left == 0 and not any(b.is_active for b in self.balls) and any(b.is_active for b in self.blocks):
            self.game_over = True
            pyxel.stop()
            pyxel.playm(2, loop=False)

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

    def draw(self):
        pyxel.cls(12)
        offset_x, offset_y = 0, 0
        if self.shake_intensity > 0:
            offset_x = random.uniform(-self.shake_intensity, self.shake_intensity)
            offset_y = random.uniform(-self.shake_intensity, self.shake_intensity)
        pyxel.camera(offset_x, offset_y)
        pyxel.rect(0, self.ground_y, pyxel.width, pyxel.height - self.ground_y, 3)
        self.launcher.draw()
        for ball in self.balls:
            ball.draw()
        for block in self.blocks:
            block.draw()
        for exp in self.explosions:
            exp.draw()
        for item in self.items:
            item.draw()
        for laser in self.lasers:
            laser.draw()
        pyxel.camera(0, 0)
        pyxel.text(5, 5, f"SCORE: {self.score}", 7)
        pyxel.text(5, 15, f"BALLS: {self.balls_left}", 7)
        pyxel.text(5, 25, f"STAGE: {self.current_stage + 1}", 7)
        if self.combo_count > 0:
            pyxel.text(5, 35, f"COMBO: {self.combo_count}", 8)
        if self.multi_ball_timer > 0:
            pyxel.text(5, 45, f"MULTI-BALL: {self.multi_ball_timer // 60}", 11)
        if self.big_ball_timer > 0:
            pyxel.text(5, 55, f"BIG-BALL: {self.big_ball_timer // 60}", 14)
        if self.laser_beam_timer > 0:
            pyxel.text(5, 65, f"LASER: {self.laser_beam_timer // 60}", 8)
        if self.fever_mode:
            pyxel.text(pyxel.width / 2 - 20, 5, f"FEVER MODE: {self.fever_timer // 60}", 8)
        if self.fantastic_display_timer > 0:
            pyxel.text(pyxel.width / 2 - 30, pyxel.height / 2 - 10, "FANTASTIC!!", 10)

        if self.game_over:
            pyxel.text(pyxel.width / 2 - 20, pyxel.height / 2 - 4, "GAME OVER", 8)
            pyxel.text(pyxel.width / 2 - 35, pyxel.height / 2 + 4, "Press ENTER to restart", 7)
        elif self.game_won:
            pyxel.text(pyxel.width / 2 - 25, pyxel.height / 2 - 4, "STAGE CLEAR!", 14)
            pyxel.text(pyxel.width / 2 - 35, pyxel.height / 2 + 4, "Press ENTER for next stage", 7)

App()