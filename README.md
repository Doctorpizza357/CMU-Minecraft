# CMU Minecraft

A 3D voxel-based Minecraft clone built entirely in CMU Graphics (Carnegie Mellon's `cmu_graphics` library). Features a custom software-rendered 3D engine with perspective projection, face culling, and real-time block interaction.

## Features

- **3D Rendering Engine** — Custom perspective projection with yaw/pitch camera, back-face culling, face exposure culling, block face caching, and painter's algorithm depth sorting
- **Block Interaction** — Place and break blocks (stone, dirt, grass) using raycasting
- **Physics** — Gravity, jumping, collision detection, and fall damage in Survival mode
- **Fly Mode** — Toggle creative-style free flight with `F`
- **Inventory System** — 24-slot inventory grid with drag-and-drop item management
- **Hotbar** — 8-slot quick-access bar with item counts and selection highlighting
- **Health & Hunger** — Visual status bars with fall damage
- **Settings Menu** — In-game toggles and sliders for FOV, render distance, sensitivity, wireframe mode, and more
- **Chat System** — In-game chat with `/tp` teleport command support
- **Start & Pause Menus** — Full game state management with UI overlays

## Controls

| Key / Input | Action |
|---|---|
| W / A / S / D | Move forward / left / backward / right |
| Mouse Drag | Look around |
| Right Click | Place block or break block (with pickaxe) |
| 1–8 | Select hotbar slot |
| E | Open / close inventory |
| F | Toggle fly mode |
| Space | Jump (survival) / Fly up (creative) |
| Q | Fly down (creative mode) |
| T | Open chat |
| L | Toggle debug info (FPS, coordinates) |
| Escape | Pause menu |

## Requirements

- Python 3
- [CMU Graphics](https://academy.cs.cmu.edu/desktop) (`cmu_graphics` package)

## Running

```bash
python cmu_minecraft.py
```

Or open the file in the CMU Graphics desktop environment.

## How It Works

The renderer projects 3D block faces onto a 2D canvas each frame using:

1. Camera-space transformation (translation + yaw/pitch rotation)
2. Perspective division to get screen coordinates
3. Face culling (back-face + neighbor occlusion) to reduce draw calls
4. Painter's algorithm for correct depth ordering
5. Block face caching to avoid redundant projection when the camera is stationary

All rendering is done with CMU Graphics primitives (`Polygon`, `Line`, `Rect`, etc.) — no external 3D libraries.

## Project Structure

```
CMU Minecraft/
├── cmu_minecraft.py   # Entire game (rendering, physics, UI, input)
└── README.md
```

## Acknowledgments

- Built on [CMU Graphics](https://academy.cs.cmu.edu/desktop) by Carnegie Mellon University
- Start screen image generated with ChatGPT image generator
