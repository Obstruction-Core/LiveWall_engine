🎨 LiveWall Engine

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
