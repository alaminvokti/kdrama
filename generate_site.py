import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin, unquote
import re
import base64

BASE_URL = "http://172.16.50.14/DHAKA-FLIX-14/KOREAN%20TV%20%26%20WEB%20Series/"
IMGBB_API_KEY = "7a087bec0d3c6db259d7f228d0db08b8"

def clean_movie_name(href):
    pattern = r'/?DHAKA-FLIX-14/KOREAN TV & WEB Series/'
    name = re.sub(pattern, '', unquote(href))
    return name.rstrip('/')

def upload_to_imgbb(image_url):
    try:
        img_response = requests.get(image_url)
        if img_response.status_code == 200:
            base64_image = base64.b64encode(img_response.content).decode('utf-8')
            
            url = "https://api.imgbb.com/1/upload"
            payload = {
                "key": IMGBB_API_KEY,
                "image": base64_image,
            }
            
            response = requests.post(url, payload)
            data = response.json()
            
            if data["success"]:
                return data["data"]["url"]
    except:
        pass
    return "https://i.ibb.co/wJqR9Pn/no-poster.jpg"

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
                poster_url = url + 'a_AL_.jpg'
                imgbb_url = upload_to_imgbb(poster_url)
                
                movies.append({
                    'name': name,
                    'url': url,
                    'poster': imgbb_url
                })
                print(f"Added: {name}")
        
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
