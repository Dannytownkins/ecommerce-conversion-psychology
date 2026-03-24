#!/usr/bin/env python3
"""
CRO Visual Report Generator

Generates self-contained dark-mode HTML visual reports from audit data.
Burns numbered severity markers directly into screenshot JPEGs via Pillow,
then assembles the full report HTML matching components.html design system.

Usage:
    python3 generate-report.py \
        --engagement docs/cro/2026-03-21-a3f7b1c2 \
        --device laptop \
        --audit audit.md \
        --baton baton.json \
        --plugin-root /path/to/ecommerce-conversion-psychology \
        --markers markers.json

Arguments:
    --engagement    Path to engagement directory
    --device        Device name (mobile, laptop, desktop)
    --audit         Audit filename (e.g., audit.md, audit-mobile.md)
    --baton         Baton filename (e.g., baton.json, baton-mobile.json)
    --plugin-root   Path to plugin root directory
    --markers       Path to marker mapping JSON (from coordinator)
    --output        Output filename (optional, auto-generated if omitted)
"""

import argparse
import base64
import io
import json
import os
import re
import sys
import tempfile
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False
    print("WARNING: Pillow not installed. Markers will not be burned into screenshots.", file=sys.stderr)
    print("Install with: pip install Pillow", file=sys.stderr)


# --- Constants (matching components.html design tokens) ---

SEVERITY_COLORS = {
    "critical": "#93000a",
    "high": "#ff9f00",
    "medium": "#10b981",
    "low": "#6b7280",
}

SEVERITY_TEXT_COLORS = {
    "critical": "#ffb4ab",
    "high": "#ffc687",
    "medium": "#34d399",
    "low": "#9ca3af",
}

SEVERITY_LABELS = {
    "critical": "Critical",
    "high": "High",
    "medium": "Medium",
    "low": "Low",
}

MARKER_RADIUS = {
    "critical": 28,
    "high": 24,
    "medium": 24,
    "low": 22,
}


# --- Marker Burning (Pillow) ---

def hex_to_rgb(hex_color):
    """Convert hex color string to RGB tuple."""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def render_annotated_screenshot_bytes(screenshot_path, markers):
    """
    Render numbered severity-colored circle markers directly onto a JPEG screenshot
    and return the encoded bytes. Keeping this in memory avoids stale or partially
    overwritten intermediate files when multiple reports are generated close together.
    """
    if not HAS_PILLOW:
        return None

    with Image.open(screenshot_path) as source_img:
        img = source_img.convert("RGB")
    draw = ImageDraw.Draw(img)

    font = None
    font_small = None
    try:
        for font_path in [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
            "C:/Windows/Fonts/arialbd.ttf",
            "C:/Windows/Fonts/segoeui.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
        ]:
            if os.path.exists(font_path):
                font = ImageFont.truetype(font_path, 18)
                font_small = ImageFont.truetype(font_path, 14)
                break
    except Exception:
        pass

    if font is None:
        try:
            font = ImageFont.load_default()
            font_small = font
        except Exception:
            font = None
            font_small = None

    for marker in markers:
        cx = marker["x"]
        cy = marker["y"]
        severity = marker.get("severity", "medium")
        number = marker["number"]
        radius = MARKER_RADIUS.get(severity, 24)

        fill_color = hex_to_rgb(SEVERITY_COLORS.get(severity, "#6b7280"))

        draw.ellipse(
            [cx - radius - 2, cy - radius - 2, cx + radius + 2, cy + radius + 2],
            fill=(255, 255, 255),
        )
        draw.ellipse(
            [cx - radius, cy - radius, cx + radius, cy + radius],
            fill=fill_color,
        )

        text = str(number)
        if font:
            use_font = font_small if number >= 10 else font
            bbox = use_font.getbbox(text)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            tx = cx - tw // 2
            ty = cy - th // 2 - 1
            draw.text((tx, ty), text, fill=(255, 255, 255), font=use_font)
        else:
            draw.text((cx - 4, cy - 5), text, fill=(255, 255, 255))

    buffer = io.BytesIO()
    img.save(buffer, "JPEG", quality=85)
    return buffer.getvalue()


def write_bytes_atomic(output_path, data):
    """Write bytes atomically to avoid partially-read intermediates."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fd, temp_path = tempfile.mkstemp(
        prefix=f".{output_path.stem}-",
        suffix=output_path.suffix,
        dir=str(output_path.parent),
    )
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        os.replace(temp_path, output_path)
    except Exception:
        try:
            os.unlink(temp_path)
        except FileNotFoundError:
            pass
        raise


def write_text_atomic(output_path, text):
    """Write UTF-8 text atomically to avoid partially-written HTML reports."""
    write_bytes_atomic(output_path, text.encode("utf-8"))


# --- Finding Parser ---

def parse_findings(audit_path):
    """Parse audit.md to extract FAIL and PARTIAL findings.

    Supports two formats:
    1. Code-fenced (preferred): findings wrapped in ``` ... ``` blocks
    2. Bare markdown (fallback): findings starting with FINDING: or **FINDING:
       at line start, terminated by the next finding or section heading

    The code-fenced format is authoritative and specified in the audit assembly
    instructions. The bare fallback exists for resilience when the coordinator
    reformats findings during assembly.
    """
    with open(audit_path, "r", encoding="utf-8") as f:
        content = f.read()

    findings = []

    # Strategy 1: Code-fenced findings (preferred)
    blocks = re.findall(
        r"```\s*\nFINDING:\s*(FAIL|PARTIAL)\s*\n(.*?)```",
        content,
        re.DOTALL,
    )

    # Strategy 2: Bare markdown findings (fallback if no fenced blocks found)
    if not blocks:
        blocks = re.findall(
            r"(?:^|\n)\*{0,2}FINDING:\s*(FAIL|PARTIAL)\*{0,2}\s*\n(.*?)(?=\n\*{0,2}FINDING:|\n## |\n---|\Z)",
            content,
            re.DOTALL,
        )
        if blocks:
            print(f"WARNING: No code-fenced findings found. Fell back to bare markdown parsing ({len(blocks)} findings).", file=sys.stderr)
            print("  Fix: wrap each finding in ``` code fences per audit assembly instructions.", file=sys.stderr)

    for idx, (verdict, block) in enumerate(blocks, 1):
        finding = {"index": idx, "verdict": verdict}

        for field in ["SECTION", "ELEMENT", "SOURCE", "PRIORITY", "OBSERVATION", "RECOMMENDATION", "REFERENCE"]:
            match = re.search(rf"^{field}:\s*(.+)$", block, re.MULTILINE)
            if match:
                finding[field.lower()] = match.group(1).strip()

        why_match = re.search(r"\*\*Why this matters:\*\*\s*(.+?)(?=\n↳|\Z)", block, re.DOTALL)
        if why_match:
            finding["why_matters"] = why_match.group(1).strip()

        cite_match = re.search(r"↳\s*(.+?)(?:\[(\w+)\])?\s*$", block, re.MULTILINE)
        if cite_match:
            finding["citation"] = cite_match.group(1).strip()
            finding["tier"] = cite_match.group(2) if cite_match.group(2) else "Bronze"

        findings.append(finding)

    # Assign cluster from section headings (### cluster_name cluster)
    cluster_sections = re.finditer(r"#{2,3}\s+(\S+)\s+cluster", content)
    cluster_ranges = []
    for cm in cluster_sections:
        cluster_ranges.append((cm.start(), cm.group(1)))

    # For each finding, find which cluster section it belongs to by position
    if cluster_ranges:
        # Find positions of all finding blocks in content
        finding_positions = []
        for match in re.finditer(r"FINDING:\s*(?:FAIL|PARTIAL)", content):
            finding_positions.append(match.start())

        for i, f in enumerate(findings):
            if i < len(finding_positions):
                pos = finding_positions[i]
                assigned_cluster = cluster_ranges[0][1]  # default to first
                for cstart, cname in cluster_ranges:
                    if cstart < pos:
                        assigned_cluster = cname
                f["cluster"] = assigned_cluster
    else:
        for f in findings:
            f["cluster"] = "general"

    return findings


def parse_citation_urls(plugin_root):
    """Parse citations/sources.md to build a lookup table: (ref_file, finding_number) -> URL."""
    sources_path = os.path.join(plugin_root, "citations", "sources.md")
    if not os.path.exists(sources_path):
        return {}

    with open(sources_path, "r", encoding="utf-8") as f:
        content = f.read()

    url_map = {}
    current_ref_file = None

    for line in content.split("\n"):
        header_match = re.match(r"^##\s+(\S+\.md)", line)
        if header_match:
            current_ref_file = header_match.group(1)
            continue

        if current_ref_file and line.startswith("|"):
            cells = [c.strip() for c in line.split("|")]
            if len(cells) >= 5:
                finding_id = cells[1].strip()
                url = cells[4].strip()
                if url.startswith("http") and finding_id not in ("Finding", "---", "------"):
                    key = (current_ref_file, finding_id)
                    url_map[key] = url

    return url_map


def resolve_citation_url(finding, url_map):
    """Resolve a finding's citation to a source URL using the url_map."""
    ref = finding.get("reference", "")
    if not ref:
        return "#"

    ref_match = re.match(r"([a-z0-9_-]+\.md)[\s,;:\u2014-]+(?:Finding\s+)?(\d+)", ref, re.IGNORECASE)
    if ref_match:
        ref_file = ref_match.group(1)
        finding_num = ref_match.group(2)
        url = url_map.get((ref_file, finding_num))
        if url:
            return url

    citation = finding.get("citation", "")
    if citation:
        cite_ref_match = re.match(r"([a-z0-9_-]+\.md)[\s,;:\u2014-]+(?:Finding\s+)?(\d+)", citation, re.IGNORECASE)
        if cite_ref_match:
            ref_file = cite_ref_match.group(1)
            finding_num = cite_ref_match.group(2)
            url = url_map.get((ref_file, finding_num))
            if url:
                return url

    return "#"


