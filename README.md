# PixelBound

> A 2D platformer built with Pygame, featuring a custom level editor, data-driven asset pipeline, scene-based architecture, and checkpoint-based gameplay.

PixelBound is a platformer project that is evolving beyond a simple game into a small, engine-like framework. The project focuses on building the game, editor, and supporting systems together so that levels can be created, saved, loaded, and played through a consistent pipeline.

The project is being developed as a learning-focused exploration of **game development, software architecture, asset management, serialization, and tool development**.

---

## Features

### Gameplay

* 2D platformer movement and jumping
* Terrain-based level layouts
* Fire hazards
* Falling/death detection
* Checkpoint-based respawning
* Start and End objects
* Pause, resume, and restart flow
* Level selection
* Background rendering through tiled textures

### Level Editor

* Grid-based level editing
* Asset palette
* Dynamic asset categories
* Category dropdown
* Terrain spritesheet extraction
* Asset placement and positioning
* Camera movement
* JSON-based level saving and loading
* Separate editor level-selection flow

### Application Architecture

* Scene-based application structure
* Centralized scene management
* Separate gameplay and editor scenes
* Reusable UI components
* Settings scene
* Settings manager
* Audio manager
* Volume sliders
* Background system
* Runtime level loading through a Level Manager

---

## Screenshots

> Add screenshots or GIFs here as the project develops.

```text
screenshots/
├── main-menu.png
├── level-select.png
├── editor.png
├── gameplay.png
└── settings.png
```

Example:

```md
![Level Editor](screenshots/editor.png)
```

---

## Tech Stack

| Technology | Purpose                                                         |
| ---------- | --------------------------------------------------------------- |
| Python     | Primary programming language                                    |
| Pygame     | Game framework, rendering, input, audio, and collision handling |
| JSON       | Level serialization                                             |
| Git        | Version control                                                 |
| GitHub     | Source-code hosting and project tracking                        |

---

## Project Architecture

PixelBound is organized around two major flows:

```text
                    PIXELBOUND
                        │
              ┌─────────┴─────────┐
              │                   │
         APPLICATION          GAME DATA
              │                   │
         SceneManager        JSON Levels
              │                   │
      ┌───────┼────────┐          │
      │       │        │          │
     Menu   Editor   GameScene    │
      │       │        │          │
      │       ▼        │          │
      │   EditorScene  │          │
      │       │        │          │
      │   Asset Library│          │
      │       │        │          │
      │       ▼        │          │
      │      JSON ◄────┘          │
      │       │                   │
      └───────┴───────┬───────────┘
                      ▼
                 LevelManager
                      │
                      ▼
               Runtime Objects
                      │
              ┌───────┼────────┐
              │       │        │
            Player   Block    Fire
              │       │        │
         Checkpoint  Start    End
```

The project separates:

* **Assets** — source images and asset metadata
* **Editor data** — positions, asset IDs, and level configuration
* **Runtime objects** — actual gameplay entities
* **Systems** — services that manage broader functionality
* **Scenes** — application states
* **UI components** — reusable interface elements

---

## Asset Pipeline

The asset pipeline is designed to ensure that the editor and game use the same asset definitions.

```text
Raw Assets
    ↓
Asset Library
    ↓
Asset Objects
    ↓
Editor Palette
    ↓
Asset ID + Position + Metadata
    ↓
JSON Level File
    ↓
LevelManager
    ↓
Runtime Objects
    ↓
GameScene
```

Each asset can contain information such as:

* Asset ID
* Display name
* Image
* Category
* Runtime object class
* Dimensions
* Editor metadata

For example:

```text
terrain_05 → Block
fire       → Fire
checkpoint → Checkpoint
start      → Start
end        → End
```

This allows the editor to place assets without needing to implement gameplay behavior itself.

---

## Terrain Consistency

Terrain assets are extracted from a spritesheet and then scaled for use in the editor and game.

The source terrain spritesheet uses smaller artwork tiles, while the editor uses a larger world/grid tile size.

```text
Source tile: 16 × 16
       ↓
Extract tile
       ↓
Scale to world/editor size
       ↓
Asset Library
       ↓
Editor + Runtime
```

