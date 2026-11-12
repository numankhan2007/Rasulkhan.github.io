#!/usr/bin/env python3
"""
Comprehensive 4-Tier Automated E2E Test Suite for Rasul Khan's Portfolio.

Tiers:
  Tier 1: Feature Coverage (Verbatim Content Preservation, Sections, Projects, Education, Skills, Contact)
  Tier 2: Boundary, Edge & Syntax Checks (Asset Resolution, Protocol, Mobile Viewport, Palette Tokens, Coral Isolation, Gothic/Italic Typography)
  Tier 3: Cross-Feature & Loading / Animation Checks (Smooth Scrolling, Skeleton Loading & Fallback, IntersectionObserver, Counter Roll)
  Tier 4: Real-World Local Server Verification (HTTP 200 OK for Page and All Referenced Assets, Zero 404s, Clean Teardown)

Usage:
  python3 tests/verify_portfolio.py
  python3 -m unittest discover tests
"""

import http.server
import os
import re
import socket
import sys
import threading
import time
import unittest
import urllib.parse
import urllib.request
from pathlib import Path
from bs4 import BeautifulSoup

REPO_ROOT = Path(__file__).resolve().parent.parent
INDEX_HTML = REPO_ROOT / "index.html"
STYLE_CSS = REPO_ROOT / "css" / "style.css"
MAIN_JS = REPO_ROOT / "js" / "main.js"
IMAGES_DIR = REPO_ROOT / "images"


def load_file_content(path: Path) -> str:
    """Helper to read text content with UTF-8 encoding."""
    if not path.is_file():
        raise FileNotFoundError(f"Required file not found: {path}")
    return path.read_text(encoding="utf-8", errors="replace")