def parse_pass_findings(audit_path):
    """Parse the What's Working Well section for PASS findings."""
    with open(audit_path, "r", encoding="utf-8") as f:
        content = f.read()

    passes = []
    well_match = re.search(r"## What's Working Well\s*\n(.*?)(?=\n## |\Z)", content, re.DOTALL)
    if well_match:
        section = well_match.group(1)
        for line in section.strip().split("\n"):
            line = line.strip()
            if line.startswith("- "):
                passes.append(line[2:])

    return passes


# --- Marker Position Calculator ---

def _auto_match_element(finding_element, elements, slide, screenshots):
    """Try to match a finding's ELEMENT CSS selector against baton elements.

    Returns the matched element dict or None.
    Uses substring matching: if the finding says 'button.product-form__submit',
    we look for baton elements whose selector or class contains 'product-form__submit'.
    """
    if not finding_element or not elements:
        return None

    # Get scroll range for this slide
    scroll_y = 0
    scroll_end = 99999
    if isinstance(screenshots, list) and slide < len(screenshots):
        ss = screenshots[slide]
        scroll_y = ss.get("scrollY", 0) if isinstance(ss, dict) else 0
        nat_h = ss.get("naturalHeight", 900) if isinstance(ss, dict) else 900
        scroll_end = scroll_y + nat_h

    # Normalize: strip tag prefix, extract class/id fragments
    search_terms = []
    # "button#ProductSubmitButton-xxx" -> ["productsubmitbutton", "button"]
    # "div.price--on-sale" -> ["price--on-sale", "price"]
    # "[class*=\"cart\"]" -> ["cart"]
    for part in re.split(r'[.#\[\]\s"*=]', finding_element):
        cleaned = part.strip().lower()
        if cleaned and len(cleaned) > 2 and cleaned not in ("class", "div", "span", "button", "input", "form", "img", "above", "fold", "area"):
            search_terms.append(cleaned)

    if not search_terms:
        return None

    for elem in elements:
        elem_y = elem.get("y", 0)
        # Only match elements within this slide's scroll range
        if elem_y < scroll_y or elem_y > scroll_end:
            continue

        elem_sel = (elem.get("selector", "") + " " + elem.get("class", "")).lower()
        elem_text = elem.get("text", "").lower()

        for term in search_terms:
            if term in elem_sel or term in elem_text:
                return elem

    return None


def compute_marker_positions(markers_mapping, baton_data, findings=None):
    """Compute pixel positions for markers on screenshots.

    If findings are provided and a marker has no baton_element_index,
    attempts to auto-match the finding's ELEMENT field against baton elements.
    Unmatched markers are spread vertically to avoid stacking.
    """
    elements = baton_data.get("elements", [])
    screenshots = baton_data.get("screenshots", [])
    sections = baton_data.get("sections", [])

    slide_markers = {}
    # Track unmatched count per slide to spread them vertically
    unmatched_count_per_slide = {}

    for mapping in markers_mapping:
        finding_idx = mapping["finding_index"]
        elem_idx = mapping.get("baton_element_index")
        slide = mapping.get("slide", 0)
        severity = mapping.get("severity", "medium")

        if slide not in slide_markers:
            slide_markers[slide] = []

        # Get screenshot dimensions for this slide
        if isinstance(screenshots, list) and slide < len(screenshots):
            ss = screenshots[slide]
            scroll_y = ss.get("scrollY", 0) if isinstance(ss, dict) else 0
            nat_h = ss.get("naturalHeight", 900) if isinstance(ss, dict) else 900
            nat_w = ss.get("naturalWidth", 1440) if isinstance(ss, dict) else 1440
        else:
            scroll_y = 0
            nat_h = 900
            nat_w = 1440

        resolved_elem = None

        # Strategy 1: Explicit baton_element_index
        if elem_idx is not None and elem_idx < len(elements):
            resolved_elem = elements[elem_idx]

        # Strategy 2: Auto-match by ELEMENT field from findings
        if resolved_elem is None and findings:
            # Find the finding by index
            for f in findings:
                if f.get("index") == finding_idx:
                    resolved_elem = _auto_match_element(
                        f.get("element", ""), elements, slide, screenshots
                    )
                    break

        if resolved_elem is not None:
            abs_y = resolved_elem.get("y", 0)
            rel_y = abs_y - scroll_y
            rel_x = resolved_elem.get("x", 0)

            cx = rel_x + resolved_elem.get("width", 0) // 2
            cy = rel_y + resolved_elem.get("height", 0) // 2

            cx = max(30, min(cx, nat_w - 30))
            cy = max(30, min(cy, nat_h - 30))

            x_pct = (cx / nat_w) * 100
            y_pct = (cy / nat_h) * 100

            slide_markers[slide].append({
                "number": finding_idx,
                "x": cx,
                "y": cy,
                "x_pct": x_pct,
                "y_pct": y_pct,
                "severity": severity,
            })
        else:
            # Fallback: spread unmatched markers vertically along left edge
            if slide not in unmatched_count_per_slide:
                unmatched_count_per_slide[slide] = 0
            n = unmatched_count_per_slide[slide]
            unmatched_count_per_slide[slide] += 1

            # Distribute from 15% to 85% of slide height, left column at 8%
            y_pct = 15 + (n * 10) % 70
            x_pct = 8

            sec_h = nat_h
            if isinstance(sections, list) and slide < len(sections):
                sec = sections[slide]
                sec_h = sec.get("height", nat_h) if isinstance(sec, dict) else nat_h

            slide_markers[slide].append({
                "number": finding_idx,
                "x": int(nat_w * x_pct / 100),
                "y": int(nat_h * y_pct / 100),
                "x_pct": x_pct,
                "y_pct": y_pct,
                "severity": severity,
            })

    return slide_markers


