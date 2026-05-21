import requests
from flask import Flask, render_template, request

app = Flask(__name__)

API_URL = "https://graphql.anilist.co"

QUERY = """
query ($search: String) {
  Media(search: $search, type: ANIME) {
    title {
      romaji
      english
      native
    }
    coverImage {
      large
      extraLarge
      medium
    }
    genres
    averageScore
    description(asHtml: false)
    recommendations(sort: RATING_DESC) {
      nodes {
        mediaRecommendation {
          title {
            romaji
            english
          }
          coverImage {
            large
            medium
          }
          genres
          averageScore
        }
      }
    }
  }
}
"""


def get_anime(anime_name):
    variables = {"search": anime_name}
    response = requests.post(
        API_URL,
        json={"query": QUERY, "variables": variables},
        headers={"Content-Type": "application/json"},
        timeout=10,
    )
    response.raise_for_status()
    payload = response.json()

    if payload.get("errors"):
        raise ValueError(payload["errors"][0].get("message", "AniList API error"))

    media = payload.get("data", {}).get("Media")
    if not media:
        return None

    title_data = media.get("title", {})
    main_title = title_data.get("romaji") or title_data.get("english") or title_data.get("native") or "Unknown"
    cover_image = media.get("coverImage", {}).get("large") or media.get("coverImage", {}).get("extraLarge") or media.get("coverImage", {}).get("medium") or ""

    recommendations = []
    for rec in media.get("recommendations", {}).get("nodes", [])[:8]:
        rec_media = rec.get("mediaRecommendation") or {}
        rec_title = rec_media.get("title", {})
        recommendations.append({
            "title": rec_title.get("romaji") or rec_title.get("english") or "Unknown",
            "image": rec_media.get("coverImage", {}).get("large") or rec_media.get("coverImage", {}).get("medium") or "",
            "genres": rec_media.get("genres", []),
            "score": rec_media.get("averageScore") or "N/A",
        })

    return {
        "title": main_title,
        "image": cover_image,
        "genres": media.get("genres", []),
        "score": media.get("averageScore") or "N/A",
        "description": media.get("description") or "No description available.",
        "recommendations": recommendations,
    }


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/recommend", methods=["POST"])
def recommend():
    anime_name = request.form.get("anime", "").strip()
    error = None
    anime_data = None

    if anime_name:
        try:
            anime_data = get_anime(anime_name)
            if not anime_data:
                error = f"No anime found for '{anime_name}'."
        except requests.RequestException:
            error = "Unable to reach AniList API. Please try again later."
        except ValueError as exc:
            error = str(exc)
    else:
        error = "Please enter an anime name."

    return render_template("result.html", anime=anime_data, error=error)


if __name__ == "__main__":
    app.run(debug=True)