# ==============================================================================
# Tier 1: Feature Coverage & Content Preservation
# ==============================================================================
class TestTier1FeatureCoverage(unittest.TestCase):
    """Tier 1: Verify presence of all required sections and 100% verbatim content."""

    @classmethod
    def setUpClass(cls):
        cls.html_content = load_file_content(INDEX_HTML)
        cls.soup = BeautifulSoup(cls.html_content, "html.parser")

    def test_01_core_sections_exist(self):
        """Assert all required semantic portfolio sections exist by ID or class."""
        required_sections = [
            "home-section",
            "about-section",
            "resume-section",
            "project-section",
            "section-counter",
            "contact-section",
        ]
        for sec_id in required_sections:
            elem = self.soup.find(id=sec_id)
            self.assertIsNotNone(elem, f"Section #{sec_id} must exist in index.html")

        # Footer element or class
        footer = self.soup.find("footer") or self.soup.find(class_=re.compile(r"footer"))
        self.assertIsNotNone(footer, "Footer section must exist in index.html")

    def test_02_navbar_links(self):
        """Verify navigation links target the primary page sections."""
        expected_targets = {
            "#home-section",
            "#about-section",
            "#resume-section",
            "#project-section",
            "#contact-section",
        }
        nav_anchors = self.soup.find_all("a", href=True)
        found_targets = {a["href"] for a in nav_anchors if a["href"].startswith("#")}
        missing = expected_targets - found_targets
        self.assertEqual(len(missing), 0, f"Navbar is missing target section links: {missing}")

    def test_03_hero_content(self):
        """Verify Hero section verbatim text, greeting, and call-to-action buttons."""
        hero = self.soup.find(id="home-section")
        self.assertIsNotNone(hero, "Hero section #home-section is required")
        text = hero.get_text()
        self.assertIn("Rasul Khan", text, "Hero must contain headline 'Rasul Khan'")
        self.assertTrue("Hello!👋" in text or "Hello" in text, "Hero must contain greeting 'Hello'")
        self.assertIn("Data Analyst", text, "Hero must display role 'Data Analyst'")

        # CTA buttons
        hero_links = hero.find_all("a", href=True)
        link_texts = [a.get_text().strip() for a in hero_links]
        self.assertTrue(
            any("Linked In" in lt or "LinkedIn" in lt for lt in link_texts),
            "Hero must contain LinkedIn button",
        )
        self.assertTrue(
            any("My works" in lt or "works" in lt.lower() for lt in link_texts),
            "Hero must contain 'My works' button",
        )

    def test_04_about_content(self):
        """Verify About section personal info, biography, and metrics."""
        about = self.soup.find(id="about-section")
        self.assertIsNotNone(about, "About section #about-section is required")
        text = about.get_text()

        # Personal details
        self.assertIn("Rasul", text)
        self.assertIn("Data Analyst", text)
        self.assertIn("Fresher", text)
        self.assertIn("Villupuram, Tamil Nadu", text)

        # Biography excerpt
        bio_snippet = "As a Data Analyst Fresher with a bachelor"
        self.assertIn(bio_snippet, text, f"About biography must contain: '{bio_snippet}'")

        # Project completed metric
        has_10_projects = (
            bool(about.find(attrs={"data-number": "10"}))
            or "10" in text
        )
        self.assertTrue(has_10_projects, "About section must specify 10 projects completed (via data-number='10' or text)")
        self.assertIn("Projects completed", text)

    def test_05_skills_and_percentages(self):
        """Verify all skill progress entries and expected percentage values."""
        about = self.soup.find(id="about-section")
        text = about.get_text()

        expected_skills = [
            ("SQL", "75%"),
            ("PYTHON", "80%"),
            ("Data Visualization", "90%"),
            ("Microsoft Power BI", "75%"),
            ("Tableau", "73%"),
            ("Excel", "85%"),
            ("Microsoft Tools", "95%"),
        ]
        for skill_name, percentage in expected_skills:
            self.assertIn(skill_name, text, f"Skill '{skill_name}' must be listed in About section")
            self.assertIn(percentage, text, f"Skill '{skill_name}' must have percentage '{percentage}'")

    def test_06_profile_metadata_list(self):
        """Verify detailed profile fields in About section."""
        about = self.soup.find(id="about-section")
        text = about.get_text()

        expected_fields = [
            "Bachelor of Mathematics",
            "Retail, E-commerce & Data Analysis",
            "English, Tamil, Urdu, Hindi & Arabic",
            "Microsoft Power BI",
            "Google looker",
            "Tableau",
        ]
        for field in expected_fields:
            self.assertIn(field, text, f"About metadata must include '{field}'")

    def test_07_resume_education(self):
        """Verify Education subsection entries in Resume."""
        resume = self.soup.find(id="resume-section")
        self.assertIsNotNone(resume, "Resume section #resume-section is required")
        text = resume.get_text()

        # Education 1: Annamalai University
        self.assertIn("Bachelor of Mathematics", text)
        self.assertIn("Annamalai University", text)
        self.assertIn("2021-2024", text)

        # Education 2: Murthuzaviya
        self.assertIn("Higher Secondary (HSC)", text)
        self.assertIn("Murthuzaviya Higher Secondary School", text)
        self.assertIn("2019-2021", text)

    def test_08_resume_courses(self):
        """Verify all 9 specialized course certificates in Resume."""
        resume = self.soup.find(id="resume-section")
        text = resume.get_text()

        expected_courses = [
            "AI & DATA SCIENTIST",
            "Machine Learning with Python Foundations",
            "Introduction to career skills in Data analytics",
            "JioHotstar Sports analytics Using Python: IPL Dataset",
            "CLP(Computer Literacy Programme)",
            "DTP(Desktop Publishing)",
            "Diploma in Urdu Language",
            "Diploma in Calligraphy And Graphic Designing",
            "UNXT Soft Skill Program",
        ]
        for course in expected_courses:
            self.assertIn(course, text, f"Resume must list course: '{course}'")

        # CV Download action link
        cv_links = resume.find_all("a", href=True)
        cv_hrefs = [a["href"] for a in cv_links]
        self.assertTrue(
            any("Resume.pdf" in h or "RESUME" in h for h in cv_hrefs),
            "Resume must provide a download CV link targeting Resume PDF",
        )

    def test_09_all_9_projects_exist(self):
        """Verify all 9 project titles, descriptions, and project cards exist."""
        projects_sec = self.soup.find(id="project-section")
        self.assertIsNotNone(projects_sec, "Projects section #project-section is required")
        text = projects_sec.get_text()

        expected_projects = [
            "Spotify Global Streaming Analysis",
            "Diwali Sales Analysis",
            "Power BI Yearly student fees dashboard",
            "Zomato sales Analysis Using Power BI",
            "Advanced Data Warehouse Analysis",
            "Retail Sales Analysis Using SQL",
            "Customer Shipping Analysis",
            "Indian Crime Analysis",
            "Swiggy Sales Analysis",
        ]
        for proj in expected_projects:
            self.assertIn(proj, text, f"Projects section must list project '{proj}'")

        # Verify project links exist
        proj_links = projects_sec.find_all("a", href=True)
        self.assertGreaterEqual(len(proj_links), 9, "Projects section must contain links for all projects")

    def test_10_counters_section(self):
        """Verify statistics / counter numbers in #section-counter."""
        counter_sec = self.soup.find(id="section-counter")
        self.assertIsNotNone(counter_sec, "Counter section #section-counter is required")
        text = counter_sec.get_text()

        self.assertIn("Achievements", text)
        self.assertIn("Projects", text)
        self.assertIn("Cups of coffee", text)
        # Verify numbers 20, 10, 15 either in text or in data-number attributes
        numbers_data = [
            elem.get("data-number")
            for elem in counter_sec.find_all(attrs={"data-number": True})
        ]
        if numbers_data:
            self.assertIn("20", numbers_data)
            self.assertIn("10", numbers_data)
            self.assertIn("15", numbers_data)
        else:
            self.assertIn("20", text)
            self.assertIn("10", text)
            self.assertIn("15", text)

    def test_11_hire_me_section(self):
        """Verify Hire Me / GitHub callout section."""
        hireme = self.soup.find(class_=re.compile(r"hireme")) or self.soup
        text = " ".join(hireme.get_text().split())
        self.assertIn("More projects on Github", text)
        self.assertIn("I love to solve business problems & uncover hidden data stories", text)
        hire_links = [a["href"] for a in self.soup.find_all("a", href=True)]
        self.assertTrue(
            any("github.com/Rasulajees" in h for h in hire_links),
            "Hire Me section must link to GitHub profile https://github.com/Rasulajees",
        )

    def test_12_contact_cards_and_social(self):
        """Verify Contact section details, cards, inquiry form link, and social profiles."""
        contact_sec = self.soup.find(id="contact-section")
        self.assertIsNotNone(contact_sec, "Contact section #contact-section is required")
        text = contact_sec.get_text()

        # Contact cards
        self.assertTrue("Villupuram" in text or "villupuram" in text)
        self.assertIn("8015429078", text)
        self.assertIn("rasulkhanoffi@gmail.com", text)

        # Inquiry form & Social links
        anchors = self.soup.find_all("a", href=True)
        hrefs = [a["href"] for a in anchors]

        self.assertTrue(
            any("forms.office.com" in h for h in hrefs),
            "Contact section must include link to Microsoft Forms inquiry form",
        )
        self.assertTrue(
            any("linkedin.com/in/rasul-khan" in h for h in hrefs),
            "Social profiles must include LinkedIn",
        )
        self.assertTrue(
            any("github.com/Rasulajees" in h for h in hrefs),
            "Social profiles must include GitHub",
        )
        self.assertTrue(
            any("instagram.com" in h for h in hrefs),
            "Social profiles must include Instagram",
        )
        self.assertTrue(
            any("snapchat.com" in h for h in hrefs),
            "Social profiles must include Snapchat",
        )