# --- HTML Helpers ---

def encode_image_base64(image_path):
    """Base64 encode an image file for data URI embedding."""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


def encode_bytes_base64(data):
    """Base64 encode raw image bytes for data URI embedding."""
    return base64.b64encode(data).decode("ascii")


def escape_html(text):
    """HTML-escape text content."""
    if not text:
        return ""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def slug_to_title(slug):
    """Convert a canonical slug to a display title."""
    return slug.replace("-", " ").title()


def aspect_ratio_value(width, height, fallback="16 / 9"):
    """Return a CSS aspect-ratio string from numeric dimensions."""
    try:
        width = int(width or 0)
        height = int(height or 0)
    except (TypeError, ValueError):
        return fallback

    if width > 0 and height > 0:
        return f"{width} / {height}"

    return fallback


def get_severity_class(priority):
    """Map priority string to severity class name."""
    return (priority or "medium").lower()


# --- SVG Icons ---

SVG_LIGHTBULB = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/></svg>'

SVG_INFO = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/></svg>'

SVG_CHART = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 20V10M12 20V4M6 20v-6"/></svg>'

SVG_TREND_UP = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M23 6l-9.5 9.5-5-5L1 18"/><path d="M17 6h6v6"/></svg>'

SVG_CHECK = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><path d="M22 4L12 14.01l-3-3"/></svg>'

SVG_X = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M15 9l-6 6M9 9l6 6"/></svg>'

SVG_CHEVRON_LEFT = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 18l-6-6 6-6"/></svg>'

SVG_CHEVRON_RIGHT = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg>'


# --- Device Frame SVGs ---

def get_device_frame_css(device):
    """Return CSS for device frame based on device type."""
    if device == "laptop":
        return """
/* Laptop Frame */
.device-frame {
  position: relative;
  padding: 1.5rem 1.5rem 0 1.5rem;
  background: linear-gradient(135deg, #2a2a2a 0%, #1a1a1a 100%);
  border-radius: 1.25rem 1.25rem 0 0;
  border: 1px solid rgba(255,255,255,0.1);
  border-bottom: none;
}
.device-frame::before {
  content: "";
  position: absolute;
  top: 0.625rem;
  left: 50%;
  transform: translateX(-50%);
  width: 0.5rem;
  height: 0.5rem;
  background: #333;
  border-radius: 50%;
  border: 1px solid #444;
}
.device-base {
  height: 1.25rem;
  background: linear-gradient(180deg, #2a2a2a 0%, #1f1f1f 100%);
  border-radius: 0 0 0.5rem 0.5rem;
  margin: 0 -0.5rem;
  position: relative;
}
.device-base::before {
  content: "";
  position: absolute;
  bottom: 0.25rem;
  left: 50%;
  transform: translateX(-50%);
  width: 6rem;
  height: 0.25rem;
  background: #333;
  border-radius: 0.125rem;
}
"""
    elif device == "mobile":
        return """
/* Mobile Frame */
.device-frame {
  position: relative;
  padding: 2.5rem 0.75rem 2rem 0.75rem;
  background: linear-gradient(135deg, #2a2a2a 0%, #1a1a1a 100%);
  border-radius: 2.5rem;
  border: 2px solid rgba(255,255,255,0.1);
  max-width: 400px;
  margin: 0 auto;
}
.device-frame::before {
  content: "";
  position: absolute;
  top: 1rem;
  left: 50%;
  transform: translateX(-50%);
  width: 5rem;
  height: 0.375rem;
  background: #333;
  border-radius: 0.25rem;
}
.device-frame::after {
  content: "";
  position: absolute;
  bottom: 0.625rem;
  left: 50%;
  transform: translateX(-50%);
  width: 2.5rem;
  height: 0.25rem;
  background: #333;
  border-radius: 0.125rem;
}
.device-base { display: none; }
"""
    else:  # desktop
        return """
/* Desktop Frame */
.device-frame {
  position: relative;
  padding: 1.25rem;
  background: linear-gradient(135deg, #2a2a2a 0%, #1a1a1a 100%);
  border-radius: 0.75rem 0.75rem 0 0;
  border: 1px solid rgba(255,255,255,0.1);
  border-bottom: none;
}
.device-frame::before {
  content: "";
  position: absolute;
  top: 0.5rem;
  left: 1rem;
  width: 0.5rem;
  height: 0.5rem;
  background: #ef4444;
  border-radius: 50%;
  box-shadow: 0.75rem 0 0 #eab308, 1.5rem 0 0 #22c55e;
}
.device-base {
  height: 3rem;
  background: linear-gradient(180deg, #2a2a2a 0%, #1f1f1f 100%);
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}
.device-base::before {
  content: "";
  width: 4rem;
  height: 0.25rem;
  background: #333;
  border-radius: 0.125rem;
}
.device-stand {
  width: 8rem;
  height: 4rem;
  background: linear-gradient(180deg, #1f1f1f 0%, #151515 100%);
  margin: 0 auto;
  clip-path: polygon(10% 0%, 90% 0%, 100% 100%, 0% 100%);
}
.device-stand-base {
  width: 12rem;
  height: 0.5rem;
  background: #1a1a1a;
  margin: 0 auto;
  border-radius: 0.25rem;
}
"""


# --- Main Report Generator ---

