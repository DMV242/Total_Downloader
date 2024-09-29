from flask import Flask, request, jsonify, render_template, send_file
import yt_dlp
import os
import tempfile

app = Flask(__name__)

# Spécifiez ici le chemin vers votre fichier de cookies sur le serveur
COOKIES_FILE = "/chemin/vers/votre/fichier/cookies.txt"


def afficher_options(formats):
    options = []
    for i, format in enumerate(formats, 1):
        format_info = f"{i}. {format['format_id']} - {format['ext']}"
        if "width" in format and "height" in format:
            format_info += f" ({format['width']}x{format['height']})"
            format_info += ' <span class="badge badge-video">Vidéo</span>'
        else:
            format_info += ' <span class="badge badge-audio">Audio</span>'
        options.append({"id": i, "info": format_info})
    return options


@app.route("/youtubedl")
def landing():
    return render_template("landing.html")


@app.route("/youtubedl/app")
def index():
    return render_template("index.html")


@app.route("/youtubedl/telecharger", methods=["POST"])
def telecharger_contenu():
    data = request.json
    platform = data.get("platform")
    url = data.get("url")

    try:
        ydl_opts = {
            "outtmpl": os.path.join(tempfile.gettempdir(), "%(title)s.%(ext)s"),
            "cookiefile": COOKIES_FILE,  # Utilisation du fichier de cookies spécifié
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info["formats"]

            options = afficher_options(formats)

            return jsonify({"options": options})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/youtubedl/telecharger/choix", methods=["POST"])
def telecharger_choix():
    data = request.json
    platform = data.get("platform")
    url = data.get("url")
    choix = data.get("choix")

    try:
        ydl_opts = {
            "outtmpl": os.path.join(tempfile.gettempdir(), "%(title)s.%(ext)s"),
            "cookiefile": COOKIES_FILE,  # Utilisation du fichier de cookies spécifié
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info["formats"]

            if 1 <= choix <= len(formats):
                format_id = formats[choix - 1]["format_id"]
                ydl_opts["format"] = format_id
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])

                # Récupérer le chemin du fichier téléchargé
                downloaded_file = ydl.prepare_filename(info)
                return jsonify(
                    {
                        "download_url": f"/youtubedl/download/{os.path.basename(downloaded_file)}"
                    }
                )
            else:
                return jsonify({"error": "Choix invalide."}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/youtubedl/download/<filename>")
def download_file(filename):
    return send_file(os.path.join(tempfile.gettempdir(), filename), as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
