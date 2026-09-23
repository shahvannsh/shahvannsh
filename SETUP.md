# Setup

1. Create the repo (must be named exactly your username):
   gh repo create shahvannsh --public --clone
   cd shahvannsh
   # copy all files from this delivery into it

2. Install deps locally (for regenerating the portrait when you change photos):
   pip install pillow numpy opencv-python-headless rembg onnxruntime

3. Put a well-lit, tightly-cropped photo (chin to above hair, 1200px+, side light)
   at scripts/cropped_input.jpg, then:
   python3 scripts/generate_portrait.py scripts/cropped_input.jpg portrait.svg

   Note: the included portrait.svg was generated WITHOUT background removal
   (rembg needs network access this sandbox didn't have). Regenerate it once
   locally with rembg installed for a clean white background — the pipeline
   already calls remove_background() automatically when rembg is present.

4. Push. The refresh-stats.yml workflow generates stats.svg/streak.svg/
   langs.svg/year.svg automatically on a nightly cron using the built-in
   GITHUB_TOKEN — no PAT needed, no local run required for stats.

5. git add -A && git commit -m "init" && git push

6. If the README doesn't show up on your profile immediately, edit it once
   via the GitHub web UI to force a cache refresh.
