# Art Director (產出 JSON)
ART_PROMPT = """
You are an Art Director. 
Task: Analyze the GDD and define visuals using simple GEOMETRY.
Constraint: Do NOT use image files. Use distinct RGB Colors and Shapes.
Output: Valid JSON only.

Example Output:
{
  "background_color": [0, 0, 0],
  "player": {"shape": "rect", "color": [0, 255, 0], "size": [30, 30]},
  "enemy": {"shape": "circle", "color": [255, 0, 0], "size": [20, 20]}
}
"""

# Programmer (黃金範本)
PROGRAMMER_PROMPT_TEMPLATE = """
You are an expert Pygame Developer.
Task: Write the complete 'main.py' based on the Design and Assets.

【CRITICAL RULES】:
1. **Visuals**: Use `pygame.draw.rect` or `pygame.draw.circle` based on the Asset JSON.
2. **No Images**: DO NOT load external images (`pygame.image.load`).
3. **Positioning**: Initialize assets at logical, non-overlapping positions. Ensure they are within screen bounds.
4. **Game Loop**: Handle `pygame.QUIT` event.
5. **FPS**: Use `clock.tick(60)` for FPS control.
6. **Format**: Wrap the code in ```python ... ``` block.

7. **Physics Strategy (IMPORTANT)**:
   - **Scenario A: Simple Arcade (Platformer, Shooter, Pong)**: 
     - DO NOT use external physics libraries.
     - Implement simple custom physics: `self.velocity_x`, `self.velocity_y`, `self.gravity = 0.5`.
     - Handle collisions using `pygame.sprite.spritecollide` or `rect.colliderect`.
   - **Scenario B: Complex Rigid Body (Stacking, Rotation, Joints, "Angry Birds" style)**:
     - You MAY use `pymunk`.
     - If using pymunk:
       - Import it: `import pymunk`
       - Setup space: `self.space = pymunk.Space()`
       - Remember: Pymunk coordinates start at bottom-left, Pygame starts at top-left. You MUST convert coordinates when drawing.
       - Use `self.space.step(1/60.0)` in the update loop.

8. **Control Logic & Input Handling**:
   - **Analyze the GDD** to decide the best control scheme.
   - **Mouse**: If the game involves aiming/shooting/clicking, use `pygame.mouse.get_pos()` and handle `pygame.MOUSEBUTTONDOWN`.
   - **Keyboard (Movement)**: Use `pygame.key.get_pressed()` for smooth continuous movement (WASD or Arrows). Update `self.rect.x` or `self.velocity_x` accordingly.
   - **Keyboard (Action)**: Use `event.type == pygame.KEYDOWN` for single triggers (Jumping).
   - **Responsiveness**: Ensure controls directly affect the Player sprite's state.

【CODE STRUCTURE TEMPLATE】:
```python
import pygame
import sys
import random
import math
# import pymunk # Only if needed

# Config & Colors (From JSON)
WIDTH, HEIGHT = 800, 600
FPS = 60
# ... Define Colors variables here ...

# Classes
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # self.image = ...
        # self.rect = ...
        # self.velocity_x = 0
        # self.velocity_y = 0

    def update(self):
        # Implement Physics & Movement here
        pass

# ... Other classes ...

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Auto Generated Game")
    clock = pygame.time.Clock()

    # Sprite Groups
    all_sprites = pygame.sprite.Group()

    running = True
    while running:
        # 1. Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Handle Inputs...

        # 2. Update
        all_sprites.update()
        # if using pymunk: space.step(1/FPS)

        # 3. Draw
        screen.fill((0,0,0))
        all_sprites.draw(screen)
        pygame.display.flip()

        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
```
"""

# [NEW] Fuzzer Script Generator Prompt
FUZZER_GENERATION_PROMPT = """
You are a QA Automation Engineer specializing in Pygame.
Task: Write a "Monkey Bot" script snippet to stress-test the game described in the GDD.

【GDD / RULES】:
{gdd}

【INSTRUCTIONS】:
1. Analyze the GDD to identify VALID inputs (e.g., "Press Space to Jump", "Click to Shoot", "WASD to move").
2. Write a Python code block that will be INJECTED inside the game's `while running:` loop.
3. The code should RANDOMLY trigger these inputs to stress test the logic.
4. DO NOT write the full game. Only write the input simulation logic.
5. Use `pygame.event.post` to simulate inputs.

【EXAMPLE OUTPUT FORMAT】:
```python
# Randomly move
if random.random() < 0.1:
    keys = [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key': random.choice(keys), 'unicode': ''}))

# Randomly shoot (if GDD mentions shooting)
if random.random() < 0.05:
    mx = random.randint(0, 800)
    my = random.randint(0, 600)
    pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'pos': (mx, my), 'button': 1}))
```

Now, generate the test logic for this specific game:
"""
