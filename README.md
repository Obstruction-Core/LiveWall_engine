# 🎨 LiveWall Engine

**Dynamic theme manager for Hyprland** – preview and apply Material You color schemes from any wallpaper: images, GIFs, or MP4 videos.

![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-6.6+-green.svg)
![Hyprland](https://img.shields.io/badge/Hyprland-Wayland-purple.svg)

## 📖 Table of Contents
* [✨ Features](#-features)
* [🖼️ Screenshots](#%EF%B8%8F-screenshots)
* [📦 Requirements](#-requirements)
* [🚀 Installation](#-installation)
* [⚙️ Configuration](#%EF%B8%8F-configuration)
* [🎮 Usage](#-usage)
* [🔌 Integration](#-integration)
* [🛠️ Troubleshooting](#%EF%B8%8F-troubleshooting)
* [🤝 Contributing](#-contributing)
* [📄 License](#-license)

---

## ✨ Features

### 🎬 Live Preview
* **Native Playback:** MP4, MKV, and WebM videos play directly inside the GUI using `QtMultimedia`.
* **Animated GIFs:** Smooth, looped previews powered by `QMovie`.
* **Static Images:** Intelligent scaling for JPEG, PNG, and WebP while preserving aspect ratio.

### 🎨 Material You Theming
* **9 matugen Color Schemes:** Content, Expressive, Fidelity, Fruit Salad, Monochrome, Neutral, Rainbow, Tonal-Spot, and Vibrant.
* **Instant Switching:** Apply Dark or Light mode with one click.
* **True Color Swatches:** Fixed dark/light swap bugs—what you see in the preview is exactly what hits your config.

### 🔄 Safe Revert & UX
* **Automatic Backups:** Every change creates a backup of your `config.json`.
* **One-Click Revert:** Instantly restore your previous wallpaper, mode, and scheme.
* **Interactive Swatches:** Click any color swatch to copy its HEX value to your clipboard.

---

## 🖼️ Screenshots
| Wallpaper Preview | Theme Selection |
| :---: | :---: |
| ![Preview](https://via.placeholder.com/400x250?text=Wallpaper+Preview) | ![Themes](https://via.placeholder.com/400x250?text=Theme+Selection) |
*Pro tip: Replace these placeholders with your actual screenshots once you upload them to your repo.*

---

## 📦 Requirements

| Dependency | Purpose | Installation (Arch) |
| :--- | :--- | :--- |
| **Python 3.10+** | Script runtime | `sudo pacman -S python` |
| **PyQt6** | GUI framework | `pip install PyQt6` |
| **matugen** | Color extraction | AUR (`matugen-bin`) |
| **ffmpeg** | Video frame extraction | `sudo pacman -S ffmpeg` |
| **mpvpaper** | Video wallpaper daemon | `sudo pacman -S mpvpaper` |

---

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone [https://github.com/yourusername/livewall-engine.git](https://github.com/yourusername/livewall-engine.git)
   cd livewall-engine

    Install Python dependencies
    Bash

    pip install --user PyQt6

    Make the script executable
    Bash

    chmod +x livewall_app.py

⚙️ Configuration

The engine integrates with the following config files:

    ~/.config/illogical-impulse/config.json (Active config)

    ~/.config/illogical-impulse/config.json.theme.bak (Theme backup)

🎮 Usage

    Launch the app from your terminal or application launcher.

    Select a file (Image/GIF/Video).

    Pick a Theme from the swatch list.

    Apply Dark or Light mode to instantly update your system.

🔌 Integration

To launch LiveWall Engine directly from the illogical-impulse wallpaper picker, add this code to your WallpaperSelectorContent.qml:
QML

IconToolbarButton {
    implicitWidth: height
    text: "rocket_launch"
    onClicked: {
        Quickshell.exec(["python3", "/path/to/livewall_app.py"])
        GlobalStates.wallpaperSelectorOpen = false;
    }
    StyledToolTip {
        text: "Launch LiveWall Engine"
    }
}

🛠️ Troubleshooting

    Video not playing: Ensure GStreamer is set up: sudo pacman -S gst-plugins-good.

    matugen issues: Check your $PATH to ensure matugen is reachable.

    UI Focus: If keys aren't working, ensure no other Hyprland layers are stealing focus.

🤝 Contributing

Feel free to open issues or submit PRs! I'm specifically looking for help with:

    Better GStreamer codec support.

    Packaging for Flatpak.

📄 License

Distributed under the MIT License. See LICENSE for more information.🎨 LiveWall Engine

Dynamic theme manager for Hyprland – preview and apply Material You color schemes from any wallpaper: images, GIFs, or MP4 videos.
📖 Table of Contents

    ✨ Features

    🖼️ Screenshots

    📦 Requirements

    🚀 Installation

    ⚙️ Configuration

    🎮 Usage

    Plug Integration with illogical-impulse

    🛠️ Troubleshooting

    🤝 Contributing

    📄 License

✨ Features
🎬 Live Preview

    Native Playback: MP4, MKV, and WebM videos play directly inside the GUI using QtMultimedia.

    Animated GIFs: Smooth, looped previews powered by QMovie.

    Static Images: Intelligent scaling for JPEG, PNG, and WebP while preserving aspect ratio.

🎨 Material You Theming

    9 matugen Color Schemes: Content, Expressive, Fidelity, Fruit Salad, Monochrome, Neutral, Rainbow, Tonal-Spot, and Vibrant.

    Instant Switching: Apply Dark or Light mode with one click.

    True Color Swatches: Fixed dark/light swap bugs—what you see in the preview is exactly what hits your config .

🔄 Safe Revert & UX

    Automatic Backups: Every change creates a backup of your config.json.

    One-Click Revert: Instantly restore your previous wallpaper, mode, and scheme.

    Interactive Swatches: Click any color swatch to copy its HEX value to your clipboard.

🖼️ Screenshots
Wallpaper Preview	Theme Selection
	
Main window with wallpaper preview, theme list, and color swatches.	
📦 Requirements
Dependency	Purpose	Installation (Arch)
Python 3.10+	Script runtime	sudo pacman -S python
PyQt6	GUI framework	pip install PyQt6
matugen	Color extraction	AUR (matugen-bin)
ffmpeg	Video frame extraction	sudo pacman -S ffmpeg
mpvpaper	Video wallpaper daemon	sudo pacman -S mpvpaper
Hyprland	Wayland compositor	Native
🚀 Installation

    Clone the repository
    Bash

    git clone https://github.com/yourusername/livewall-engine.git
    cd livewall-engine

    Install Python dependencies
    Bash

    pip install --user PyQt6

    Make the script executable
    Bash

    chmod +x livewall_app.py

⚙️ Configuration

The engine integrates with the illogical-impulse environment. It automatically tracks state in:

    ~/.config/illogical-impulse/config.json (Active config)

    ~/.config/illogical-impulse/config.json.theme.bak (Theme backup)

🔌 Integration with illogical-impulse

To launch LiveWall Engine directly from your existing Quickshell wallpaper picker:

    Open WallpaperSelectorContent.qml.

    Locate the Row containing extraOptions.

    Add this button to the Toolbar:

QML

IconToolbarButton {
    implicitWidth: height
    text: "rocket_launch"
    onClicked: {
        Quickshell.exec(["python3", "/path/to/livewall_app.py"])
        GlobalStates.wallpaperSelectorOpen = false;
    }
    StyledToolTip {
        text: "Launch LiveWall Engine (Valkyrie)"
    }
}

🛠️ Troubleshooting

    MP4 not playing: Ensure GStreamer plugins are installed: sudo pacman -S gst-plugins-good.

    Path Errors: If launching via .desktop file, use absolute paths for the Exec and Icon fields.

    Weeb Policy: Note that certain directories (like /homework) are hidden unless the weeb policy is enabled in your global config .

📄 License

Distributed under the MIT License. See LICENSE for more information.
