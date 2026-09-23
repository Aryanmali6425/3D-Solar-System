"""
ui_manager.py
Dear ImGui overlay: top HUD, splash screen, help legend, and the click-to-inspect
info panel with tabs for Facts / Time Travel / Weather & Gravity / Destroy.

Uses `imgui` (pyimgui) with its GLFW backend. Callbacks are NOT auto-attached
(attach_callbacks=False) because main.py already owns the GLFW callbacks for
free-fly camera controls and picking -- see main.py's callback wrappers,
which forward events into this renderer and check `want_capture_mouse` /
`want_capture_keyboard` before treating a click as "scene" input.
"""

import imgui
from imgui.integrations.glfw import GlfwRenderer

ACCENT = (0.42, 0.62, 1.0)
ACCENT_HOVER = (0.55, 0.72, 1.0)
DANGER = (1.0, 0.35, 0.3)
DANGER_HOVER = (1.0, 0.48, 0.42)


class UIManager:
    def __init__(self, window):
        imgui.create_context()
        self.renderer = GlfwRenderer(window, attach_callbacks=False)
        self._apply_theme()

    # ------------------------------------------------------------------ #
    # Theme
    # ------------------------------------------------------------------ #
    def _apply_theme(self):
        style = imgui.get_style()
        style.window_rounding = 10.0
        style.frame_rounding = 6.0
        style.grab_rounding = 6.0
        style.child_rounding = 8.0
        style.window_border_size = 1.0
        style.frame_border_size = 0.0
        style.window_padding = (16, 14)
        style.item_spacing = (10, 10)

        c = style.colors
        c[imgui.COLOR_WINDOW_BACKGROUND] = (0.05, 0.06, 0.10, 0.82)
        c[imgui.COLOR_TITLE_BACKGROUND_ACTIVE] = (0.08, 0.10, 0.18, 0.95)
        c[imgui.COLOR_TITLE_BACKGROUND] = (0.08, 0.10, 0.18, 0.95)
        c[imgui.COLOR_HEADER] = (*ACCENT, 0.35)
        c[imgui.COLOR_HEADER_HOVERED] = (*ACCENT_HOVER, 0.5)
        c[imgui.COLOR_HEADER_ACTIVE] = (*ACCENT, 0.65)
        c[imgui.COLOR_BUTTON] = (0.16, 0.19, 0.30, 0.9)
        c[imgui.COLOR_BUTTON_HOVERED] = (*ACCENT_HOVER, 0.55)
        c[imgui.COLOR_BUTTON_ACTIVE] = (*ACCENT, 0.85)
        c[imgui.COLOR_FRAME_BACKGROUND] = (0.12, 0.14, 0.22, 0.85)
        c[imgui.COLOR_FRAME_BACKGROUND_HOVERED] = (0.16, 0.19, 0.30, 0.9)
        c[imgui.COLOR_FRAME_BACKGROUND_ACTIVE] = (0.18, 0.22, 0.34, 0.95)
        c[imgui.COLOR_SLIDER_GRAB] = ACCENT
        c[imgui.COLOR_SLIDER_GRAB_ACTIVE] = ACCENT_HOVER
        c[imgui.COLOR_CHECK_MARK] = ACCENT_HOVER
        c[imgui.COLOR_TAB] = (0.10, 0.12, 0.20, 0.9)
        c[imgui.COLOR_TAB_HOVERED] = (*ACCENT_HOVER, 0.6)
        c[imgui.COLOR_TAB_ACTIVE] = (*ACCENT, 0.75)
        c[imgui.COLOR_SEPARATOR] = (0.3, 0.34, 0.45, 0.5)
        c[imgui.COLOR_TEXT] = (0.92, 0.94, 0.98, 1.0)

    # ------------------------------------------------------------------ #
    # Frame lifecycle
    # ------------------------------------------------------------------ #
    def start_frame(self, dt):
        self.renderer.io.delta_time = max(dt, 1.0 / 240.0)
        self.renderer.process_inputs()
        imgui.new_frame()

    def end_frame(self):
        imgui.render()
        self.renderer.render(imgui.get_draw_data())

    def wants_mouse(self):
        return imgui.get_io().want_capture_mouse

    def wants_keyboard(self):
        return imgui.get_io().want_capture_keyboard

    def resize(self, width, height):
        self.renderer.io.display_size = (width, height)

    def shutdown(self):
        self.renderer.shutdown()

    # ------------------------------------------------------------------ #
    # Splash screen
    # ------------------------------------------------------------------ #
    def render_splash(self, screen_w, screen_h, alpha):
        imgui.set_next_window_position(0, 0)
        imgui.set_next_window_size(screen_w, screen_h)
        flags = (imgui.WINDOW_NO_TITLE_BAR | imgui.WINDOW_NO_RESIZE | imgui.WINDOW_NO_MOVE |
                 imgui.WINDOW_NO_SCROLLBAR | imgui.WINDOW_NO_INPUTS | imgui.WINDOW_NO_BACKGROUND)
        imgui.begin("##splash", flags=flags)
        imgui.push_style_color(imgui.COLOR_TEXT, 0.85, 0.90, 1.0, alpha)

        title = "SOLAR SYSTEM SIMULATOR"
        subtitle = "an interactive CGI experience"
        imgui.set_window_font_scale(2.4)
        tw, _ = imgui.calc_text_size(title)
        imgui.set_cursor_pos((screen_w / 2 - tw / 2, screen_h / 2 - 40))
        imgui.text(title)

        imgui.set_window_font_scale(1.1)
        sw, _ = imgui.calc_text_size(subtitle)
        imgui.set_cursor_pos((screen_w / 2 - sw / 2, screen_h / 2 + 10))
        imgui.text(subtitle)

        imgui.pop_style_color()
        imgui.end()

    # ------------------------------------------------------------------ #
    # Top HUD bar
    # ------------------------------------------------------------------ #
    def render_top_hud(self, fps, help_visible):
        imgui.set_next_window_position(16, 16)
        flags = imgui.WINDOW_NO_RESIZE | imgui.WINDOW_NO_MOVE | imgui.WINDOW_ALWAYS_AUTO_RESIZE
        imgui.begin("Solar System Simulator", flags=flags)
        imgui.text_colored("SOLAR SYSTEM SIMULATOR", *ACCENT, 1.0)
        imgui.text_disabled(f"{fps:.0f} FPS")
        imgui.separator()
        imgui.text("Click a planet to inspect it.")
        imgui.text("Press H to toggle the controls legend.")
        imgui.end()

        if help_visible:
            imgui.set_next_window_position(16, 130)
            imgui.begin("Controls", flags=flags)
            for line in [
                "WASD - move camera", "Mouse drag - look around", "Scroll - move faster/slower",
                "Left click on a planet - inspect", "R - reset gravity on selected planet",
                "ESC - deselect / close panel",
            ]:
                imgui.bullet_text(line)
            imgui.end()

    # ------------------------------------------------------------------ #
    # Info panel for the selected body
    # ------------------------------------------------------------------ #
    def render_info_panel(self, body, facts, screen_w, screen_h):
        """
        Returns an actions dict the caller (main.py) applies to the sim:
        {gravity_multiplier, rain_toggled, time_travel_years, destroy_clicked,
         rebuild_clicked, close_clicked}
        """
        actions = {
            "gravity_multiplier": body.gravity_multiplier,
            "rain_toggled": None,
            "time_travel_years": body.time_travel_years,
            "destroy_clicked": False,
            "rebuild_clicked": False,
            "close_clicked": False,
        }

        panel_w = 380
        imgui.set_next_window_position(screen_w - panel_w - 16, 16)
        imgui.set_next_window_size(panel_w, 0)
        imgui.begin(f"{body.name}##info", flags=imgui.WINDOW_NO_RESIZE | imgui.WINDOW_NO_COLLAPSE)

        imgui.text_colored(body.name.upper(), *ACCENT, 1.0)
        imgui.text_disabled(facts.get("type", ""))
        imgui.separator()

        if imgui.begin_tab_bar("info_tabs"):
            if imgui.begin_tab_item("Facts")[0]:
                imgui.text(f"Moons: {facts.get('moons', 0)}")
                imgui.text(f"Day length: {facts.get('day_length', 'N/A')}")
                imgui.text(f"Year length: {facts.get('year_length', 'N/A')}")
                imgui.text(f"Diameter: {facts.get('diameter_km', 'N/A')}")
                imgui.text(f"Distance from Sun: {facts.get('distance_from_sun', 'N/A')}")
                imgui.spacing()
                imgui.text_colored("Did you know?", *ACCENT, 1.0)
                for f in facts.get("fun_facts", []):
                    imgui.bullet_text(f)
                    imgui.spacing()
                imgui.end_tab_item()

            if imgui.begin_tab_item("Time Travel")[0]:
                imgui.text_wrapped(facts.get("future_note", ""))
                imgui.spacing()
                changed, val = imgui.slider_float(
                    "Years", body.time_travel_years, -100.0, 100.0, "%.0f yrs")
                if changed:
                    actions["time_travel_years"] = val
                imgui.text_disabled("Drag left for a 'past' preview, right for 'future'.")
                imgui.end_tab_item()

            if imgui.begin_tab_item("Weather & Gravity")[0]:
                changed, val = imgui.checkbox("Enable rain", body.rain_enabled)
                if changed:
                    actions["rain_toggled"] = val
                imgui.text_disabled("Stylized weather particles, not a climate model.")
                imgui.spacing()
                imgui.separator()
                imgui.text("Gravity multiplier")
                changed_g, val_g = imgui.slider_float(
                    "##gravity", body.gravity_multiplier, 0.1, 3.0, "%.2fx")
                if changed_g:
                    actions["gravity_multiplier"] = val_g
                imgui.text_disabled("< 1x: moons drift outward | > 1x: moons spiral inward")
                if imgui.button("Reset gravity"):
                    actions["gravity_multiplier"] = 1.0
                imgui.end_tab_item()

            if imgui.begin_tab_item("Destroy")[0]:
                imgui.text_wrapped(
                    "Trigger a full destruction sequence: shrink, detonate, "
                    "debris + shockwave, then ash cloud.")
                imgui.spacing()
                if not body.destroyed:
                    imgui.push_style_color(imgui.COLOR_BUTTON, *DANGER, 0.85)
                    imgui.push_style_color(imgui.COLOR_BUTTON_HOVERED, *DANGER_HOVER, 0.95)
                    if imgui.button("DESTROY PLANET", width=-1, height=40):
                        actions["destroy_clicked"] = True
                    imgui.pop_style_color(2)
                else:
                    imgui.text_colored("This body has been destroyed.", *DANGER, 1.0)
                    if imgui.button("Rebuild", width=-1, height=34):
                        actions["rebuild_clicked"] = True
                imgui.end_tab_item()

            imgui.end_tab_bar()

        imgui.spacing()
        if imgui.button("Close", width=-1):
            actions["close_clicked"] = True

        imgui.end()
        return actions
