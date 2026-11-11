
"""Scrollable asset palette for the independent PixelBound Editor."""

import math
import pygame as p


class Palette:
    HEADER_RESERVED = 112

    OUTER_PADDING = 8
    COLUMN_GAP = 8

    ROW_HEIGHT = 88
    THUMBNAIL_SIZE = 56

    SCROLLBAR_WIDTH = 12
    SCROLLBAR_GAP = 5
    MIN_THUMB_HEIGHT = 26

    def __init__(self, assets, x, y, width, category):

        self.assets = assets

        self.x = int(x)
        self.y = int(y)
        self.width = max(1, int(width))

        self.category = category

        # Scrolling
        self.scroll_row = 0

        # Editor-owned hit detection.
        self.item_rects = {}

        # Viewport geometry
        self.viewport_rect = p.Rect(0, 0, 0, 0)
        self.content_rect = p.Rect(0, 0, 0, 0)

        # Scrollbar geometry
        self.scrollbar_track_rect = p.Rect(0, 0, 0, 0)
        self.scrollbar_thumb_rect = p.Rect(0, 0, 0, 0)

        # Scroll calculations
        self.total_rows = 0
        self.visible_rows = 1
        self.max_scroll = 0

        # Scrollbar dragging
        self._dragging_scrollbar = False
        self._drag_offset_y = 0

        # Category tracking
        self._last_category = None

        self.font = p.font.SysFont("Arial", 11)

    # --------------------------------------------------
    # ASSET HELPERS
    # --------------------------------------------------

    def _all_assets(self):
        """Return all assets from the supplied collection."""

        if isinstance(self.assets, dict):
            values = list(self.assets.values())

        else:
            try:
                values = list(self.assets)
            except TypeError:
                values = []

        return [
            asset
            for asset in values
            if getattr(asset, "image", None) is not None
        ]

    def _category_assets(self):
        """Return assets belonging to the selected category."""

        category = str(
            self.category or ""
        ).strip().upper()

        assets = [
            asset
            for asset in self._all_assets()
            if str(
                getattr(asset, "category", "")
            ).strip().upper() == category
        ]

        return sorted(
            assets,
            key=lambda asset: str(
                getattr(
                    asset,
                    "name",
                    getattr(asset, "id", "Asset"),
                )
            ).lower(),
        )

    def _columns(self):
        """Determine the number of palette columns."""

        return 2 if self.width >= 190 else 1

    def _cell_width(self):
        """Calculate the width of an individual asset cell."""

        columns = self._columns()

        available_width = max(
            1,
            self.content_rect.width - 2 * self.OUTER_PADDING,
        )

        total_gaps = self.COLUMN_GAP * (columns - 1)

        return max(
            1,
            (available_width - total_gaps) // columns,
        )

    def _content_top(self):
        return self.y + self.HEADER_RESERVED

    @staticmethod
    def _thumbnail(image, max_size):
        """Scale a preview while preserving its aspect ratio."""

        source_w, source_h = image.get_size()

        if source_w <= 0 or source_h <= 0:
            return image

        scale = min(
            max_size / source_w,
            max_size / source_h,
        )

        target_size = (
            max(1, round(source_w * scale)),
            max(1, round(source_h * scale)),
        )

        if target_size == image.get_size():
            return image

        return p.transform.scale(
            image,
            target_size,
        )

    # --------------------------------------------------
    # SCROLLBAR
    # --------------------------------------------------

    def _update_scrollbar(self):
        """Calculate the scrollbar track and draggable thumb."""

        if self.max_scroll <= 0 or self.total_rows <= 0:

            self.scrollbar_track_rect = p.Rect(0, 0, 0, 0)
            self.scrollbar_thumb_rect = p.Rect(0, 0, 0, 0)

            self._dragging_scrollbar = False

            return

        track_x = (
            self.x
            + self.width
            - self.SCROLLBAR_WIDTH
        )

        track_width = max(
            1,
            self.SCROLLBAR_WIDTH - 3,
        )

        self.scrollbar_track_rect = p.Rect(
            track_x,
            self.content_rect.top,
            track_width,
            self.content_rect.height,
        )

        track_height = self.scrollbar_track_rect.height

        thumb_height = round(
            track_height
            * self.visible_rows
            / self.total_rows
        )

        thumb_height = max(
            self.MIN_THUMB_HEIGHT,
            thumb_height,
        )

        thumb_height = min(
            track_height,
            thumb_height,
        )

        travel = track_height - thumb_height

        if travel > 0:
            scroll_ratio = self.scroll_row / self.max_scroll
        else:
            scroll_ratio = 0

        thumb_y = (
            self.scrollbar_track_rect.top
            + round(travel * scroll_ratio)
        )

        self.scrollbar_thumb_rect = p.Rect(
            track_x,
            thumb_y,
            track_width,
            thumb_height,
        )

    def _set_scroll_from_mouse_y(self, mouse_y):
        """Update scrolling from the scrollbar's mouse position."""

        if self.max_scroll <= 0:
            self.scroll_row = 0
            return

        track = self.scrollbar_track_rect
        thumb = self.scrollbar_thumb_rect

        travel = track.height - thumb.height

        if travel <= 0:
            self.scroll_row = 0
            return

        target_thumb_y = mouse_y - self._drag_offset_y

        target_thumb_y = max(
            track.top,
            min(
                target_thumb_y,
                track.bottom - thumb.height,
            ),
        )

        ratio = (
            target_thumb_y - track.top
        ) / travel

        self.scroll_row = round(
            ratio * self.max_scroll
        )

    # --------------------------------------------------
    # DRAW PALETTE
    # --------------------------------------------------

    def draw_palette(self, screen):
        """Render the asset grid, thumbnails and scrollbar."""

        assets = self._category_assets()

        current_category = str(
            self.category or ""
        ).strip().upper()

        # Reset scrolling when the category changes.
        if current_category != self._last_category:

            self.scroll_row = 0

            self._last_category = current_category

            self._dragging_scrollbar = False

        content_top = self._content_top()

        height = max(
            0,
            screen.get_height() - content_top,
        )

        self.viewport_rect = p.Rect(
            self.x,
            content_top,
            self.width,
            height,
        )

        # Reserve space for the scrollbar.
        content_width = max(
            1,
            self.width
            - self.SCROLLBAR_WIDTH
            - self.SCROLLBAR_GAP,
        )

        self.content_rect = p.Rect(
            self.x,
            content_top,
            content_width,
            height,
        )

        # All selection geometry belongs to Palette.
        self.item_rects.clear()

        if height <= 0:
            return

        columns = self._columns()

        cell_width = self._cell_width()

        self.total_rows = (
            math.ceil(len(assets) / columns)
            if assets
            else 0
        )

        self.visible_rows = max(
            1,
            height // self.ROW_HEIGHT,
        )

        self.max_scroll = max(
            0,
            self.total_rows - self.visible_rows,
        )

        # Keep scroll position valid.
        self.scroll_row = max(
            0,
            min(
                self.scroll_row,
                self.max_scroll,
            ),
        )

        self._update_scrollbar()

        previous_clip = screen.get_clip()

        screen.set_clip(
            self.content_rect.clip(previous_clip)
        )

        try:

            # ------------------------------------------
            # ASSET GRID
            # ------------------------------------------

            for index, asset in enumerate(assets):

                row = index // columns
                col = index % columns

                visible_row = row - self.scroll_row

                if (
                    visible_row < 0
                    or visible_row >= self.visible_rows
                ):
                    continue

                cell_rect = p.Rect(
                    self.content_rect.x
                    + self.OUTER_PADDING
                    + col * (
                        cell_width + self.COLUMN_GAP
                    ),

                    content_top
                    + visible_row * self.ROW_HEIGHT,

                    cell_width,
                    self.ROW_HEIGHT - 4,
                )

                if not cell_rect.colliderect(
                    self.content_rect
                ):
                    continue

                # --------------------------------------
                # CELL BACKGROUND
                # --------------------------------------

                p.draw.rect(
                    screen,
                    (43, 48, 60),
                    cell_rect,
                    border_radius=5,
                )

                # --------------------------------------
                # THUMBNAIL
                # --------------------------------------

                thumb = self._thumbnail(
                    asset.image,
                    self.THUMBNAIL_SIZE,
                )

                thumb_rect = thumb.get_rect(
                    centerx=cell_rect.centerx,
                    top=cell_rect.top + 3,
                )

                screen.blit(
                    thumb,
                    thumb_rect,
                )

                # --------------------------------------
                # ASSET NAME
                # --------------------------------------

                label = str(
                    getattr(
                        asset,
                        "name",
                        getattr(asset, "id", "Asset"),
                    )
                )

                max_chars = max(
                    8,
                    (cell_width - 8) // 6,
                )

                if len(label) > max_chars:

                    label = (
                        label[:max_chars - 1]
                        + "…"
                    )

                label_surface = self.font.render(
                    label,
                    True,
                    (225, 229, 238),
                )

                label_rect = label_surface.get_rect(
                    centerx=cell_rect.centerx,
                    bottom=cell_rect.bottom - 3,
                )

                screen.blit(
                    label_surface,
                    label_rect,
                )

                # --------------------------------------
                # EDITOR-OWNED HIT DETECTION
                # --------------------------------------

                self.item_rects[id(asset)] = (
                    cell_rect.copy()
                )

        finally:

            # Always restore the original clipping region.
            screen.set_clip(previous_clip)

        # ----------------------------------------------
        # DRAW SCROLLBAR
        # ----------------------------------------------

        if self.max_scroll > 0:

            track = self.scrollbar_track_rect
            thumb = self.scrollbar_thumb_rect

            p.draw.rect(
                screen,
                (35, 39, 49),
                track,
                border_radius=5,
            )

            p.draw.rect(
                screen,
                (115, 132, 157),
                thumb,
                border_radius=5,
            )

            p.draw.rect(
                screen,
                (180, 191, 209),
                thumb,
                width=1,
                border_radius=5,
            )

    # --------------------------------------------------
    # ASSET SELECTION
    # --------------------------------------------------

    def get_clicked_asset(self, position):
        """Return the asset selected by the mouse position."""

        point = tuple(position)

        for asset in self._category_assets():

            rect = self.item_rects.get(
                id(asset)
            )

            if (
                rect is not None
                and rect.collidepoint(point)
            ):
                return asset

        return None

    # --------------------------------------------------
    # INPUT EVENTS
    # --------------------------------------------------

    def handle_event(self, event):
        """
        Handle scrolling, scrollbar dragging and track clicks.

        Returns True when the palette consumes the event.
        """

        # ----------------------------------------------
        # LEFT MOUSE BUTTON
        # ----------------------------------------------

        if (
            event.type == p.MOUSEBUTTONDOWN
            and event.button == 1
        ):

            # Drag the scrollbar thumb.
            if self.scrollbar_thumb_rect.collidepoint(
                event.pos
            ):

                self._dragging_scrollbar = True

                self._drag_offset_y = (
                    event.pos[1]
                    - self.scrollbar_thumb_rect.top
                )

                return True

            # Click the scrollbar track.
            if self.scrollbar_track_rect.collidepoint(
                event.pos
            ):

                self._dragging_scrollbar = True

                self._drag_offset_y = (
                    self.scrollbar_thumb_rect.height // 2
                )

                self._set_scroll_from_mouse_y(
                    event.pos[1]
                )

                return True

        # ----------------------------------------------
        # SCROLLBAR DRAG
        # ----------------------------------------------

        elif event.type == p.MOUSEMOTION:

            if self._dragging_scrollbar:

                self._set_scroll_from_mouse_y(
                    event.pos[1]
                )

                return True

        # ----------------------------------------------
        # RELEASE MOUSE BUTTON
        # ----------------------------------------------

        elif (
            event.type == p.MOUSEBUTTONUP
            and event.button == 1
        ):

            self._dragging_scrollbar = False

        # ----------------------------------------------
        # MODERN PYGAME MOUSE WHEEL
        # ----------------------------------------------

        elif event.type == p.MOUSEWHEEL:

            mouse_pos = p.mouse.get_pos()

            if self.viewport_rect.collidepoint(mouse_pos):

                self.scroll_row = max(
                    0,
                    min(
                        self.scroll_row - int(event.y),
                        self.max_scroll,
                    ),
                )

                return True

        # ----------------------------------------------
        # LEGACY PYGAME MOUSE WHEEL
        # ----------------------------------------------

        elif (
            event.type == p.MOUSEBUTTONDOWN
            and event.button in (4, 5)
        ):

            if self.viewport_rect.collidepoint(
                event.pos
            ):

                direction = (
                    1 if event.button == 5 else -1
                )

                self.scroll_row = max(
                    0,
                    min(
                        self.scroll_row + direction,
                        self.max_scroll,
                    ),
                )

                return True

        return False
