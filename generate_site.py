import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin, unquote
import re

BASE_URL = "http://172.16.50.14/DHAKA-FLIX-14/KOREAN%20TV%20%26%20WEB%20Series/"

def clean_movie_name(href):
    pattern = r'/?DHAKA-FLIX-14/KOREAN TV & WEB Series/'
    name = re.sub(pattern, '', unquote(href))
    return name.rstrip('/')

def check_poster_formats(url):
    poster_formats = [
        'a_AL_.jpg',
        'a_VL_.jpg',
        'a_A1_.jpg',
        'a_V1_.jpg',
        'a11.jpg',
        'a22.jpg',
        'a20.jpg',
        'ae.jpg',
        'a_AL_.jpeg',
        'a_A1_.jpeg',
        'a1_.jpeg',
        'a.1_.jpeg',
        'a0_AL_.jpg',
        'a234.jpg',
        'aV1_.jpg',
        'a._V1_.jpg',
        'aer.jpeg',
        'a0.jpg',
        'a06_.jpg',
        'a606_.jpg',
        'aa06_.jpg',
        'a35.jpg',
        'age.jpg',
        'aou.jpg',
        'a58.jpg',
        'a_b.jpg',
        'poster.jpg',
        'cover.jpg'
    ]
    
    for format in poster_formats:
        poster_url = urljoin(url, format)
        try:
            response = requests.head(poster_url, timeout=1)
            if response.status_code == 200:
                return poster_url
        except:
            continue
    
    return None

def get_movies():
    try:
        response = requests.get(BASE_URL)
        soup = BeautifulSoup(response.text, 'html.parser')
        movies = []

        for link in soup.find_all('a'):
            href = link.get('href')
            if href and not href.startswith('?') and href != '../':
                name = clean_movie_name(href)
                url = urljoin(BASE_URL, href)
                poster = check_poster_formats(url)
                
                if poster:  # Only add movies with valid posters
                    movies.append({
                        'name': name,
                        'url': url,
                        'poster': poster
                    })
                    print(f"Added: {name} (with poster)")
                else:
                    print(f"Warning: No poster found for {name}")
                    # Add movie with default poster
                    movies.append({
                        'name': name,
                        'url': url,
                        'poster': 'https://via.placeholder.com/300x450.png?text=No+Poster'
                    })
        
        return sorted(movies, key=lambda x: x['name'])
    except Exception as e:
        print(f"Error: {e}")
        return []

def generate_html(movies):
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Korean Series Browser</title>
    <style>
        body { background: #f0f0f0; margin: 0; font-family: Arial, sans-serif; }
        .movie-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 20px; padding: 20px; }
        .movie-card { background: #fff; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); transition: transform 0.2s; cursor: pointer; overflow: hidden; }
        .movie-card:hover { transform: translateY(-5px); }
        .movie-poster { width: 100%; height: 300px; object-fit: cover; border-radius: 8px 8px 0 0; }
        .movie-title { padding: 10px; font-size: 14px; text-align: center; color: #333; }
        .search-container { padding: 20px; text-align: center; position: sticky; top: 0; background: #f0f0f0; z-index: 100; }
        #searchInput { padding: 10px; width: 80%; max-width: 500px; border: 1px solid #ddd; border-radius: 4px; font-size: 16px; }
        .no-poster { 
            height: 300px; 
            background: #ddd; 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            padding: 10px; 
            color: #666;
            text-align: center;
            font-size: 14px;
            line-height: 1.4;
        }
    </style>
</head>
<body>
    <div class="search-container">
        <input type="text" id="searchInput" placeholder="Search movies...">
    </div>
    <div class="movie-grid" id="movieGrid"></div>

    <script>
        const movies = ''' + json.dumps(movies) + ''';

        function displayMovies(moviesToShow) {
            const movieGrid = document.getElementById('movieGrid');
            movieGrid.innerHTML = '';
            
            moviesToShow.forEach(movie => {
                const card = document.createElement('div');
                card.className = 'movie-card';
                
                card.innerHTML = `
                    <div class="poster-container">
                        <img class="movie-poster" 
                             src="${movie.poster}" 
                             onerror="this.parentElement.innerHTML='<div class=\\'no-poster\\'>${movie.name}<br><small>No Poster Available</small></div>'"
                             alt="${movie.name}">
                    </div>
                    <div class="movie-title">${movie.name}</div>
                `;
                
                card.onclick = () => window.open(movie.url, '_blank');
                movieGrid.appendChild(card);
            });
        }

        document.getElementById('searchInput').addEventListener('input', (e) => {
            const searchTerm = e.target.value.toLowerCase();
            const filteredMovies = movies.filter(movie => 
                movie.name.toLowerCase().includes(searchTerm)
            );
            displayMovies(filteredMovies);
        });

        displayMovies(movies);
    </script>
</body>
</html>'''
    
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"Generated index.html with {len(movies)} movies")

if __name__ == '__main__':
    print("Fetching movies...")
    movies = get_movies()
    print(f"Found {len(movies)} movies")
    print("Generating HTML...")
    generate_html(movies)
    print("Done!")
