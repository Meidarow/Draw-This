# Draw-This

**Draw-This** is a cross-platform slideshow app for artists and reference collectors.
It can crawl folders full of images, store them in a database, and display them using different rendering backends:

- **Tkinter GUI**: simple interface for folder management and session control.
- **FEH backend**: lightweight slideshow using the `feh` image viewer.
- **OpenGL backend**: custom renderer using `moderngl_window` for smooth, GPU-accelerated slideshows.

The project is written in **Python 3.11+** with an **MVVM-style separation** (Model–ViewModel–View/GUI) to keep code clean and extensible.

---

## Features

- 📂 **Incremental folder crawling** — scan directories and subdirectories for images, store results in an SQLite database.
- 🔀 **Randomized playback** — images are assigned a random order on load.
- 🖼 **Multiple backends** — choose FEH (system-level) or OpenGL (GPU-accelerated).
- ⚡ **Rolling buffer (planned)** — keep a window of decoded textures for smooth navigation.
- 🗄 **Caching optimizations (planned)** — thumbnails for huge TIFF/JP2 files, lazy full decode.
- 🔔 **Signals & events** — GUI and backend communicate via a central signal queue.
- 🧪 **Tests included** — crawler and rendering tests with `pytest`.

---

<img width="1000" height="632" alt="image" src="https://github.com/user-attachments/assets/80ddc73a-92ec-4418-b4fe-8ebcc833bc04" />

---

## Project Layout

```
src/drawthis/
├── app/
│   ├── __init__.py
│   └── signals.py          # Signal definitions (session_started, session_ended)
│
├── gui/
│   ├── tkinter_gui.py       # Tkinter-based GUI frontend
│   ├── model.py             # Application state (folders, timers, sessions)
│   └── viewmodel.py         # Orchestration between GUI, model, and backends
│
├── logic/
│   └── file_listing.py      # Crawler + Loader for SQLite-backed image paths
│
├── render/
│   ├── feh_backend.py       # FEH slideshow backend
│   └── opengl_backend.py    # OpenGL slideshow backend (moderngl_window)
│
├── utils/
│   ├── config.py            # Settings manager (JSON persistence in ~/.config)
│   ├── logger.py            # Simple logger (to be replaced with stdlib logging)
│   ├── shader_parser.py     # Helper to load GLSL shaders
│   └── subprocess_queue.py  # Multiprocessing signal queue
│
├── tests/
│   ├── test_file_listing.py
│   └── test_render_textures.py
│
├── __init__.py              # Package entry (re-exports common classes)
└── main.py                  # App entry point
```

---

## Installation

### Requirements

- Python 3.11+
- Pip packages (see `requirements.txt`):
  - `moderngl_window`
  - `numpy`
  - `pillow`
  - `pytest` (for testing)

On Linux, **[FEH](https://feh.finalrewind.org/)** must be installed if you want the FEH backend:

```bash
sudo apt install feh
```

### Setup

Clone the repository:

```bash
git clone https://github.com/yourusername/Draw-This.git
cd Draw-This
```

Create a virtual environment and install dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Usage

### Run with Tkinter GUI

```bash
python -m drawthis.main
```

From the GUI you can:
- Add or remove folders,
- Choose a backend (FEH or OpenGL),
- Start or stop a slideshow,
- Configure timers.

### Run directly with FEH backend

```bash
python -m drawthis.render.feh_backend --folders ~/Pictures/refs --geometry 1920x1080
```

### Run directly with OpenGL backend

```bash
python -m drawthis.render.opengl_backend --folders ~/Pictures/refs
```

---

## Development Guide

### Architecture Overview

- **Model (`gui/model.py`)**
  Holds app state: selected folders, timers, last session.

- **ViewModel (`gui/viewmodel.py`)**
  Central coordinator: connects GUI events to backend actions.
  Starts crawlers, manages the signal queue, handles logging.

- **View (`gui/tkinter_gui.py`)**
  Tkinter-based frontend. All user interactions pass through ViewModel.

- **Logic (`logic/file_listing.py`)**
  `Crawler` walks directories and populates SQLite.
  `Loader` reads from SQLite (currently bulk, future: block streaming).

- **Renderers (`render/*.py`)**
  - `feh_backend`: external viewer.
  - `opengl_backend`: GPU textures + event loop.

- **Utils (`utils/*.py`)**
  Helpers: persistence, logging, shaders, multiprocessing signals.

---

### Coding Conventions

- **Type hints**: required for new functions (`def foo(x: str) -> int:`).
- **Docstrings**: use **Google style**:

  ```python
  def crawl(root_dir: Path) -> None:
      """
      Recursively crawl a directory and insert image paths into the DB.

      Args:
          root_dir (Path): Root directory to scan.

      Raises:
          PermissionError: If a directory cannot be read.
      """
  ```

- **Constants**: put at top of file in ALL_CAPS. Example: `COMMIT_BLOCK_SIZE = 1500`.
- **Logging**: use `utils.logger.Logger` for now, but prefer Python’s `logging` in new code.
- **Events**: new events should be registered in `app/signals.py` and always sent via `SignalQueue`.

---

### Roadmap / TODOs

1. **Texture & Path Prebuffering**
   - Implement rolling buffer with forward/back prefetch.
   - Asynchronous decode workers.

2. **Caching / Decoding Optimizations**
   - Thumbnails for huge TIFF/JP2.
   - Two-level cache (thumbnail vs. full).

3. **Database Enhancements**
   - Add `active` flag for deselected folders.
   - `Loader.block_loader()` for streaming.

4. **Exceptions & Logging**
   - Introduce domain-specific exceptions (`CrawlerError`, `TextureDecodeError`, …).
   - Replace custom logger with `logging`.

5. **Documentation & Testing**
   - Expand unit vs. integration test coverage.
   - Add headless OpenGL tests.
   - Keep README + CONTRIBUTING.md in sync.

---

## Testing

Run all tests with:

```bash
pytest src/drawthis/tests
```

- Unit tests cover crawler and DB insertion.
- Integration tests may use real folders (mark them with `pytest -m integration`).
- Rendering tests may require a GUI context — skip in CI unless a headless GL driver is available.

---

## Contributing

Pull requests are welcome! Please:

1. Use type hints in all new code.
2. Follow Google-style docstrings.
3. Run `pytest` before submitting.
4. Use `black` for formatting and `flake8` for linting.

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for more details.

---

## License

[MIT License](../LICENSE)

---

## Acknowledgements

- [moderngl_window](https://moderngl-window.readthedocs.io/) for the OpenGL framework.
- [FEH](https://feh.finalrewind.org/) for lightweight image viewing.
- Pillow and NumPy for image handling.
