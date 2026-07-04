from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)
app.config["APPLICATION_ROOT"] = "/song-requests"  # add this

SONG_FILE = "requested-songz.txt"

NAMES = ["Jim", "Rad John", "Sammy G", "Taylor F", "Zeb", "ErikNerd"]  # update as needed

def load_songs():
    if not os.path.exists(SONG_FILE):
        return []
    with open(SONG_FILE) as f:
        songs = []
        for line in f:
            parts = line.strip().split("|")
            if len(parts) == 3:
                songs.append(parts)
        return songs

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form.get("name")
        artist = request.form.get("artist", "").strip()
        title = request.form.get("title", "").strip()
        if name and artist and title:
            with open(SONG_FILE, "a") as f:
                f.write(f"{name}|{artist}|{title}\n")
        return redirect("/song-requests/")
    return render_template("songz2do.html", names=NAMES, songs=load_songs())

@app.route("/delete", methods=["POST"])
def delete():
    idx = int(request.form.get("idx"))
    songs = load_songs()
    if 0 <= idx < len(songs):
        songs.pop(idx)
        with open(SONG_FILE, "w") as f:
            for s in songs:
                f.write("|".join(s) + "\n")
    return redirect("/song-requests/")

if __name__ == "__main__":
    app.run(debug=True)
