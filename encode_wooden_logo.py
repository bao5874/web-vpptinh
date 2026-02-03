#!/usr/bin/env python
# -*- coding: utf-8 -*-
import base64
import os

# Your wooden logo - create a placeholder with better branding
# Since we can't directly embed the image file, use a high-quality placeholder
# that represents VPP (office supplies) with wood texture feel

WOODEN_LOGO_SVG = '''<svg width="50" height="50" viewBox="0 0 50 50" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <radialGradient id="woodGrad" cx="40%" cy="40%">
      <stop offset="0%" style="stop-color:#d4a574;stop-opacity:1" />
      <stop offset="50%" style="stop-color:#a8825a;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#7a5e42;stop-opacity:1" />
    </radialGradient>
  </defs>
  <!-- Wood texture background -->
  <circle cx="25" cy="25" r="24" fill="url(#woodGrad)" stroke="#5c3d1a" stroke-width="1"/>
  <!-- Wood grain lines -->
  <line x1="10" y1="15" x2="40" y2="18" stroke="#6b5340" stroke-width="0.5" opacity="0.6"/>
  <line x1="8" y1="25" x2="42" y2="27" stroke="#6b5340" stroke-width="0.5" opacity="0.6"/>
  <line x1="12" y1="35" x2="38" y2="33" stroke="#6b5340" stroke-width="0.5" opacity="0.6"/>
  <!-- Pen icon -->
  <g transform="translate(15, 18)">
    <rect x="0" y="0" width="3" height="12" fill="none" stroke="#fff" stroke-width="1.5" rx="1.5"/>
    <circle cx="1.5" cy="13" r="1" fill="#fff"/>
  </g>
  <!-- Paper icon -->
  <g transform="translate(23, 18)">
    <rect x="0" y="0" width="5" height="8" fill="none" stroke="#fff" stroke-width="1" rx="0.5"/>
    <line x1="1" y1="2" x2="4" y2="2" stroke="#fff" stroke-width="0.5"/>
    <line x1="1" y1="4" x2="4" y2="4" stroke="#fff" stroke-width="0.5"/>
  </g>
  <!-- Ruler icon -->
  <g transform="translate(12, 32)">
    <rect x="0" y="0" width="10" height="2" fill="none" stroke="#fff" stroke-width="1" rx="0.5"/>
    <line x1="2" y1="-0.5" x2="2" y2="2.5" stroke="#fff" stroke-width="0.5"/>
    <line x1="5" y1="-0.5" x2="5" y2="2.5" stroke="#fff" stroke-width="0.5"/>
    <line x1="8" y1="-0.5" x2="8" y2="2.5" stroke="#fff" stroke-width="0.5"/>
  </g>
</svg>'''

encoded = base64.b64encode(WOODEN_LOGO_SVG.encode()).decode()
print("Wood-textured logo (base64):")
print(f"data:image/svg+xml;base64,{encoded}")
print("\nLength:", len(encoded))
