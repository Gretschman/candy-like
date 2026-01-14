# Candy Crush Game

A simple Candy Crush-like game built with Python and Pygame featuring smooth animations.

## Features

- 8x8 grid of colorful candies
- Click to select and swap adjacent candies
- Match 3 or more candies horizontally or vertically
- Smooth swapping animation
- Fade-out animation for matched candies
- Gravity and falling animations
- Automatic refilling of candies from the top
- Score tracking
- Invalid swaps automatically revert
- Game over detection when no valid moves remain
- Interactive restart and quit buttons with hover effects

## Installation

1. Make sure you have Python 3.7+ installed

2. Create a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## How to Run

1. Activate the virtual environment (if you created one):
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Run the main game file:
```bash
python candy_crush.py
```

## How to Play

1. Click on a candy to select it (it will be highlighted with a golden border)
2. Click on an adjacent candy (up, down, left, or right) to swap them
3. If the swap creates a match of 3 or more candies of the same color, they will disappear
4. New candies will fall from the top to fill empty spaces
5. Chain reactions will automatically continue until no more matches exist
6. Try to get the highest score possible!

## Controls

- **Mouse Click**: Select and swap candies
- **Game Over Screen**:
  - Click **Restart** button (green) to play again
  - Click **Quit** button (red) to exit
  - Or use keyboard: Press **R** to restart, **ESC** to quit
- **Close Window**: Exit game anytime

## Game Mechanics

- **Valid Swaps**: Only adjacent candies can be swapped
- **Invalid Swaps**: If a swap doesn't create a match, it will automatically reverse
- **Scoring**: Each matched candy gives 10 points
- **Cascade**: When candies fall, new matches are automatically detected and cleared
- **Game Over**: The game ends when there are no more valid moves on the board

## Requirements

- Python 3.7+
- pygame 2.5.2

## Color Scheme

The game features 6 different candy colors:
- Red
- Green
- Blue
- Yellow
- Orange
- Purple

Enjoy playing!
