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
4. **Game Loop**: Handle `pygame.QUIT` event. Use `clock.tick(60)`.
5. **Format**: Wrap the code in ```python ... ``` block.

6. **Sprite Update Safety (CRITICAL)**:
   - When using `all_sprites.update()`, Pygame passes arguments to ALL sprites.
   - **Requirement**: Define `update(self, *args)` for ALL Sprite classes, even if they don't use arguments.
   - Example: `def update(self, *args): ...` prevents `TypeError` crashes.

7. **Physics Strategy**:
   - **Scenario A: Simple Arcade (Platformer, Shooter)**: 
     - DO NOT use external physics libraries.
     - Implement custom physics: `velocity_x`, `velocity_y`, `gravity`.
     - Collision: `pygame.sprite.spritecollide`.
   - **Scenario B: Complex Rigid Body (Pool, Angry Birds, Stacking)**:
     - You MAY use `pymunk`.
     - Setup: `import pymunk`, `self.space = pymunk.Space()`.
     - **Coordinates**: Pymunk (Bottom-Left) <-> Pygame (Top-Left). You MUST convert y-coordinates when drawing.
     - Update: `self.space.step(1/60.0)`.

8. **Control Logic & Input Handling**:
   - **Analyze the GDD** to decide the best control scheme.
   - **WASD/Arrows**: Use `pygame.key.get_pressed()` for smooth movement.
   - **Mouse Dragging (For Pool/Slingshot Games)**:
     - **Interaction Type**: 
        - **Global Drag (Recommended)**: Player can click anywhere to aim. `MOUSEBUTTONDOWN` sets `aiming=True` regardless of cursor position.
        - **Object Drag**: Player must click the ball. Check `if self.rect.collidepoint(event.pos)`.
     - **State**: Use `self.aiming = False` and `self.start_pos`.
     - **Logic**:
        - `MOUSEBUTTONDOWN`: `self.aiming = True`, `self.start_pos = event.pos`.
        - `MOUSEBUTTONUP`: if `aiming`: calculate vector `(start_pos - end_pos)`, apply force, reset `aiming`.
     - **Visuals**: Draw an aiming line when `aiming` is True.

9. **Robustness**:
   - **Zero Division**: Check `if vec.length() > 0` before normalizing.
   - **Boundaries**: Keep objects inside the screen.

10. **Token Efficiency**: 
   - Write **MINIMAL comments**. Only comment complex logic.
   - Do NOT add docstrings for every function.

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

    def update(self, *args): # MUST accept *args to prevent crash
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
        # Safe update call (passing *args is handled by class definition)
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
1. Analyze the GDD to identify VALID inputs.
2. **Handling Dragging (Important)**: 
   - If the game controls involve "Dragging" (e.g., Pull back to shoot, Slingshot, Pool):
   - You MUST simulate a `MOUSEBUTTONDOWN` at one location, and a `MOUSEBUTTONUP` at a DIFFERENT location.
   - **FORCE GENERATION**: Ensure the drag distance is LARGE enough (100px+) to overcome friction. Small drags might be ignored by game logic.
   - **TARGETING**: Try `start_pos` near the CENTER.
3. Use `pygame.event.post` to simulate inputs.
4. Output ONLY the logic code block.

【EXAMPLE OUTPUT FORMAT】:
```python
# Randomly move (Keyboard)
if random.random() < 0.1:
    keys = [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key': random.choice(keys), 'unicode': ''}))

# Randomly Drag-and-Shoot (Mouse)
# Simulates a STRONG pull back
if random.random() < 0.05:
    # Assume object is near center (or global drag)
    center_x, center_y = globals().get('WIDTH', 800) // 2, globals().get('HEIGHT', 600) // 2
    start_pos = (center_x + random.randint(-20, 20), center_y + random.randint(-20, 20))

    # Drag FAR away to create strong force (at least 100px)
    # Using large offsets to ensure movement
    dx = random.choice([-150, 150]) + random.randint(-50, 50)
    dy = random.choice([-150, 150]) + random.randint(-50, 50)
    end_pos = (start_pos[0] + dx, start_pos[1] + dy)

    # Post DOWN event (Start Drag)
    pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'pos': start_pos, 'button': 1}))

    # Post UP event (Release Drag)
    pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONUP, {'pos': end_pos, 'button': 1}))
```

Now, generate the test logic for this specific game:
"""