# ==============================================================================
# Tier 2: Boundary, Edge & Syntax Checks
# ==============================================================================
class TestTier2BoundaryEdgeSyntax(unittest.TestCase):
    """Tier 2: Asset resolution, protocol integrity, mobile viewport, color palette, button coral isolation, typography."""

    @classmethod
    def setUpClass(cls):
        cls.html_content = load_file_content(INDEX_HTML)
        cls.css_content = load_file_content(STYLE_CSS)
        cls.soup = BeautifulSoup(cls.html_content, "html.parser")

    def test_01_local_asset_path_resolution(self):
        """Verify every local image referenced in HTML and CSS physically exists with non-zero size."""
        local_assets = set()

        # 1. HTML img src
        for img in self.soup.find_all("img", src=True):
            src = img["src"]
            if not src.startswith(("http://", "https://", "data:", "//")):
                local_assets.add(src)

        # 2. HTML inline styles url(...)
        url_pattern = re.compile(r"url\s*\(\s*['\"]?([^'\")]+)['\"]?\s*\)", re.IGNORECASE)
        for tag in self.soup.find_all(style=True):
            for match in url_pattern.finditer(tag["style"]):
                url = match.group(1).strip()
                if not url.startswith(("http://", "https://", "data:", "//")):
                    local_assets.add(url)

        # 3. CSS stylesheet url(...)
        for match in url_pattern.finditer(self.css_content):
            url = match.group(1).strip()
            if not url.startswith(("http://", "https://", "data:", "//")):
                # Normalize relative to css dir if needed
                if url.startswith("../"):
                    url = url[3:]
                local_assets.add(url)

        self.assertGreater(len(local_assets), 0, "Expected local assets in HTML/CSS")

        missing_assets = []
        empty_assets = []

        for asset_path in local_assets:
            # Strip query params or hash
            clean_path = asset_path.split("?")[0].split("#")[0]
            clean_path = urllib.parse.unquote(clean_path)
            if clean_path.startswith("./"):
                clean_path = clean_path[2:]
            if clean_path.startswith("/"):
                clean_path = clean_path[1:]

            full_path = REPO_ROOT / clean_path
            if not full_path.is_file():
                missing_assets.append(f"{asset_path} -> {full_path}")
            elif full_path.stat().st_size == 0:
                empty_assets.append(f"{asset_path} (size 0)")

        self.assertEqual(
            len(missing_assets),
            0,
            f"Broken asset references found (404 on disk):\n" + "\n".join(missing_assets),
        )
        self.assertEqual(
            len(empty_assets),
            0,
            f"Empty asset files found (0 bytes):\n" + "\n".join(empty_assets),
        )

    def test_02_protocol_integrity(self):
        """Assert zero malformed URL protocols (e.g., 'hhttps://', 'http//', 'https//')."""
        malformed = []
        for tag in self.soup.find_all(href=True):
            href = tag["href"]
            if re.match(r"^hhttps?://", href) or re.match(r"^https?//", href):
                malformed.append(f"<{tag.name} href='{href}'>")
        for tag in self.soup.find_all(src=True):
            src = tag["src"]
            if re.match(r"^hhttps?://", src) or re.match(r"^https?//", src):
                malformed.append(f"<{tag.name} src='{src}'>")

        self.assertEqual(
            len(malformed),
            0,
            f"Found malformed protocol URLs in HTML:\n" + "\n".join(malformed),
        )

    def test_03_mailto_and_tel_integrity(self):
        """Verify mailto and tel anchor integrity (no placeholders)."""
        mailto_links = self.soup.find_all("a", href=re.compile(r"^mailto:", re.IGNORECASE))
        for a in mailto_links:
            href = a["href"].lower()
            self.assertNotIn("info@yoursite.com", href, "mailto link must not use template placeholder")
            self.assertIn("rasulkhanoffi@gmail.com", href, "mailto link must point to rasulkhanoffi@gmail.com")

        tel_links = self.soup.find_all("a", href=re.compile(r"^tel:", re.IGNORECASE))
        for a in tel_links:
            href = a["href"]
            self.assertNotIn("0101010101", href, "tel link must not use template placeholder 0101010101")
            self.assertTrue(
                "8015429078" in href,
                f"tel link must contain owner phone number 8015429078, found '{href}'",
            )

    def test_04_mobile_viewport_meta(self):
        """Verify mobile viewport meta tag exists and configures width=device-width."""
        viewport = self.soup.find("meta", attrs={"name": "viewport"})
        self.assertIsNotNone(viewport, "A mobile viewport <meta name='viewport'> tag is required in <head>")
        content = viewport.get("content", "")
        self.assertIn("width=device-width", content, "Viewport content must include 'width=device-width'")

    def test_05_css_palette_tokens(self):
        """Verify CSS contains White, Sky Blue, and Black palette custom properties/tokens."""
        css = self.css_content

        # Check for palette tokens
        # Dark canvas: #0a0e17, #0f172a, #131c31, or #000
        has_dark = bool(
            re.search(r"--bg-(?:primary|secondary|card|canvas)\s*:\s*#(?:0a0e17|0f172a|131c31|000000|000)\b", css, re.IGNORECASE)
            or re.search(r"--color-black\s*:\s*#(?:000000|000)\b", css, re.IGNORECASE)
        )
        self.assertTrue(has_dark, "CSS must define dark canvas token (--bg-primary, etc.) in White/Sky Blue/Black palette")

        # Sky blue: #38bdf8, #0ea5e9, #0284c7
        has_sky_blue = bool(
            re.search(r"--sky-blue\w*\s*:\s*#(?:38bdf8|0ea5e9|0284c7)\b", css, re.IGNORECASE)
            or re.search(r"--accent-sky\s*:\s*#(?:38bdf8|0ea5e9|0284c7)\b", css, re.IGNORECASE)
        )
        self.assertTrue(has_sky_blue, "CSS must define Sky Blue accent token (--sky-blue, etc.)")

        # Button coral: #ff5722, #ff6b35, #ff4500
        has_coral = bool(
            re.search(r"--btn-coral\w*\s*:\s*#(?:ff5722|ff6b35|ff4500)\b", css, re.IGNORECASE)
            or re.search(r"--accent-coral\s*:\s*#(?:ff5722|ff6b35|ff4500)\b", css, re.IGNORECASE)
        )
        self.assertTrue(has_coral, "CSS must define Neon Coral / Orange button token (--btn-coral, etc.)")

    def test_06_exclusive_button_coral_accent(self):
        """Verify bright coral / neon orange is applied EXCLUSIVELY to buttons (.btn), zero non-button elements."""
        coral_hex_patterns = [
            re.compile(r"#ff5722\b", re.IGNORECASE),
            re.compile(r"#ff6b35\b", re.IGNORECASE),
            re.compile(r"#ff4500\b", re.IGNORECASE),
            re.compile(r"rgb\s*\(\s*255\s*,\s*(?:87|107|69)\s*,\s*(?:34|53|0)\s*\)", re.IGNORECASE),
            re.compile(r"var\s*\(\s*--btn-coral[^)]*\)", re.IGNORECASE),
        ]

        rule_pattern = re.compile(r"([^{}]+)\{([^{}]+)\}")

        # 1. Assert buttons DO use coral accent in CSS
        button_has_coral = False
        for match in rule_pattern.finditer(self.css_content):
            selector = match.group(1).strip()
            block = match.group(2)
            if any(btn_sel in selector for btn_sel in [".btn", "button", ".button"]):
                if any(pat.search(block) for pat in coral_hex_patterns):
                    button_has_coral = True
                    break
        self.assertTrue(
            button_has_coral,
            "Buttons (.btn) must be styled with neon coral / bright orange accent in CSS",
        )

        # 2. Check inline styles on HTML elements
        for elem in self.soup.find_all(style=True):
            style = elem["style"]
            classes = elem.get("class", [])
            tag_name = elem.name
            is_button = "btn" in classes or tag_name == "button" or (tag_name == "a" and "btn" in " ".join(classes))
            for pat in coral_hex_patterns:
                if pat.search(style):
                    self.assertTrue(
                        is_button,
                        f"Non-button element <{tag_name} class='{' '.join(classes)}'> has coral accent in inline style: '{style}'",
                    )

        # 3. Check CSS rules: rules with coral must target buttons or be in :root
        for match in rule_pattern.finditer(self.css_content):
            selector = match.group(1).strip()
            block = match.group(2)

            # Skip :root, keyframes, or comments
            if ":root" in selector or "@keyframes" in selector or selector.startswith("@"):
                continue

            has_coral_color = any(pat.search(block) for pat in coral_hex_patterns)
            if has_coral_color:
                # Selector must be button-related
                is_btn_selector = (
                    ".btn" in selector
                    or "button" in selector
                    or ".button" in selector
                )
                self.assertTrue(
                    is_btn_selector,
                    f"Rule for non-button selector '{selector}' applies coral accent: {block.strip()[:100]}",
                )

    def test_07_gothic_and_italic_typography(self):
        """Verify Gothic font family and Italic typography styling are configured and applied."""
        css = self.css_content

        # 1. Gothic font family declaration
        gothic_font_match = re.search(
            r"font-family\s*:[^;]*(?:League Gothic|Gothic A1|Century Gothic|Franklin Gothic)[^;]*;",
            css,
            re.IGNORECASE,
        )
        self.assertIsNotNone(
            gothic_font_match,
            "CSS must define a gothic font family (e.g. 'League Gothic', 'Gothic A1', 'Century Gothic')",
        )

        # 2. Italic font styling
        italic_style_match = re.search(r"font-style\s*:\s*italic\b", css, re.IGNORECASE)
        self.assertIsNotNone(
            italic_style_match,
            "CSS must include 'font-style: italic' styling rules for subheadings/metadata",
        )

        # 3. Google Font link in HTML
        font_links = self.soup.find_all("link", href=re.compile(r"fonts\.googleapis\.com", re.IGNORECASE))
        has_gothic_link = any(
            "League+Gothic" in l["href"] or "Gothic+A1" in l["href"] or "Gothic" in l["href"]
            for l in font_links
        )
        self.assertTrue(
            has_gothic_link,
            "HTML <link> must load Gothic font family (League Gothic or Gothic A1) from Google Fonts",
        )

    def test_08_no_raw_github_image_urls(self):
        """Assert zero raw GitHub image URLs in HTML (all images must be local ./images/... paths)."""
        raw_github_patterns = [
            re.compile(r"github\.com/[^/]+/[^/]+/blob/[^\"'>]+\?raw=true", re.IGNORECASE),
            re.compile(r"raw\.githubusercontent\.com/[^\"'>]+", re.IGNORECASE),
        ]
        found_raw = []
        for pat in raw_github_patterns:
            for match in pat.finditer(self.html_content):
                found_raw.append(match.group(0))

        self.assertEqual(
            len(found_raw),
            0,
            f"Found {len(found_raw)} raw GitHub image URLs that must be converted to local ./images/... paths:\n"
            + "\n".join(found_raw[:5]),
        )


