import time
from datetime import datetime
from typing import Optional

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

from kitty.fast_data_types import Screen, add_timer
from kitty.tab_bar import DrawData, ExtraData, TabBarData, as_rgb, draw_title

# Catppuccin Macchiato
BG      = as_rgb(0x24273a)
SURFACE = as_rgb(0x363a4f)
OVERLAY = as_rgb(0x494d64)
TEXT    = as_rgb(0xcad3f5)
BLUE    = as_rgb(0x8aadf4)
MAUVE   = as_rgb(0xc6a0f6)
TEAL    = as_rgb(0x8bd5ca)
YELLOW  = as_rgb(0xeed49f)

_timer_id: Optional[int] = None
_net_prev = None
_net_prev_time: float = 0.0


def _fmt_bytes(b: float) -> str:
    if b < 1024:
        return f"{b:.0f}B"
    if b < 1024 ** 2:
        return f"{b / 1024:.1f}K"
    return f"{b / 1024 ** 2:.1f}M"


def _net_speed():
    global _net_prev, _net_prev_time
    if not HAS_PSUTIL:
        return "─", "─"
    now = time.monotonic()
    cur = psutil.net_io_counters()
    if _net_prev is None or (now - _net_prev_time) < 0.5:
        _net_prev, _net_prev_time = cur, now
        return "─", "─"
    dt = now - _net_prev_time
    dl = (cur.bytes_recv - _net_prev.bytes_recv) / dt
    ul = (cur.bytes_sent - _net_prev.bytes_sent) / dt
    _net_prev, _net_prev_time = cur, now
    return _fmt_bytes(dl), _fmt_bytes(ul)


def _status_str() -> str:
    t = datetime.now().strftime("%H:%M")
    if not HAS_PSUTIL:
        return f"   {t} "
    cpu = psutil.cpu_percent(interval=None)
    mem = psutil.virtual_memory().percent
    bat = psutil.sensors_battery()
    bat_str = f"{bat.percent:.0f}%" if bat else "─"
    dl, ul = _net_speed()
    return (
        f"  󰍛 {cpu:.0f}%"
        f"   {mem:.0f}%"
        f"  󰓅 {dl}/s 󰕒 {ul}/s"
        f"  󰁹 {bat_str}"
        f"   {t} "
    )


def _redraw_tab_bar(*args) -> None:
    try:
        from kitty.boss import get_boss
        boss = get_boss()
        if boss is not None:
            for tm in boss.all_tab_managers:
                tm.mark_tab_bar_dirty()
    except Exception:
        pass


def draw_tab(
    draw_data: DrawData,
    screen: Screen,
    tab: TabBarData,
    before_first_tab: bool,
    max_tab_length: int,
    index: int,
    is_last: bool,
    extra_data: ExtraData,
) -> int:
    global _timer_id
    if _timer_id is None:
        _timer_id = add_timer(_redraw_tab_bar, 5.0, True)

    if before_first_tab:
        screen.cursor.bg = BG
        screen.draw(" ")

    if tab.is_active:
        screen.cursor.bg = MAUVE
        screen.cursor.fg = BG
    else:
        screen.cursor.bg = SURFACE
        screen.cursor.fg = TEXT

    screen.draw(f" {index} ")
    draw_title(draw_data, screen, tab, index, max_tab_length - 4)
    screen.draw(" ")

    if is_last:
        status = _status_str()
        screen.cursor.bg = BG
        screen.cursor.fg = TEXT
        remaining = screen.columns - screen.cursor.x
        padding = remaining - len(status)
        if padding > 0:
            screen.draw(" " * padding)
        screen.draw(status)

    end_x = screen.cursor.x
    screen.cursor.bg = BG
    screen.cursor.fg = TEXT
    return end_x
