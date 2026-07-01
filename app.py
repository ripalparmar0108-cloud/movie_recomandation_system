import streamlit as st
import pickle
import pandas as pd
import requests
import os

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(
    page_title="Movie Recommender",
    page_icon="🎬",
    layout="wide"
)

API_KEY = "94ff7ab39fef18638eb9b2b3997cf2e3"

# ---------------------------------------------------
# LOAD DATA
# ---------------------------------------------------
print("movies_dict.pkl exists:", os.path.exists("movies_dict.pkl"))
print("movies_dict.pkl size:", os.path.getsize("movies_dict.pkl"))

with open("movies_dict.pkl", "rb") as f:
    movies_dict = pickle.load(f)


movies = pd.DataFrame(movies_dict)


with open("similarity.pkl", "rb") as f:
    data = pickle.load(f)

# ---------------------------------------------------
# SESSION STATE
# ---------------------------------------------------
if "page" not in st.session_state:
    st.session_state.page = "home"

if "selected_movie_id" not in st.session_state:
    st.session_state.selected_movie_id = None

if "recommendations" not in st.session_state:
    st.session_state.recommendations = None

if "user_ratings" not in st.session_state:
    st.session_state.user_ratings = {}

# ---------------------------------------------------
# FUNCTIONS
# ---------------------------------------------------
def fetch_movie_details(movie_id):

    response = requests.get(
        f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
    )

    data = response.json()

    poster = (
        "https://image.tmdb.org/t/p/w500"
        + data.get("poster_path", "")
    )

    rating = data.get(
        "vote_average",
        "N/A"
    )

    return poster, rating


def recommend(movie):

    movie_index = movies[
        movies["title"] == movie
    ].index[0]

    distances = similarity[
        movie_index
    ]

    movies_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    names = []
    posters = []
    ratings = []
    movie_ids = []

    for i in movies_list:

        movie_id = movies.iloc[
            i[0]
        ].movie_id

        poster, rating = fetch_movie_details(
            movie_id
        )

        names.append(
            movies.iloc[
                i[0]
            ].title
        )

        posters.append(
            poster
        )

        ratings.append(
            rating
        )

        movie_ids.append(
            movie_id
        )

    return (
        names,
        posters,
        ratings,
        movie_ids
    )


def show_movie_details(movie_id):

    response = requests.get(
        f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
    )

    data = response.json()

    poster = (
        "https://image.tmdb.org/t/p/w500"
        + data.get(
            "poster_path",
            ""
        )
    )

    col1, col2 = st.columns(
        [1, 2]
    )

    with col1:

        st.image(
            poster,
            use_container_width=True
        )

    with col2:

        st.title(
            data.get(
                "title",
                ""
            )
        )

        st.write(
            f"⭐ Rating: {data.get('vote_average', 'N/A')}"
        )

        st.write(
            f"📅 Release Date: {data.get('release_date', 'N/A')}"
        )

        st.write(
            f"⏱ Runtime: {data.get('runtime', 'N/A')} minutes"
        )

        genres = ", ".join(
            [
                genre["name"]
                for genre in data.get(
                    "genres",
                    []
                )
            ]
        )

        st.write(
            f"🎭 Genres: {genres}"
        )

        st.subheader(
            "Overview"
        )

        st.write(
            data.get(
                "overview",
                "No overview available."
            )
        )

    st.write("")

    if st.button("⬅ Back"):

        st.session_state.page = "home"

        st.rerun()

# ---------------------------------------------------
# HOME PAGE
# ---------------------------------------------------
if st.session_state.page == "home":

    st.title(
        "🎬 Movie Recommender System"
    )

    selected_movie_name = st.selectbox(
        "Choose a movie you like:",
        movies["title"].values
    )

    if st.button(
        "Recommend"
    ):

        names, posters, ratings, movie_ids = recommend(
            selected_movie_name
        )

        st.session_state.recommendations = {

            "names": names,

            "posters": posters,

            "ratings": ratings,

            "movie_ids": movie_ids
        }

    if st.session_state.recommendations:

        names = st.session_state.recommendations[
            "names"
        ]

        posters = st.session_state.recommendations[
            "posters"
        ]

        ratings = st.session_state.recommendations[
            "ratings"
        ]

        movie_ids = st.session_state.recommendations[
            "movie_ids"
        ]

        cols = st.columns(5)

        for i in range(5):

            with cols[i]:

                st.image(
                    posters[i],
                    use_container_width=True
                )

                st.subheader(
                    names[i]
                )

                st.write(
                    f"⭐ TMDB Rating: {ratings[i]}"
                )

                rating = st.radio(
                    "Rate Movie",
                    [1, 2, 3, 4, 5],
                    horizontal=True,
                    key=f"movie_rating_{i}"
                )

                st.session_state.user_ratings[
                    names[i]
                ] = rating

                st.write(
                    f"You rated: {'⭐' * rating}"
                )

                if st.button(
                    "🎬 View Details",
                    key=f"details_{i}"
                ):

                    st.session_state.selected_movie_id = (
                        movie_ids[i]
                    )

                    st.session_state.page = "details"

                    st.rerun()

# ---------------------------------------------------
# DETAILS PAGE
# ---------------------------------------------------
elif st.session_state.page == "details":

    show_movie_details(
        st.session_state.selected_movie_id
    )