def generate_report(
    engagement_dir,
    device,
    audit_file,
    baton_file,
    plugin_root,
    markers_file,
    output_file=None,
):
    """Generate the complete visual report HTML."""

    engagement_path = Path(engagement_dir)
    plugin_path = Path(plugin_root)

    # --- Load data ---
    with open(engagement_path / baton_file, "r", encoding="utf-8") as f:
        baton = json.load(f)

    meta_path = engagement_path / "meta.json"
    meta = {}
    if meta_path.exists():
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)

    findings = parse_findings(engagement_path / audit_file)
    pass_findings = parse_pass_findings(engagement_path / audit_file)

    # Resolve citation URLs from sources.md
    url_map = parse_citation_urls(plugin_root)
    for f in findings:
        f["source_url"] = resolve_citation_url(f, url_map)

    markers_mapping = []
    if markers_file and os.path.exists(markers_file):
        with open(markers_file, "r", encoding="utf-8") as f:
            markers_mapping = json.load(f)

    # --- Process screenshots ---
    viewport = baton.get("viewport", {})
    default_slide_aspect_ratio = aspect_ratio_value(viewport.get("width"), viewport.get("height"))
    screenshots = baton.get("screenshots", [])
    screenshot_paths = []
    for ss in screenshots:
        if isinstance(ss, dict):
            screenshot_paths.append(ss.get("path", ss.get("file", "")))
        elif isinstance(ss, str):
            screenshot_paths.append(ss)

    # Compute marker positions
    slide_markers = compute_marker_positions(markers_mapping, baton, findings)

    # Burn markers into screenshots (if Pillow available)
    annotated_dir = engagement_path / "annotated" / device
    annotated_dir.mkdir(parents=True, exist_ok=True)

    slide_base64 = []
    slide_aspect_ratios = []
    for i, ss_path in enumerate(screenshot_paths):
        full_path = engagement_path / ss_path
        if not full_path.exists():
            continue

        screenshot_meta = screenshots[i] if i < len(screenshots) and isinstance(screenshots[i], dict) else {}
        slide_aspect_ratios.append(
            aspect_ratio_value(
                screenshot_meta.get("naturalWidth") or screenshot_meta.get("width") or viewport.get("width"),
                screenshot_meta.get("naturalHeight") or screenshot_meta.get("height") or viewport.get("height"),
                default_slide_aspect_ratio,
            )
        )

        markers_for_slide = slide_markers.get(i, [])
        annotated_path = annotated_dir / f"annotated-{i}.jpg"

        if HAS_PILLOW and markers_for_slide:
            annotated_bytes = render_annotated_screenshot_bytes(str(full_path), markers_for_slide)
            if annotated_bytes:
                write_bytes_atomic(annotated_path, annotated_bytes)
                slide_base64.append(encode_bytes_base64(annotated_bytes))
            else:
                slide_base64.append(encode_image_base64(str(full_path)))
        else:
            slide_base64.append(encode_image_base64(str(full_path)))

    if not slide_base64:
        print("ERROR: No screenshots found to encode.", file=sys.stderr)
        sys.exit(1)

    # --- Count severities ---
    severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for f in findings:
        sev = get_severity_class(f.get("priority"))
        if sev in severity_counts:
            severity_counts[sev] += 1

    total_findings = sum(severity_counts.values())

    # --- Compute metrics ---
    gold_silver = sum(1 for f in findings if f.get("tier", "").lower() in ("gold", "silver"))
    intent_reliability = round(gold_silver / max(total_findings, 1) * 100, 1)

    projected_lift = min(
        severity_counts["critical"] * 5
        + severity_counts["high"] * 3
        + severity_counts["medium"] * 1.5
        + severity_counts["low"] * 0.5,
        35,
    )

    # --- Ethics check ---
    has_ethics_violations = any(
        "ethics" in (f.get("reference") or "").lower() and f.get("priority", "").lower() == "critical"
        for f in findings
    )

    # --- Load font CSS ---
    font_path = plugin_path / "templates" / "font-embed.css"
    font_css = ""
    if font_path.exists():
        with open(font_path, "r", encoding="utf-8") as f:
            font_css = f.read()

    # --- Metadata ---
    viewport = baton.get("viewport", {})
    device_label = f"{device.title()} ({viewport.get('width', '?')}×{viewport.get('height', '?')})"
    date_str = meta.get("created", "")[:10] if meta.get("created") else "Unknown"
    engagement_id = meta.get("id", engagement_path.name)
    page_url = meta.get("page", {}).get("url", "Unknown URL")
    page_type = (meta.get("page", {}).get("type") or "Unknown").title()
    platform = (meta.get("platform") or "Unknown").title()
    source_mode = meta.get("source_mode", "Unknown")

    # --- Build thumbnails HTML ---
    thumb_html = ""
    for i, b64 in enumerate(slide_base64):
        active = " active" if i == 0 else ""
        thumb_aspect_ratio = slide_aspect_ratios[i] if i < len(slide_aspect_ratios) else default_slide_aspect_ratio
        thumb_html += f'''<div class="thumb{active}" onclick="setSlide({i})" style="--thumb-aspect-ratio:{thumb_aspect_ratio};">
      <img src="data:image/jpeg;base64,{b64}" alt="Section {i+1}" />
    </div>\n'''

    # --- Build clickable marker overlays HTML ---
    # Build finding cluster lookup
    finding_cluster_map = {f["index"]: f.get("cluster", "general") for f in findings}

    marker_overlays_html = ""
    for slide_idx, markers in slide_markers.items():
        for marker in markers:
            display = "flex" if slide_idx == 0 else "none"
            sev = marker.get("severity", "medium")
            cluster_id = finding_cluster_map.get(marker['number'], 'general')
            marker_overlays_html += f'''<a href="#finding-{marker['number']}" class="marker-overlay" data-slide="{slide_idx}" data-severity="{sev}" data-finding="{marker['number']}" data-cluster="{cluster_id}" style="top:{marker['y_pct']:.1f}%;left:{marker['x_pct']:.1f}%;display:{display};"></a>\n'''

    # --- Build cluster tabs HTML ---
    cluster_order = []
    cluster_counts_map = {}
    for f in findings:
        c = f.get("cluster", "general")
        if c not in cluster_counts_map:
            cluster_order.append(c)
            cluster_counts_map[c] = 0
        cluster_counts_map[c] += 1

    CLUSTER_DISPLAY = {
        "visual-cta": ("Visual & CTA", "#ff9f00"),
        "trust-conversion": ("Trust", "#10b981"),
        "context-platform": ("Context", "#6366f1"),
        "audience-journey": ("Audience", "#a78bfa"),
        "general": ("General", "#9ca3af"),
    }

    cluster_tabs_html = '<div class="cluster-tabs">\n'
    for i, cluster_id in enumerate(cluster_order):
        label, color = CLUSTER_DISPLAY.get(cluster_id, (cluster_id.replace("-", " ").title(), "#9ca3af"))
        active = " active" if i == 0 else ""
        count = cluster_counts_map[cluster_id]
        cluster_tabs_html += f'          <button class="cluster-tab{active}" data-tab="{cluster_id}" onclick="switchCluster(this)"><span class="tab-dot" style="background:{color}"></span>{escape_html(label)}<span class="tab-count">{count}</span></button>\n'
    cluster_tabs_html += '        </div>\n'

    default_cluster = cluster_order[0] if cluster_order else "general"

    # --- Build finding cards HTML ---
    finding_cards = ""
    for f in findings:
        idx = f["index"]
        sev = get_severity_class(f.get("priority"))
        sev_label = SEVERITY_LABELS.get(sev, "Medium")
        section_title = slug_to_title(f.get("section", "unknown"))
        source_type = (f.get("source") or "DOM").upper()
        tier = (f.get("tier") or "Bronze").lower()
        tier_label = tier.title()

        finding_cards += f'''
    <article id="finding-{idx}" class="finding-card" data-finding="{idx}" data-cluster="{f.get('cluster', 'general')}">
      <div class="finding-accent {sev}"></div>
      <div class="finding-header">
        <div class="finding-header-left">
          <span class="finding-number">{idx}</span>
          <span class="severity-badge {sev}">{escape_html(sev_label)}</span>
        </div>
        <span class="finding-source">{escape_html(source_type)}</span>
      </div>
      <h3 class="finding-title">{escape_html(section_title)}</h3>
      <p class="finding-observation">{escape_html(f.get('observation', ''))}</p>
      <div class="recommendation-box">
        <div class="recommendation-header {sev}">
          {SVG_LIGHTBULB}
          <span class="recommendation-label">Recommendation</span>
        </div>
        <p class="recommendation-text">{escape_html(f.get('recommendation', ''))}</p>
      </div>
      <div class="why-matters">
        {SVG_INFO}
        <span>{escape_html(f.get('why_matters', ''))}</span>
      </div>
      <div class="finding-footer">
        <div class="finding-footer-left">
          <span class="ref-id">{escape_html(f.get('reference', ''))}</span>
          <span class="tier-badge tier-badge--{tier}">{escape_html(tier_label)}</span>
        </div>
        <a href="{escape_html(f.get('source_url', '#'))}" class="view-source" target="_blank" rel="noopener noreferrer"{'  style="display:none"' if f.get('source_url', '#') == '#' else ''}>View Source</a>
      </div>
    </article>
'''

    # --- Severity distribution bars ---
    max_count = max(severity_counts.values()) if any(severity_counts.values()) else 1
    severity_bars = ""
    for sev_name in ["critical", "high", "medium", "low"]:
        count = severity_counts[sev_name]
        if count > 0:
            width_pct = count / max_count * 100
            severity_bars += f'''
      <div class="severity-bar">
        <div class="severity-bar-header">
          <span class="severity-bar-label">{sev_name.title()}</span>
          <span class="severity-bar-count {sev_name}">{count}</span>
        </div>
        <div class="severity-bar-track">
          <div class="severity-bar-fill {sev_name}" style="width:{width_pct:.0f}%"></div>
        </div>
      </div>
'''

    # --- Ethics card ---
    if has_ethics_violations:
        ethics_card = f'''
    <div class="summary-card" style="flex-direction: column; align-items: stretch;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
        <div>
          <div class="summary-label">Ethics Check</div>
          <div class="summary-value critical">FAIL</div>
        </div>
        <div class="summary-icon-circle fail">
          {SVG_X}
        </div>
      </div>
      <div class="ethics-violations">
        <div class="ethics-violation-item">
          <span class="ethics-violation-icon">&#10007;</span>
          <span>Dark pattern detected in findings</span>
        </div>
      </div>
    </div>
'''
    else:
        ethics_card = f'''
    <div class="summary-card">
      <div>
        <div class="summary-label">Ethics Check</div>
        <div class="summary-value green">PASS</div>
        <div class="summary-note">No dark patterns detected</div>
      </div>
      <div class="summary-icon-circle pass">
        {SVG_CHECK}
      </div>
    </div>
'''

    # --- Device frame CSS ---
    device_frame_css = get_device_frame_css(device)

    # --- Desktop-specific HTML ---
    device_stand_html = ""
    if device == "desktop":
        device_stand_html = '''<div class="device-stand"></div>
        <div class="device-stand-base"></div>'''

    # --- Slide sources JSON ---
    slide_sources_json = json.dumps([f"data:image/jpeg;base64,{b64}" for b64 in slide_base64])
    slide_aspect_ratios_json = json.dumps(slide_aspect_ratios)
    initial_slide_aspect_ratio = slide_aspect_ratios[0] if slide_aspect_ratios else default_slide_aspect_ratio

    # --- Assemble final HTML ---
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; font-src data:;">
  <title>CRO Visual Report — {escape_html(engagement_id)}</title>
  <style>{font_css}</style>
  <style>
