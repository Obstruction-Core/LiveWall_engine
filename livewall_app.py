#!/usr/bin/env python3
# LiveWall Engine - Full version with native video/GIF preview (fixed aspect ratio)

import sys, os, subprocess, json, tempfile
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QMessageBox,
    QFrame, QListWidget, QListWidgetItem,
    QSizePolicy
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QUrl
from PyQt6.QtGui import QShortcut, QKeySequence, QMovie, QPixmap, QIcon
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtMultimediaWidgets import QVideoWidget


# Helper: get an image file from any media (extract first frame for videos)
def get_image_for_matugen(media_path):
    ext = media_path.lower()
    if ext.endswith(('.mp4', '.mkv', '.webm', '.mov')):
        temp_img = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        temp_img.close()
        subprocess.run([
            "ffmpeg", "-i", media_path, "-vframes", "1",
            "-vf", "scale=800:-1", temp_img.name, "-y"
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return temp_img.name
    else:
        return media_path


# ── Preview worker (dry-run, no file writes) ───────────────────────────────────
class PreviewWorker(QThread):
    done  = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, image, schemes):
        super().__init__()
        self.image  = image
        self.schemes = schemes

    def run(self):
        results = {}
        try:
            temp_image = None
            if self.image.lower().endswith(('.mp4', '.mkv', '.webm', '.mov')):
                temp_image = get_image_for_matugen(self.image)
                matugen_source = temp_image
            else:
                matugen_source = self.image

            def run_mode(scheme, mode):
                cmd = ["matugen", "image", matugen_source,
                       "-t", scheme, "-m", mode,
                       "--source-color-index", "0", "--dry-run", "-j", "hex"]
                raw = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode()
                return json.loads(raw).get("colors", {})

            for scheme in self.schemes:
                scheme_colors = {"dark": [], "light": []}
                for mode in ["dark", "light"]:
                    colors_data = run_mode(scheme, mode)
                    primary_colors = []
                    for role in ["primary", "secondary", "tertiary", "error"]:
                        color_entry = colors_data.get(role, {})
                        mode_colors = color_entry.get(mode) or color_entry.get("default") or {}
                        hex_color = mode_colors.get("color") or mode_colors.get("hex") or "#000000"
                        primary_colors.append(hex_color)
                    scheme_colors[mode] = primary_colors
                results[scheme] = scheme_colors

            if temp_image and os.path.exists(temp_image):
                os.remove(temp_image)
            self.done.emit(results)
        except subprocess.CalledProcessError as e:
            self.error.emit(e.output.decode() if e.output else str(e))
        except Exception as e:
            self.error.emit(str(e))


# ── Apply worker (same as before, uses get_image_for_matugen for videos) ───
class ApplyWorker(QThread):
    done  = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, image, scheme, mode, config_path, backup_path, theme_backup_path, theme_prev_backup_path):
        super().__init__()
        self.image             = image
        self.scheme            = scheme
        self.mode              = mode
        self.config_path       = config_path
        self.backup_path       = backup_path
        self.theme_backup_path = theme_backup_path
        self.theme_prev_backup_path = theme_prev_backup_path

    def run(self):
        try:
            if os.path.exists(self.config_path):
                if not os.path.exists(self.backup_path):
                    subprocess.run(["cp", self.config_path, self.backup_path])
                with open(self.config_path) as f:
                    data = json.load(f)
                if "background" in data:
                    data["background"]["wallpaperPath"] = ""
                with open(self.config_path, "w") as f:
                    json.dump(data, f, indent=4)

            if os.path.exists(self.theme_backup_path):
                subprocess.run(["cp", self.theme_backup_path, self.theme_prev_backup_path])
            with open(self.theme_backup_path, "w") as f:
                json.dump({"wallpaperPath": self.image,
                           "mode": self.mode, "scheme": self.scheme}, f, indent=4)

            subprocess.run(["pkill", "awww-daemon"], stderr=subprocess.DEVNULL)
            subprocess.run(["pkill", "mpvpaper"],    stderr=subprocess.DEVNULL)

            temp_image = None
            if self.image.lower().endswith(('.mp4', '.mkv', '.webm', '.mov')):
                temp_image = get_image_for_matugen(self.image)
                matugen_source = temp_image
            else:
                matugen_source = self.image

            ext = self.image.lower()
            if ext.endswith(".gif"):
                subprocess.Popen(["awww-daemon"], stdout=subprocess.DEVNULL)
                subprocess.run(["sleep", "1"])
                subprocess.run(["awww", "img", self.image])
            elif ext.endswith(('.mp4', '.mkv', '.webm', '.mov')):
                try:
                    mon = subprocess.check_output(
                        "hyprctl monitors | grep 'Monitor' | awk '{print $2}' | head -n 1",
                        shell=True, text=True
                    ).strip()
                    if not mon:
                        mon = "eDP-1"
                except:
                    mon = "eDP-1"
                subprocess.Popen(["mpvpaper", "-o", "loop", mon, self.image])

            subprocess.run([
                "matugen", "image", matugen_source,
                "-t", self.scheme, "-m", self.mode,
                "--source-color-index", "0",
            ], check=True)

            if temp_image and os.path.exists(temp_image):
                os.remove(temp_image)

            subprocess.run(["hyprctl", "dispatch", "exec", "quickshell --reload"])
            self.done.emit(f"{self.mode} · {self.scheme.replace('scheme-', '')}")

        except subprocess.CalledProcessError as e:
            if b"ffmpeg" in e.output or b"not found" in e.output:
                self.error.emit("ffmpeg not installed. Please install ffmpeg to use video wallpapers.")
            else:
                self.error.emit(e.output.decode() if e.output else str(e))
        except Exception as e:
            self.error.emit(str(e))