The editor and runtime now use the same asset image rather than independently generating terrain visuals.

This prevents the editor from displaying one terrain appearance while the game renders another.

---

## Dynamic Asset Categories

Asset categories are discovered from the Asset Library rather than being permanently hardcoded into the editor.

```text
Asset Library
      ↓
Available Categories
      ↓
Category Dropdown
      ↓
Palette
      ↓
Assets in Selected Category
```

This allows new categories to be introduced without rewriting the entire palette system.

Potential categories include:

```text
Tiles
Characters
Traps
Items
Checkpoints
Backgrounds
```

The exact categories depend on the assets currently registered in the project.

---

## Level Selection

PixelBound includes separate level-selection flows for playing and editing.

```text
Main Menu
   │
   ├── Play
   │     ↓
   │  Level Select
   │     ↓
   │  GameScene
   │
   └── Editor
         ↓
      Editor Level Select
         ↓
      EditorScene
```

The level-selection system supports pagination so that larger numbers of levels can be displayed across multiple pages.

Conceptually:

```text
Page 1 → Levels 1–10
Page 2 → Levels 11–20
Page 3 → Levels 21–30
```

Level files are numerically sorted to avoid alphabetical ordering problems such as:

```text
level1
level10
level2
```

---

## Level Data

Levels are stored as JSON files.

A simplified level structure looks like this:

```json
{
  "version": 1,
  "level_name": "Level 1",
  "background": "green",
  "objects": [
    {
      "type": "block",
      "asset": "terrain_05",
      "x": 10,
      "y": 8
    },
    {
      "type": "fire",
      "asset": "fire",
      "x": 15,
      "y": 9
    }
  ]
}
```

The actual schema may evolve as more object types and metadata are added.

The `version` field is intended to support future changes to the level format.

---

## LevelManager

The LevelManager connects serialized level data to runtime gameplay.

```text
level.json
    ↓
LevelManager
    ↓
Read level data
    ↓
Find asset
    ↓
Determine runtime object
    ↓
Instantiate object
    ↓
Add to GameScene
```

For example:

```text
asset = "terrain_05"
        ↓
Asset Library
        ↓
Block
        ↓
Runtime terrain object
```

This keeps level loading separate from the editor and allows the same level data to be used by the game.

---

## Gameplay Systems

### Checkpoint System

The checkpoint system uses a dedicated CheckpointManager to track the player's starting position and active checkpoint.

```text
Player touches checkpoint
          ↓
CheckpointManager
          ↓
Update active checkpoint
```

When the player dies:

```text
Player death
     ↓
CheckpointManager
     ↓
Get respawn position
     ↓
Player.respawn()
```

This allows multiple death causes to share the same respawn behavior.

### Fire and Fall Respawn

Fire hazards and falling outside the playable area are treated as death conditions.

```text
Fire collision ──────┐
                     │
Fall detection ──────┤
                     ▼
                 Respawn
                     ↓
             Active checkpoint
```

The player is reset to the appropriate position and gameplay state.

### Start Object

The Start object defines where the player initially spawns in a level.

```text
Start object
     ↓
Initial spawn position
     ↓
CheckpointManager
     ↓
Player
```

### End Object

The End object marks the completion point of a level.

The intended flow is:

```text
Player reaches End
        ↓
Level completed
        ↓
Completion flow
        ↓
Next Level / Level Select
```

The complete polished level-completion flow is still under development.

---

## Background System

PixelBound uses tiled backgrounds rather than stretching a single image across the entire screen.

```text
Background texture
       ↓
Repeated across viewport
       ↓
TiledBackground
       ↓
Rendered scene
```

This preserves the intended appearance of the source artwork.

Background selection is also being separated from ordinary placeable objects so that it can be stored as level metadata.

Example:

```json
{
  "background": "green"
}
```

---

## Scene Architecture

Scenes represent different states of the application.

Each scene follows a common lifecycle:

```python
handle_events(events)
update()
draw(screen)
```

Current scene responsibilities include:

