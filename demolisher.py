import pyxel
import math
import random

class Launcher:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = -45  # Initial angle in degrees (-90 to 0)
        self.power = 5    # Initial power (1 to 10)

    def update(self):
        # Adjust angle
        if pyxel.btn(pyxel.KEY_LEFT):
            self.angle -= 1
        if pyxel.btn(pyxel.KEY_RIGHT):
            self.angle += 1
        self.angle = max(-90, min(0, self.angle)) # Limit angle

        # Adjust power
        if pyxel.btn(pyxel.KEY_UP):
            self.power += 0.1
        if pyxel.btn(pyxel.KEY_DOWN):
            self.power -= 0.1
        self.power = max(1, min(10, self.power)) # Limit power

    def draw(self):
        # Draw launcher base
        pyxel.rect(self.x - 5, self.y, 10, 5, 13) # Darker base

        # Draw aiming line
        end_x = self.x + math.cos(math.radians(self.angle)) * (self.power * 3)
        end_y = self.y + math.sin(math.radians(self.angle)) * (self.power * 3)
        pyxel.line(self.x, self.y, end_x, end_y, 7) # White aiming line

        # Draw power indicator
        pyxel.text(self.x - 10, self.y - 10, f"P:{int(self.power)}", 7)

class Ball:
    def __init__(self, x, y, angle, power, ball_type="normal"):
        self.x = x
        self.y = y
        self.vx = math.cos(math.radians(angle)) * power
        self.vy = math.sin(math.radians(angle)) * power
        self.radius = 3
        self.is_active = True
        self.ball_type = ball_type
        self.pierce_count = 0 # For pierce ball

    def update(self):
        if not self.is_active:
            return
        
        # Apply gravity
        self.vy += 0.15 # Gravity strength
        
        self.x += self.vx
        self.y += self.vy

        # Deactivate if off-screen or below ground
        if self.x < -self.radius or self.x > pyxel.width + self.radius or self.y > pyxel.height + self.radius:
            self.is_active = False

    def draw(self):
        if self.is_active:
            color = 10 # Default orange
            if self.ball_type == "bomb":
                color = 8 # Red
            elif self.ball_type == "pierce":
                color = 6 # Pink
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
            self.color = 3 # Brown
            self.explosion_color = 5 # Darker brown for particles
            self.destruction_sound_id = 1
        elif block_type == "stone":
            self.hp = 1
            self.color = 1 # Dark gray
            self.explosion_color = 0 # Black for particles
            self.destruction_sound_id = 2
        elif block_type == "glass":
            self.hp = 1
            self.color = 12 # Light blue (transparent look)
            self.explosion_color = 7 # White for particles
            self.destruction_sound_id = 1
        else:
            self.hp = 1
            self.color = 3
            self.explosion_color = 5
            self.destruction_sound_id = 1
        self.max_hp = self.hp # Store max HP for explosion color

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.is_active = False
            return True # Block was destroyed
        return False # Block was not destroyed

    def draw(self):
        if self.is_active:
            pyxel.rect(self.x, self.y, self.width, self.height, self.color)
            pyxel.rectb(self.x, self.y, self.width, self.height, 0) # Black border

class Explosion:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.life = 20  # frames
        self.particles = []
        for _ in range(8): # Create some particles
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
            p['vy'] += 0.05 # Gravity for particles

    def draw(self):
        if self.life > 0:
            for p in self.particles:
                pyxel.pset(p['x'], p['y'], p['color'])

