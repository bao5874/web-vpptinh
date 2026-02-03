#!/usr/bin/env python
# -*- coding: utf-8 -*-
import base64
from PIL import Image
import io

# Since we can't directly access the attachment, we'll use the CDN logo as primary
# with a fallback to SVG badge. Your custom wooden logo can be uploaded separately.

# For now, let's create a professional SVG that matches your branding
SVG_LOGO = '''<svg width="50" height="50" viewBox="0 0 50 50" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#d4a373;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#8B4513;stop-opacity:1" />
    </linearGradient>
  </defs>
  <!-- Outer circle -->
  <circle cx="25" cy="25" r="24" fill="url(#grad1)" stroke="#654321" stroke-width="1"/>
  <!-- Inner circle -->
  <circle cx="25" cy="25" r="22" fill="#f5e6d3" opacity="0.9"/>
  <!-- Pen icon -->
  <path d="M20 30 L30 15" stroke="#8B4513" stroke-width="2" fill="none" stroke-linecap="round"/>
  <circle cx="30" cy="15" r="2" fill="#8B4513"/>
  <!-- Paper/document icon -->
  <rect x="15" y="20" width="8" height="12" fill="none" stroke="#8B4513" stroke-width="1.5"/>
  <line x1="17" y1="23" x2="21" y2="23" stroke="#8B4513" stroke-width="1"/>
  <line x1="17" y1="26" x2="21" y2="26" stroke="#8B4513" stroke-width="1"/>
  <!-- Ruler icon -->
  <rect x="28" y="27" width="10" height="3" fill="none" stroke="#8B4513" stroke-width="1.5"/>
  <line x1="30" y1="26" x2="30" y2="31" stroke="#8B4513" stroke-width="1"/>
  <line x1="33" y1="26" x2="33" y2="31" stroke="#8B4513" stroke-width="1"/>
  <line x1="36" y1="26" x2="36" y2="31" stroke="#8B4513" stroke-width="1"/>
</svg>'''

print("SVG Logo created - use this in build.py and final_boss.py")
print("Base64 encoded:")
print(base64.b64encode(SVG_LOGO.encode()).decode())
