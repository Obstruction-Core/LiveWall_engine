
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