# ── Custom theme item widget with color previews ─────────────────────────────
class ThemeListItem(QWidget):
    def __init__(self, scheme_name, colors_dark, colors_light, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout()
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(12)

        name = scheme_name.replace("scheme-", "").replace("-", " ").title()
        name_label = QLabel(name)
        name_label.setStyleSheet("font-weight: bold; font-size: 13px; color: #cdd6f4;")
        name_label.setFixedWidth(110)
        layout.addWidget(name_label)

        dark_label = QLabel("Dark")
        dark_label.setStyleSheet("font-size: 10px; color: #6c7086;")
        dark_label.setFixedWidth(35)
        layout.addWidget(dark_label)
        for color in colors_dark:
            swatch = QFrame()
            swatch.setFixedSize(22, 22)
            swatch.setStyleSheet(f"background-color: {color}; border-radius: 4px; border: 1px solid rgba(255,255,255,0.15);")
            layout.addWidget(swatch)

        layout.addSpacing(8)

        light_label = QLabel("Light")
        light_label.setStyleSheet("font-size: 10px; color: #6c7086;")
        light_label.setFixedWidth(35)
        layout.addWidget(light_label)
        for color in colors_light:
            swatch = QFrame()
            swatch.setFixedSize(22, 22)
            swatch.setStyleSheet(f"background-color: {color}; border-radius: 4px; border: 1px solid rgba(0,0,0,0.1);")
            layout.addWidget(swatch)

        layout.addStretch()
        self.setLayout(layout)


# ── Main window with native preview and proper aspect ratio ──────────────────
class LiveWallApp(QWidget):

    SCHEMES = [
        "scheme-content", "scheme-expressive", "scheme-fidelity",
        "scheme-fruit-salad", "scheme-monochrome", "scheme-neutral",
        "scheme-rainbow", "scheme-tonal-spot", "scheme-vibrant",
    ]

    def __init__(self):
        super().__init__()
        self.config_path       = os.path.expanduser("~/.config/illogical-impulse/config.json")
        self.backup_path       = self.config_path + ".bak"
        self.theme_backup_path = self.config_path + ".theme.bak"
        self.theme_prev_backup_path = self.config_path + ".theme.prev.bak"
        self.file_path = None
        self._preview  = None
        self._applier  = None
        self._theme_colors = {}
        self._initUI()

    def _initUI(self):
        self.setWindowTitle("LiveWall Engine — Native Preview")
        self.setFixedSize(860, 760)

        # ── Set window icon ────────────────────────────────────────────────
        icon_path = "/home/obsidian/Downloads/art-and-design.png"
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            # Fallback to system theme icon
            self.setWindowIcon(QIcon.fromTheme("applications-graphics"))

        self.setStyleSheet("""
            QWidget { background: #0f0f17; color: #cdd6f4; font-family: 'Segoe UI', sans-serif; }
            QListWidget { background: #1a1b26; border: 1px solid #2a2b3a; border-radius: 12px; outline: none; padding: 4px; }
            QListWidget::item { border-radius: 8px; margin: 2px; }
            QListWidget::item:selected { background: #2d2e3f; }
            QPushButton { border-radius: 10px; font-weight: bold; font-size: 13px; padding: 10px; }
            QPushButton:hover { opacity: 0.9; }
            QFrame#card { background: #181926; border-radius: 16px; border: 1px solid #2a2b3a; }
            QLabel#status { background: #1a1b26; border-radius: 20px; padding: 6px 12px; }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)

        # Header
        header = QHBoxLayout()
        title = QLabel("🎨 LiveWall Engine")
        title.setStyleSheet("font-size: 26px; font-weight: bold; color: #cba6f7;")
        header.addWidget(title)
        header.addStretch()
        self.close_btn = QPushButton("✕  Close")
        self.close_btn.setStyleSheet("background: #313244; color: #f38ba8; padding: 6px 16px; border-radius: 20px;")
        self.close_btn.clicked.connect(self.close)
        header.addWidget(self.close_btn)
        main_layout.addLayout(header)

        # Preview card (with fixed height and proper scaling)
        preview_card = QFrame()
        preview_card.setObjectName("card")
        preview_layout = QVBoxLayout(preview_card)
        preview_layout.addWidget(QLabel("🔍 Live Preview"))

        self.preview_container = QFrame()
        self.preview_container.setStyleSheet("background: #0f0f17; border-radius: 8px;")
        self.preview_container.setFixedHeight(240)   # fixed height, width stretches
        self.preview_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # Label for static images and GIFs
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setScaledContents(False)
        self.preview_label.setMinimumHeight(220)
        self.preview_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Video widget
        self.video_widget = QVideoWidget()
        self.video_widget.setVisible(False)
        self.video_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        stack_layout = QVBoxLayout(self.preview_container)
        stack_layout.addWidget(self.preview_label)
        stack_layout.addWidget(self.video_widget)

        preview_layout.addWidget(self.preview_container)
        main_layout.addWidget(preview_card)

        # Media player for videos
        self.media_player = QMediaPlayer()
        self.media_player.setVideoOutput(self.video_widget)
        self.media_player.mediaStatusChanged.connect(self._loop_video)

        # Wallpaper card
        wallpaper_card = QFrame()
        wallpaper_card.setObjectName("card")
        wallpaper_layout = QVBoxLayout(wallpaper_card)
        wallpaper_layout.addWidget(QLabel("📁 Wallpaper"))
        self.btn_select = QPushButton("🖼️  Browse Wallpaper")
        self.btn_select.setStyleSheet("background: #2a2b3a; padding: 12px;")
        self.btn_select.clicked.connect(self._open_file)
        wallpaper_layout.addWidget(self.btn_select)
        self.lbl_file = QLabel("No file selected")
        self.lbl_file.setStyleSheet("font-size: 11px; color: #6c7086;")
        self.lbl_file.setWordWrap(True)
        self.lbl_file.setAlignment(Qt.AlignmentFlag.AlignCenter)
        wallpaper_layout.addWidget(self.lbl_file)
        main_layout.addWidget(wallpaper_card)

        # Theme selection card
        theme_card = QFrame()
        theme_card.setObjectName("card")
        theme_layout = QVBoxLayout(theme_card)
        theme_layout.addWidget(QLabel("✨ Available Themes"))
        self.theme_list = QListWidget()
        self.theme_list.setMinimumHeight(260)
        self.theme_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.theme_list.itemClicked.connect(self._on_theme_selected)
        theme_layout.addWidget(self.theme_list)
        main_layout.addWidget(theme_card)

        # Action buttons
        action_card = QFrame()
        action_card.setObjectName("card")
        action_layout = QVBoxLayout(action_card)
        mode_row = QHBoxLayout()
        mode_row.setSpacing(12)
        self.btn_dark = QPushButton("🌙  Apply Dark Mode")
        self.btn_dark.setStyleSheet("background: #313244;")
        self.btn_dark.setEnabled(False)
        self.btn_dark.clicked.connect(lambda: self._apply("dark"))
        mode_row.addWidget(self.btn_dark)
        self.btn_light = QPushButton("☀️  Apply Light Mode")
        self.btn_light.setStyleSheet("background: #eff1f5; color: #11111b;")
        self.btn_light.setEnabled(False)
        self.btn_light.clicked.connect(lambda: self._apply("light"))
        mode_row.addWidget(self.btn_light)
        self.btn_revert = QPushButton("↺  Revert to Last State")
        self.btn_revert.setStyleSheet("background: #f38ba8; color: #11111b;")
        self.btn_revert.clicked.connect(self._revert)
        mode_row.addWidget(self.btn_revert)
        action_layout.addLayout(mode_row)
        main_layout.addWidget(action_card)

        # Status bar
        self.lbl_status = QLabel("⚡ Ready — select a wallpaper to begin")
        self.lbl_status.setObjectName("status")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.lbl_status)

        # Esc to close
        QShortcut(QKeySequence("Esc"), self).activated.connect(self.close)

    # ── Preview update with aspect ratio preservation ──────────────────────────
    def _update_preview(self):
        """Update preview area – scales all media while keeping aspect ratio."""
        if not self.file_path or not os.path.exists(self.file_path):
            self.preview_label.clear()
            self.preview_label.setVisible(True)
            self.video_widget.setVisible(False)
            return

        ext = os.path.splitext(self.file_path)[1].lower()
        self.media_player.stop()
        self.preview_label.setMovie(None)
        self.video_widget.setVisible(False)
        self.preview_label.setVisible(True)

        if ext == '.gif':
            movie = QMovie(self.file_path)
            # Scale movie to fit label while keeping aspect ratio
            movie.setScaledSize(self.preview_label.size())
            self.preview_label.setMovie(movie)
            movie.start()
        elif ext in ('.mp4', '.mkv', '.webm', '.mov'):
            self.preview_label.setVisible(False)
            self.video_widget.setVisible(True)
            # Ensure video widget is properly sized
            available_size = self.preview_container.size()
            self.video_widget.resize(available_size.width() - 10, available_size.height() - 10)
            self.media_player.setSource(QUrl.fromLocalFile(self.file_path))
            self.media_player.play()
        else:
            # Static image
            pixmap = QPixmap(self.file_path)
            self._set_scaled_pixmap(pixmap)

    def _set_scaled_pixmap(self, pixmap):
        """Scale pixmap to fit label while preserving aspect ratio."""
        if pixmap.isNull():
            return
        label_size = self.preview_label.size()
        if label_size.width() <= 0 or label_size.height() <= 0:
            return
        scaled = pixmap.scaled(label_size, Qt.AspectRatioMode.KeepAspectRatio,
                               Qt.TransformationMode.SmoothTransformation)
        self.preview_label.setPixmap(scaled)

    def _loop_video(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.media_player.play()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if not hasattr(self, 'preview_label'):
            return
        # Rescale static image or GIF when window is resized
        if self.preview_label.isVisible():
            if self.preview_label.pixmap() and not self.preview_label.pixmap().isNull():
                self._set_scaled_pixmap(self.preview_label.pixmap())
            elif self.preview_label.movie():
                new_size = self.preview_label.size()
                self.preview_label.movie().setScaledSize(new_size)
        # Resize video widget if visible
        if hasattr(self, 'video_widget') and self.video_widget.isVisible():
            container_size = self.preview_container.size()
            self.video_widget.resize(container_size.width() - 10, container_size.height() - 10)

    # ── File picker and preview generation ────────────────────────────────────
    def _open_file(self):
        fname, _ = QFileDialog.getOpenFileName(
            self, "Select Wallpaper",
            os.path.expanduser("~/Pictures/Wallpapers"),
            "Media (*.gif *.mp4 *.mkv *.webm *.png *.jpg *.jpeg *.webp)"
        )
        if not fname:
            return
        self.file_path = fname
        short = os.path.basename(fname)
        self.btn_select.setText(f"📝  {short[:40]}{'…' if len(short)>40 else ''}")
        self.lbl_file.setText(fname)
        self._update_preview()
        self._refresh_preview()

    def _refresh_preview(self):
        if not self.file_path:
            return
        if self._preview and self._preview.isRunning():
            self._preview.terminate()
            self._preview.wait()
        self._set_status("⏳ Generating theme previews...", "#f9e2af")
        self._preview = PreviewWorker(self.file_path, self.SCHEMES)
        self._preview.done.connect(self._on_preview_done)
        self._preview.error.connect(self._on_preview_error)
        self._preview.start()

    def _on_preview_done(self, theme_colors):
        self._theme_colors = theme_colors
        self._populate_theme_list(theme_colors)
        self._set_status("✓ Preview ready — select a theme and click Apply", "#a6e3a1")

    def _on_preview_error(self, msg):
        self._set_status("❌ Preview failed — check matugen & ffmpeg", "#f38ba8")
        QMessageBox.critical(self, "Preview Error", msg)

    def _populate_theme_list(self, theme_colors):
        self.theme_list.clear()
        for scheme in self.SCHEMES:
            if scheme in theme_colors:
                # Swap dark/light to match actual matugen apply output
                colors_light = theme_colors[scheme]["dark"]
                colors_dark  = theme_colors[scheme]["light"]
                item_widget = ThemeListItem(scheme, colors_dark, colors_light)
                list_item = QListWidgetItem(self.theme_list)
                list_item.setSizeHint(item_widget.sizeHint())
                self.theme_list.addItem(list_item)
                self.theme_list.setItemWidget(list_item, item_widget)
                list_item.setData(Qt.ItemDataRole.UserRole, scheme)

    def _on_theme_selected(self, item):
        if self.file_path:
            self.btn_dark.setEnabled(True)
            self.btn_light.setEnabled(True)
            scheme = item.data(Qt.ItemDataRole.UserRole)
            nice_name = scheme.replace("scheme-", "").replace("-", " ").title()
            self._set_status(f"🎨 Selected: {nice_name} — ready to apply", "#cba6f7")

    def _apply(self, mode):
        if not self.file_path:
            return
        selected = self.theme_list.selectedItems()
        if not selected:
            self._set_status("❌ Please select a theme first", "#f38ba8")
            return
        if self._applier and self._applier.isRunning():
            return
        selected_scheme = selected[0].data(Qt.ItemDataRole.UserRole)
        self._set_buttons_enabled(False)
        self._set_status(f"⏳ Applying {mode} theme... please wait", "#f9e2af")
        self._applier = ApplyWorker(
            self.file_path, selected_scheme, mode,
            self.config_path, self.backup_path,
            self.theme_backup_path, self.theme_prev_backup_path
        )
        self._applier.done.connect(self._on_applied)
        self._applier.error.connect(self._on_apply_error)
        self._applier.start()

    def _on_applied(self, label):
        self._set_status(f"✅ Successfully applied: {label}", "#a6e3a1")
        self._set_buttons_enabled(True)

    def _on_apply_error(self, msg):
        self._set_status("❌ Application failed", "#f38ba8")
        self._set_buttons_enabled(True)
        QMessageBox.critical(self, "Apply Error", msg)

    def _set_buttons_enabled(self, val):
        self.btn_dark.setEnabled(val)
        self.btn_light.setEnabled(val)

    def _revert(self):
        if not os.path.exists(self.backup_path):
            QMessageBox.warning(self, "No Backup", "Nothing to revert to.")
            return
        subprocess.run(["mv", self.backup_path, self.config_path])
        subprocess.run(["pkill", "awww-daemon"], stderr=subprocess.DEVNULL)
        subprocess.run(["pkill", "mpvpaper"],    stderr=subprocess.DEVNULL)
        with open(self.config_path) as f:
            old_wall = json.load(f).get("background", {}).get("wallpaperPath", "")
        old_mode, old_scheme = "dark", "scheme-tonal-spot"
        if os.path.exists(self.theme_prev_backup_path):
            with open(self.theme_prev_backup_path) as f:
                prev = json.load(f)
            old_mode = prev.get("mode", "dark")
            old_scheme = prev.get("scheme", "scheme-tonal-spot")
            os.remove(self.theme_prev_backup_path)
        if os.path.exists(self.theme_backup_path):
            os.remove(self.theme_backup_path)
        if old_wall and os.path.exists(old_wall):
            temp_img = None
            if old_wall.lower().endswith(('.mp4', '.mkv', '.webm', '.mov')):
                temp_img = get_image_for_matugen(old_wall)
                matugen_source = temp_img
            else:
                matugen_source = old_wall
            subprocess.run([
                "matugen", "image", matugen_source,
                "-t", old_scheme, "-m", old_mode,
                "--source-color-index", "0",
            ])
            if temp_img and os.path.exists(temp_img):
                os.remove(temp_img)
        elif old_wall:
            QMessageBox.warning(self, "Revert", f"Previous wallpaper not found:\n{old_wall}")
        subprocess.run(["hyprctl", "dispatch", "exec", "quickshell --reload"])
        self._set_status(f"↺ Reverted to {old_mode} · {old_scheme.replace('scheme-','')}", "#cba6f7")
        self._set_buttons_enabled(True)

    def _set_status(self, text, color="#6c7086"):
        self.lbl_status.setText(text)
        self.lbl_status.setStyleSheet(f"background: #1a1b26; border-radius: 20px; padding: 6px 12px; color: {color};")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = LiveWallApp()
    window.show()
    sys.exit(app.exec())
