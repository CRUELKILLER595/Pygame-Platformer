
import threading

import pygame as p
import requests

from game.settings import WIDTH, HEIGHT


API_BASE_URL = "http://127.0.0.1:8000"


class AuthPopup:
    def __init__(self):
        self.visible = False
        self.mode = "login"
        self.active_field = "email"

        self.fields = {
            "display_name": "",
            "email": "",
            "password": "",
        }

        self.message = ""
        self.message_color = (230, 100, 100)
        self.busy = False
        self.user = None

        self.title_font = p.font.SysFont("Arial", 30, bold=True)
        self.font = p.font.SysFont("Arial", 21)
        self.small_font = p.font.SysFont("Arial", 16)

        self.panel = p.Rect(0, 0, 520, 510)
        self.panel.center = (WIDTH // 2, HEIGHT // 2)

        self.close_rect = p.Rect(
            self.panel.right - 46,
            self.panel.y + 12,
            34,
            34,
        )

        self.field_rects = {}
        self.submit_rect = p.Rect(0, 0, 280, 48)
        self.switch_rect = p.Rect(0, 0, 360, 36)
        self.layout_fields()

    def layout_fields(self):
        """Position fields and buttons for the current mode."""
        center_x = self.panel.centerx
        field_width = 400
        field_height = 46

        if self.mode == "signup":
            positions = {
                "display_name": self.panel.y + 130,
                "email": self.panel.y + 208,
                "password": self.panel.y + 286,
            }
            status_y = self.panel.y + 338
            submit_y = self.panel.y + 365
        else:
            positions = {
                "email": self.panel.y + 170,
                "password": self.panel.y + 248,
            }
            status_y = self.panel.y + 300
            submit_y = self.panel.y + 328

        for name, y in positions.items():
            self.field_rects[name] = p.Rect(
                center_x - field_width // 2,
                y,
                field_width,
                field_height,
            )

        self.status_y = status_y
        self.submit_rect.center = (
            center_x,
            submit_y + self.submit_rect.height // 2,
        )
        self.switch_rect.center = (
            center_x,
            self.panel.y + 445,
        )

    def show(self):
        self.visible = True
        self.message = ""
        self.active_field = (
            "display_name" if self.mode == "signup" else "email"
        )
        self.layout_fields()
        p.key.start_text_input()

    def close(self):
        self.visible = False
        p.key.stop_text_input()

    def switch_mode(self):
        self.mode = "signup" if self.mode == "login" else "login"
        self.message = ""
        self.active_field = (
            "display_name" if self.mode == "signup" else "email"
        )
        self.layout_fields()

    def handle_event(self, event):
        """Handle input only while the popup is open."""
        if not self.visible:
            return False

        if event.type == p.KEYDOWN:
            if event.key == p.K_ESCAPE:
                self.close()
                return True

            if event.key == p.K_TAB:
                available = (
                    ["display_name", "email", "password"]
                    if self.mode == "signup"
                    else ["email", "password"]
                )
                index = available.index(self.active_field)
                self.active_field = available[
                    (index + 1) % len(available)
                ]
                return True

            if event.key == p.K_RETURN:
                self.submit()
                return True

            if (
                event.key == p.K_BACKSPACE
                and self.active_field in self.fields
            ):
                self.fields[self.active_field] = (
                    self.fields[self.active_field][:-1]
                )
                return True

        if event.type == p.TEXTINPUT:
            if self.active_field in self.fields:
                limits = {
                    "display_name": 40,
                    "email": 254,
                    "password": 128,
                }
                name = self.active_field
                current = self.fields[name]
                remaining = limits[name] - len(current)

                if remaining > 0:
                    self.fields[name] += event.text[:remaining]
            return True

        if event.type == p.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos

            if self.close_rect.collidepoint(mouse_pos):
                self.close()
                return True

            if self.switch_rect.collidepoint(mouse_pos):
                self.switch_mode()
                return True

            if self.submit_rect.collidepoint(mouse_pos):
                self.submit()
                return True

            for name, rect in self.field_rects.items():
                if rect.collidepoint(mouse_pos):
                    self.active_field = name
                    return True

            # Clicking elsewhere must not click menu buttons underneath.
            return True

        # Consume other events while the modal is visible.
        return True

    def submit(self):
        if self.busy:
            return

        email = self.fields["email"].strip()
        password = self.fields["password"]

        if self.mode == "signup" and not self.fields[
            "display_name"
        ].strip():
            self.message = "Enter a display name."
            self.message_color = (255, 170, 100)
            return

        if not email or not password:
            self.message = "Enter your email and password."
            self.message_color = (255, 170, 100)
            return

        payload = {
            "email": email,
            "password": password,
        }

        if self.mode == "signup":
            payload["display_name"] = self.fields[
                "display_name"
            ].strip()

        self.busy = True
        self.message = "Connecting to PixelBound..."
        self.message_color = (210, 220, 240)

        threading.Thread(
            target=self.send_request,
            args=(self.mode, payload),
            daemon=True,
        ).start()

    def send_request(self, mode, payload):
        """Contact the existing FastAPI authentication endpoints."""
        try:
            response = requests.post(
                f"{API_BASE_URL}/auth/{mode}",
                json=payload,
                timeout=15,
            )

            try:
                data = response.json()
            except ValueError:
                data = {}

            if response.ok:
                self.user = data
                name = data.get("display_name", data.get("email", "Player"))
                self.message = f"Welcome, {name}!"
                self.message_color = (100, 230, 150)
            else:
                detail = data.get(
                    "detail",
                    data.get("message", "Authentication failed."),
                )
                self.message = str(detail)
                self.message_color = (255, 120, 120)

        except requests.RequestException:
            self.message = (
                "Cannot reach the server. Is FastAPI running?"
            )
            self.message_color = (255, 120, 120)

        finally:
            self.busy = False

    def draw(self, screen):
        if not self.visible:
            return

        # Darken the menu behind the popup.
        overlay = p.Surface(screen.get_size(), p.SRCALPHA)
        overlay.fill((0, 0, 0, 185))
        screen.blit(overlay, (0, 0))

        # Popup panel and border.
        p.draw.rect(
            screen,
            (28, 34, 49),
            self.panel,
            border_radius=14,
        )
        p.draw.rect(
            screen,
            (120, 155, 190),
            self.panel,
            width=2,
            border_radius=14,
        )

        title = (
            "CREATE ACCOUNT"
            if self.mode == "signup"
            else "WELCOME BACK"
        )
        title_surface = self.title_font.render(
            title, True, (245, 245, 255)
        )
        screen.blit(
            title_surface,
            title_surface.get_rect(
                center=(self.panel.centerx, self.panel.y + 49)
            ),
        )

        # Close button.
        p.draw.rect(
            screen,
            (145, 60, 65),
            self.close_rect,
            border_radius=7,
        )
        close_text = self.font.render("X", True, (255, 255, 255))
        screen.blit(
            close_text,
            close_text.get_rect(center=self.close_rect.center),
        )

        labels = {
            "display_name": "Display name",
            "email": "Email",
            "password": "Password",
        }

        for name, rect in self.field_rects.items():
            label = self.small_font.render(
                labels[name], True, (195, 205, 225)
            )
            screen.blit(label, (rect.x, rect.y - 23))

            active = name == self.active_field
            border_color = (
                (100, 205, 165)
                if active
                else (95, 110, 135)
            )

            p.draw.rect(
                screen,
                (42, 49, 66),
                rect,
                border_radius=7,
            )
            p.draw.rect(
                screen,
                border_color,
                rect,
                width=2,
                border_radius=7,
            )

            value = self.fields[name]

            if name == "password":
                value = "*" * len(value)

            text_surface = self.font.render(
                value, True, (245, 245, 250)
            )
            screen.blit(
                text_surface,
                (rect.x + 12, rect.y + 11),
            )

        # Feedback from the backend.
        if self.message:
            message_surface = self.small_font.render(
                self.message[:58],
                True,
                self.message_color,
            )
            screen.blit(
                message_surface,
                message_surface.get_rect(
                    center=(
                        self.panel.centerx,
                        self.status_y + 11,
                    )
                ),
            )

        button_text = (
            "PLEASE WAIT..."
            if self.busy
            else "CREATE ACCOUNT"
            if self.mode == "signup"
            else "LOGIN"
        )

        button_color = (
            (80, 90, 105)
            if self.busy
            else (40, 145, 100)
        )

        p.draw.rect(
            screen,
            button_color,
            self.submit_rect,
            border_radius=9,
        )
        submit_surface = self.font.render(
            button_text, True, (255, 255, 255)
        )
        screen.blit(
            submit_surface,
            submit_surface.get_rect(
                center=self.submit_rect.center
            ),
        )

        switch_text = (
            "Already registered? Click here to Login"
            if self.mode == "signup"
            else "New player? Click here to Sign Up"
        )
        switch_surface = self.small_font.render(
            switch_text, True, (190, 210, 240)
        )
        screen.blit(
            switch_surface,
            switch_surface.get_rect(
                center=self.switch_rect.center
            ),
        )
