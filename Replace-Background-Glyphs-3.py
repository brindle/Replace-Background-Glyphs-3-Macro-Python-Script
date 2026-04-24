# MenuTitle: Glyphs 3 Background Replacer
# -*- coding: utf-8 -*-
from GlyphsApp import Glyphs, Message, GSBackgroundLayer
# --------------------------------------------------------------
# SETTINGS
# --------------------------------------------------------------
SOURCE_GLYPH_NAME         = "uni00000"  # Name of source glyph
TARGET_LAYER_NAME         = "Regular"     # Name of layer to target
REPLACE_ALL_BACKGROUNDS   = False         # If False, applies only to selected glyphs. CAREFUL! True will replace ALL backgrounds in an ENTIRE font for target_layer.
DELETE_CURRENT_BACKGROUND = True          # Clear target background before replacing
REPLACE_ONLY_IF_EMPTY     = False         # Replace only if background is empty
# --------------------------------------------------------------
def safe_list(obj, attr):
    """Safely get iterable attribute as a list, or [] if missing."""
    try:
        val = getattr(obj, attr, None)
        if val is None:
            return []
        return list(val)
    except Exception:
        return []
def copy_background(source_layer, target_layer, clear_first=True, replace_only_if_empty=False):
    """Copy background paths and components from one layer to another."""
    try:
        src_bg = source_layer.background
        dst_bg = target_layer.background
        if replace_only_if_empty and safe_list(dst_bg, "paths"):
            # Skip if background already has content
            return
        if clear_first:
            dst_bg.clear()
        # Copy paths
        for path in safe_list(src_bg, "paths"):
            dst_bg.paths.append(path.copy())
        # Copy components
        for comp in safe_list(src_bg, "components"):
            dst_bg.components.append(comp.copy())
        # Copy background anchors (optional, optional safety)
        for anchor in safe_list(src_bg, "anchors"):
            try:
                dst_bg.anchors.append(anchor.copy())
            except Exception:
                pass
    except Exception as e:
        print(f"Error copying background: {e}")
def run():
    font = Glyphs.font
    if not font:
        Message("No font open!", "Error")
        return
    source_glyph = font.glyphs[SOURCE_GLYPH_NAME]
    if not source_glyph:
        Message(f"Source glyph '{SOURCE_GLYPH_NAME}' not found.", "Error")
        return
    master = None
    for m in font.masters:
        if m.name == TARGET_LAYER_NAME:
            master = m
            break
    if not master:
        Message(f"Target layer '{TARGET_LAYER_NAME}' not found.", "Error")
        return
    source_layer = source_glyph.layers[master.id]
    if not source_layer or not source_layer.background:
        Message(f"Source glyph '{SOURCE_GLYPH_NAME}' has no background content.", "Error")
        return
    if REPLACE_ALL_BACKGROUNDS:
        glyphs_to_process = list(font.glyphs)
    else:
        tab = font.currentTab
        if tab and tab.selectedLayers:
            glyphs_to_process = [l.parent for l in tab.selectedLayers if l.parent]
        else:
            glyphs_to_process = [l.parent for l in font.selectedLayers] if font.selectedLayers else []
        if not glyphs_to_process:
            Message("No target glyphs selected.", "Error")
            return
    font.disableUpdateInterface()
    replaced_count = 0
    try:
        for glyph in glyphs_to_process:
            if glyph.name == SOURCE_GLYPH_NAME:
                continue  # skip self
            target_layer = glyph.layers[master.id]
            if target_layer:
                copy_background(source_layer, target_layer, DELETE_CURRENT_BACKGROUND, REPLACE_ONLY_IF_EMPTY)
                replaced_count += 1
    finally:
        font.enableUpdateInterface()
    Message(f"Copied background from '{SOURCE_GLYPH_NAME}' to {replaced_count} glyph(s) on layer '{TARGET_LAYER_NAME}'.", "Done")
run()
