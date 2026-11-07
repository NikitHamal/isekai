#!/usr/bin/env python3
"""Close-up preview: python3 tools/closeup.py model.glb out.png [node-prefix=head] -- 3 shaded views (front, 3/4, side) of the matching nodes."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import qa_asset as q
from PIL import Image
g, b = q.load(sys.argv[1]); pre = sys.argv[3] if len(sys.argv) > 3 else "head"; pr = [p for p in q.flatten(g, b) if p["name"].startswith(pre)]
sh = Image.new("RGB", (1536, 512)); [sh.paste(q.render(pr, g, b, "shaded", y, .08), (i * 512, 0)) for i, y in enumerate((0.0, -.7, -1.5))]; sh.save(sys.argv[2])
