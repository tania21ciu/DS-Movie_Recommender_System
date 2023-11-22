import streamlit as st
import pickle
import pandas as pd
import requests 
from concurrent.futures import ThreadPoolExecutor
import time

movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

def fetch_poster(movie_id):
    # read access token
    # eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJkYTdjYjU2NDkyY2VmOTZmY2I5OGE2OThkYTExNWNjOCIsInN1YiI6IjY1NDllZTllOTI0Y2U2MDBhZGIwNDlkNCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.jNgJhS0SfEYkPwVKwOj6pwkhvxSroLaYx9nSk09RWmE

    # API key
    # da7cb56492cef96fcb98a698da115cc8

    response = requests.get('https://api.themoviedb.org/3/movie/{}?api_key=da7cb56492cef96fcb98a698da115cc8&language=en-US'.format(movie_id))
    data = response.json()
    return "https://image.tmdb.org/t/p/w500/" + data['poster_path']

def recommend(movie):
    start_time = time.time()

    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_poster = []

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(fetch_poster, movies.iloc[i[0]].movie_id) for i in movies_list]

    for i, future in enumerate(futures):
        recommended_movies.append(movies.iloc[movies_list[i][0]].title)
        recommended_movies_poster.append(future.result())

    end_time = time.time() 
    execution_time = end_time - start_time
    st.write(f"Execution Time: {execution_time:.2f} seconds")

    # for i in movies_list:
    #     movie_id = movies.iloc[i[0]].movie_id

    #     recommended_movies.append(movies.iloc[i[0]].title)
    #     recommended_movies_poster.append(fetch_poster(movie_id))

    return recommended_movies, recommended_movies_poster

st.title('Movie Recommender System')

selected_movie_name = st.selectbox( "Type or select a movie from the dropdown", movies['title'])

if st.button('Recommend'):
    names, posters = recommend(selected_movie_name)

    col_objects = st.columns(5)  
    for i in range(5):
        with col_objects[i]:
            st.text(names[i])
            st.image(posters[i])