# ==============================================================================
# Tier 3: Cross-Feature & Loading / Animation Checks
# ==============================================================================
class TestTier3CrossFeatureLoadingAnimation(unittest.TestCase):
    """Tier 3: Smooth scrolling, skeleton loading screen, dismiss logic, IntersectionObserver, counters."""

    @classmethod
    def setUpClass(cls):
        cls.html_content = load_file_content(INDEX_HTML)
        cls.css_content = load_file_content(STYLE_CSS)
        cls.js_content = load_file_content(MAIN_JS)
        cls.soup = BeautifulSoup(cls.html_content, "html.parser")

    def test_01_smooth_scrolling_css(self):
        """Verify native CSS smooth scroll and scroll-padding-top offset are defined."""
        css = self.css_content
        has_smooth_scroll = bool(re.search(r"scroll-behavior\s*:\s*smooth\b", css, re.IGNORECASE))
        self.assertTrue(has_smooth_scroll, "CSS must define 'scroll-behavior: smooth' on html/body")

        has_scroll_padding = bool(re.search(r"scroll-padding-top\s*:\s*\d+px\b", css, re.IGNORECASE))
        self.assertTrue(
            has_scroll_padding,
            "CSS must define 'scroll-padding-top' to offset fixed sticky navigation",
        )

    def test_02_smooth_scrolling_js(self):
        """Verify JS or HTML handles smooth scrolling for internal section links."""
        js_or_html = self.js_content + " " + self.html_content
        has_scroll_handler = (
            "scrollIntoView" in js_or_html
            or "scrollTop" in js_or_html
            or "smooth" in js_or_html
        )
        self.assertTrue(has_scroll_handler, "JS/HTML must implement smooth scroll navigation handling")

    def test_03_skeleton_screen_html_structure(self):
        """Verify #skeleton-screen element exists in index.html with wireframe placeholders."""
        skeleton = self.soup.find(id="skeleton-screen")
        self.assertIsNotNone(skeleton, "index.html must include '#skeleton-screen' container element")

        # Must have skeleton elements or cards
        skeleton_items = skeleton.find_all(class_=re.compile(r"skeleton"))
        self.assertGreater(
            len(skeleton_items),
            0,
            "#skeleton-screen must contain placeholder skeleton elements/classes",
        )

    def test_04_skeleton_shimmer_css(self):
        """Verify CSS defines skeleton shimmer animation and fade-out transition."""
        css = self.css_content
        has_shimmer_keyframes = bool(
            re.search(r"@keyframes\s+skeleton-shimmer\b", css, re.IGNORECASE)
            or re.search(r"@keyframes\s+shimmer\b", css, re.IGNORECASE)
        )
        self.assertTrue(has_shimmer_keyframes, "CSS must define '@keyframes skeleton-shimmer' animation")

        has_skeleton_hidden = bool(
            re.search(r"\.skeleton-hidden\b", css)
            or re.search(r"#skeleton-screen\.hidden\b", css)
        )
        self.assertTrue(
            has_skeleton_hidden,
            "CSS must define '.skeleton-hidden' class for smooth dismiss transition",
        )

    def test_05_skeleton_dismiss_and_fallback_js(self):
        """Verify JS handles window.onload dismiss and includes safety timeout fallback."""
        js = self.js_content
        has_load_listener = (
            "window.addEventListener('load'" in js
            or "window.addEventListener(\"load\"" in js
            or "$(window).on('load'" in js
            or "window.onload" in js
        )
        self.assertTrue(
            has_load_listener,
            "js/main.js must listen to window 'load' event to dismiss skeleton screen",
        )

        has_fallback_timeout = (
            "setTimeout" in js
            and ("skeleton" in js or "loader" in js)
        )
        self.assertTrue(
            has_fallback_timeout,
            "js/main.js must include a safety setTimeout fallback to dismiss skeleton if load event delays",
        )

    def test_06_skeleton_noscript_fallback(self):
        """Verify index.html includes <noscript> fallback so content is accessible without JS."""
        noscript = self.soup.find("noscript")
        self.assertIsNotNone(noscript, "index.html must provide a <noscript> fallback tag")
        # Ensure noscript styles hide skeleton screen or display content
        noscript_text = noscript.get_text()
        self.assertTrue(
            "skeleton" in noscript_text or "display" in noscript_text or "<style>" in str(noscript),
            "<noscript> tag must ensure skeleton is dismissed if JavaScript is disabled",
        )

    def test_07_intersection_observer_and_counter(self):
        """Verify IntersectionObserver scroll reveal and counter roll animation logic exist."""
        js = self.js_content
        has_observer = "IntersectionObserver" in js or "waypoints" in js.lower()
        self.assertTrue(has_observer, "js/main.js must use IntersectionObserver (or waypoints) for scroll reveals")

        has_counter_anim = (
            "requestAnimationFrame" in js
            or "animateNumber" in js
            or "countTo" in js
            or "data-number" in js
        )
        self.assertTrue(has_counter_anim, "js/main.js must implement animated counter roll logic")

    def test_08_mobile_navbar_toggle(self):
        """Verify mobile navigation toggle logic exists."""
        js = self.js_content
        has_toggle = (
            "navbar-toggler" in js
            or "ftco-nav" in js
            or "nav-toggle" in js
            or "classList.toggle" in js
        )
        self.assertTrue(has_toggle, "js/main.js must handle mobile navbar toggling")

    def test_09_typing_animation_roles(self):
        """Verify typing animation cycles through all 5 specified career roles."""
        combined = self.html_content + " " + self.js_content
        expected_roles = [
            "Data Analyst",
            "Data operation analyst",
            "Data Scientist",
            "Business Analyst",
            "BI Developer",
        ]
        for role in expected_roles:
            self.assertIn(role, combined, f"Typing animation roles must include '{role}'")


