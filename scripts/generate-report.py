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
import json
import os
import re
import sys
from pathlib import Path
from datetime import datetime

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
    "medium": "#27ae60",
    "low": "#6b7280",
}

SEVERITY_TEXT_COLORS = {
    "critical": "#ffb4ab",
    "high": "#ffc687",
    "medium": "#8fe3b0",
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


def burn_markers_into_screenshot(screenshot_path, markers, output_path):
    """
    Burn numbered severity-colored circle markers directly onto a JPEG screenshot.
    """
    if not HAS_PILLOW:
        return False

    img = Image.open(screenshot_path).convert("RGB")
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

    img.save(output_path, "JPEG", quality=85)
    return True


# --- Finding Parser ---

def parse_findings(audit_path):
    """Parse audit.md to extract FAIL and PARTIAL findings.

    Supports two formats:
    1. Fenced: findings wrapped in triple-backtick code blocks
    2. Unfenced: FINDING: line followed by field lines, terminated by blank
       line, next heading (** or #), or EOF

    Also detects cluster membership from ### cluster headings.
    """
    with open(audit_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Build cluster map: list of (char_offset, cluster_slug) from ### headings
    cluster_map = []
    for m in re.finditer(r"^### ([\w-]+) cluster", content, re.MULTILINE):
        cluster_map.append((m.start(), m.group(1)))

    def cluster_at(pos):
        """Return cluster slug for a character position in content."""
        result = None
        for offset, slug in cluster_map:
            if offset <= pos:
                result = slug
            else:
                break
        return result

    findings = []

    # Strategy 1: fenced blocks  ```\nFINDING: FAIL\n...\n```
    fenced = list(re.finditer(
        r"```\s*\nFINDING:\s*(FAIL|PARTIAL)\s*\n(.*?)```",
        content,
        re.DOTALL,
    ))

    # Strategy 2: unfenced blocks
    if not fenced:
        fenced = list(re.finditer(
            r"^FINDING:\s*(FAIL|PARTIAL)\s*\n(.*?)(?=\n\n\*\*\d|^FINDING:|^## |^### |^# |\Z)",
            content,
            re.DOTALL | re.MULTILINE,
        ))

    for idx, m in enumerate(fenced, 1):
        verdict = m.group(1)
        block = m.group(2)
        finding = {"index": idx, "verdict": verdict}

        # Assign cluster from position in document
        cluster = cluster_at(m.start())
        if cluster:
            finding["cluster"] = cluster

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

    return findings


def parse_sources(plugin_path):
    """Parse citations/sources.md into a lookup dict.

    Returns dict keyed by "filename:finding_number" → first URL found.
    Example: "checkout-optimization.md:1" → "https://baymard.com/..."
    """
    sources_path = Path(plugin_path) / "citations" / "sources.md"
    if not sources_path.exists():
        return {}

    lookup = {}
    current_file = None
    with open(sources_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # Detect section headers like "## checkout-optimization.md"
            if line.startswith("## ") and line.endswith(".md"):
                current_file = line[3:].strip()
                continue
            # Parse table rows: | Finding | Description | Source | URL |
            if current_file and line.startswith("|") and "http" in line:
                cols = [c.strip() for c in line.split("|")]
                # cols[0] is empty (before first |), cols[1]=finding, ..., last non-empty has URL
                if len(cols) >= 5:
                    finding_num = cols[1].strip()
                    url = cols[-2].strip()  # URL is second-to-last (last is empty after trailing |)
                    if finding_num.isdigit() and url.startswith("http"):
                        key = f"{current_file}:{finding_num}"
                        if key not in lookup:  # keep first URL per finding
                            lookup[key] = url

    return lookup


def resolve_citation_url(reference_str, sources_lookup):
    """Resolve a finding's REFERENCE field to a citation URL.

    Reference format examples:
      "cta-design-and-placement.md — Finding 3"
      "cta-design-and-placement.md — Findings 6, 9, 18"
      "cta-design-and-placement.md — Finding 3; color-psychology.md — Finding 2"

    Returns the first matching URL, or None.
    """
    if not reference_str or not sources_lookup:
        return None

    # Split on semicolons for multi-file references
    parts = re.split(r";\s*", reference_str)
    for part in parts:
        match = re.match(r"([\w\-]+\.md)\s*[:\u2014\u2013\-]+\s*Findings?\s*([\d,\s]+)", part.strip())
        if match:
            filename = match.group(1)
            # Take the first finding number
            nums = re.findall(r"\d+", match.group(2))
            for num in nums:
                key = f"{filename}:{num}"
                if key in sources_lookup:
                    return sources_lookup[key]

    return None


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

def compute_marker_positions(markers_mapping, baton_data):
    """Compute pixel positions for markers on screenshots."""
    elements = baton_data.get("elements", [])
    screenshots = baton_data.get("screenshots", [])
    sections = baton_data.get("sections", [])
    viewport = baton_data.get("viewport", {})
    default_nat_w = int(viewport.get("width") or 1440)
    default_nat_h = int(viewport.get("height") or 900)

    slide_markers = {}

    for mapping in markers_mapping:
        finding_idx = mapping["finding_index"]
        elem_idx = mapping.get("baton_element_index")
        slide = mapping.get("slide", 0)
        severity = mapping.get("severity", "medium")

        if slide not in slide_markers:
            slide_markers[slide] = []

        if elem_idx is not None and elem_idx < len(elements):
            elem = elements[elem_idx]

            if isinstance(screenshots, list) and slide < len(screenshots):
                ss = screenshots[slide]
                scroll_y = ss.get("scrollY", 0) if isinstance(ss, dict) else 0
                nat_h = (
                    ss.get("naturalHeight")
                    or ss.get("height")
                    or default_nat_h
                ) if isinstance(ss, dict) else default_nat_h
                nat_w = (
                    ss.get("naturalWidth")
                    or ss.get("width")
                    or default_nat_w
                ) if isinstance(ss, dict) else default_nat_w
            else:
                scroll_y = 0
                nat_h = default_nat_h
                nat_w = default_nat_w

            abs_y = elem.get("y", 0)
            rel_y = abs_y - scroll_y
            rel_x = elem.get("x", 0)

            cx = rel_x + elem.get("width", 0) // 2
            cy = rel_y + elem.get("height", 0) // 2

            cx = max(30, min(cx, nat_w - 30))
            cy = max(30, min(cy, nat_h - 30))

            # Store both pixel coords AND percentage for CSS overlays
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
            if isinstance(sections, list) and slide < len(sections):
                sec = sections[slide]
                sec_h = sec.get("height", 400) if isinstance(sec, dict) else 400
                slide_markers[slide].append({
                    "number": finding_idx,
                    "x": 100,
                    "y": sec_h // 2,
                    "x_pct": 10,
                    "y_pct": 50,
                    "severity": severity,
                })

    return slide_markers


# --- HTML Helpers ---

def encode_image_base64(image_path):
    """Base64 encode an image file for data URI embedding."""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


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

SVG_SQUARE = '<svg viewBox="0 0 24 24" fill="currentColor"><rect x="7" y="7" width="10" height="10" rx="2"/></svg>'

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

    # --- Resolve citation URLs ---
    sources_lookup = parse_sources(plugin_path)
    for f in findings:
        url = resolve_citation_url(f.get("reference", ""), sources_lookup)
        if url:
            f["source_url"] = url

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
    slide_markers = compute_marker_positions(markers_mapping, baton)

    # Burn markers into screenshots (if Pillow available)
    annotated_dir = engagement_path / "annotated"
    annotated_dir.mkdir(exist_ok=True)

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
            burn_markers_into_screenshot(str(full_path), markers_for_slide, str(annotated_path))
            slide_base64.append(encode_image_base64(str(annotated_path)))
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
    generated_date = datetime.now().strftime("%Y-%m-%d")

    # --- Build thumbnails HTML ---
    thumb_html = ""
    for i, b64 in enumerate(slide_base64):
        active = " active" if i == 0 else ""
        thumb_aspect_ratio = slide_aspect_ratios[i] if i < len(slide_aspect_ratios) else default_slide_aspect_ratio
        thumb_html += f'''<div class="thumb{active}" onclick="setSlide({i})" style="--thumb-aspect-ratio:{thumb_aspect_ratio};">
      <img src="data:image/jpeg;base64,{b64}" alt="Section {i+1}" />
    </div>\n'''

    # --- Build clickable marker overlays HTML ---
    marker_overlays_html = ""
    for slide_idx, markers in slide_markers.items():
        for marker in markers:
            display = "flex" if slide_idx == 0 else "none"
            sev = marker.get("severity", "medium")
            marker_overlays_html += f'''<a href="#finding-{marker['number']}" class="marker-overlay" data-slide="{slide_idx}" data-severity="{sev}" data-finding="{marker['number']}" style="top:{marker['y_pct']:.1f}%;left:{marker['x_pct']:.1f}%;display:{display};"></a>\n'''

    # --- Build cluster tabs HTML ---
    CLUSTER_LABELS = {
        "visual-cta": "Visual & CTA",
        "trust-conversion": "Trust",
        "context-platform": "Context",
        "audience-journey": "Journey",
    }
    CLUSTER_COLORS = {
        "visual-cta": "#f59e0b",
        "trust-conversion": "#22c55e",
        "context-platform": "#8b5cf6",
        "audience-journey": "#3b82f6",
    }

    # Count findings per cluster
    cluster_counts = {}
    for f in findings:
        c = f.get("cluster", "unknown")
        cluster_counts[c] = cluster_counts.get(c, 0) + 1

    cluster_tabs_html = ""
    if len(cluster_counts) > 1:
        cluster_tabs_html = '<div class="cluster-tabs">\n'
        cluster_tabs_html += f'  <button class="cluster-tab active" data-cluster="all" onclick="filterCluster(\'all\')"><span class="cluster-dot" style="background:#999"></span> All <span class="cluster-count">{len(findings)}</span></button>\n'
        for slug in ["visual-cta", "trust-conversion", "context-platform", "audience-journey"]:
            if slug in cluster_counts:
                label = CLUSTER_LABELS.get(slug, slug)
                color = CLUSTER_COLORS.get(slug, "#999")
                count = cluster_counts[slug]
                cluster_tabs_html += f'  <button class="cluster-tab" data-cluster="{slug}" onclick="filterCluster(\'{slug}\')"><span class="cluster-dot" style="background:{color}"></span> {label} <span class="cluster-count">{count}</span></button>\n'
        cluster_tabs_html += '</div>\n'

    # --- Build finding cards HTML ---
    finding_cards = cluster_tabs_html
    for f in findings:
        idx = f["index"]
        sev = get_severity_class(f.get("priority"))
        sev_label = SEVERITY_LABELS.get(sev, "Medium")
        section_title = slug_to_title(f.get("section", "unknown"))
        source_type = (f.get("source") or "DOM").upper()
        tier = (f.get("tier") or "Bronze").lower()
        tier_label = tier.title()
        cluster_slug = f.get("cluster", "unknown")

        finding_cards += f'''
    <article id="finding-{idx}" class="finding-card" data-finding="{idx}" data-cluster="{cluster_slug}" data-severity="{sev}">
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
        <a href="{f.get('source_url', '#')}" class="view-source" {'target="_blank" rel="noopener noreferrer"' if f.get('source_url') else ''}>{('View Source' if f.get('source_url') else '')}</a>
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

    severity_total = max(total_findings, 1)
    severity_inline_stats = ""
    severity_inline_segments = ""
    severity_text_items = []
    for sev_name in ["critical", "high", "medium", "low"]:
        count = severity_counts[sev_name]
        if count > 0:
            width_pct = count / severity_total * 100
            severity_inline_stats += f'<span class="summary-severity-chip {sev_name}">{sev_name[0].upper()} {count}</span>'
            severity_inline_segments += f'<span class="summary-severity-fill {sev_name}" style="width:{width_pct:.1f}%"></span>'
            severity_text_items.append(
                f'<span class="summary-severity-item {sev_name}"><span class="summary-severity-dot {sev_name}"></span><span>{count} {sev_name.title()}</span></span>'
            )

    severity_text_html = '<span class="summary-severity-text">' + '<span class="summary-severity-separator">·</span>'.join(severity_text_items) + '</span>'

    # --- Ethics card ---
    if has_ethics_violations:
        ethics_main = "FAIL"
        ethics_main_class = "critical"
        ethics_note = "Dark pattern detected in findings"
        ethics_icon = SVG_X
    else:
        ethics_main = "PASS"
        ethics_main_class = "green"
        ethics_note = "No dark patterns detected"
        ethics_icon = SVG_CHECK

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
  --medium: #27ae60;
  --medium-text: #8fe3b0;
  --medium-bg: rgba(39,174,96,0.14);
  --medium-border: rgba(39,174,96,0.28);
  --low: #6b7280;
  --low-text: #9ca3af;
  --low-bg: rgba(107,114,128,0.1);
  --low-border: rgba(107,114,128,0.2);
  --success: #10b981;
  --success-text: #34d399;
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

a {{ color: var(--medium-text); text-decoration: none; }}
a:hover {{ text-decoration: underline; }}

.container {{
  max-width: 1600px;
  margin: 0 auto;
  padding: 2rem 3rem 2.5rem;
  position: relative;
  z-index: 1;
}}

header {{ margin-bottom: 1rem; }}

.header-content {{
  display: block;
}}

.header-main {{ max-width: none; }}

.eyebrow {{
  display: flex;
  align-items: center;
  margin-bottom: 0.45rem;
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
  font-size: clamp(3.35rem, 4.8vw, 4rem);
  font-weight: 800;
  letter-spacing: -0.05em;
  line-height: 0.96;
  margin-bottom: 0;
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 0.2em 0.28em;
}}
h1 .amber {{ color: var(--amber); }}

.subtitle {{ display: none; }}

.main-grid {{
  display: grid;
  grid-template-columns: 7fr 5fr;
  gap: 1rem;
  align-items: start;
}}

.evidence-canvas {{ position: sticky; top: 1rem; }}

.section-label {{
  font-size: 0.6875rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.25em;
  color: var(--text-dim);
  padding-bottom: 0.625rem;
  border-bottom: 1px solid var(--border-light);
  margin-bottom: 0.75rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}}

.nav-buttons {{ display: flex; gap: 0.75rem; }}
.nav-btn {{
  width: 2.125rem;
  height: 2.125rem;
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
  background: linear-gradient(to top, rgba(0,0,0,0.5), transparent 40%);
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
.marker-overlay:hover,
.marker-overlay.linked-hover {{
  transform: translate(-50%, -50%) scale(1.18);
}}
.marker-overlay[data-severity="critical"]:hover,
.marker-overlay[data-severity="critical"].linked-hover {{
  box-shadow: 0 0 0 2px rgba(147,0,10,0.5), 0 0 18px rgba(147,0,10,0.28);
}}
.marker-overlay[data-severity="high"]:hover,
.marker-overlay[data-severity="high"].linked-hover {{
  box-shadow: 0 0 0 2px rgba(255,159,0,0.48), 0 0 18px rgba(255,159,0,0.26);
}}
.marker-overlay[data-severity="medium"]:hover,
.marker-overlay[data-severity="medium"].linked-hover {{
  box-shadow: 0 0 0 2px rgba(39,174,96,0.46), 0 0 18px rgba(39,174,96,0.24);
}}
.marker-overlay[data-severity="low"]:hover,
.marker-overlay[data-severity="low"].linked-hover {{
  box-shadow: 0 0 0 2px rgba(107,114,128,0.4), 0 0 16px rgba(107,114,128,0.2);
}}
.marker-overlay[data-severity="critical"] {{ width: 3.5rem; height: 3.5rem; }}

.marker-tooltip {{
  position: absolute;
  z-index: 20;
  max-width: 16rem;
  padding: 0.45rem 0.6rem;
  border-radius: 0.5rem;
  border: 1px solid rgba(255,255,255,0.08);
  background: rgba(15,15,15,0.95);
  color: rgba(255,255,255,0.92);
  font-size: 0.75rem;
  line-height: 1.35;
  box-shadow: 0 10px 30px rgba(0,0,0,0.35);
  pointer-events: none;
  opacity: 0;
  transform: translateY(-50%);
  transition: opacity 0.16s ease;
}}

.marker-tooltip.visible {{
  opacity: 1;
}}

.thumbnails {{
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.75rem;
  margin-top: 0.75rem;
  margin-bottom: 0.75rem;
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
.metric-icon.green svg {{ color: var(--success); }}
.metric-label {{
  font-size: 0.625rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  color: var(--text-dim);
  margin-bottom: 0.25rem;
}}
.metric-value {{ font-size: 1.5rem; font-weight: 700; }}
.metric-value.green {{ color: var(--success); }}

.findings {{ display: flex; flex-direction: column; gap: 1.5rem; }}

.cluster-tabs {{
  display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 0.5rem;
}}
.cluster-tab {{
  display: flex; align-items: center; gap: 0.5rem;
  padding: 0.5rem 1rem; border-radius: 8px;
  background: transparent; border: 1px solid var(--border);
  color: var(--muted); font-size: 0.85rem; font-weight: 600;
  letter-spacing: 0.05em; text-transform: uppercase;
  cursor: pointer; transition: all 0.2s;
}}
.cluster-tab:hover {{ border-color: var(--text); color: var(--text); }}
.cluster-tab.active {{ border-color: currentColor; color: var(--text); background: rgba(255,255,255,0.05); }}
.cluster-dot {{ width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }}
.cluster-count {{
  background: rgba(255,255,255,0.1); padding: 0.1rem 0.45rem;
  border-radius: 999px; font-size: 0.75rem; font-weight: 700;
}}
.finding-card[data-hidden="true"] {{ display: none; }}

.finding-card {{
  background: var(--panel);
  backdrop-filter: blur(24px);
  padding: 2rem;
  border-radius: 1rem;
  border: 1px solid var(--border);
  position: relative;
  overflow: hidden;
  transition: background 0.2s, border-color 0.2s, box-shadow 0.2s, transform 0.2s;
}}
.finding-card:hover {{
  background: rgba(255,255,255,0.06);
  transform: translateY(-1px);
}}
.finding-card[data-severity="critical"]:hover {{
  box-shadow: 0 0 0 2px rgba(147,0,10,0.32), 0 0 30px rgba(147,0,10,0.26);
}}
.finding-card[data-severity="high"]:hover {{
  box-shadow: 0 0 0 2px rgba(255,159,0,0.28), 0 0 28px rgba(255,159,0,0.22);
}}
.finding-card[data-severity="medium"]:hover {{
  box-shadow: 0 0 0 2px rgba(127,140,155,0.32), 0 0 28px rgba(127,140,155,0.22);
}}
.finding-card[data-severity="low"]:hover {{
  box-shadow: 0 0 0 2px rgba(107,114,128,0.22), 0 0 24px rgba(107,114,128,0.18);
}}
.finding-card.highlight {{
  background: rgba(255,255,255,0.07);
}}
.finding-card.linked-hover {{
  background: rgba(255,255,255,0.06);
  border-color: rgba(255,159,0,0.22);
  box-shadow: 0 0 0 1px rgba(255,159,0,0.12);
}}
.finding-card.highlight[data-severity="critical"] {{
  border-color: rgba(147,0,10,0.55);
  box-shadow: 0 0 0 2px rgba(147,0,10,0.5), 0 0 28px rgba(147,0,10,0.26);
}}
.finding-card.highlight[data-severity="high"] {{
  border-color: rgba(255,159,0,0.5);
  box-shadow: 0 0 0 2px rgba(255,159,0,0.46), 0 0 28px rgba(255,159,0,0.24);
}}
.finding-card.highlight[data-severity="medium"] {{
  border-color: rgba(127,140,155,0.52);
  box-shadow: 0 0 0 2px rgba(127,140,155,0.46), 0 0 28px rgba(127,140,155,0.24);
}}
.finding-card.highlight[data-severity="low"] {{
  border-color: rgba(107,114,128,0.4);
  box-shadow: 0 0 0 2px rgba(107,114,128,0.36), 0 0 24px rgba(107,114,128,0.18);
}}

.finding-accent {{
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  opacity: 0.78;
}}
.finding-accent.critical {{ background: linear-gradient(to right, var(--critical), transparent); }}
.finding-accent.high {{ background: linear-gradient(to right, var(--high), transparent); }}
.finding-accent.medium {{ background: linear-gradient(to right, var(--medium), transparent); }}
.finding-accent.low {{ background: linear-gradient(to right, var(--low), transparent); }}

.finding-header {{
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
}}
.finding-header-left {{
  display: flex;
  align-items: center;
  gap: 1rem;
}}

.finding-number {{
  font-size: 3rem;
  font-weight: 300;
  letter-spacing: -0.05em;
  line-height: 1;
  color: var(--text);
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
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 1rem;
  color: var(--text);
}}

.finding-observation {{
  color: rgba(255,255,255,0.6);
  margin-bottom: 2rem;
  line-height: 1.7;
}}

.recommendation-box {{
  background: rgba(255,255,255,0.05);
  padding: 1.25rem;
  border-radius: 0.75rem;
  border: 1px solid rgba(255,255,255,0.05);
  margin-bottom: 1.5rem;
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
  align-items: center;
  gap: 0.75rem;
  font-size: 0.75rem;
  color: var(--text-dim);
}}
.why-matters svg {{ width: 1rem; height: 1rem; flex-shrink: 0; }}

.finding-footer {{
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border-light);
  display: flex;
  justify-content: space-between;
  align-items: center;
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
}}
.view-source {{
  font-size: 0.625rem;
  color: var(--text-muted);
  font-weight: 500;
  transition: color 0.2s;
}}
.view-source:hover {{ color: var(--text); }}

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
  margin: 0 0 1rem 0;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0.75rem;
}}

.summary-card {{
  background: #141414;
  backdrop-filter: blur(16px);
  min-height: 66px;
  padding: 0.75rem 0.9rem;
  border-radius: 0.875rem;
  border: 1px solid rgba(255,255,255,0.07);
  display: flex;
  flex-direction: row;
  justify-content: flex-start;
  align-items: center;
  gap: 0.5rem;
  min-width: 0;
}}

.summary-card-head {{
  display: none;
}}

.summary-inline {{
  width: 100%;
  display: flex;
  align-items: flex-start;
  justify-content: flex-start;
  gap: 0.3rem;
  flex-direction: column;
  min-width: 0;
}}

.summary-kpi-label {{
  font-size: 0.625rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: rgba(255,255,255,0.46);
  white-space: nowrap;
  flex-shrink: 0;
}}

.summary-kpi-value {{
  font-size: 1.15rem;
  font-weight: 700;
  line-height: 1;
  text-align: right;
}}
.summary-kpi-value.amber {{ color: var(--amber); }}
.summary-kpi-value.green {{ color: var(--success); }}
.summary-kpi-value.critical {{ color: var(--critical-text); }}

.summary-card--kpi .summary-inline {{
  align-items: flex-start;
}}

.summary-kpi-main {{
  font-size: 1rem;
  font-weight: 700;
  line-height: 1;
  white-space: nowrap;
}}
.summary-kpi-main.amber {{ color: var(--amber); }}
.summary-kpi-main.green {{ color: var(--success); }}
.summary-kpi-main.critical {{ color: var(--critical-text); }}

.summary-kpi-value-group {{
  display: inline-flex;
  align-items: center;
  justify-content: flex-start;
  gap: 0.35rem;
  flex-shrink: 0;
  white-space: nowrap;
}}

.summary-kpi-iconbox {{
  width: auto;
  height: auto;
  border-radius: 0;
  border: none;
  background: transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}}
.summary-kpi-iconbox svg {{
  width: 16px;
  height: 16px;
}}
.summary-kpi-iconbox.amber svg {{ color: rgba(255,159,0,0.72); }}
.summary-kpi-iconbox.green svg {{ color: var(--success-text); }}
.summary-kpi-iconbox.critical svg {{ color: var(--critical-text); }}
.summary-kpi-iconbox.neutral svg {{ color: rgba(255,255,255,0.5); }}

.summary-card--severity {{
  justify-content: flex-start;
}}

.summary-severity-inline {{
  min-width: 0;
  width: 100%;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-start;
  gap: 0.4rem;
  overflow: hidden;
}}

.summary-severity-text {{
  display: flex;
  align-items: center;
  gap: 0.35rem;
  flex-wrap: nowrap;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
}}

.summary-severity-item {{
  display: inline-flex;
  align-items: center;
  gap: 0.32rem;
  font-size: 0.82rem;
  font-weight: 700;
  white-space: nowrap;
}}
.summary-severity-item.critical {{ color: var(--critical-text); }}
.summary-severity-item.high {{ color: var(--high); }}
.summary-severity-item.medium {{ color: var(--medium); }}
.summary-severity-item.low {{ color: var(--low-text); }}

.summary-severity-dot {{
  width: 0.42rem;
  height: 0.42rem;
  border-radius: 999px;
  flex-shrink: 0;
}}
.summary-severity-dot.critical {{ background: var(--critical); }}
.summary-severity-dot.high {{ background: var(--high); }}
.summary-severity-dot.medium {{ background: var(--medium); }}
.summary-severity-dot.low {{ background: var(--low); }}

.summary-severity-separator {{
  color: rgba(255,255,255,0.32);
  font-size: 0.8rem;
  line-height: 1;
}}

.summary-label {{
  font-size: 0.625rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.2em;
  color: var(--text-dim);
  margin-bottom: 0.25rem;
}}
.summary-value {{ font-size: 1.5rem; font-weight: 700; }}
.summary-value.amber {{ color: var(--amber); }}
.summary-value.green {{ color: var(--success); }}
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
.summary-icon-circle.pass svg {{ color: var(--success); }}
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
  h1 {{ font-size: 2.25rem; }}
  .summary-section {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
}}

@media (max-width: 768px) {{
  .container {{ padding: 2rem 1rem; }}
  h1 {{ font-size: 2.5rem; }}
  .summary-section {{ grid-template-columns: 1fr; }}
  .thumbnails {{ grid-template-columns: repeat(2, 1fr); }}
}}

.report-footer {{
  margin-top: 1.25rem;
  padding-top: 0.875rem;
  border-top: 1px solid var(--border-light);
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  font-size: 0.75rem;
  color: var(--text-dim);
}}

.report-footer-left {{
  color: var(--text-muted);
  white-space: nowrap;
}}

.report-footer-right {{
  text-align: right;
}}

.report-footer-meta {{
  display: block;
  margin-top: 0.2rem;
  font-size: 0.6875rem;
  color: rgba(255,255,255,0.34);
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

      </div>
    </header>

    <section class="summary-section">
      <div class="summary-card summary-card--kpi">
        <div class="summary-inline">
          <span class="summary-kpi-label">Evidence Confidence</span>
          <span class="summary-kpi-value-group"><span class="summary-kpi-iconbox amber">{SVG_CHECK}</span><span class="summary-kpi-main amber">HIGH</span></span>
        </div>
      </div>

      <div class="summary-card summary-card--kpi">
        <div class="summary-inline">
          <span class="summary-kpi-label">Projected Lift</span>
          <span class="summary-kpi-value-group"><span class="summary-kpi-iconbox green">{SVG_TREND_UP}</span><span class="summary-kpi-main green">+{projected_lift:.0f}%</span></span>
        </div>
      </div>

      <div class="summary-card summary-card--severity">
        <div class="summary-inline">
          <span class="summary-kpi-label">Severity Distribution</span>
          <div class="summary-severity-inline"><span class="summary-kpi-iconbox neutral">{SVG_SQUARE}</span>{severity_text_html}</div>
        </div>
      </div>

      <div class="summary-card summary-card--kpi">
        <div class="summary-inline">
          <span class="summary-kpi-label">Ethics Check</span>
          <span class="summary-kpi-value-group"><span class="summary-kpi-iconbox {ethics_main_class}">{ethics_icon}</span><span class="summary-kpi-main {ethics_main_class}">{ethics_main}</span></span>
        </div>
      </div>
    </section>

    <div class="main-grid">

      <section class="evidence-canvas">
        <div class="section-label">
          <span>Primary Interface Evidence</span>
          <div class="nav-buttons">
            <button class="nav-btn" onclick="prevSlide()">{SVG_CHEVRON_LEFT}</button>
            <button class="nav-btn" onclick="nextSlide()">{SVG_CHEVRON_RIGHT}</button>
          </div>
        </div>

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

      </section>

      <section class="findings">
        <div class="section-label">Diagnostic Insights</div>
        {finding_cards}
      </section>

    </div>

    <footer class="report-footer">
      <div class="report-footer-left">CRO Conversion Psychology v4.5.1</div>
      <div class="report-footer-right">
        Generated {generated_date} · {escape_html(device.title())} viewport · {total_findings} findings · Engagement {escape_html(engagement_id)}
        <span class="report-footer-meta">Page Type {escape_html(page_type)} · Platform {escape_html(platform)} · Device {escape_html(device_label)} · Source Mode {escape_html(source_mode)} · Audit Date {escape_html(date_str)}</span>
      </div>
    </footer>

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
  var markerTooltip = document.createElement('div');
  markerTooltip.className = 'marker-tooltip';
  if (mainSlide) {{
    mainSlide.appendChild(markerTooltip);
  }}

  function getCardForFinding(findingId) {{
    return document.getElementById('finding-' + findingId);
  }}

  function getMarkersForFinding(findingId) {{
    return document.querySelectorAll('.marker-overlay[data-finding="' + findingId + '"]');
  }}

  function clearLinkedHover() {{
    findingCards.forEach(function(card) {{
      card.classList.remove('linked-hover');
    }});
    markers.forEach(function(marker) {{
      marker.classList.remove('linked-hover');
    }});
    markerTooltip.classList.remove('visible');
    markerTooltip.textContent = '';
  }}

  function showMarkerTooltip(marker, text) {{
    if (!mainSlide || !text) {{
      return;
    }}
    var slideRect = mainSlide.getBoundingClientRect();
    var markerRect = marker.getBoundingClientRect();
    markerTooltip.textContent = text;
    markerTooltip.style.left = '0px';
    markerTooltip.style.top = '0px';
    markerTooltip.classList.add('visible');

    var tooltipRect = markerTooltip.getBoundingClientRect();
    var placeLeft = markerRect.right - slideRect.left + tooltipRect.width + 16 > slideRect.width;
    var left = placeLeft
      ? markerRect.left - slideRect.left - tooltipRect.width - 10
      : markerRect.right - slideRect.left + 10;
    var top = markerRect.top - slideRect.top + (markerRect.height / 2);

    left = Math.max(8, Math.min(left, slideRect.width - tooltipRect.width - 8));
    markerTooltip.style.left = left + 'px';
    markerTooltip.style.top = top + 'px';
  }}

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
    marker.addEventListener('mouseenter', function() {{
      clearLinkedHover();
      var findingNum = this.getAttribute('data-finding');
      var targetCard = getCardForFinding(findingNum);
      if (targetCard) {{
        targetCard.classList.add('linked-hover');
        var title = targetCard.querySelector('.finding-title');
        showMarkerTooltip(this, title ? title.textContent.trim() : '');
      }}
    }});

    marker.addEventListener('mouseleave', function() {{
      clearLinkedHover();
    }});

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
    card.addEventListener('mouseenter', function() {{
      var findingId = card.id.replace('finding-', '');
      getMarkersForFinding(findingId).forEach(function(marker) {{
        marker.classList.add('linked-hover');
      }});
    }});

    card.addEventListener('mouseleave', function() {{
      var findingId = card.id.replace('finding-', '');
      getMarkersForFinding(findingId).forEach(function(marker) {{
        marker.classList.remove('linked-hover');
      }});
    }});

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

function filterCluster(slug) {{
  document.querySelectorAll('.cluster-tab').forEach(function(t) {{
    t.classList.toggle('active', t.getAttribute('data-cluster') === slug);
  }});
  document.querySelectorAll('.finding-card').forEach(function(c) {{
    if (slug === 'all') {{
      c.setAttribute('data-hidden', 'false');
    }} else {{
      c.setAttribute('data-hidden', c.getAttribute('data-cluster') !== slug ? 'true' : 'false');
    }}
  }});
}}
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
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

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
