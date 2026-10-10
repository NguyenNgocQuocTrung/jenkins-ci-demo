
import os
import re
import sys
from pathlib import Path

image = os.environ.get("IMAGE")
if not image:
    sys.exit("ERROR: IMAGE environment variable is not set")

path = Path(sys.argv[1] if len(sys.argv) > 1 else
            "jenkins-demo/deployment.yaml")

if not path.is_file():
    sys.exit(f"ERROR: Manifest not found: {path}")

content = path.read_text()

pattern = r"(?m)^(\s*image:\s*).+$"
matches = list(re.finditer(pattern, content))

if len(matches) != 1:
    sys.exit(
        f"ERROR: Expected exactly one image field, found {len(matches)}"
    )

updated = re.sub(
    pattern,
    lambda match: match.group(1) + image,
    content,
    count=1,
)

if updated == content:
    print(f"Image is already up to date: {image}")
else:
    path.write_text(updated)
    print(f"Updated image to: {image}")
