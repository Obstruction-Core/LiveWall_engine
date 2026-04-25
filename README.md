
# 🎨 LiveWall Engine: The Ultimate Material You Companion

**Transform your Hyprland desktop into a living canvas.** LiveWall Engine isn't just a wallpaper picker; it’s a high-performance bridge between your media and the **Material You** ecosystem. Preview 4K videos, animated GIFs, and high-res stills, then instantly inject their DNA into your system colors.

![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Hyprland](https://img.shields.io/badge/Hyprland-Wayland-purple.svg)
![State](https://img.shields.io/badge/Status-Optimized_for_End--4-orange.svg)

---

## 🚀 Why LiveWall?

Most theme managers make you guess. LiveWall lets you **feel** the vibe before you commit. Built with a C++/Python hybrid mindset, it handles heavy video assets with zero lag, ensuring your workflow stays as fast as your hardware.

### 🎥 Media-First Preview
Don't settle for static thumbnails.
* **Motion Support:** Native `QtMultimedia` integration for `.mp4`, `.mkv`, and `.webm`.
* **GIF Mastery:** Smooth, low-overhead looping via `QMovie`.
* **Smart Scaling:** Perfectly fitted previews that respect your wallpaper's native aspect ratio.

### 🧠 Intelligent Color Extraction
Powered by **Matugen**, choose from 9 distinct algorithms to match your mood:
* **Fruit Salad & Rainbow:** For high-energy, vibrant setups.
* **Monochrome & Neutral:** For the clean, minimal developer aesthetic.
* **Tonal Spot:** The classic, balanced Android-inspired look.

---

## 🖼️ Visual Gallery

### The Control Center
| Interface Overview | Real-time Color Swatches |
| :---: | :---: |
| ![UI Preview](https://via.placeholder.com/400x250?text=LiveWall+Main+GUI) | ![Swatches](https://via.placeholder.com/400x250?text=Matugen+Color+Palette) |
| *Clean, intuitive PyQt6 interface* | *Click any swatch to copy HEX to clipboard* |

### Deep Integration
https://github.com/user-attachments/assets/abf49a8d-01a1-431d-8ab5-c668b82f2edc

---

## 📦 Requirements & Stack

| Component | Role | Arch Linux Command |
| :--- | :--- | :--- |
| **Python 3.10+** | Core Logic | `sudo pacman -S python` |
| **PyQt6** | High-Performance UI | `pip install PyQt6` |
| **Matugen** | Color Engine | `yay -S matugen-bin` |
| **GStreamer** | Video Backend | `sudo pacman -S gst-plugins-good gst-libav` |
| **Mpvpaper** | Live Wallpapers | `sudo pacman -S mpvpaper` |

---

## ⚡ Quick Start

1.  **Clone & Enter**
    ```bash
    git clone [https://github.com/yourusername/LiveWall_engine.git](https://github.com/yourusername/LiveWall_engine.git) && cd LiveWall_engine
    ```

2.  **Ignite**
    ```bash
    python livewall_app.py
    ```

---

## 🛠️ Advanced Functionality

### 🔄 Fail-Safe State Management
Never lose a "perfect" setup again. LiveWall creates a `config.json.theme.bak` before every application. If a scheme looks off, the **One-Click Revert** restores:
* The exact Wallpaper path.
* The previous Light/Dark mode state.
* The specific Matugen scheme used.

### 🔌 Developer Integration
Running **illogical-impulse**? Add this to your `WallpaperSelector.qml` to launch LiveWall directly from your dashboard:

```qml
IconToolbarButton {
    text: "rocket_launch"
    toolTipText: "Open LiveWall Engine"
    onClicked: {
        Quickshell.exec(["python3", "/home/" + String.getenv("USER") + "/path/to/livewall_app.py"])
        GlobalStates.wallpaperSelectorOpen = false;
    }
}

```
## 🤝 Contributing
Have a performance optimization or a new codec to suggest?
 1. Fork the repo.
 2. Create your feature branch (git checkout -b feature/ValkyrieOptimization).
 3. Commit your changes.
 4. Push to the branch and open a Pull Request.
## 📄 License
Distributed under the **MIT License**. Built with ❤️ for the Linux community.
**Special Thanks:**
 * **End-4** for the architectural inspiration.
 * **InioX** for the Matugen magic.
```

```
* [🚀 Installation](#-installation)
* [⚙️ Configuration](#-configuration)
* [🎮 Usage](#-usage)
* [🔌 Integration](#-integration-with-illogical-impulse)
* [🛠️ Troubleshooting](#-troubleshooting)
* [🤝 Contributing](#-contributing)
* [📄 License](#-license)

---

## ✨ Features

### 🎬 Live Preview
* **Native playback** – MP4, MKV, and WebM videos play directly inside the GUI using `QtMultimedia`.
* **Animated GIFs** – Smooth, looped previews powered by `QMovie`.
* **Static images** – Support for JPEG, PNG, and WebP with aspect-ratio-aware scaling.

### 🎨 Material You Theming
* **9 matugen color schemes** – Choose from content, expressive, fidelity, fruit-salad, monochrome, neutral, rainbow, tonal-spot, and vibrant.
* **Dark / Light mode** – Toggle and apply instantly.
* **True color preview** – Real-time swatches show the exact HEX values generated.

### 🔄 Safe Revert & UX
* **Automatic backup** – Saves your `config.json` state before every change.
* **One-click revert** – Instantly restores your previous wallpaper, mode, and scheme.
* **Interactive Swatches** – Click any color swatch to copy its HEX value to your clipboard.

---

## 🖼️ Preview

https://github.com/user-attachments/assets/abf49a8d-01a1-431d-8ab5-c668b82f2edc

---

## 📦 Requirements

| Dependency | Purpose | Installation (Arch) |
| :--- | :--- | :--- |
| **Python 3.10+** | Script runtime | `sudo pacman -S python` |
| **PyQt6** | GUI framework | `pip install PyQt6` |
| **matugen** | Theme generation | [InioX/matugen](https://github.com/InioX/matugen) |
| **ffmpeg** | Video processing | `sudo pacman -S ffmpeg` |
| **mpvpaper** | Video wallpaper backend | `sudo pacman -S mpvpaper` |
| **gst-plugins-good** | Video preview support | `sudo pacman -S gst-plugins-good` |

---

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone [https://github.com/yourusername/LiveWall_engine.git](https://github.com/yourusername/LiveWall_engine.git)
   cd LiveWall_engine

   ```
2. **Install Python dependencies**
   ```bash
   pip install PyQt6
   
   ```
 3. **Run the application**
   ```bash
   python livewall_app.py
   
   ```
## ⚙️ Configuration
The engine automatically manages state within your illogical-impulse directory:
 * **Config Path:** ~/.config/illogical-impulse/config.json
 * **Backup Path:** ~/.config/illogical-impulse/config.json.theme.bak
## 🎮 Usage
 1. **Select a wallpaper** – Browse to an image, GIF, or video file.
 2. **Watch live preview** – Videos and GIFs will loop automatically in the preview window.
 3. **Choose a theme** – Select one of the 9 Material You schemes from the list.
 4. **Apply** – Click **Apply Dark** or **Apply Light** to update your system theme.
 5. **Revert** – If you want to go back, click **Revert to Last State**.
## 🔌 Integration with illogical-impulse
To add a launch button inside your WallpaperSelector.qml, insert this code snippet. **Note:** Replace /path/to/ with the actual directory where you cloned the engine.
```qml
IconToolbarButton {
    text: "rocket_launch"
    onClicked: {
        // Change the path below to your actual script location
        Quickshell.exec(["python3", "/home/USER/path/to/livewall_app.py"])
        GlobalStates.wallpaperSelectorOpen = false;
    }
}

```
## 🛠️ Troubleshooting
 * **MP4 preview not playing:** Ensure gst-plugins-good and gst-libav are installed for QtMultimedia support.
 * **matugen not found:** Ensure matugen is in your $PATH. If you are using illogical-impulse defaults, this should already be set.
 * **Revert failed:** The app looks for config.json.theme.prev.bak. If this file was moved or deleted, the revert function will be disabled.
## 🤝 Contributing
Contributions are welcome! Please open an issue or pull request for:
 * Better error handling and logging.
 * Support for additional video codecs.
 * Flatpak or AUR packaging.
## 📄 License
This project is licensed under the **MIT License**. See the LICENSE file for details.
## 🙏 Acknowledgements
 * **end-4** – For the incredible illogical-impulse dotfiles and inspiration.
 * **matugen** – The core color extraction engine.
 * **Hyprland** – For providing the best Wayland experience.