| Scene                    | Responsibility                     |
| ------------------------ | ---------------------------------- |
| `MenuScene`              | Main menu and navigation           |
| `LevelSelectScene`       | Select a level to play             |
| `EditorLevelSelectScene` | Select a level to edit             |
| `EditorScene`            | Create and modify levels           |
| `GameScene`              | Run gameplay                       |
| `PauseScene`             | Pause gameplay and provide actions |
| `SettingsScene`          | Modify application settings        |

The SceneManager controls which scene is currently active.

---

## Pause, Resume, and Restart

The pause system distinguishes between resuming an existing game and restarting a level.

### Resume

Returns to the existing GameScene state.

```text
Pause
  ↓
Resume
  ↓
Existing GameScene
```

The current player position and level state are preserved.

### Restart

Creates a fresh gameplay state.

```text
Pause
  ↓
Restart
  ↓
New GameScene
  ↓
Level loaded again
```

This resets the player and level state.

---

## Settings System

Settings are separated into a UI layer and a data-management layer.

```text
SettingsScene
      ↓
SettingsManager
      ↓
Application Settings
```

Current settings include concepts such as:

* Music volume
* Sound effects volume
* Brightness

The SettingsScene is responsible for displaying controls and receiving input.

The SettingsManager is responsible for storing the current configuration.

This separation allows settings to be reused by other scenes and systems.

---

## AudioManager

The AudioManager centralizes audio operations.

```text
SettingsManager
      ↓
AudioManager
      ↓
Pygame Mixer
```

Its responsibilities include:

* Playing music
* Stopping or changing music
* Setting music volume
* Setting sound-effects volume
* Playing sound effects

This prevents individual scenes from directly managing all audio behavior.

---

## UI Components

PixelBound includes reusable UI components such as:

* Buttons
* Sliders
* Dropdowns / OptionBoxes
* Asset palettes

### Button

Responsible for:

* Rendering text or icons
* Detecting mouse interaction
* Triggering an action

### Slider

Responsible for:

* Displaying a value range
* Handling dragging
* Returning a normalized value

Example:

```text
0.0 ─────────────── 1.0
```

The SettingsScene determines what that value represents.

### OptionBox

Responsible for:

* Displaying available options
* Handling selection
* Returning the selected value

The editor uses it to switch asset categories dynamically.

---

## Project Structure

The structure below represents the current architectural direction. File names may differ slightly as the project continues to evolve.

```text
PixelBound/
│
├── assets/
│   ├── Terrain/
│   ├── MainCharacters/
│   ├── Traps/
│   ├── Items/
│   ├── Background/
│   └── Menu/
│
├── levels/
│   ├── level1.json
│   ├── level2.json
│   └── ...
│
├── game/
│   ├── application.py
│   ├── scenemanager.py
│   ├── settings.py
│   │
│   ├── scenes/
│   │   ├── base_scene.py
│   │   ├── menu_scene.py
│   │   ├── level_select_scene.py
│   │   ├── level_editor_select_scene.py
│   │   ├── EditorScene.py
│   │   ├── game_scene.py
│   │   ├── pausescene.py
│   │   └── settingscene.py
│   │
│   ├── objects/
│   │   ├── object.py
│   │   ├── player.py
│   │   ├── block.py
│   │   ├── fire.py
│   │   ├── checkpoint.py
│   │   ├── start.py
│   │   └── end.py
│   │
│   └── systems/
│       ├── level_manager.py
│       ├── checkpoint_manager.py
│       ├── background.py
│       ├── settings_manager.py
│       └── audio_manager.py
│
├── editor/
│   ├── asset_library.py
│   ├── tile_loader.py
│   ├── json_manager.py
│   ├── Grid.py
│   ├── camera.py
│   ├── palette.py
│   └── dropdown.py
│
├── requirements.txt
└── README.md
```

> This is an architectural representation, not a guarantee that every file currently exists under exactly these names.

---

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd PixelBound
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it:

**Windows**

```bash
.venv\Scripts\activate
```

**Linux/macOS**

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

If a requirements file is not yet present:

```bash
pip install pygame
```

### 4. Run the project

Use the current application entry point:

```bash
python <entry-point>.py
```

> Replace `<entry-point>.py` with the file currently used to launch the application.

---

## Controls

The exact controls may change during development.