:root {{
  --bg: #000000;
  --panel: rgba(255,255,255,0.04);
  --border: rgba(255,255,255,0.05);
  --border-light: rgba(255,255,255,0.1);
  --text: rgba(255,255,255,0.9);
  --text-muted: rgba(255,255,255,0.5);
  --text-dim: rgba(255,255,255,0.4);
  --text-faint: rgba(255,255,255,0.2);
  --amber: #ff9f00;
  --amber-light: #ffc687;
  --amber-glow: #ffb347;
  --critical: #93000a;
  --critical-text: #ffb4ab;
  --critical-bg: rgba(147,0,10,0.2);
  --critical-border: rgba(147,0,10,0.3);
  --high: #ff9f00;
  --high-bg: rgba(255,159,0,0.2);
  --high-border: rgba(255,159,0,0.3);
  --medium: #10b981;
  --medium-text: #34d399;
  --medium-bg: rgba(16,185,129,0.1);
  --medium-border: rgba(16,185,129,0.2);
  --low: #6b7280;
  --low-text: #9ca3af;
  --low-bg: rgba(107,114,128,0.1);
  --low-border: rgba(107,114,128,0.2);
  --tier-gold: #fbbf24;
  --tier-gold-bg: rgba(251,191,36,0.1);
  --tier-gold-border: rgba(251,191,36,0.25);
  --tier-silver: #9ca3af;
  --tier-silver-bg: rgba(156,163,175,0.1);
  --tier-silver-border: rgba(156,163,175,0.2);
  --tier-bronze: #cd7f32;
  --tier-bronze-bg: rgba(205,127,50,0.1);
  --tier-bronze-border: rgba(205,127,50,0.25);
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --font-mono: 'JetBrains Mono', 'SF Mono', 'Fira Code', 'Consolas', monospace;
}}

*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
html {{ scroll-behavior: smooth; }}

body {{
  font-family: var(--font-sans);
  background: var(--bg);
  color: var(--text);
  line-height: 1.6;
  min-height: 100vh;
  position: relative;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}}

body::before {{
  content: "";
  position: fixed;
  inset: 0;
  pointer-events: none;
  background-image:
    linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px);
  background-size: 40px 40px;
  z-index: 0;
}}

a {{ color: var(--medium-text); text-decoration: none; }}
a:hover {{ text-decoration: underline; }}

.container {{
  max-width: 1600px;
  margin: 0 auto;
  padding: 4rem;
  position: relative;
  z-index: 1;
}}

header {{ margin-bottom: 3rem; }}

.header-content {{
  display: grid;
  grid-template-columns: 3fr 2fr;
  gap: 2.5rem;
  align-items: start;
}}

.header-main {{ }}

.eyebrow {{
  display: flex;
  align-items: center;
  margin-bottom: 1rem;
}}
.eyebrow-line {{
  width: 4rem;
  height: 1px;
  background: rgba(255,255,255,0.2);
  margin-right: 1rem;
}}
.eyebrow-text {{
  color: var(--text-muted);
  font-size: 0.625rem;
  font-weight: 700;
  letter-spacing: 0.3em;
  text-transform: uppercase;
}}

h1 {{
  font-size: 3.5rem;
  font-weight: 800;
  letter-spacing: -0.04em;
  line-height: 1.15;
  margin-bottom: 1rem;
}}
h1 .amber {{ color: var(--amber); }}

.subtitle {{
  font-size: 1.125rem;
  color: var(--text-muted);
  font-weight: 400;
  max-width: 48rem;
}}

.metadata {{
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem 1.5rem;
  border-left: 1px solid var(--border-light);
  padding-left: 2rem;
  align-self: center;
}}
.meta-item label {{
  display: block;
  font-size: 0.625rem;
  font-weight: 700;
  color: var(--text-dim);
  text-transform: uppercase;
  letter-spacing: 0.15em;
  margin-bottom: 0.25rem;
}}
.meta-item span {{ font-size: 1rem; font-weight: 500; }}
.meta-item .highlight {{ color: var(--amber); }}

.main-grid {{
  display: grid;
  grid-template-columns: 3fr 2fr;
  grid-template-rows: auto 1fr;
  gap: 0 3rem;
  align-items: start;
}}

.evidence-canvas {{ position: sticky; top: 2rem; }}

