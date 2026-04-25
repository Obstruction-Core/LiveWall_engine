🎨 LiveWall Engine

    Dynamic theme manager for Hyprland – preview and apply Material You color schemes from any wallpaper: images, GIFs, or MP4 videos.

https://img.shields.io/badge/License-MIT-blue.svg
https://img.shields.io/badge/python-3.10+-blue.svg
https://img.shields.io/badge/PyQt6-6.6+-green.svg
https://img.shields.io/badge/Hyprland-Wayland-purple.svg
📖 Table of Contents

    ✨ Features

    🖼️ Screenshots

    📦 Requirements

    🚀 Installation

    ⚙️ Configuration

    🎮 Usage

    🔌 Integration with illogical‑impulse

    🛠️ Troubleshooting

    🤝 Contributing

    📄 License

    🙏 Acknowledgements

✨ Features
🎬 Live Preview

    Native playback – MP4, MKV, WebM videos play directly inside the GUI using QtMultimedia.

    Animated GIFs – smooth, looped preview with QMovie.

    Static images – JPEG, PNG, WebP, scaled to fit while preserving aspect ratio.

🎨 Material You Theming

    9 color schemes from matugen:

        scheme-content, scheme-expressive, scheme-fidelity

        scheme-fruit-salad, scheme-monochrome, scheme-neutral

        scheme-rainbow, scheme-tonal-spot, scheme-vibrant

    Dark / Light mode – apply either with one click.

    True color preview – swatches show the exact colors you'll get (fixed dark/light swap bug).

🖱️ Interactive Swatches

    Click any color swatch to copy its HEX value to clipboard.

    Primary, secondary, tertiary, and error colors shown for both modes.

🔄 Safe Revert

    Automatic backup of config.json and previous theme state.

    One‑click revert restores your last wallpaper + mode + scheme.

⌨️ Keyboard Shortcuts

    Esc – close the app.

    Full grid navigation (Arrows, Enter) when theme list is focused.

🧩 Seamless Integration

    Launch directly from illogical‑impulse wallpaper picker via a custom button ("Valkyrie Engine").

    Respects your existing matugen and mpvpaper / awww-daemon setup.

🖼️ Screenshots

    Placeholder – add your own screenshots here

text

[Main window with wallpaper preview, theme list, and color swatches]

https://screenshot.png
📦 Requirements
Dependency	Purpose	Installation (Arch)
Python 3.10+	Script runtime	sudo pacman -S python
PyQt6	GUI framework	pip install PyQt6
matugen	Color extraction & theme generation	AUR / end-4 dotfiles
ffmpeg	Extract frames from videos	sudo pacman -S ffmpeg
mpvpaper	Video wallpaper daemon (optional)	sudo pacman -S mpvpaper
awww-daemon	GIF wallpaper (optional)	sudo pacman -S awww
Hyprland	Wayland compositor	–

    Note: matugen is part of end-4’s dotfiles. Install it separately or use the included installer.

🚀 Installation
1. Clone the repository
bash

git clone https://github.com/yourusername/livewall-engine.git
cd livewall-engine

2. Install Python dependencies
bash

pip install --user PyQt6

3. Make the script executable
bash

chmod +x livewall_app.py

4. (Optional) Desktop entry

Create ~/.local/share/applications/livewall.desktop:
ini

[Desktop Entry]
Name=LiveWall Engine
Comment=Dynamic theme manager for matugen wallpapers
Exec=/usr/bin/python3 /absolute/path/to/livewall_app.py
Icon=/path/to/icon.png
Terminal=false
Type=Application
Categories=Utility;Settings;
StartupWMClass=LiveWallApp

Then run:
bash

update-desktop-database ~/.local/share/applications/

⚙️ Configuration

LiveWall Engine stores its state in:
text

~/.config/illogical-impulse/config.json          # matugen config
~/.config/illogical-impulse/config.json.bak      # backup of original config
~/.config/illogical-impulse/config.json.theme.bak # last applied theme
~/.config/illogical-impulse/config.json.theme.prev.bak # previous theme (for revert)

    No manual editing required – the app manages all backups automatically.

🎮 Usage
Starting the app

    From terminal: python3 livewall_app.py

    From application launcher: search for “LiveWall Engine”

    From illogical‑impulse wallpaper picker: click the Valkyrie Engine button (see Integration).

Workflow

    Select a wallpaper – browse to an image, GIF, or video.

    Watch the live preview – video/GIF plays automatically.

    Choose a theme – click any theme in the list.

    Pick a mode – press Apply Dark or Apply Light.

    Enjoy – your desktop wallpaper and color scheme instantly update.

    Revert – if you don’t like the result, click Revert to Last State.

Tips

    The preview always shows the actual colors that matugen will apply – we fixed the dark/light swap bug.

    Click any swatch to copy its HEX code (great for manual tweaks).

    Videos loop automatically in the preview and on your desktop (via mpvpaper).

🔌 Integration with illogical‑impulse

LiveWall Engine is designed to work seamlessly with end-4’s illogical-impulse dotfiles.

To add a launch button inside the illogical‑impulse wallpaper picker:

    Locate the QML file that defines the picker (e.g., WallpaperSelector.qml).

    Insert this button inside the ColumnLayout:

qml

RippleButton {
    Layout.fillWidth: true
    Layout.bottomMargin: 8
    implicitHeight: 38
    colBackground: Appearance.colors.colSecondaryContainer
    colBackgroundHover: Appearance.colors.colSecondaryContainerHover

    contentItem: RowLayout {
        MaterialSymbol { text: "rocket_launch" }
        StyledText { text: "Valkyrie Engine"; font.bold: true }
    }

    onClicked: {
        Quickshell.exec(["/usr/bin/python3", "/path/to/livewall_app.py"])
    }
}

    Replace /path/to/livewall_app.py with your actual script location.

    Restart Quickshell.

Now you can launch LiveWall Engine directly from the wallpaper picker sidebar.
🛠️ Troubleshooting
Issue	Solution
MP4 preview not playing	Install ffmpeg and gst‑plugins‑good (PyQt6 uses GStreamer). Run sudo pacman -S ffmpeg gst-plugins-good.
matugen command not found	Make sure matugen is installed and in your PATH (it’s part of end-4’s dotfiles).
App doesn’t start from .desktop	Use absolute paths in Exec= and Icon=. Add Path=/home/youruser to the .desktop file.
Wallpaper doesn’t change	Check that mpvpaper (for videos) or awww-daemon (for GIFs) is installed.
Revert doesn’t restore previous mode	The backup system stores the previous state before each apply – ensure config.json.theme.prev.bak exists.
Preview shows wrong colors	We already swapped dark/light in the preview – if still wrong, report as issue.
🤝 Contributing

Contributions are welcome! Please open an issue or pull request.

Areas that need help:

    Better error handling for missing dependencies.

    Support for more video codecs via GStreamer.

    Packaging as Flatpak / AppImage.

    Translations.

📄 License

MIT License – see LICENSE file.
🙏 Acknowledgements

    end-4 – for the incredible illogical‑impulse dotfiles and matugen integration.

    matugen – the core color extraction engine.

    Qt / PyQt6 – for the beautiful, native widget toolkit.

    Hyprland – the reason we have such a fantastic Wayland experience.

<p align="center">Made with ❤️ for the Hyprland community</p>
