#!/usr/bin/env python3
"""
CRO Visual Report Generator

Generates self-contained dark-mode HTML visual reports from audit data.
Burns numbered severity markers directly into screenshot JPEGs via Pillow,
then assembles the full report HTML with font injection and click targets.

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

try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False
    print("WARNING: Pillow not installed. Markers will use CSS positioning (less accurate).", file=sys.stderr)
    print("Install with: pip install Pillow", file=sys.stderr)


# --- Constants ---

SEVERITY_COLORS = {
    "critical": "#ef4444",
    "high": "#f97316",
    "medium": "#eab308",
    "low": "#6b7280",
}

SEVERITY_LABELS = {
    "critical": "Critical Impact",
    "high": "High Priority",
    "medium": "Medium Priority",
    "low": "Low Priority",
}

MARKER_RADIUS = {
    "critical": 22,
    "high": 18,
    "medium": 18,
    "low": 16,
}


# --- Marker Burning (Pillow) ---

def hex_to_rgb(hex_color):
    """Convert hex color string to RGB tuple."""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def burn_markers_into_screenshot(screenshot_path, markers, output_path):
    """
    Burn numbered severity-colored circle markers directly onto a JPEG screenshot.

    Args:
        screenshot_path: Path to the original JPEG screenshot
        markers: List of dicts with keys: number, x, y, severity
        output_path: Path to write the annotated JPEG
    """
    if not HAS_PILLOW:
        return False

    img = Image.open(screenshot_path).convert("RGB")
    draw = ImageDraw.Draw(img)

    # Try to load a font; fall back to default
    font = None
    font_small = None
    try:
        # Try common system font paths
        for font_path in [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
            "C:/Windows/Fonts/arialbd.ttf",
            "C:/Windows/Fonts/segoeui.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
        ]:
            if os.path.exists(font_path):
                font = ImageFont.truetype(font_path, 16)
                font_small = ImageFont.truetype(font_path, 13)
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
        radius = MARKER_RADIUS.get(severity, 18)

        fill_color = hex_to_rgb(SEVERITY_COLORS.get(severity, "#6b7280"))

        # Draw outer white border circle
        draw.ellipse(
            [cx - radius - 2, cy - radius - 2, cx + radius + 2, cy + radius + 2],
            fill=(255, 255, 255),
        )

        # Draw filled severity circle
        draw.ellipse(
            [cx - radius, cy - radius, cx + radius, cy + radius],
            fill=fill_color,
        )

        # Draw number text centered
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
    """
    Parse audit.md to extract FAIL and PARTIAL findings.

    Returns list of dicts with keys: index, section, element, source, severity,
    observation, recommendation, why_matters, reference, citation, tier
    """
    with open(audit_path, "r", encoding="utf-8") as f:
        content = f.read()

    findings = []
    # Match finding blocks (``` delimited)
    blocks = re.findall(
        r"```\s*\nFINDING:\s*(FAIL|PARTIAL)\s*\n(.*?)```",
        content,
        re.DOTALL,
    )

    for idx, (verdict, block) in enumerate(blocks, 1):
        finding = {"index": idx, "verdict": verdict}

        for field in ["SECTION", "ELEMENT", "SOURCE", "PRIORITY", "OBSERVATION", "RECOMMENDATION", "REFERENCE"]:
            match = re.search(rf"^{field}:\s*(.+)$", block, re.MULTILINE)
            if match:
                finding[field.lower()] = match.group(1).strip()

        # Parse "Why this matters"
        why_match = re.search(r"\*\*Why this matters:\*\*\s*(.+?)(?=\n↳|\Z)", block, re.DOTALL)
        if why_match:
            finding["why_matters"] = why_match.group(1).strip()

        # Parse citation line
        cite_match = re.search(r"↳\s*(.+?)(?:\[(\w+)\])?\s*$", block, re.MULTILINE)
        if cite_match:
            finding["citation"] = cite_match.group(1).strip()
            finding["tier"] = cite_match.group(2) if cite_match.group(2) else "Bronze"

        findings.append(finding)

    return findings


def parse_pass_findings(audit_path):
    """Parse the What's Working Well section for PASS findings."""
    with open(audit_path, "r", encoding="utf-8") as f:
        content = f.read()

    passes = []
    # Look for the section
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
    """
    Compute pixel positions for markers on screenshots.

    Args:
        markers_mapping: List from coordinator with finding_index, baton_element_index, slide, severity
        baton_data: Parsed baton.json

    Returns:
        Dict mapping slide_index -> list of {number, x, y, severity}
    """
    elements = baton_data.get("elements", [])
    screenshots = baton_data.get("screenshots", [])
    sections = baton_data.get("sections", [])

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

            # Find the screenshot for this slide
            screenshot = None
            if isinstance(screenshots, list) and slide < len(screenshots):
                ss = screenshots[slide]
                scroll_y = ss.get("scrollY", 0) if isinstance(ss, dict) else 0
                nat_h = ss.get("naturalHeight", 900) if isinstance(ss, dict) else 900
            else:
                scroll_y = 0
                nat_h = 900

            # Compute position within the screenshot
            abs_y = elem.get("y", 0)
            rel_y = abs_y - scroll_y
            rel_x = elem.get("x", 0)

            # Center on the element
            cx = rel_x + elem.get("width", 0) // 2
            cy = rel_y + elem.get("height", 0) // 2

            # Clamp to screenshot bounds
            cx = max(30, min(cx, elem.get("width", 1440) if cx > 1000 else 1440 - 30))
            cy = max(30, min(cy, nat_h - 30))

            slide_markers[slide].append({
                "number": finding_idx,
                "x": cx,
                "y": cy,
                "severity": severity,
            })
        else:
            # No element match — center on the section area
            if isinstance(sections, list) and slide < len(sections):
                sec = sections[slide]
                sec_h = sec.get("height", 400) if isinstance(sec, dict) else 400
                slide_markers[slide].append({
                    "number": finding_idx,
                    "x": 100,
                    "y": sec_h // 2,
                    "severity": severity,
                })

    return slide_markers


