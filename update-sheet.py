#!/usr/bin/env python3
import os
import logging
from datetime import datetime

SOURCE_PATH = "/home/etl4tech_gmail_com/google-drive/othertrax/"
OUTPUT_FILE = "/var/www/html/othertrax.html"

logging.basicConfig(
    filename="/var/tmp/kf-offmenu.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logging.getLogger("googleapiclient.discovery_cache").setLevel(logging.ERROR)


def list_tracks():
    rows = []
    for fname in sorted(os.listdir(SOURCE_PATH)):
        if fname.endswith(".mp4"):
            mtime = os.path.getmtime(os.path.join(SOURCE_PATH, fname))
            name = fname[:-4]
            parts = name.split(" - ", 1)
            artist, title = (parts[0], parts[1]) if len(parts) == 2 else (parts[0], "")
            rows.append((mtime, artist, title))
    return rows


def write_html(rows):
    rows_newest_first = sorted(rows, key=lambda r: r[0], reverse=True)
    rows_html = ""
    for mtime, artist, title in rows_newest_first:
        date_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
        rows_html += f'  <tr><td>{artist}</td><td>{title}</td><td>{date_str}</td></tr>\n'

    html = f"""<!DOCTYPE html>
<html>
<head>
  <title>Othertrax</title>
  <style>
    body {{ font-family: Arial, sans-serif; }}
    table {{ border-collapse: collapse; }}
    th, td {{ border: 1px solid #ccc; padding: 6px 12px; }}
    th {{ cursor: pointer; background: #eee; }}
  </style>
</head>
<body>
  <h2>Othertrax</h2>
  <p>Sort by: <a href="?sort=date">Newest First</a> | <a href="?sort=artist">Artist A-Z</a></p>
  <table id="tracks">
    <thead><tr><th>Artist</th><th>Title</th><th>Added</th></tr></thead>
    <tbody>
{rows_html}    </tbody>
  </table>
  <script>
    const params = new URLSearchParams(window.location.search);
    if (params.get('sort') === 'artist') {{
      const tbody = document.querySelector('#tracks tbody');
      Array.from(tbody.rows)
        .sort((a, b) => a.cells[0].textContent.localeCompare(b.cells[0].textContent))
        .forEach(r => tbody.appendChild(r));
    }}
  </script>
</body>
</html>"""

    with open(OUTPUT_FILE, "w") as f:
        f.write(html)
    logging.info(f"Wrote {len(rows)} tracks to {OUTPUT_FILE}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--test", action="store_true")
    args = parser.parse_args()
    try:
        rows = list_tracks()
        if args.test:
            print(f"Would write {len(rows)} tracks to {OUTPUT_FILE}")
        else:
            write_html(rows)
    except Exception as e:
        logging.error(f"Failed: {e}")