.section-label {{
  font-size: 0.6875rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.25em;
  color: var(--text-dim);
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--border-light);
  margin-bottom: 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  min-height: 2.5rem;
  align-self: end;
}}

.nav-buttons {{ display: flex; gap: 0.75rem; }}
.nav-btn {{
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 50%;
  border: 1px solid var(--border-light);
  background: transparent;
  color: var(--text);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}}
.nav-btn:hover {{ background: rgba(255,255,255,0.05); }}

{device_frame_css}

.screenshot-wrapper {{
  position: relative;
}}

.screenshot-container {{
  position: relative;
  aspect-ratio: var(--slide-aspect-ratio, 16 / 9);
  border-radius: 0.25rem;
  overflow: hidden;
  background: #0a0a0a;
}}
.screenshot-container img {{
  width: 100%;
  height: 100%;
  object-fit: cover;
  opacity: 0.95;
}}
.screenshot-overlay {{
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, rgba(0,0,0,0.3), transparent 30%);
  pointer-events: none;
}}

/* Clickable Marker Overlays */
.marker-overlay {{
  position: absolute;
  width: 3rem;
  height: 3rem;
  border-radius: 50%;
  transform: translate(-50%, -50%);
  cursor: pointer;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s, box-shadow 0.2s;
  /* Transparent - the visual marker is burned into the image */
  background: transparent;
}}
.marker-overlay:hover {{
  transform: translate(-50%, -50%) scale(1.15);
  box-shadow: 0 0 0 3px rgba(255,255,255,0.3);
}}
.marker-overlay[data-severity="critical"] {{ width: 3.5rem; height: 3.5rem; }}

.thumbnails {{
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  margin-top: 1.5rem;
  margin-bottom: 1.5rem;
}}
.thumb {{
  aspect-ratio: var(--thumb-aspect-ratio, 16 / 10);
  border-radius: 0.5rem;
  overflow: hidden;
  border: 1px solid var(--border-light);
  opacity: 0.5;
  cursor: pointer;
  transition: all 0.2s;
}}
.thumb:hover {{ opacity: 1; border-color: rgba(255,255,255,0.3); }}
.thumb.active {{
  opacity: 1;
  outline: 2px solid rgba(255,255,255,0.5);
  outline-offset: 2px;
}}
.thumb img {{ width: 100%; height: 100%; object-fit: cover; }}

.metrics-bar {{
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}}
.metric-card {{
  background: var(--panel);
  backdrop-filter: blur(24px);
  padding: 1.25rem;
  border-radius: 1rem;
  border: 1px solid var(--border);
  display: flex;
  align-items: center;
  gap: 1rem;
}}
.metric-icon {{
  width: 3rem;
  height: 3rem;
  border-radius: 0.75rem;
  background: rgba(255,255,255,0.05);
  border: 1px solid var(--border-light);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}}
.metric-icon svg {{ width: 1.5rem; height: 1.5rem; }}
.metric-icon.amber svg {{ color: var(--amber); }}
.metric-icon.green svg {{ color: var(--medium); }}
.metric-label {{
  font-size: 0.625rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  color: var(--text-dim);
  margin-bottom: 0.25rem;
}}
.metric-value {{ font-size: 1.5rem; font-weight: 700; }}
.metric-value.green {{ color: var(--medium); }}

.findings {{ display: flex; flex-direction: column; gap: 1.5rem; }}

.finding-card {{
  background: var(--panel);
  backdrop-filter: blur(24px);
  padding: 2rem;
  border-radius: 1rem;
  border: 1px solid var(--border);
  position: relative;
  overflow: hidden;
  transition: background 0.2s, border-color 0.2s, box-shadow 0.2s;
}}
.finding-card:hover {{ background: rgba(255,255,255,0.06); }}
.finding-card.highlight {{
  border-color: var(--amber);
  box-shadow: 0 0 0 1px var(--amber), 0 0 20px rgba(255,159,0,0.2);
}}

.finding-accent {{
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  opacity: 0.5;
}}
.finding-accent.critical {{ background: linear-gradient(to right, var(--critical), transparent); }}
.finding-accent.high {{ background: linear-gradient(to right, var(--high), transparent); }}
.finding-accent.medium {{ background: linear-gradient(to right, var(--medium), transparent); }}
.finding-accent.low {{ background: linear-gradient(to right, var(--low), transparent); }}

.finding-header {{
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.25rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border-light);
}}
.finding-header-left {{
  display: flex;
  align-items: center;
  gap: 1rem;
}}

.finding-number {{
  font-size: 1.75rem;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  line-height: 1;
  color: var(--text-muted);
  min-width: 2rem;
  cursor: pointer;
  transition: color 0.2s;
}}
.finding-number:hover {{ color: var(--amber); }}

.severity-badge {{
  padding: 0.375rem 1rem;
  border-radius: 9999px;
  font-size: 0.625rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.15em;
}}
.severity-badge.critical {{
  background: var(--critical-bg);
  color: var(--critical-text);
  border: 1px solid var(--critical-border);
}}
.severity-badge.high {{
  background: var(--high-bg);
  color: var(--amber-glow);
  border: 1px solid var(--high-border);
}}
.severity-badge.medium {{
  background: var(--medium-bg);
  color: var(--medium-text);
  border: 1px solid var(--medium-border);
}}
.severity-badge.low {{
  background: var(--low-bg);
  color: var(--low-text);
  border: 1px solid var(--low-border);
}}

.finding-source {{
  font-size: 0.625rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  color: var(--text-dim);
}}

.finding-title {{
  font-size: 1.25rem;
  font-weight: 700;
  margin-bottom: 0.75rem;
  letter-spacing: -0.01em;
  color: var(--text);
}}

.finding-observation {{
  color: rgba(255,255,255,0.6);
  margin-bottom: 1.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid var(--border-light);
  line-height: 1.7;
  font-size: 0.9375rem;
}}

.recommendation-box {{
  background: rgba(255,255,255,0.04);
  padding: 1.25rem 1.5rem;
  border-radius: 0.75rem;
  border-left: 2px solid var(--amber);
  border-top: none;
  border-right: none;
  border-bottom: none;
  margin-bottom: 1.25rem;
}}
.recommendation-header {{
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}}
.recommendation-header svg {{ width: 1.25rem; height: 1.25rem; }}
.recommendation-header.critical svg {{ color: var(--critical-text); }}
.recommendation-header.high svg {{ color: var(--amber); }}
.recommendation-header.medium svg {{ color: var(--medium); }}
.recommendation-header.low svg {{ color: var(--low-text); }}
.finding-card:has(.recommendation-header.critical) .recommendation-box {{ border-left-color: var(--critical); }}
.finding-card:has(.recommendation-header.high) .recommendation-box {{ border-left-color: var(--amber); }}
.finding-card:has(.recommendation-header.medium) .recommendation-box {{ border-left-color: var(--medium); }}
.finding-card:has(.recommendation-header.low) .recommendation-box {{ border-left-color: var(--low-text); }}
.recommendation-label {{
  font-size: 0.6875rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  color: rgba(255,255,255,0.8);
}}
.recommendation-text {{
  color: rgba(255,255,255,0.7);
  font-style: italic;
}}

.why-matters {{
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  font-size: 0.8125rem;
  line-height: 1.6;
  padding: 0.75rem 0;
  color: var(--text-dim);
}}
.why-matters svg {{ width: 1rem; height: 1rem; flex-shrink: 0; margin-top: 0.15rem; opacity: 0.5; }}

