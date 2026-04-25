# 🎨 LiveWall Engine

**Dynamic theme manager for Hyprland** – preview and apply Material You color schemes from any wallpaper: images, GIFs, or MP4 videos.

![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-6.6+-green.svg)
![Hyprland](https://img.shields.io/badge/Hyprland-Wayland-purple.svg)

## 📖 Table of Contents
* [⚠️ IMPORTANT!](#-Note)
* [✨ Features](#-features)
* [🖼️ Preview](#%EF%B8%8F-Preview)
* [📦 Requirements](#-requirements)
* [🚀 Installation](#-installation)
* [⚙️ Configuration](#%EF%B8%8F-configuration)
* [🎮 Usage](#-usage)
* [🔌 Integration with illogical-impulse](#-integration-with-illogical-impulse)
* [🛠️ Troubleshooting](#%EF%B8%8F-troubleshooting)
* [🤝 Contributing](#-contributing)
* [📄 License](#-license)
* [🙏 Acknowledgements](#-acknowledgements)

---

## Note
Please acknowledge this, i made this app on the illogical impulse end 4 dotfiles based hyprland, becuase i though this will be one more feature many people may/may not need but if you are using any other wm like niri,kde,gnome please test it and make aure it is stable as i only made this based on quickshell of illogical impulse. I really appreciate you trying out this project🙂

## ✨ Features
### 🎬 Live Preview
* **Native playback** – MP4, MKV, WebM videos play directly inside the GUI using `QtMultimedia`.
* **Animated GIFs** – Smooth, looped preview with `QMovie`.
* **Static images** – JPEG, PNG, WebP, scaled to fit while preserving aspect ratio.

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
