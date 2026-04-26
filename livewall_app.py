#!/usr/bin/env python3
"""
LiveWall Engine v2.0
Glassmorphism UI · Smart state management · History & Favorites · Batch apply
"""

from __future__ import annotations
import sys, os, subprocess, json, tempfile, logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QFileDialog, QMessageBox,
    QFrame, QListWidget, QListWidgetItem, QTabWidget,
    QSizePolicy, QStackedWidget, QScrollArea, QProgressBar,
    QCheckBox, QToolButton, QMenu, QWidgetAction, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import (
    Qt, QThread, pyqtSignal, QUrl, QSize, QPropertyAnimation,
    QEasingCurve, QTimer, QPoint, pyqtProperty, QObject
)
from PyQt6.QtGui import (
    QShortcut, QKeySequence, QMovie, QPixmap, QIcon, QColor,
    QPainter, QPainterPath, QLinearGradient, QBrush, QPen, QFont,
    QFontDatabase, QCursor
)
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtMultimediaWidgets import QVideoWidget


# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(Path.home() / ".config/livewall/livewall.log", mode="a"),
    ]
)
log = logging.getLogger("LiveWall")


# ── Constants ─────────────────────────────────────────────────────────────────
APP_DIR        = Path.home() / ".config" / "livewall"
HISTORY_FILE   = APP_DIR / "history.json"
FAVORITES_FILE = APP_DIR / "favorites.json"
CONFIG_PATH    = Path.home() / ".config/illogical-impulse/config.json"
BACKUP_PATH    = CONFIG_PATH.with_suffix(".json.bak")
THEME_BACKUP   = CONFIG_PATH.with_suffix(".json.theme.bak")
THEME_PREV_BAK = CONFIG_PATH.with_suffix(".json.theme.prev.bak")

SCHEMES = [
    "scheme-content", "scheme-expressive", "scheme-fidelity",
    "scheme-fruit-salad", "scheme-monochrome", "scheme-neutral",
    "scheme-rainbow", "scheme-tonal-spot", "scheme-vibrant",
]

SCHEME_EMOJI = {
    "scheme-content":     "🎯",
    "scheme-expressive":  "🌈",
    "scheme-fidelity":    "🔬",
    "scheme-fruit-salad": "🍉",
    "scheme-monochrome":  "⬛",
    "scheme-neutral":     "🪨",
    "scheme-rainbow":     "🌠",
    "scheme-tonal-spot":  "💜",
    "scheme-vibrant":     "⚡",
}

# Glassmorphism palette
GLASS = {
    "bg":           "#09090f",
    "surface":      "rgba(255,255,255,0.04)",
    "surface_high": "rgba(255,255,255,0.08)",
    "border":       "rgba(255,255,255,0.10)",
    "border_high":  "rgba(255,255,255,0.20)",
    "accent":       "#c084fc",      # violet
    "accent2":      "#38bdf8",      # sky
    "accent3":      "#34d399",      # emerald
    "danger":       "#f87171",
    "warn":         "#fbbf24",
    "text":         "#f1f5f9",
    "text_muted":   "#64748b",
    "text_dim":     "#334155",
}

MEDIA_EXTS = {".gif", ".mp4", ".mkv", ".webm", ".mov", ".png", ".jpg", ".jpeg", ".webp", ".avif"}
VIDEO_EXTS  = {".mp4", ".mkv", ".webm", ".mov"}


# ── Utilities ─────────────────────────────────────────────────────────────────
def ensure_app_dir():
    APP_DIR.mkdir(parents=True, exist_ok=True)