.finding-footer {{
  margin-top: 1.25rem;
  padding-top: 1.25rem;
  border-top: 1px solid var(--border-light);
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}}
.finding-footer-left {{
  display: flex;
  align-items: center;
  gap: 0.75rem;
}}
.ref-id {{
  font-size: 0.5625rem;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  font-weight: 700;
  color: var(--text-faint);
  line-height: 1.4;
}}
.view-source {{
  font-size: 0.6875rem;
  color: var(--amber);
  font-weight: 600;
  transition: color 0.2s;
  text-decoration: none;
  opacity: 0.7;
}}
.view-source:hover {{ color: var(--amber); opacity: 1; }}

/* Cluster Tabs */
.cluster-tabs {{
  display: flex;
  gap: 0.25rem;
  margin-bottom: 1.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--border-light);
}}
.cluster-tab {{
  padding: 0.75rem 1.5rem;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-dim);
  cursor: pointer;
  border: 1px solid var(--border-light);
  border-radius: 0.5rem;
  background: transparent;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.625rem;
  white-space: nowrap;
}}
.cluster-tab:hover {{ color: var(--text); background: rgba(255,255,255,0.04); }}
.cluster-tab.active {{ color: var(--text); background: rgba(255,255,255,0.08); border-color: var(--amber); }}
.cluster-tab .tab-dot {{ width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }}
.cluster-tab .tab-count {{
  font-size: 0.625rem; font-weight: 600;
  background: rgba(255,255,255,0.08);
  padding: 0.125rem 0.5rem; border-radius: 9999px; color: var(--text-dim);
}}
.cluster-tab.active .tab-count {{ background: rgba(255,159,0,0.15); color: var(--amber); }}

.tier-badge {{
  display: inline-flex;
  align-items: center;
  padding: 0.125rem 0.5rem;
  border-radius: 9999px;
  font-size: 0.5625rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}}
.tier-badge--gold {{
  background: var(--tier-gold-bg);
  color: var(--tier-gold);
  border: 1px solid var(--tier-gold-border);
}}
.tier-badge--silver {{
  background: var(--tier-silver-bg);
  color: var(--tier-silver);
  border: 1px solid var(--tier-silver-border);
}}
.tier-badge--bronze {{
  background: var(--tier-bronze-bg);
  color: var(--tier-bronze);
  border: 1px solid var(--tier-bronze-border);
}}

.summary-section {{
  margin-top: 4rem;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
}}

.summary-card {{
  background: var(--panel);
  backdrop-filter: blur(24px);
  padding: 2rem;
  border-radius: 1rem;
  border: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  align-items: center;
}}

.summary-label {{
  font-size: 0.625rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.2em;
  color: var(--text-dim);
  margin-bottom: 0.5rem;
}}
.summary-value {{ font-size: 1.5rem; font-weight: 700; }}
.summary-value.amber {{ color: var(--amber); }}
.summary-value.green {{ color: var(--medium); }}
.summary-value.critical {{ color: var(--critical-text); }}
.summary-note {{
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-top: 0.5rem;
}}

.summary-icon {{ width: 3rem; height: 3rem; flex-shrink: 0; }}
.summary-icon svg {{ width: 100%; height: 100%; }}
.summary-icon.amber svg {{ color: rgba(255,159,0,0.3); }}

.summary-icon-circle {{
  width: 3.5rem;
  height: 3.5rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}}
.summary-icon-circle svg {{ width: 1.75rem; height: 1.75rem; }}
.summary-icon-circle.pass {{ background: rgba(16,185,129,0.1); }}
.summary-icon-circle.pass svg {{ color: var(--medium); }}
.summary-icon-circle.fail {{ background: rgba(147,0,10,0.1); }}
.summary-icon-circle.fail svg {{ color: var(--critical-text); }}

.severity-dist {{ display: flex; gap: 1rem; width: 100%; }}
.severity-bar {{ flex: 1; }}
.severity-bar-header {{
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 0.5rem;
}}
.severity-bar-label {{
  font-size: 0.625rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  color: rgba(255,255,255,0.8);
}}
.severity-bar-count {{ font-size: 0.75rem; font-weight: 700; }}
.severity-bar-count.critical {{ color: var(--critical-text); }}
.severity-bar-count.high {{ color: var(--high); }}
.severity-bar-count.medium {{ color: var(--medium); }}
.severity-bar-count.low {{ color: var(--low-text); }}
.severity-bar-track {{
  height: 0.25rem;
  background: rgba(255,255,255,0.05);
  border-radius: 9999px;
  overflow: hidden;
}}
.severity-bar-fill {{ height: 100%; border-radius: 9999px; }}
.severity-bar-fill.critical {{ background: var(--critical); }}
.severity-bar-fill.high {{ background: var(--high); }}
.severity-bar-fill.medium {{ background: var(--medium); }}
.severity-bar-fill.low {{ background: var(--low); }}

.ethics-violations {{ display: flex; flex-direction: column; gap: 0.5rem; }}
.ethics-violation-item {{
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  font-size: 0.8125rem;
  color: var(--critical-text);
  padding: 0.5rem 0.75rem;
  background: var(--critical-bg);
  border-radius: 0.5rem;
  border: 1px solid var(--critical-border);
}}
.ethics-violation-icon {{ font-weight: 700; flex-shrink: 0; }}

@media (max-width: 1200px) {{
  .main-grid {{ grid-template-columns: 1fr; }}
  .evidence-canvas {{ position: static; }}
  h1 {{ font-size: 3.5rem; }}
  .header-content {{ grid-template-columns: 1fr; }}
  .metadata {{ border-left: none; padding-left: 0; border-top: 1px solid var(--border-light); padding-top: 2rem; }}
}}

@media (max-width: 768px) {{
  .container {{ padding: 2rem 1rem; }}
  h1 {{ font-size: 2.5rem; }}
  .summary-section {{ grid-template-columns: 1fr; }}
  .metadata {{ grid-template-columns: repeat(2, 1fr); }}
  .thumbnails {{ grid-template-columns: repeat(2, 1fr); }}
}}
  </style>
