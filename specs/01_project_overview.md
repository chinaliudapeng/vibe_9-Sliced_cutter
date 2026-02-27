# Project Overview: 9-Slice Image Optimizer

## 1. Project Goal
Develop a desktop GUI utility for game developers to visually configure 9-slice (9-patch) borders on UI images, remove the redundant center cross, and export a perfectly stitched, memory-optimized image. 

## 2. Target Audience & Standard
- **Primary Users:** Game UI designers, Technical Artists, and Client Programmers.
- **Engine Compatibility:** The output images must be perfectly compatible with standard game engine UI components (e.g., Unity's Image component, SpriteAtlas pipelines).

## 3. Technology Stack
- **Language:** Python 3.10+
- **GUI Framework:** PySide6 (Qt for Python). Chosen for native cross-platform rendering and robust event handling.
- **Image Processing:** Pillow (PIL). Chosen for fast, lightweight pixel manipulation.
- **Packaging:** PyInstaller. 

## 4. Supported Platforms
- Windows (Primary development environment)
- macOS (Must compile via PyInstaller without changing source code)

## 5. Architecture Pattern
- Separate UI logic from Image Processing logic.
- Use Qt's Signal/Slot mechanism for all state synchronization.