class App:
    def __init__(self):
        pyxel.init(200, 150, title="Pyxel Demolisher")
        
        # Define sounds
        # Sound 0: Ball impact (sharp, short)
        pyxel.sounds[0].set(
            'c2', 't', '7', 's', 3
        )
        # Sound 1: Wood destruction (dull, short)
        pyxel.sounds[1].set(
            'c1', 'n', '777', 's', 8
        )
        # Sound 2: Stone destruction (heavy, resonant)
        pyxel.sounds[2].set(
            'c2', 't', '7', 's', 10
        )
        # Sound 3: Ball launch (quick, rising tone)
        pyxel.sounds[3].set(
            'c1e1g1', 't', '7', 's', 5
        )

        self.current_stage = 0
        self.reset_game()
        pyxel.run(self.update, self.draw)

    def reset_game(self):
        self.launcher = Launcher(20, pyxel.height - 10) # Launcher at bottom left
        self.balls = []
        self.blocks = []
        self.explosions = [] # New: to manage explosions
        self.score = 0
        self.game_over = False
        self.balls_left = 5 # Number of balls player has
        self.current_ball_type = "normal" # Default ball type
        self.shake_duration = 0 # New: for screen shake
        self.shake_intensity = 0
        self.game_won = False # New: for stage clear
        self.combo_count = 0
        self.combo_timer = 0

        # Define ground
        self.ground_y = pyxel.height - 5

        self.generate_random_blocks()

        # Set ball type for current stage
        if self.current_stage % 3 == 0:
            self.current_ball_type = "normal"
        elif self.current_stage % 3 == 1:
            self.current_ball_type = "bomb"
        elif self.current_stage % 3 == 2:
            self.current_ball_type = "pierce"

    def generate_random_blocks(self):
        self.blocks = []
        num_blocks = 5 + self.current_stage * 2 # More blocks as stages progress
        for _ in range(num_blocks):
            block_type = random.choice(["wood", "stone", "glass"])
            x = random.randint(pyxel.width // 2, pyxel.width - 20)
            y_offset = random.randint(10, pyxel.height // 2) # Random height
            self.blocks.append(Block(x, self.ground_y - y_offset, 10, 10, block_type=block_type))

    def update(self):
        if self.game_over:
            if pyxel.btnp(pyxel.KEY_RETURN):
                self.reset_game()
            return

        if self.game_won:
            if pyxel.btnp(pyxel.KEY_RETURN):
                self.current_stage += 1
                self.reset_game() # Load next stage
            return

        # Update combo timer
        if self.combo_timer > 0:
            self.combo_timer -= 1
        else:
            if self.combo_count > 0: # Combo ended
                # Add combo bonus to score
                self.score += self.combo_count * 50 # Example bonus: 50 points per combo count
                self.combo_count = 0

        self.launcher.update()

        # Launch ball
        if pyxel.btnp(pyxel.KEY_SPACE) and self.balls_left > 0:
            self.balls.append(Ball(self.launcher.x, self.launcher.y, self.launcher.angle, self.launcher.power, ball_type=self.current_ball_type))
            self.balls_left -= 1
            pyxel.play(3, 0) # Play launch sound

        # Update balls
        for ball in self.balls:
            ball.update()

            # Ball-Block collision
            for block in self.blocks:
                if block.is_active and self.check_collision(ball, block):
                    if ball.ball_type == "normal":
                        ball.is_active = False # Normal ball disappears on impact
                    elif ball.ball_type == "bomb":
                        ball.is_active = False # Bomb ball disappears on impact
                        # Destroy surrounding blocks
                        for other_block in self.blocks:
                            if other_block.is_active and abs(block.x - other_block.x) < 20 and abs(block.y - other_block.y) < 20:
                                if other_block.take_damage(1): # If block was destroyed
                                    self.score += 100 # Score for destroying
                                    self.explosions.append(Explosion(other_block.x + other_block.width / 2, other_block.y + other_block.height / 2, other_block.explosion_color)) # Create explosion
                                    pyxel.play(1, 0) # Play destruction sound
                                    self.shake_duration = 10 # Start screen shake
                                    self.shake_intensity = 2
                    elif ball.ball_type == "pierce":
                        ball.pierce_count += 1
                        if ball.pierce_count >= 3: # Pierce 3 blocks then disappear
                            ball.is_active = False

                    pyxel.play(0, 0) # Play impact sound
                    if block.take_damage(1): # If block was destroyed
                        self.score += 100 # Score for destroying
                        self.explosions.append(Explosion(block.x + block.width / 2, block.y + block.height / 2, block.explosion_color)) # Create explosion
                        pyxel.play(block.destruction_sound_id, 0) # Play destruction sound
                        self.shake_duration = 10 # Start screen shake
                        self.shake_intensity = 2
                        
                        # Combo logic
                        self.combo_count += 1
                        self.combo_timer = 30 # Reset combo timer (30 frames = 0.5 seconds)

        # Update explosions
        for exp in self.explosions:
            exp.update()
        self.explosions = [exp for exp in self.explosions if exp.life > 0]

        # Handle screen shake
        if self.shake_duration > 0:
            self.shake_duration -= 1

        # Remove inactive balls and blocks
        self.balls = [b for b in self.balls if b.is_active]
        self.blocks = [b for b in self.blocks if b.is_active]

        # Game over / Stage clear condition
        # Check for stage clear (all blocks destroyed)
        if not any(b.is_active for b in self.blocks) and not self.game_won: # Ensure it's not already won
            self.game_won = True
            # Optionally, clear any active balls immediately to prevent further interaction
            self.balls = []
            self.balls_left = 0 # No more balls needed for this stage

        # Game over condition (only if not already won and no balls left and blocks still active)
        if not self.game_won and self.balls_left == 0 and not any(b.is_active for b in self.balls) and any(b.is_active for b in self.blocks):
            self.game_over = True

    def check_collision(self, ball, block):
        # Simple AABB collision for now
        return (ball.x - ball.radius < block.x + block.width and
                ball.x + ball.radius > block.x and
                ball.y - ball.radius < block.y + block.height and
                ball.y + ball.radius > block.y)

    def draw(self):
        pyxel.cls(12) # Light blue sky background

        # Apply screen shake offset
        offset_x, offset_y = 0, 0
        if self.shake_duration > 0:
            offset_x = random.randint(-self.shake_intensity, self.shake_intensity)
            offset_y = random.randint(-self.shake_intensity, self.shake_intensity)

        pyxel.camera(offset_x, offset_y) # Apply camera offset for shake

        # Draw ground
        pyxel.rect(0, self.ground_y, pyxel.width, pyxel.height - self.ground_y, 3) # Brown ground

        self.launcher.draw()

        for ball in self.balls:
            ball.draw()
        for block in self.blocks:
            block.draw()

        # Draw explosions
        for exp in self.explosions:
            exp.draw()

        # Reset camera for UI elements
        pyxel.camera(0, 0)

        # Draw UI
        pyxel.text(5, 5, f"SCORE: {self.score}", 7)
        pyxel.text(5, 15, f"BALLS: {self.balls_left}", 7)
        pyxel.text(5, 25, f"STAGE: {self.current_stage + 1}", 7)
        if self.combo_count > 0:
            pyxel.text(5, 35, f"COMBO: {self.combo_count}", 8)

        if self.game_over:
            pyxel.text(pyxel.width / 2 - 20, pyxel.height / 2 - 4, "GAME OVER", 8)
            pyxel.text(pyxel.width / 2 - 35, pyxel.height / 2 + 4, "Press ENTER to restart", 7)
        elif self.game_won:
            pyxel.text(pyxel.width / 2 - 25, pyxel.height / 2 - 4, "STAGE CLEAR!", 14)
            pyxel.text(pyxel.width / 2 - 35, pyxel.height / 2 + 4, "Press ENTER for next stage", 7)

App()