</head>
<body>
  <div class="container">

    <header>
      <div class="header-content">
        <div class="header-main">
          <div class="eyebrow">
            <div class="eyebrow-line"></div>
            <span class="eyebrow-text">Strategic Intelligence Report</span>
          </div>
          <h1>CRO <span class="amber">Conversion</span> Audit</h1>
          <p class="subtitle">{escape_html(device.title())} viewport analysis — {escape_html(page_url)}</p>
        </div>

        <div class="metadata">
          <div class="meta-item"><label>Page Type</label><span>{escape_html(page_type)}</span></div>
          <div class="meta-item"><label>Platform</label><span>{escape_html(platform)}</span></div>
          <div class="meta-item"><label>Device</label><span>{escape_html(device_label)}</span></div>
          <div class="meta-item"><label>Source Mode</label><span>{escape_html(source_mode)}</span></div>
          <div class="meta-item"><label>Audit Date</label><span>{escape_html(date_str)}</span></div>
          <div class="meta-item"><label>Engagement</label><span class="highlight">{escape_html(engagement_id)}</span></div>
        </div>
      </div>
    </header>

    <div class="main-grid">

      <div class="section-label">
        <span>Primary Interface Evidence</span>
        <div class="nav-buttons">
          <button class="nav-btn" onclick="prevSlide()">{SVG_CHEVRON_LEFT}</button>
          <button class="nav-btn" onclick="nextSlide()">{SVG_CHEVRON_RIGHT}</button>
        </div>
      </div>
      <div class="section-label">Diagnostic Insights</div>

      <section class="evidence-canvas">
        <div class="screenshot-wrapper">
          <div class="device-frame">
            <div class="screenshot-container" id="mainSlide" style="--slide-aspect-ratio:{initial_slide_aspect_ratio};">
              <img id="mainImage" src="data:image/jpeg;base64,{slide_base64[0]}" alt="Screenshot" />
              <div class="screenshot-overlay"></div>
              {marker_overlays_html}
            </div>
          </div>
          <div class="device-base"></div>
          {device_stand_html}
        </div>

        <div class="thumbnails">
          {thumb_html}
        </div>

        <div class="metrics-bar">
          <div class="metric-card">
            <div class="metric-icon amber">
              {SVG_CHART}
            </div>
            <div>
              <div class="metric-label">Intent Reliability</div>
              <div class="metric-value">{intent_reliability}%</div>
            </div>
          </div>
          <div class="metric-card">
            <div class="metric-icon green">
              {SVG_TREND_UP}
            </div>
            <div>
              <div class="metric-label">Projected Lift</div>
              <div class="metric-value green">+{projected_lift:.0f}%</div>
            </div>
          </div>
        </div>
      </section>

      <section class="findings">
        {cluster_tabs_html}
        {finding_cards}
      </section>

    </div>

    <section class="summary-section">
      <div class="summary-card">
        <div>
          <div class="summary-label">Evidence Confidence</div>
          <div class="summary-value amber">HIGH</div>
          <div class="summary-note">URL + DOM dual-source analysis</div>
        </div>
        <div class="summary-icon amber">
          {SVG_CHECK}
        </div>
      </div>

      <div class="summary-card" style="flex-direction: column; align-items: stretch;">
        <div class="summary-label" style="margin-bottom: 1.25rem;">Severity Distribution</div>
        <div class="severity-dist">
          {severity_bars}
        </div>
      </div>

      {ethics_card}
    </section>

  </div>

  <script>
(function() {{
  'use strict';

  var slideSources = {slide_sources_json};
  var slideAspectRatios = {slide_aspect_ratios_json};
  var currentSlide = 0;
  var mainSlide = document.getElementById('mainSlide');
  var mainImage = document.getElementById('mainImage');
  var thumbs = document.querySelectorAll('.thumb');
  var markers = document.querySelectorAll('.marker-overlay');
  var findingCards = document.querySelectorAll('.finding-card');

  function updateMarkerVisibility(slideIndex) {{
    markers.forEach(function(m) {{
      var markerSlide = parseInt(m.getAttribute('data-slide') || '0', 10);
      m.style.display = markerSlide === slideIndex ? 'flex' : 'none';
    }});
  }}

  function setMainSlideAspectRatio(index) {{
    if (mainSlide && slideAspectRatios[index]) {{
      mainSlide.style.setProperty('--slide-aspect-ratio', slideAspectRatios[index]);
    }}
  }}

  window.setSlide = function(index) {{
    currentSlide = index;
    setMainSlideAspectRatio(index);
    if (mainImage && slideSources[index]) {{
      mainImage.src = slideSources[index];
    }}
    thumbs.forEach(function(thumb, i) {{
      thumb.classList.toggle('active', i === index);
    }});
    updateMarkerVisibility(index);
  }};

  window.prevSlide = function() {{
    window.setSlide(currentSlide === 0 ? slideSources.length - 1 : currentSlide - 1);
  }};

  window.nextSlide = function() {{
    window.setSlide(currentSlide === slideSources.length - 1 ? 0 : currentSlide + 1);
  }};

  // Marker click -> scroll to finding card
  markers.forEach(function(marker) {{
    marker.addEventListener('click', function(e) {{
      e.preventDefault();
      var findingNum = this.getAttribute('data-finding');
      var targetCard = document.getElementById('finding-' + findingNum);
      if (targetCard) {{
        targetCard.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
        highlightCard(targetCard);
      }}
    }});
  }});

  // Finding number click -> switch to correct slide
  findingCards.forEach(function(card) {{
    var num = card.querySelector('.finding-number');
    if (num) {{
      num.addEventListener('click', function() {{
        var findingId = card.id.replace('finding-', '');
        var targetMarker = document.querySelector('.marker-overlay[data-finding="' + findingId + '"]');
        if (targetMarker) {{
          var targetSlide = parseInt(targetMarker.getAttribute('data-slide') || '0', 10);
          window.setSlide(targetSlide);
        }}
        highlightCard(card);
      }});
    }}
  }});

  function highlightCard(card) {{
    findingCards.forEach(function(c) {{ c.classList.remove('highlight'); }});
    card.classList.add('highlight');
    setTimeout(function() {{ card.classList.remove('highlight'); }}, 2500);
  }}
}})();

  function switchCluster(btn) {{
    document.querySelectorAll('.cluster-tab').forEach(function(t) {{ t.classList.remove('active'); }});
    btn.classList.add('active');
    var cluster = btn.getAttribute('data-tab');
    document.querySelectorAll('.finding-card[data-cluster]').forEach(function(card) {{
      card.style.display = (card.getAttribute('data-cluster') === cluster) ? 'block' : 'none';
    }});
    document.querySelectorAll('.marker-overlay[data-cluster]').forEach(function(marker) {{
      marker.style.visibility = (marker.getAttribute('data-cluster') === cluster) ? 'visible' : 'hidden';
    }});
  }}

  document.addEventListener('DOMContentLoaded', function() {{
    var defaultTab = document.querySelector('.cluster-tab.active');
    if (defaultTab) switchCluster(defaultTab);
  }});
  </script>

</body>
</html>'''

    # --- Write output ---
    if not output_file:
        if device == "laptop":
            output_file = "visual-report.html"
        else:
            output_file = f"visual-report-{device}.html"

    output_path = engagement_path / output_file
    write_text_atomic(output_path, html)

    print(f"Report written to: {output_path}")
    print(f"  Device: {device_label}")
    print(f"  Findings: {total_findings}")
    print(f"  Screenshots: {len(slide_base64)}")
    print(f"  Markers burned: {sum(len(m) for m in slide_markers.values())}")
    print(f"  Click overlays: {sum(len(m) for m in slide_markers.values())}")
    print(f"  Pillow: {'yes' if HAS_PILLOW else 'no'}")


# --- CLI ---

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate CRO visual report")
    parser.add_argument("--engagement", required=True, help="Path to engagement directory")
    parser.add_argument("--device", required=True, choices=["mobile", "laptop", "desktop"], help="Device name")
    parser.add_argument("--audit", required=True, help="Audit filename (e.g., audit.md)")
    parser.add_argument("--baton", required=True, help="Baton filename (e.g., baton.json)")
    parser.add_argument("--plugin-root", required=True, help="Path to plugin root directory")
    parser.add_argument("--markers", default=None, help="Path to marker mapping JSON")
    parser.add_argument("--output", default=None, help="Output filename (auto-generated if omitted)")

    args = parser.parse_args()

    generate_report(
        engagement_dir=args.engagement,
        device=args.device,
        audit_file=args.audit,
        baton_file=args.baton,
        plugin_root=args.plugin_root,
        markers_file=args.markers,
        output_file=args.output,
    )