Typical controls include:

| Action                 | Input                     |
| ---------------------- | ------------------------- |
| Move left              | A / Left Arrow            |
| Move right             | D / Right Arrow           |
| Jump                   | Space                     |
| Pause                  | Escape                    |
| Editor camera movement | Project-specific controls |
| Place asset            | Mouse                     |
| Select asset           | Mouse                     |
| Adjust slider          | Mouse drag                |

---

## Current Development Status

PixelBound is actively under development.

### Completed or Implemented

* [x] Basic Pygame platformer foundation
* [x] Scene-based application structure
* [x] Asset Library
* [x] Terrain spritesheet extraction
* [x] Editor/runtime terrain consistency fix
* [x] Dynamic asset categories
* [x] Category dropdown
* [x] Level-selection pagination
* [x] Tiled background rendering
* [x] Checkpoint system foundation
* [x] Start and End objects
* [x] Fire/fall respawn behavior foundation
* [x] Pause/resume/restart flow
* [x] Settings scene foundation
* [x] SettingsManager foundation
* [x] AudioManager foundation
* [x] Volume sliders
* [x] JSON-based level pipeline

### In Progress

* [ ] Complete and polish level-completion flow
* [ ] Finalize all runtime object constructors
* [ ] Improve level validation
* [ ] Complete settings persistence
* [ ] Improve audio transitions
* [ ] Stabilize all scene transitions
* [ ] Expand editor functionality
* [ ] Improve UI polish
* [ ] Add more playable levels

---

## Known Issues and Technical Debt

### Asset Constructor Consistency

Some runtime objects may still need their constructors standardized so that assets are consistently provided by the Asset Library rather than loaded independently.

### Shared Settings State

The SettingsManager should exist as a shared application-level system rather than being independently instantiated by different scenes.

### Fire Collision Box

Animated fire sprites may require a stable gameplay hitbox independent of the current animation frame.

### Background Metadata

Backgrounds are registered as assets, but their role as level metadata should remain distinct from ordinary placeable gameplay objects.

### Level Validation

The editor still needs stronger validation for:

* Missing Start objects
* Missing End objects
* Duplicate Start objects
* Invalid asset IDs
* Invalid level data
* Unsupported JSON versions

### JSON Versioning

The level format is expected to evolve. Migration support may be required when the schema changes.

### Error Handling

Missing assets, malformed JSON, and invalid level data should eventually produce clearer user-facing errors.

### Scene Dependencies

Local imports have been used to avoid circular imports. A more centralized scene factory or transition mechanism may be introduced later if the project grows.

### Audio and Settings Persistence

Settings and audio behavior still need further integration and testing across all scenes.

---

## Development Roadmap

### Phase 1 — Stabilize Core Systems

* Fix remaining asset inconsistencies
* Standardize runtime constructors
* Make settings and audio state shared
* Test checkpoint and respawn behavior
* Test pause/resume/restart
* Test all scene transitions

### Phase 2 — Finish the Editor Pipeline

* Complete asset placement support
* Improve background selection
* Add level validation
* Improve save/load reliability
* Add object deletion and editing improvements
* Improve camera and grid behavior

### Phase 3 — Complete the Gameplay Loop

* Finish End-object behavior
* Add level-completion screen
* Add next-level navigation
* Add replay functionality
* Connect completion to level selection

### Phase 4 — Polish and Expansion

* Improve UI
* Add sound effects and transitions
* Add particles and visual effects
* Add more levels
* Improve gameplay progression
* Explore controller and mobile support

---

## Why This Project Exists

PixelBound is not only about making a platformer.

It is also an exploration of how game development systems fit together:

```text
Game Loop
Scene Management
Asset Management
Level Editing
Serialization
Runtime Instantiation
Collision Systems
Camera Systems
State Management
Audio Abstraction
UI Components
```

The long-term goal is to understand these systems deeply enough to apply the same principles when building larger projects, including a future custom C++ game engine.

---

## Author

**Bhavya Moolchandani**

Computer Science and Engineering student interested in:

* Game Development
* Game Engine Architecture
* C++
* System Design
* Graphics Programming

---

## License

License information will be added as the project develops.
