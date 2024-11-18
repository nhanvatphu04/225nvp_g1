# Chess Game with AI

A chess game implemented in Python using Pygame with AI opponent.

## Author
Developed by [nhanvatphu04](https://github.com/nhanvatphu04).
- **Name**: Đỗ Xuân Trường
- **Student ID**: 22103100225

## Features
- Full chess rules implementation
- AI opponent
- Piece promotion
- Castling
- En passant
- Check/Checkmate detection
- Move highlighting
- Game state saving/loading
- Background animation
- Loading screen with progress bar

## Installation
1. Clone the repository
2. Install dependencies:
pip install -r requirements.txt

## Build Instructions
1. Install PyInstaller:
pip install pyinstaller

2. Build the executable using the spec file:
pyinstaller build.spec

3. The executable will be created in the `dist` folder as `Chess.exe`

Note: The build process will automatically:
- Include all necessary assets (images, sounds, fonts)
- Create a windowed application (no console)
- Set the application icon

## Running the Game
python main.py

## Controls
- Left click: Select and move pieces
- Right click: Delete piece
- R: Restore deleted piece
- Space: Restart game
- ESC: Quit game

## Project Structure
- `assets/`: Game assets (images, sounds)
  - `models/`: Chess piece images
  - `chessboard/`: Chessboard textures
  - `background/`: Background animations
  - `bgmusic/`: Background music
  - `icon/`: Game icon
- `config/`: Configuration files
- `game/`: Game logic
- `src/`: Source code
  - `modules/`: Game components
  - `userinterface/`: UI elements