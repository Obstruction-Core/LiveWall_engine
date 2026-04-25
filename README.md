```markdown
# 🎨 LiveWall Engine

**Dynamic theme manager for Hyprland** – preview and apply Material You color schemes from any wallpaper: images, GIFs, or MP4 videos.

![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-6.6+-green.svg)
![Hyprland](https://img.shields.io/badge/Hyprland-Wayland-purple.svg)

---

> [!IMPORTANT]
> **Optimized for `illogical-impulse` dotfiles.**
> This tool was built specifically to integrate with the `quickshell` environment. While it may work on other Wayland compositors (Niri) or DEs (KDE/Gnome), support is currently experimental.

---

## 📖 Table of Contents
* [✨ Features](#-features)
* [🖼️ Preview](#-preview)
* [📦 Requirements](#-requirements)
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
```

```
### 🎨 Material You Theming
* **9 color schemes from matugen** – scheme-content, expressive, fidelity, fruit-salad, monochrome, neutral, rainbow, tonal-spot, and vibrant.
* **Dark / Light mode** – apply either with one click.
* **True color preview** – swatches show the exact colors you'll get.

### 🔄 Safe Revert & UX
* **Automatic backup** of `config.json` and previous theme state.
* **One-click revert** restores your last wallpaper + mode + scheme.
* **Interactive Swatches** – Click any color swatch to copy its HEX value to clipboard.

---

## 🖼️ Preview
| Video Preview |

| :---: | :---: |




https://github.com/user-attachments/assets/abf49a8d-01a1-431d-8ab5-c668b82f2edc













---

## 📦 Requirements
| Dependency | Purpose | Installation (Arch) |
| :--- | :--- | :--- |
| **Python 3.10+** | Script runtime | `sudo pacman -S python` |
| **PyQt6** | GUI framework | `pip install PyQt6` |
| **matugen** | Theme generation | AUR / end-4 dotfiles |
| **ffmpeg** | Video processing | `sudo pacman -S ffmpeg` |
| **mpvpaper** | Video wallpaper | `sudo pacman -S mpvpaper` |

---

## 🚀 Installation
1. **Clone the repository**
   ```bash
   git clone [https://github.com/yourusername/LiveWall_engine.git](https://github.com/yourusername/LiveWall_engine.git)
   cd LiveWall_engine

    Install dependencies
    Bash

    pip install PyQt6

    Run the app
    Bash

    python livewall_app.py

⚙️ Configuration

The engine automatically manages state in your illogical-impulse config folder:

    ~/.config/illogical-impulse/config.json

    ~/.config/illogical-impulse/config.json.theme.bak (Backups)

🎮 Usage

    Select a wallpaper – Browse to an image, GIF, or video.

    Watch live preview – Video/GIF plays automatically.

    Choose a theme – Click any theme in the list.

    Pick a mode – Press Apply Dark or Apply Light.

    Revert – If you don’t like the result, click Revert to Last State.

🔌 Integration with illogical-impulse

To add a launch button inside your WallpaperSelector.qml, insert this code:
QML

IconToolbarButton {
    text: "rocket_launch"
    onClicked: {
        Quickshell.exec(["python3", "/path/to/livewall_app.py"])
        GlobalStates.wallpaperSelectorOpen = false;
    }
}

🛠️ Troubleshooting

    MP4 preview not playing – Install GStreamer plugins: sudo pacman -S gst-plugins-good.

    matugen not found – Ensure matugen is in your PATH.

    Revert fail – Check if config.json.theme.prev.bak exists.

🤝 Contributing

Contributions are welcome! Please open an issue or pull request for:

    Better error handling.

    Flatpak packaging.

    Support for more video codecs.

📄 License

This project is licensed under the MIT License – see the LICENSE file for details.
🙏 Acknowledgements

    end-4 – For the incredible illogical-impulse dotfiles and matugen integration.

    matugen – The core color extraction engine.

    Hyprland – For the amazing Wayland experience.