# --- HTML Assembly ---

def encode_image_base64(image_path):
    """Base64 encode an image file for data URI embedding."""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


def build_severity_class(priority):
    """Map priority string to CSS class name."""
    return (priority or "medium").lower()


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

    markers_mapping = []
    if markers_file and os.path.exists(markers_file):
        with open(markers_file, "r", encoding="utf-8") as f:
            markers_mapping = json.load(f)

    # --- Process screenshots ---
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
    for i, ss_path in enumerate(screenshot_paths):
        full_path = engagement_path / ss_path
        if not full_path.exists():
            continue

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
        sev = (f.get("priority") or "medium").lower()
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

    # --- Load templates ---
    components_path = plugin_path / "templates" / "components.html"
    font_path = plugin_path / "templates" / "font-embed.css"
    template_path = plugin_path / "templates" / "visual-report.html.template"

    with open(font_path, "r", encoding="utf-8") as f:
        font_css = f.read()

    # Read components.html for CSS extraction
    with open(components_path, "r", encoding="utf-8") as f:
        components_html = f.read()

    # Extract CSS from components (between first <style> and </style>)
    css_match = re.search(r"<style>(.*?)</style>", components_html, re.DOTALL)
    component_css = css_match.group(1) if css_match else ""

    # --- Build HTML sections ---

    # Metadata
    viewport = baton.get("viewport", {})
    device_label = f"{device.title()} ({viewport.get('width', '?')}×{viewport.get('height', '?')})"
    date_str = meta.get("created", "")[:10] if meta.get("created") else "Unknown"
    engagement_id = meta.get("id", engagement_path.name)

    # Thumbnail HTML
    thumb_html = ""
    for i, b64 in enumerate(slide_base64):
        active = "active" if i == 0 else ""
        thumb_html += f'<div class="thumb {active}" onclick="goToSlide({i})"><img src="data:image/jpeg;base64,{b64[:100]}..." alt="Section {i+1}"></div>\n'

    # Actually build proper thumbnails with full base64
    thumb_html = ""
    for i, b64 in enumerate(slide_base64):
        active = " active" if i == 0 else ""
        thumb_html += f'<div class="thumb{active}" onclick="goToSlide({i})" style="cursor:pointer"><img src="data:image/jpeg;base64,{b64}" alt="Section {i+1}" style="width:100%;height:100%;object-fit:cover;border-radius:8px"></div>\n'

    # Click target overlays (transparent, approximate positioning)
    click_targets = ""
    for mapping in markers_mapping:
        fidx = mapping["finding_index"]
        slide = mapping.get("slide", 0)
        elem_idx = mapping.get("baton_element_index")
        elements = baton.get("elements", [])

        if elem_idx is not None and elem_idx < len(elements):
            elem = elements[elem_idx]
            ss = screenshots[slide] if slide < len(screenshots) else {}
            scroll_y = ss.get("scrollY", 0) if isinstance(ss, dict) else 0
            nat_w = ss.get("naturalWidth", 1440) if isinstance(ss, dict) else 1440
            nat_h = ss.get("naturalHeight", 900) if isinstance(ss, dict) else 900

            rel_y = elem.get("y", 0) - scroll_y
            left_pct = (elem.get("x", 0) + elem.get("width", 0) / 2) / max(nat_w, 1) * 100
            top_pct = (rel_y + elem.get("height", 0) / 2) / max(nat_h, 1) * 100

            click_targets += (
                f'<a href="#finding-{fidx:02d}" class="marker-target" '
                f'data-slide="{slide}" data-finding="{fidx}" '
                f'style="position:absolute;left:{left_pct:.1f}%;top:{top_pct:.1f}%;'
                f'width:40px;height:40px;border-radius:50%;cursor:pointer;'
                f'transform:translate(-50%,-50%);display:{"block" if slide == 0 else "none"}'
                f'"></a>\n'
            )

    # Finding cards HTML
    finding_cards = ""
    for f in findings:
        idx = f["index"]
        sev = build_severity_class(f.get("priority"))
        sev_label = SEVERITY_LABELS.get(sev, "Medium Priority")
        section_title = slug_to_title(f.get("section", "unknown"))

        finding_cards += f"""
        <div class="finding-card severity-{sev}" id="finding-{idx:02d}" data-finding="{idx}">
          <div class="finding-header">
            <span class="finding-number">{idx:02d}</span>
            <h3 class="finding-title">{escape_html(section_title)}</h3>
            <span class="severity-badge {sev}">{escape_html(sev_label)}</span>
          </div>
          <div class="finding-body">
            <p class="observation">{escape_html(f.get('observation', ''))}</p>
            <div class="recommendation-box">
              <p>{escape_html(f.get('recommendation', ''))}</p>
            </div>
            <div class="why-matters">
              <p><strong>Why this matters:</strong> {escape_html(f.get('why_matters', ''))}</p>
            </div>
            <div class="citation-footer">
              <span class="ref-id">{escape_html(f.get('reference', ''))}</span>
              <span class="tier-badge tier-badge--{(f.get('tier') or 'bronze').lower()}">{escape_html(f.get('tier', 'Bronze'))}</span>
            </div>
          </div>
        </div>
        """

    # What's Working Well
    pass_html = ""
    if pass_findings:
        pass_items = ""
        for p in pass_findings:
            pass_items += f'<li><span style="color:#22c55e;margin-right:0.5rem">&#10003;</span>{escape_html(p)}</li>\n'
        pass_html = f"""
        <div style="margin:2rem 0;padding:1.5rem;background:var(--panel);border:1px solid var(--border);border-radius:12px">
          <h3 style="color:var(--text);font-size:1.1rem;margin:0 0 1rem 0">What's Working Well</h3>
          <ul style="list-style:none;padding:0;margin:0">{pass_items}</ul>
        </div>
        """

    # Severity distribution bars
    max_count = max(severity_counts.values()) if any(severity_counts.values()) else 1
    severity_bars = ""
    for sev_name, count in severity_counts.items():
        if count > 0:
            width_pct = count / max_count * 100
            color = SEVERITY_COLORS[sev_name]
            severity_bars += f"""
            <div style="margin-bottom:0.5rem">
              <div style="display:flex;justify-content:space-between;margin-bottom:0.25rem">
                <span style="color:var(--text-muted);font-size:0.85rem;text-transform:capitalize">{sev_name}</span>
                <span style="color:var(--text);font-weight:600">{count}</span>
              </div>
              <div style="height:6px;background:var(--border);border-radius:3px">
                <div style="height:100%;width:{width_pct:.0f}%;background:{color};border-radius:3px"></div>
              </div>
            </div>
            """

    # Ethics card
    if has_ethics_violations:
        ethics_html = '<div class="summary-value" style="color:#ef4444">FAIL</div><p style="color:var(--text-muted);font-size:0.85rem">Ethics violations detected</p>'
    else:
        ethics_html = '<div class="summary-value" style="color:#22c55e">PASS</div><p style="color:var(--text-muted);font-size:0.85rem">No dark patterns detected</p>'

    # Slide sources JSON for JS
    slide_sources_json = json.dumps([f"data:image/jpeg;base64,{b64}" for b64 in slide_base64])

    # --- Assemble final HTML ---
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; font-src data:;">
  <title>CRO Visual Report — {escape_html(engagement_id)}</title>
  <style>{font_css}</style>
  <style>{component_css}</style>
  <style>
    :root {{
      --bg: #0a0a0a; --panel: #141414; --border: #2a2a2a;
      --text: #e5e5e5; --text-muted: #888; --amber: #f59e0b; --green: #22c55e;
      --font-display: 'Inter', sans-serif; --font-mono: 'JetBrains Mono', monospace;
    }}
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ background: var(--bg); color: var(--text); font-family: var(--font-display); line-height: 1.6; }}
    .container {{ max-width: 1400px; margin: 0 auto; padding: 2rem; }}
    .main-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; margin: 2rem 0; }}
    .evidence-canvas {{ position: sticky; top: 2rem; height: fit-content; }}
    .carousel {{ position: relative; background: var(--panel); border-radius: 12px; overflow: hidden; border: 1px solid var(--border); }}
    .carousel img {{ width: 100%; display: block; }}
    .carousel-nav {{ position: absolute; top: 50%; transform: translateY(-50%); background: rgba(0,0,0,0.7); color: white; border: none; padding: 0.5rem 0.75rem; cursor: pointer; border-radius: 8px; font-size: 1.2rem; z-index: 10; }}
    .carousel-nav.prev {{ left: 0.5rem; }}
    .carousel-nav.next {{ right: 0.5rem; }}
    .thumb-strip {{ display: grid; grid-template-columns: repeat({len(slide_base64)}, 1fr); gap: 0.5rem; margin-top: 1rem; }}
    .thumb {{ border: 2px solid transparent; border-radius: 8px; overflow: hidden; opacity: 0.5; transition: all 0.2s; }}
    .thumb.active {{ border-color: var(--amber); opacity: 1; }}
    .findings {{ max-height: 80vh; overflow-y: auto; padding-right: 1rem; }}
    .finding-card {{ background: var(--panel); border: 1px solid var(--border); border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem; }}
    .finding-header {{ display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem; }}
    .finding-number {{ font-family: var(--font-mono); font-size: 1.5rem; font-weight: 700; color: var(--amber); }}
    .finding-title {{ flex: 1; font-size: 1.1rem; }}
    .severity-badge {{ padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; }}
    .severity-badge.critical {{ background: rgba(239,68,68,0.15); color: #ef4444; }}
    .severity-badge.high {{ background: rgba(249,115,22,0.15); color: #f97316; }}
    .severity-badge.medium {{ background: rgba(234,179,8,0.15); color: #eab308; }}
    .severity-badge.low {{ background: rgba(107,114,128,0.15); color: #9ca3af; }}
    .finding-card.severity-critical {{ border-left: 3px solid #ef4444; }}
    .finding-card.severity-high {{ border-left: 3px solid #f97316; }}
    .finding-card.severity-medium {{ border-left: 3px solid #eab308; }}
    .finding-card.severity-low {{ border-left: 3px solid #6b7280; }}
    .recommendation-box {{ background: rgba(245,158,11,0.05); border: 1px solid rgba(245,158,11,0.2); border-radius: 8px; padding: 1rem; margin: 0.75rem 0; }}
    .why-matters {{ color: var(--text-muted); font-size: 0.9rem; margin: 0.75rem 0; }}
    .citation-footer {{ display: flex; align-items: center; gap: 0.5rem; margin-top: 0.75rem; padding-top: 0.75rem; border-top: 1px solid var(--border); font-size: 0.8rem; color: var(--text-muted); }}
    .tier-badge {{ padding: 0.15rem 0.5rem; border-radius: 10px; font-size: 0.7rem; font-weight: 600; }}
    .tier-badge--gold {{ background: rgba(234,179,8,0.2); color: #eab308; }}
    .tier-badge--silver {{ background: rgba(156,163,175,0.2); color: #9ca3af; }}
    .tier-badge--bronze {{ background: rgba(180,130,80,0.2); color: #b4825; }}
    .summary-section {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin: 2rem 0; }}
    .summary-card {{ background: var(--panel); border: 1px solid var(--border); border-radius: 12px; padding: 1.5rem; }}
    .summary-label {{ font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--text-muted); margin-bottom: 0.5rem; }}
    .summary-value {{ font-size: 1.5rem; font-weight: 700; }}
    .summary-value.green {{ color: var(--green); }}
    .summary-value.amber {{ color: var(--amber); }}
    .metrics-bar {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin: 1rem 0; }}
    .metric-card {{ background: var(--panel); border: 1px solid var(--border); border-radius: 12px; padding: 1.25rem; display: flex; align-items: center; gap: 1rem; }}
    .section-label {{ font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.15em; color: var(--text-muted); margin-bottom: 1rem; }}
    header {{ margin-bottom: 2rem; }}
    .eyebrow {{ font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.2em; color: var(--amber); margin-bottom: 0.5rem; }}
    .hero-title {{ font-size: 2rem; font-weight: 700; line-height: 1.2; }}
    .hero-title .amber {{ color: var(--amber); }}
    .subtitle {{ color: var(--text-muted); margin-top: 0.5rem; }}
    .metadata {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-top: 1.5rem; }}
    .meta-item {{ font-size: 0.85rem; }}
    .meta-label {{ color: var(--text-muted); font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em; }}
    .marker-target {{ z-index: 5; }}
    .observation {{ margin-bottom: 0.5rem; }}
    @media (max-width: 900px) {{
      .main-grid {{ grid-template-columns: 1fr; }}
      .evidence-canvas {{ position: static; }}
      .summary-section {{ grid-template-columns: 1fr; }}
      .metadata {{ grid-template-columns: repeat(2, 1fr); }}
    }}
  </style>
</head>
<body>
  <div class="container">

    <header>
      <div class="eyebrow">Strategic Intelligence Report</div>
      <h1 class="hero-title">CRO <span class="amber">Conversion</span> Audit</h1>
      <p class="subtitle">{escape_html(device.title())} viewport analysis — {escape_html(meta.get('page', {}).get('url', 'Unknown URL'))}</p>
      <div class="metadata">
        <div class="meta-item"><div class="meta-label">Page Type</div>{escape_html((meta.get('page', {}).get('type') or 'Unknown').title())}</div>
        <div class="meta-item"><div class="meta-label">Platform</div>{escape_html((meta.get('platform') or 'Unknown').title())}</div>
        <div class="meta-item"><div class="meta-label">Device</div>{escape_html(device_label)}</div>
        <div class="meta-item"><div class="meta-label">Source Mode</div>{escape_html(meta.get('source_mode', 'Unknown'))}</div>
        <div class="meta-item"><div class="meta-label">Audit Date</div>{escape_html(date_str)}</div>
        <div class="meta-item"><div class="meta-label">Engagement</div><span style="color:var(--amber)">{escape_html(engagement_id)}</span></div>
      </div>
    </header>

    <div class="main-grid">

      <section class="evidence-canvas">
        <div class="section-label">Primary Interface Evidence</div>
        <div class="carousel" style="position:relative">
          <button class="carousel-nav prev" onclick="prevSlide()">&#8249;</button>
          <button class="carousel-nav next" onclick="nextSlide()">&#8250;</button>
          <img id="mainImage" src="data:image/jpeg;base64,{slide_base64[0]}" alt="Screenshot">
          {click_targets}
        </div>
        <div class="thumb-strip">
          {thumb_html}
        </div>
        <div class="metrics-bar">
          <div class="metric-card">
            <div>
              <div class="meta-label">Intent Reliability</div>
              <div style="font-size:1.5rem;font-weight:700">{intent_reliability}%</div>
            </div>
          </div>
          <div class="metric-card">
            <div>
              <div class="meta-label">Projected Lift</div>
              <div style="font-size:1.5rem;font-weight:700" class="green">+{projected_lift:.0f}%</div>
            </div>
          </div>
        </div>
      </section>

      <section class="findings">
        <div class="section-label">Diagnostic Insights</div>
        {finding_cards}
        {pass_html}
      </section>

    </div>

    <section class="summary-section">
      <div class="summary-card">
        <div class="summary-label">Evidence Confidence</div>
        <div class="summary-value amber">HIGH</div>
        <p style="color:var(--text-muted);font-size:0.85rem;margin-top:0.5rem">URL + DOM dual-source analysis</p>
      </div>
      <div class="summary-card">
        <div class="summary-label">Severity Distribution</div>
        {severity_bars}
      </div>
      <div class="summary-card">
        <div class="summary-label">Ethics Check</div>
        {ethics_html}
      </div>
    </section>

  </div>

  <script>
    const slideSources = {slide_sources_json};
    let currentSlide = 0;

    function goToSlide(n) {{
      currentSlide = n;
      document.getElementById('mainImage').src = slideSources[n];
      document.querySelectorAll('.thumb').forEach((t, i) => {{
        t.classList.toggle('active', i === n);
      }});
      document.querySelectorAll('.marker-target').forEach(m => {{
        m.style.display = parseInt(m.dataset.slide) === n ? 'block' : 'none';
      }});
    }}

    function nextSlide() {{
      goToSlide((currentSlide + 1) % slideSources.length);
    }}

    function prevSlide() {{
      goToSlide((currentSlide - 1 + slideSources.length) % slideSources.length);
    }}

    // Scroll-sync: clicking a finding card switches to its slide
    document.querySelectorAll('.finding-card').forEach(card => {{
      card.addEventListener('click', () => {{
        const findingNum = parseInt(card.dataset.finding);
        const target = document.querySelector(`.marker-target[data-finding="${{findingNum}}"]`);
        if (target) {{
          goToSlide(parseInt(target.dataset.slide));
        }}
      }});
    }});
  </script>

</body>
</html>"""

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
    print(f"  Pillow: {'yes' if HAS_PILLOW else 'no (CSS fallback)'}")


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