def get_image_for_matugen(media_path: str) -> str:
    """Extract first frame from video for matugen colour analysis."""
    if Path(media_path).suffix.lower() in VIDEO_EXTS:
        tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        tmp.close()
        subprocess.run(
            ["ffmpeg", "-i", media_path, "-vframes", "1", "-vf", "scale=800:-1", tmp.name, "-y"],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        log.debug("Extracted frame → %s", tmp.name)
        return tmp.name
    return media_path


def cleanup_temp(path: Optional[str]):
    if path and os.path.exists(path):
        os.remove(path)


# ── Persistence helpers ───────────────────────────────────────────────────────
def load_json(path: Path, default):
    try:
        if path.exists():
            return json.loads(path.read_text())
    except Exception as e:
        log.warning("Could not load %s: %s", path, e)
    return default


def save_json(path: Path, data):
    try:
        ensure_app_dir()
        path.write_text(json.dumps(data, indent=2))
    except Exception as e:
        log.error("Could not save %s: %s", path, e)


# ── History & Favorites store ─────────────────────────────────────────────────
class Store:
    def __init__(self):
        self.history:   list[dict] = load_json(HISTORY_FILE,   [])
        self.favorites: list[str]  = load_json(FAVORITES_FILE, [])

    def add_history(self, entry: dict):
        self.history = [e for e in self.history if e.get("path") != entry["path"]]
        self.history.insert(0, entry)
        self.history = self.history[:50]
        save_json(HISTORY_FILE, self.history)

    def toggle_favorite(self, path: str) -> bool:
        if path in self.favorites:
            self.favorites.remove(path)
            is_fav = False
        else:
            self.favorites.append(path)
            is_fav = True
        save_json(FAVORITES_FILE, self.favorites)
        return is_fav

    def is_favorite(self, path: str) -> bool:
        return path in self.favorites


# ── Workers ───────────────────────────────────────────────────────────────────
class PreviewWorker(QThread):
    done     = pyqtSignal(dict)
    error    = pyqtSignal(str)
    progress = pyqtSignal(int)

    def __init__(self, image: str, schemes: list[str]):
        super().__init__()
        self.image   = image
        self.schemes = schemes

    def run(self):
        temp_image = None
        results = {}
        try:
            if Path(self.image).suffix.lower() in VIDEO_EXTS:
                temp_image = get_image_for_matugen(self.image)
                src = temp_image
            else:
                src = self.image

            for i, scheme in enumerate(self.schemes):
                scheme_colors: dict[str, list] = {}
                for mode in ("dark", "light"):
                    try:
                        cmd = ["matugen", "image", src, "-t", scheme, "-m", mode,
                               "--source-color-index", "0", "--dry-run", "-j", "hex"]
                        raw = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode()
                        colors_data = json.loads(raw).get("colors", {})
                        palette = []
                        for role in ("primary", "secondary", "tertiary", "error"):
                            entry = colors_data.get(role, {})
                            c = entry.get(mode) or entry.get("default") or {}
                            palette.append(c.get("color") or c.get("hex") or "#1e1e2e")
                        scheme_colors[mode] = palette
                    except Exception as e:
                        log.warning("Preview error [%s/%s]: %s", scheme, mode, e)
                        scheme_colors[mode] = ["#1e1e2e", "#313244", "#45475a", "#f38ba8"]
                results[scheme] = scheme_colors
                self.progress.emit(int((i + 1) / len(self.schemes) * 100))

            self.done.emit(results)
        except Exception as e:
            log.exception("PreviewWorker failed")
            self.error.emit(str(e))
        finally:
            cleanup_temp(temp_image)


class ApplyWorker(QThread):
    done     = pyqtSignal(str)
    error    = pyqtSignal(str)
    progress = pyqtSignal(str)

    def __init__(self, image: str, scheme: str, mode: str):
        super().__init__()
        self.image  = image
        self.scheme = scheme
        self.mode   = mode

    def run(self):
        temp_image = None
        try:
            self.progress.emit("Saving config backup…")
            if CONFIG_PATH.exists():
                if not BACKUP_PATH.exists():
                    subprocess.run(["cp", str(CONFIG_PATH), str(BACKUP_PATH)])
                data = json.loads(CONFIG_PATH.read_text())
                if "background" in data:
                    data["background"]["wallpaperPath"] = ""
                CONFIG_PATH.write_text(json.dumps(data, indent=4))

            if THEME_BACKUP.exists():
                subprocess.run(["cp", str(THEME_BACKUP), str(THEME_PREV_BAK)])
            THEME_BACKUP.write_text(json.dumps({
                "wallpaperPath": self.image,
                "mode": self.mode,
                "scheme": self.scheme,
            }, indent=2))

            self.progress.emit("Stopping active wallpaper daemons…")
            subprocess.run(["pkill", "awww-daemon"], stderr=subprocess.DEVNULL)
            subprocess.run(["pkill", "mpvpaper"],    stderr=subprocess.DEVNULL)

            self.progress.emit("Preparing colour source…")
            ext = Path(self.image).suffix.lower()
            if ext in VIDEO_EXTS:
                temp_image = get_image_for_matugen(self.image)
                src = temp_image
            else:
                src = self.image

            self.progress.emit("Launching wallpaper…")
            if ext == ".gif":
                subprocess.Popen(["awww-daemon"], stdout=subprocess.DEVNULL)
                subprocess.run(["sleep", "1"])
                subprocess.run(["awww", "img", self.image])
            elif ext in VIDEO_EXTS:
                try:
                    mon = subprocess.check_output(
                        "hyprctl monitors | grep 'Monitor' | awk '{print $2}' | head -n 1",
                        shell=True, text=True
                    ).strip() or "eDP-1"
                except Exception:
                    mon = "eDP-1"
                subprocess.Popen(["mpvpaper", "-o", "loop", mon, self.image])
            else:  # static image
                subprocess.Popen(["awww-daemon"], stdout=subprocess.DEVNULL)
                subprocess.run(["sleep", "1"])
                subprocess.run(["awww", "img", self.image])

            self.progress.emit("Running matugen colour engine…")
            subprocess.run([
                "matugen", "image", src,
                "-t", self.scheme, "-m", self.mode,
                "--source-color-index", "0",
            ], check=True)

            self.progress.emit("Reloading shell…")
            subprocess.run(["hyprctl", "dispatch", "exec", "quickshell --reload"])

            label = f"{self.mode.title()} · {self.scheme.replace('scheme-', '').replace('-', ' ').title()}"
            log.info("Applied: %s → %s", self.image, label)
            self.done.emit(label)

        except subprocess.CalledProcessError as e:
            out = e.output.decode() if e.output else str(e)
            log.error("ApplyWorker CalledProcessError: %s", out)
            if "ffmpeg" in out or "not found" in out.lower():
                self.error.emit("ffmpeg not installed. Please install ffmpeg to use video wallpapers.")
            else:
                self.error.emit(out)
        except Exception as e:
            log.exception("ApplyWorker failed")
            self.error.emit(str(e))
        finally:
            cleanup_temp(temp_image)


# ── Glassmorphism card widget ──────────────────────────────────────────────────
class GlassCard(QFrame):
    def __init__(self, parent=None, accent: bool = False):
        super().__init__(parent)
        self.accent = accent
        self.setObjectName("glassCard")
        self._setup_shadow()

    def _setup_shadow(self):
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(32)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.setGraphicsEffect(shadow)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect().adjusted(1, 1, -1, -1)
        path = QPainterPath()
        path.addRoundedRect(rect.x(), rect.y(), rect.width(), rect.height(), 16, 16)

        bg = QColor(255, 255, 255, 10 if not self.accent else 16)
        p.fillPath(path, bg)

        pen_color = QColor(255, 255, 255, 26 if not self.accent else 50)
        p.setPen(QPen(pen_color, 1))
        p.drawPath(path)
        p.end()


# ── Animated status badge ─────────────────────────────────────────────────────
class StatusBadge(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFixedHeight(36)
        self._base_style = f"""
            QLabel {{
                border-radius: 18px;
                padding: 4px 18px;
                font-size: 12px;
                font-weight: 600;
                letter-spacing: 0.3px;
            }}
        """
        self.set_ready()

    def _apply(self, text: str, fg: str, bg: str):
        self.setText(text)
        self.setStyleSheet(self._base_style + f"QLabel {{ color: {fg}; background: {bg}; }}")

    def set_ready(self):
        self._apply("⚡  Ready — select a wallpaper to begin", GLASS["text_muted"],
                    "rgba(255,255,255,0.05)")

    def set_loading(self, msg: str = "Working…"):
        self._apply(f"⏳  {msg}", GLASS["warn"], "rgba(251,191,36,0.12)")

    def set_success(self, msg: str):
        self._apply(f"✓  {msg}", GLASS["accent3"], "rgba(52,211,153,0.12)")

    def set_error(self, msg: str):
        self._apply(f"✕  {msg}", GLASS["danger"], "rgba(248,113,113,0.12)")

    def set_info(self, msg: str):
        self._apply(f"◆  {msg}", GLASS["accent"], "rgba(192,132,252,0.12)")


# ── Theme swatch item ──────────────────────────────────────────────────────────
class ThemeListItem(QWidget):
    def __init__(self, scheme: str, colors_dark: list, colors_light: list, is_fav: bool = False):
        super().__init__()
        self.scheme = scheme
        layout = QHBoxLayout()
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(10)

        emoji = SCHEME_EMOJI.get(scheme, "🎨")
        name  = scheme.replace("scheme-", "").replace("-", " ").title()
        lbl = QLabel(f"{emoji}  {name}")
        lbl.setStyleSheet(f"font-weight: 700; font-size: 13px; color: {GLASS['text']}; background: transparent;")
        lbl.setFixedWidth(145)
        layout.addWidget(lbl)

        d_label = QLabel("D")
        d_label.setStyleSheet(f"font-size: 9px; font-weight: 700; color: {GLASS['text_muted']}; background: transparent;")
        d_label.setFixedWidth(12)
        layout.addWidget(d_label)
        for color in colors_dark:
            sw = QFrame()
            sw.setFixedSize(20, 20)
            sw.setStyleSheet(f"""
                background: {color};
                border-radius: 5px;
                border: 1px solid rgba(255,255,255,0.12);
            """)
            layout.addWidget(sw)

        layout.addSpacing(6)

        l_label = QLabel("L")
        l_label.setStyleSheet(f"font-size: 9px; font-weight: 700; color: {GLASS['text_muted']}; background: transparent;")
        l_label.setFixedWidth(12)
        layout.addWidget(l_label)
        for color in colors_light:
            sw = QFrame()
            sw.setFixedSize(20, 20)
            sw.setStyleSheet(f"""
                background: {color};
                border-radius: 5px;
                border: 1px solid rgba(0,0,0,0.15);
            """)
            layout.addWidget(sw)

        layout.addStretch()

        self.fav_btn = QToolButton()
        self.fav_btn.setFixedSize(26, 26)
        self.fav_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.set_favorite(is_fav)
        self.fav_btn.setStyleSheet("border: none; background: transparent;")
        layout.addWidget(self.fav_btn)

        self.setLayout(layout)

    def set_favorite(self, val: bool):
        self._is_fav = val
        self.fav_btn.setText("★" if val else "☆")
        color = GLASS["warn"] if val else GLASS["text_dim"]
        self.fav_btn.setStyleSheet(f"border: none; background: transparent; color: {color}; font-size: 16px;")


# ── History item ──────────────────────────────────────────────────────────────
class HistoryItem(QWidget):
    restore_requested = pyqtSignal(dict)

    def __init__(self, entry: dict):
        super().__init__()
        self.entry = entry
        layout = QHBoxLayout()
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(10)

        thumb = QLabel()
        thumb.setFixedSize(54, 36)
        thumb.setStyleSheet("border-radius: 6px; background: rgba(255,255,255,0.05);")
        path = entry.get("path", "")
        if path and Path(path).exists() and Path(path).suffix.lower() not in VIDEO_EXTS | {".gif"}:
            px = QPixmap(path).scaled(54, 36, Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                                      Qt.TransformationMode.SmoothTransformation)
            thumb.setPixmap(px)
        layout.addWidget(thumb)

        info = QVBoxLayout()
        info.setSpacing(2)
        name_lbl = QLabel(Path(path).name if path else "Unknown")
        name_lbl.setStyleSheet(f"font-size: 12px; font-weight: 600; color: {GLASS['text']}; background: transparent;")
        name_lbl.setMaximumWidth(280)
        info.addWidget(name_lbl)

        meta = f"{entry.get('mode','?').title()} · {entry.get('scheme','?').replace('scheme-','').replace('-',' ').title()}"
        ts   = entry.get("timestamp", "")
        meta_lbl = QLabel(f"{meta}   {ts}")
        meta_lbl.setStyleSheet(f"font-size: 10px; color: {GLASS['text_muted']}; background: transparent;")
        info.addWidget(meta_lbl)
        layout.addLayout(info)
        layout.addStretch()

        restore_btn = QPushButton("↺")
        restore_btn.setFixedSize(32, 32)
        restore_btn.setToolTip("Restore this wallpaper")
        restore_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        restore_btn.setStyleSheet(f"""
            QPushButton {{
                background: rgba(192,132,252,0.15);
                color: {GLASS['accent']};
                border-radius: 8px;
                font-size: 16px;
                border: 1px solid rgba(192,132,252,0.25);
            }}
            QPushButton:hover {{
                background: rgba(192,132,252,0.28);
            }}
        """)
        restore_btn.clicked.connect(lambda: self.restore_requested.emit(self.entry))
        layout.addWidget(restore_btn)
        self.setLayout(layout)


# ── Pill button ────────────────────────────────────────────────────────────────
def make_pill_btn(text: str, bg: str, fg: str, width: int = 0) -> QPushButton:
    btn = QPushButton(text)
    btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
    w = f"min-width: {width}px;" if width else ""
    btn.setStyleSheet(f"""
        QPushButton {{
            background: {bg};
            color: {fg};
            border-radius: 10px;
            font-weight: 700;
            font-size: 13px;
            padding: 10px 20px;
            border: 1px solid rgba(255,255,255,0.08);
            {w}
        }}
        QPushButton:hover {{
            background: {bg.replace('0.15', '0.25').replace('0.12', '0.22')};
            border: 1px solid rgba(255,255,255,0.16);
        }}
        QPushButton:disabled {{
            background: rgba(255,255,255,0.04);
            color: rgba(255,255,255,0.2);
            border: 1px solid rgba(255,255,255,0.04);
        }}
    """)
    return btn


# ── Main window ────────────────────────────────────────────────────────────────
class LiveWallApp(QWidget):

    def __init__(self):
        super().__init__()
        ensure_app_dir()
        self.store        = Store()
        self.file_path: Optional[str] = None
        self._preview_worker: Optional[PreviewWorker] = None
        self._apply_worker:   Optional[ApplyWorker]   = None
        self._theme_colors: dict = {}
        self._current_pixmap: Optional[QPixmap] = None
        self._current_scheme: Optional[str] = None
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle("LiveWall Engine  v2")
        self.setFixedSize(940, 860)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)

        icon_path = Path.home() / "Downloads/art-and-design.png"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        self.setStyleSheet(f"""
            QWidget {{
                background: {GLASS['bg']};
                color: {GLASS['text']};
                font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
            }}
            QListWidget {{
                background: transparent;
                border: none;
                outline: none;
            }}
            QListWidget::item {{
                border-radius: 10px;
                margin: 2px 0;
                background: rgba(255,255,255,0.03);
                border: 1px solid rgba(255,255,255,0.05);
            }}
            QListWidget::item:selected {{
                background: rgba(192,132,252,0.12);
                border: 1px solid rgba(192,132,252,0.30);
            }}
            QListWidget::item:hover {{
                background: rgba(255,255,255,0.06);
            }}
            QTabWidget::pane {{
                border: none;
                background: transparent;
            }}
            QTabBar::tab {{
                background: rgba(255,255,255,0.04);
                color: {GLASS['text_muted']};
                padding: 8px 22px;
                border-radius: 8px;
                margin-right: 4px;
                font-weight: 600;
                font-size: 12px;
                border: 1px solid rgba(255,255,255,0.06);
            }}
            QTabBar::tab:selected {{
                background: rgba(192,132,252,0.18);
                color: {GLASS['accent']};
                border: 1px solid rgba(192,132,252,0.35);
            }}
            QScrollBar:vertical {{
                background: transparent;
                width: 6px;
                margin: 0;
            }}
            QScrollBar::handle:vertical {{
                background: rgba(255,255,255,0.15);
                border-radius: 3px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
            }}
            QProgressBar {{
                background: rgba(255,255,255,0.06);
                border-radius: 3px;
                border: none;
                height: 4px;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 {GLASS['accent']}, stop:1 {GLASS['accent2']});
                border-radius: 3px;
            }}
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(18)

        root.addLayout(self._build_header())
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(4)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.hide()
        root.addWidget(self.progress_bar)

        top_row = QHBoxLayout()
        top_row.setSpacing(16)
        top_row.addWidget(self._build_preview_card(), stretch=3)
        top_row.addWidget(self._build_file_card(), stretch=2)
        root.addLayout(top_row)

        root.addWidget(self._build_tabs())
        root.addWidget(self._build_action_bar())
        self.status = StatusBadge()
        root.addWidget(self.status)

        self.media_player = QMediaPlayer()
        self.media_player.setVideoOutput(self.video_widget)
        self.media_player.mediaStatusChanged.connect(self._loop_video)

        QShortcut(QKeySequence("Esc"),    self).activated.connect(self.close)
        QShortcut(QKeySequence("Ctrl+O"), self).activated.connect(self._open_file)
        QShortcut(QKeySequence("Ctrl+D"), self).activated.connect(lambda: self._apply("dark"))
        QShortcut(QKeySequence("Ctrl+L"), self).activated.connect(lambda: self._apply("light"))
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(self._toggle_favorite)

    def _build_header(self) -> QHBoxLayout:
        h = QHBoxLayout()
        title = QLabel("⬡  LiveWall Engine")
        title.setStyleSheet(f"font-size: 24px; font-weight: 800; color: {GLASS['accent']};")
        h.addWidget(title)
        h.addStretch()
        version = QLabel("v2.0 · glassmorphism")
        version.setStyleSheet(f"font-size: 10px; color: {GLASS['text_dim']}; font-weight: 600;")
        h.addWidget(version)
        h.addSpacing(16)
        close_btn = make_pill_btn("✕  Close", "rgba(248,113,113,0.12)", GLASS["danger"])
        close_btn.clicked.connect(self.close)
        h.addWidget(close_btn)
        return h

    def _build_preview_card(self) -> GlassCard:
        card = GlassCard()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        row = QHBoxLayout()
        lbl = QLabel("🔍  Live Preview")
        lbl.setStyleSheet(f"font-weight: 700; font-size: 13px; color: {GLASS['text_muted']};")
        row.addWidget(lbl)
        row.addStretch()
        self.fav_indicator = QLabel("☆")
        self.fav_indicator.setStyleSheet(f"font-size: 18px; color: {GLASS['text_dim']};")
        row.addWidget(self.fav_indicator)
        layout.addLayout(row)

        self.preview_stack = QStackedWidget()
        self.preview_stack.setMinimumHeight(190)
        self.preview_stack.setMaximumHeight(190)
        self.preview_stack.setStyleSheet("border-radius: 10px; background: rgba(0,0,0,0.3);")

        self.preview_label = QLabel("Drop a wallpaper here")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet(f"color: {GLASS['text_dim']}; font-size: 13px;")

        self.video_widget = QVideoWidget()
        self.video_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.preview_stack.addWidget(self.preview_label)
        self.preview_stack.addWidget(self.video_widget)
        layout.addWidget(self.preview_stack)
        return card

    def _build_file_card(self) -> GlassCard:
        card = GlassCard()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        lbl = QLabel("📁  Wallpaper Source")
        lbl.setStyleSheet(f"font-weight: 700; font-size: 13px; color: {GLASS['text_muted']};")
        layout.addWidget(lbl)

        self.btn_select = make_pill_btn("🖼️   Browse…", "rgba(192,132,252,0.15)", GLASS["accent"])
        self.btn_select.clicked.connect(self._open_file)
        layout.addWidget(self.btn_select)

        self.lbl_file = QLabel("No file selected")
        self.lbl_file.setWordWrap(True)
        self.lbl_file.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_file.setStyleSheet(f"font-size: 10px; color: {GLASS['text_dim']};")
        layout.addWidget(self.lbl_file)

        layout.addStretch()

        self.file_info = QLabel("")
        self.file_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.file_info.setStyleSheet(f"""
            background: rgba(255,255,255,0.05);
            border-radius: 8px;
            padding: 4px 10px;
            font-size: 10px;
            color: {GLASS['text_muted']};
        """)
        layout.addWidget(self.file_info)
        return card

    def _build_tabs(self) -> QTabWidget:
        self.tabs = QTabWidget()

        themes_widget = QWidget()
        themes_layout = QVBoxLayout(themes_widget)
        themes_layout.setContentsMargins(0, 8, 0, 0)

        self.theme_list = QListWidget()
        self.theme_list.setMinimumHeight(240)
        self.theme_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.theme_list.itemClicked.connect(self._on_theme_selected)
        self._populate_theme_placeholder()
        themes_layout.addWidget(self.theme_list)
        self.tabs.addTab(themes_widget, "✨  Themes")

        history_widget = QWidget()
        history_layout = QVBoxLayout(history_widget)
        history_layout.setContentsMargins(0, 8, 0, 0)
        self.history_list = QListWidget()
        self.history_list.setMinimumHeight(240)
        history_layout.addWidget(self.history_list)
        self._refresh_history_list()
        self.tabs.addTab(history_widget, "🕑  History")

        favs_widget = QWidget()
        favs_layout = QVBoxLayout(favs_widget)
        favs_layout.setContentsMargins(0, 8, 0, 0)
        self.favs_list = QListWidget()
        self.favs_list.setMinimumHeight(240)
        favs_layout.addWidget(self.favs_list)
        self._refresh_favs_list()
        self.tabs.addTab(favs_widget, "★  Favorites")

        return self.tabs

    def _build_action_bar(self) -> GlassCard:
        card = GlassCard(accent=True)
        layout = QHBoxLayout(card)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(10)

        self.btn_dark = make_pill_btn("🌙  Dark Mode", "rgba(139,92,246,0.20)", GLASS["accent"], 160)
        self.btn_dark.setEnabled(False)
        self.btn_dark.clicked.connect(lambda: self._apply("dark"))
        layout.addWidget(self.btn_dark)

        self.btn_light = make_pill_btn("☀️  Light Mode", "rgba(251,191,36,0.15)", GLASS["warn"], 160)
        self.btn_light.setEnabled(False)
        self.btn_light.clicked.connect(lambda: self._apply("light"))
        layout.addWidget(self.btn_light)

        layout.addStretch()

        self.btn_fav = make_pill_btn("☆  Favorite", "rgba(255,255,255,0.06)", GLASS["text_muted"])
        self.btn_fav.clicked.connect(self._toggle_favorite)
        layout.addWidget(self.btn_fav)

        self.btn_revert = make_pill_btn("↺  Revert", "rgba(248,113,113,0.15)", GLASS["danger"])
        self.btn_revert.clicked.connect(self._revert)
        layout.addWidget(self.btn_revert)

        return card

    def _populate_theme_placeholder(self):
        self.theme_list.clear()
        placeholder = QListWidgetItem("  Select a wallpaper to generate themes…")
        placeholder.setForeground(QColor(GLASS["text_dim"]))
        placeholder.setFlags(Qt.ItemFlag.NoItemFlags)
        self.theme_list.addItem(placeholder)

    def _populate_theme_list(self, theme_colors: dict):
        self.theme_list.clear()
        for scheme in SCHEMES:
            if scheme not in theme_colors:
                continue
            colors_dark  = theme_colors[scheme].get("dark",  [])
            colors_light = theme_colors[scheme].get("light", [])
            is_fav = self.store.is_favorite(scheme)
            item_widget = ThemeListItem(scheme, colors_dark, colors_light, is_fav)
            item_widget.fav_btn.clicked.connect(lambda _, s=scheme, w=item_widget: self._toggle_scheme_fav(s, w))
            list_item = QListWidgetItem(self.theme_list)
            list_item.setSizeHint(QSize(0, 52))
            list_item.setData(Qt.ItemDataRole.UserRole, scheme)
            self.theme_list.addItem(list_item)
            self.theme_list.setItemWidget(list_item, item_widget)

    def _toggle_scheme_fav(self, scheme: str, widget: ThemeListItem):
        is_fav = self.store.toggle_favorite(scheme)
        widget.set_favorite(is_fav)
        self._refresh_favs_list()

    def _refresh_history_list(self):
        self.history_list.clear()
        if not self.store.history:
            item = QListWidgetItem("  No history yet — apply a theme to begin")
            item.setForeground(QColor(GLASS["text_dim"]))
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.history_list.addItem(item)
            return
        for entry in self.store.history:
            widget = HistoryItem(entry)
            widget.restore_requested.connect(self._restore_from_history)
            list_item = QListWidgetItem(self.history_list)
            list_item.setSizeHint(QSize(0, 64))
            self.history_list.addItem(list_item)
            self.history_list.setItemWidget(list_item, widget)

    def _refresh_favs_list(self):
        self.favs_list.clear()
        favs = [e for e in self.store.history if e.get("path") in self.store.favorites
                or e.get("scheme") in self.store.favorites]
        if not favs:
            item = QListWidgetItem("  No favorites yet — star a theme or wallpaper")
            item.setForeground(QColor(GLASS["text_dim"]))
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.favs_list.addItem(item)
            return
        for entry in favs:
            widget = HistoryItem(entry)
            widget.restore_requested.connect(self._restore_from_history)
            list_item = QListWidgetItem(self.favs_list)
            list_item.setSizeHint(QSize(0, 64))
            self.favs_list.addItem(list_item)
            self.favs_list.setItemWidget(list_item, widget)

    def _restore_from_history(self, entry: dict):
        path   = entry.get("path", "")
        scheme = entry.get("scheme", "scheme-tonal-spot")
        mode   = entry.get("mode", "dark")
        if not path or not Path(path).exists():
            self.status.set_error("Wallpaper file no longer exists")
            return
        self.file_path = path
        self._update_file_ui()
        self._update_preview()
        self._refresh_preview_colors()
        self._start_apply(path, scheme, mode)

    def _open_file(self):
        fname, _ = QFileDialog.getOpenFileName(
            self, "Select Wallpaper",
            str(Path.home() / "Pictures/Wallpapers"),
            "Media (*.gif *.mp4 *.mkv *.webm *.png *.jpg *.jpeg *.webp *.avif)"
        )
        if not fname:
            return
        self.file_path = fname
        self._update_file_ui()
        self._update_preview()
        self._refresh_preview_colors()

    def _update_file_ui(self):
        if not self.file_path:
            return
        p = Path(self.file_path)
        short = p.name
        self.btn_select.setText(f"📝  {short[:36]}{'…' if len(short) > 36 else ''}")
        self.lbl_file.setText(self.file_path)

        try:
            size_mb = p.stat().st_size / 1_048_576
            self.file_info.setText(f"{p.suffix.upper().lstrip('.')}  ·  {size_mb:.1f} MB")
        except Exception:
            self.file_info.setText("")

        is_fav = self.store.is_favorite(self.file_path)
        self._update_fav_btn(is_fav)

    def _update_fav_btn(self, is_fav: bool):
        if is_fav:
            self.btn_fav.setText("★  Favorited")
            self.btn_fav.setStyleSheet(make_pill_btn("★  Favorited", "rgba(255,255,255,0.06)", GLASS["warn"]).styleSheet())
            self.fav_indicator.setText("★")
            self.fav_indicator.setStyleSheet(f"font-size: 18px; color: {GLASS['warn']};")
        else:
            self.btn_fav.setText("☆  Favorite")
            self.btn_fav.setStyleSheet(make_pill_btn("☆  Favorite", "rgba(255,255,255,0.06)", GLASS["text_muted"]).styleSheet())
            self.fav_indicator.setText("☆")
            self.fav_indicator.setStyleSheet(f"font-size: 18px; color: {GLASS['text_dim']};")

    def _toggle_favorite(self):
        if not self.file_path:
            return
        is_fav = self.store.toggle_favorite(self.file_path)
        self._update_fav_btn(is_fav)
        self._refresh_favs_list()
        self.status.set_info("Added to favorites ★" if is_fav else "Removed from favorites")

    def _update_preview(self):
        if not self.file_path or not Path(self.file_path).exists():
            self.preview_stack.setCurrentIndex(0)
            self.preview_label.clear()
            self.preview_label.setText("Drop a wallpaper here")
            return

        ext = Path(self.file_path).suffix.lower()
        self.media_player.stop()
        if self.preview_label.movie():
            self.preview_label.movie().stop()
            self.preview_label.setMovie(None)

        avail = QSize(self.preview_stack.width() or 400, self.preview_stack.height() or 190)

        if ext == ".gif":
            self.preview_stack.setCurrentIndex(0)
            movie = QMovie(self.file_path)
            movie.setScaledSize(avail)
            self.preview_label.setMovie(movie)
            movie.start()

        elif ext in VIDEO_EXTS:
            self.preview_stack.setCurrentIndex(1)
            self.media_player.setSource(QUrl.fromLocalFile(self.file_path))
            self.media_player.play()

        else:
            self.preview_stack.setCurrentIndex(0)
            px = QPixmap(self.file_path)
            if not px.isNull():
                scaled = px.scaled(avail, Qt.AspectRatioMode.KeepAspectRatio,
                                   Qt.TransformationMode.SmoothTransformation)
                self.preview_label.setPixmap(scaled)
                self._current_pixmap = px

    def _loop_video(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.media_player.play()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if not self.file_path:
            return
        avail = QSize(self.preview_stack.width(), self.preview_stack.height())
        if avail.width() <= 0:
            return
        if self.preview_stack.currentIndex() == 0:
            movie = self.preview_label.movie()
            if movie:
                movie.setScaledSize(avail)
            elif self._current_pixmap and not self._current_pixmap.isNull():
                self.preview_label.setPixmap(
                    self._current_pixmap.scaled(avail, Qt.AspectRatioMode.KeepAspectRatio,
                                                Qt.TransformationMode.SmoothTransformation)
                )

    def _refresh_preview_colors(self):
        if not self.file_path:
            return
        if self._preview_worker and self._preview_worker.isRunning():
            self._preview_worker.terminate()
            self._preview_worker.wait()

        self.btn_dark.setEnabled(False)
        self.btn_light.setEnabled(False)

        self.progress_bar.setValue(0)
        self.progress_bar.show()
        self.status.set_loading("Generating theme previews…")
        self._populate_theme_placeholder()

        self._preview_worker = PreviewWorker(self.file_path, SCHEMES)
        self._preview_worker.done.connect(self._on_preview_done)
        self._preview_worker.error.connect(self._on_preview_error)
        self._preview_worker.progress.connect(self.progress_bar.setValue)
        self._preview_worker.start()

    def _on_preview_done(self, theme_colors: dict):
        self._theme_colors = theme_colors
        self._populate_theme_list(theme_colors)
        self.progress_bar.hide()
        self.status.set_success("Preview ready — pick a theme and apply")

    def _on_preview_error(self, msg: str):
        self.progress_bar.hide()
        self.status.set_error("Preview failed — check matugen & ffmpeg")
        log.error("Preview error: %s", msg)
        QMessageBox.critical(self, "Preview Error", msg)
        self.btn_dark.setEnabled(False)
        self.btn_light.setEnabled(False)

    def _on_theme_selected(self, item: QListWidgetItem):
        scheme = item.data(Qt.ItemDataRole.UserRole)
        if not scheme or not self.file_path:
            return
        self._current_scheme = scheme
        self.btn_dark.setEnabled(True)
        self.btn_light.setEnabled(True)
        nice = scheme.replace("scheme-", "").replace("-", " ").title()
        self.status.set_info(f"Selected: {SCHEME_EMOJI.get(scheme, '🎨')}  {nice} — click to apply")

    def _apply(self, mode: str):
        if not self.file_path:
            self.status.set_error("No wallpaper selected")
            return
        selected = self.theme_list.selectedItems()
        if not selected:
            self.status.set_error("Please select a theme first")
            return
        scheme = selected[0].data(Qt.ItemDataRole.UserRole)
        if not scheme:
            return
        self._start_apply(self.file_path, scheme, mode)

    def _start_apply(self, path: str, scheme: str, mode: str):
        if self._apply_worker and self._apply_worker.isRunning():
            return
        self._set_apply_buttons(False)
        self.progress_bar.setRange(0, 0)
        self.progress_bar.show()

        self._apply_worker = ApplyWorker(path, scheme, mode)
        self._apply_worker.done.connect(self._on_applied)
        self._apply_worker.error.connect(self._on_apply_error)
        self._apply_worker.progress.connect(lambda m: self.status.set_loading(m))
        self._apply_worker.start()

    def _on_applied(self, label: str):
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)
        QTimer.singleShot(800, self.progress_bar.hide)
        self.status.set_success(f"Applied: {label}")
        self._set_apply_buttons(True)

        if self.file_path and self._apply_worker:
            entry = {
                "path":      self.file_path,
                "scheme":    self._apply_worker.scheme,
                "mode":      self._apply_worker.mode,
                "timestamp": datetime.now().strftime("%d %b %Y · %H:%M"),
            }
            self.store.add_history(entry)
            self._refresh_history_list()
            self._refresh_favs_list()

    def _on_apply_error(self, msg: str):
        self.progress_bar.setRange(0, 100)
        self.progress_bar.hide()
        self.status.set_error("Application failed — see logs")
        self._set_apply_buttons(True)
        QMessageBox.critical(self, "Apply Error", msg)

    def _set_apply_buttons(self, enabled: bool):
        self.btn_dark.setEnabled(enabled)
        self.btn_light.setEnabled(enabled)

    # ======================== FIXED REVERT METHOD =========================
    def _revert(self):
        if not BACKUP_PATH.exists():
            QMessageBox.warning(self, "No Backup", "Nothing to revert to — no backup found.")
            return
        try:
            # 1. Restore original config
            subprocess.run(["mv", str(BACKUP_PATH), str(CONFIG_PATH)])

            # 2. Get previous wallpaper, scheme, mode
            old_wall = ""
            with open(CONFIG_PATH) as f:
                old_wall = json.load(f).get("background", {}).get("wallpaperPath", "")

            old_mode, old_scheme = "dark", "scheme-tonal-spot"
            if THEME_PREV_BAK.exists():
                with open(THEME_PREV_BAK) as f:
                    prev = json.load(f)
                old_mode = prev.get("mode", old_mode)
                old_scheme = prev.get("scheme", old_scheme)
                THEME_PREV_BAK.unlink()
            if THEME_BACKUP.exists():
                THEME_BACKUP.unlink()

            # 3. Kill current wallpaper daemons
            subprocess.run(["pkill", "awww-daemon"], stderr=subprocess.DEVNULL)
            subprocess.run(["pkill", "mpvpaper"], stderr=subprocess.DEVNULL)

            # 4. Run matugen with old wallpaper (if exists and valid)
            if old_wall and Path(old_wall).exists():
                temp_img = None
                try:
                    if Path(old_wall).suffix.lower() in VIDEO_EXTS:
                        temp_img = get_image_for_matugen(old_wall)
                        src = temp_img
                    else:
                        src = old_wall
                    subprocess.run([
                        "matugen", "image", src,
                        "-t", old_scheme, "-m", old_mode,
                        "--source-color-index", "0",
                    ], check=True)
                finally:
                    cleanup_temp(temp_img)

                # 5. Restart wallpaper daemon for the old wallpaper
                ext = Path(old_wall).suffix.lower()
                if ext == ".gif":
                    subprocess.Popen(["awww-daemon"], stdout=subprocess.DEVNULL)
                    subprocess.run(["sleep", "1"])
                    subprocess.run(["awww", "img", old_wall])
                elif ext in VIDEO_EXTS:
                    try:
                        mon = subprocess.check_output(
                            "hyprctl monitors | grep 'Monitor' | awk '{print $2}' | head -n 1",
                            shell=True, text=True
                        ).strip() or "eDP-1"
                    except Exception:
                        mon = "eDP-1"
                    subprocess.Popen(["mpvpaper", "-o", "loop", mon, old_wall])
                else:  # static images
                    subprocess.Popen(["awww-daemon"], stdout=subprocess.DEVNULL)
                    subprocess.run(["sleep", "1"])
                    subprocess.run(["awww", "img", old_wall])
            elif old_wall:
                QMessageBox.warning(self, "Revert", f"Previous wallpaper not found:\n{old_wall}")

            # 6. Reload shell
            subprocess.run(["hyprctl", "dispatch", "exec", "quickshell --reload"])

            # 7. Update UI to reflect restored wallpaper
            if old_wall and Path(old_wall).exists():
                self.file_path = old_wall
                self._update_file_ui()
                self._update_preview()
                self._refresh_preview_colors()

            nice = f"{old_mode.title()} · {old_scheme.replace('scheme-','').replace('-',' ').title()}"
            self.status.set_info(f"Reverted to: {nice}")
            self._set_apply_buttons(True)
            log.info("Reverted to %s", nice)

        except Exception as e:
            log.exception("Revert failed")
            self.status.set_error(f"Revert failed: {e}")


# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = LiveWallApp()
    window.show()
    sys.exit(app.exec())