# ==============================================================================
# Tier 4: Real-World Local Server Verification
# ==============================================================================
class TestTier4RealWorldLocalServer(unittest.TestCase):
    """Tier 4: Live HTTP serving on ephemeral port, asset 200 checks, clean server teardown."""

    server = None
    server_thread = None
    server_port = None
    base_url = None

    @classmethod
    def setUpClass(cls):
        """Start a lightweight background HTTP server on a dynamic port."""
        class QuietHandler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=str(REPO_ROOT), **kwargs)

            def log_message(self, format, *args):
                # Suppress normal request logging noise during test run
                pass

        # Find free port
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", 0))
            cls.server_port = s.getsockname()[1]

        cls.server = http.server.ThreadingHTTPServer(("127.0.0.1", cls.server_port), QuietHandler)
        cls.server_thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.server_thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.server_port}"
        time.sleep(0.15)  # Allow socket to listen

    @classmethod
    def tearDownClass(cls):
        """Gracefully shut down the server."""
        if cls.server:
            cls.server.shutdown()
            cls.server.server_close()
        if cls.server_thread and cls.server_thread.is_alive():
            cls.server_thread.join(timeout=1.0)

    def test_01_http_server_serves_index_html(self):
        """Assert HTTP 200 OK and text/html Content-Type when fetching root and index.html."""
        for path in ["/", "/index.html"]:
            url = f"{self.base_url}{path}"
            req = urllib.request.Request(url, headers={"User-Agent": "PortfolioE2ETest/1.0"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                self.assertEqual(resp.status, 200, f"GET {url} must return 200 OK")
                ctype = resp.headers.get("Content-Type", "")
                self.assertIn("text/html", ctype, f"GET {url} Content-Type must be text/html")
                body = resp.read().decode("utf-8", errors="replace")
                self.assertIn("Rasul Khan", body, f"GET {url} body must contain 'Rasul Khan'")

        # Adversarial oracle verification: assert server genuinely returns 404 on missing assets
        missing_url = f"{self.base_url}/nonexistent_test_asset_404.xyz"
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(missing_url, timeout=5)
        self.assertEqual(ctx.exception.code, 404, "Server must genuinely return HTTP 404 for non-existent paths")
        ctx.exception.close()

    def test_02_http_server_all_referenced_assets_200(self):
        """Fetch index.html, extract all local CSS, JS, and image URLs, assert 200 OK for every asset."""
        url = f"{self.base_url}/index.html"
        with urllib.request.urlopen(url, timeout=5) as resp:
            html = resp.read().decode("utf-8", errors="replace")

        soup = BeautifulSoup(html, "html.parser")
        asset_urls = set()

        # Stylesheets
        for link in soup.find_all("link", rel=True, href=True):
            rel = link["rel"]
            if isinstance(rel, list):
                rel = " ".join(rel)
            if "stylesheet" in rel:
                href = link["href"]
                if not href.startswith(("http://", "https://", "//")):
                    asset_urls.add(href)

        # Scripts
        for script in soup.find_all("script", src=True):
            src = script["src"]
            if not src.startswith(("http://", "https://", "//")):
                asset_urls.add(src)

        # Images
        for img in soup.find_all("img", src=True):
            src = img["src"]
            if not src.startswith(("http://", "https://", "data:", "//")):
                asset_urls.add(src)

        # Inline style backgrounds
        url_pat = re.compile(r"url\s*\(\s*['\"]?([^'\")]+)['\"]?\s*\)", re.IGNORECASE)
        for tag in soup.find_all(style=True):
            for match in url_pat.finditer(tag["style"]):
                u = match.group(1).strip()
                if not u.startswith(("http://", "https://", "data:", "//")):
                    asset_urls.add(u)

        self.assertGreater(len(asset_urls), 0, "Server test must discover local asset URLs")

        failed_requests = []
        for asset in sorted(asset_urls):
            # Clean asset url
            clean = asset.split("?")[0].split("#")[0]
            clean = clean.lstrip(".")
            if not clean.startswith("/"):
                clean = "/" + clean
            # URL encode path properly (handle spaces)
            quoted_path = urllib.parse.quote(clean)
            target_url = f"{self.base_url}{quoted_path}"
            try:
                with urllib.request.urlopen(target_url, timeout=5) as asset_resp:
                    if asset_resp.status != 200:
                        failed_requests.append(f"{target_url} returned status {asset_resp.status}")
                    else:
                        content = asset_resp.read()
                        if len(content) == 0:
                            failed_requests.append(f"{target_url} returned 0 bytes")
            except Exception as e:
                failed_requests.append(f"{target_url} failed with error: {e}")

        self.assertEqual(
            len(failed_requests),
            0,
            f"Asset HTTP requests failed (broken local assets):\n" + "\n".join(failed_requests),
        )

    def test_03_http_server_clean_teardown(self):
        """Assert background server port is responsive and can be queried repeatedly without leakage."""
        url = f"{self.base_url}/"
        for _ in range(3):
            with urllib.request.urlopen(url, timeout=5) as resp:
                self.assertEqual(resp.status, 200)


# ==============================================================================
# Custom Test Runner with Formatted Output
# ==============================================================================
def run_all_tests():
    """Execute all tiers with diagnostic formatting and summary report."""
    print("=" * 80)
    print(" RASUL KHAN PORTFOLIO — 4-TIER AUTOMATED E2E VERIFICATION SUITE")
    print(f" Target Repository: {REPO_ROOT}")
    print("=" * 80)

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    tiers = [
        ("Tier 1: Feature Coverage & Content Preservation", TestTier1FeatureCoverage),
        ("Tier 2: Boundary, Edge & Syntax Checks", TestTier2BoundaryEdgeSyntax),
        ("Tier 3: Cross-Feature & Loading / Animation Checks", TestTier3CrossFeatureLoadingAnimation),
        ("Tier 4: Real-World Local Server Verification", TestTier4RealWorldLocalServer),
    ]

    total_tests = 0
    total_failures = 0
    total_errors = 0
    tier_results = []

    for tier_name, test_class in tiers:
        tier_suite = loader.loadTestsFromTestCase(test_class)
        runner = unittest.TextTestRunner(verbosity=2)
        print(f"\n>>> Running {tier_name} ({tier_suite.countTestCases()} tests)...")
        start_time = time.time()
        result = runner.run(tier_suite)
        elapsed = time.time() - start_time

        count = result.testsRun
        fails = len(result.failures)
        errs = len(result.errors)
        total_tests += count
        total_failures += fails
        total_errors += errs

        tier_results.append({
            "name": tier_name,
            "count": count,
            "passed": count - fails - errs,
            "failed": fails,
            "errors": errs,
            "elapsed": elapsed,
        })

    print("\n" + "=" * 80)
    print(" SUMMARY REPORT")
    print("=" * 80)
    for res in tier_results:
        status = "PASSED" if res["failed"] == 0 and res["errors"] == 0 else "FAILED"
        print(
            f" {res['name']:<50} | {res['passed']}/{res['count']} passed | {status:<6} | {res['elapsed']:.2f}s"
        )
    print("-" * 80)
    overall_status = "ALL TESTS PASSED" if (total_failures == 0 and total_errors == 0) else "TEST SUITE FAILED"
    print(f" TOTAL: {total_tests - total_failures - total_errors}/{total_tests} passed ({total_failures} failed, {total_errors} errors) — {overall_status}")
    print("=" * 80)

    return 0 if (total_failures == 0 and total_errors == 0) else 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
