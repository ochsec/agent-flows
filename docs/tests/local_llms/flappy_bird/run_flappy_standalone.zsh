#!/bin/zsh

# Execute Flappy Bird task with the new standalone LM Studio executor
cd /Users/<username>/agent-flows

python -m workflows.jira_task.task_executor_lmstudio_standalone \
  "Create a complete Flappy Bird game using pygame. Create these files in docs/tests/local_llms/flappy_bird/<model>/:

1. main.py - Complete main game loop with pygame initialization, 800x600 window
2. bird.py - Bird class with gravity physics (0.5 px/frame²) and jump mechanics (-8 velocity)
3. pipe.py - Pipe class with collision detection and movement (150px gaps)
4. game.py - Game state management (menu, playing, game over states)
5. requirements.txt - pygame dependency
6. README.md - Installation and play instructions

Implement a fully playable Flappy Bird game with:
- Yellow circular bird (30x30 pixels)
- Green rectangular pipes with 150px gaps
- Spacebar controls for jumping
- Gravity simulation (0.5 pixels/frame²)
- Collision detection using pygame.Rect
- Scoring system (+1 per pipe passed)
- 60 FPS game loop
- Game states with proper transitions

Make it immediately playable by running 'python main.py' from the <model> directory." \
  --model "<model>" \
  --base-url "<url>/v1"