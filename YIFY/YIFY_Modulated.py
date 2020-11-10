# python 3.9

import os
import requests as rq
from bs4 import BeautifulSoup

class YIFY:
    def __init__(self):        
        self.save_path = ''
        self.base_url = r'https://yts-subs.com/'
        self.movies : list[dict[str, str]] = []
        self.subtitles : list[dict[str, str]] = []

        if os.name == 'nt':
            self.save_path = os.popen('ECHO %USERPROFILE%').read().replace('\n', '') + r'\Downloads'
        else:
            self.save_path = os.path.join(os.path.expanduser('~'), 'downloads')


    def search(self, search_term : str) -> dict[str, str]:
        '''
        Get search term as an input and return a dictionary 
        full of movies and their links
        '''
        search_url = f'{self.base_url}search/ajax?mov={search_term}'                
        search_response = rq.get(search_url)

        if search_response.status_code == 200:
            json_response = search_response.json()

            for movie in json_response:
                title = movie['mv_mainTitle']
                movie_code = movie['mv_imdbCode']
                link = f'{self.base_url}movie-imdb/{movie_code}'
                item = {'title':title, 'link':link}                
                self.movies.append(item)
            
            return self.movies
        
        else:
            raise Exception('Search Request Failed')


    def get_subtitles(self, movie_link : str, lang='English') -> dict[str, str]:
        '''
        Get movie link and language(Optional) and return dictionary 
        full of above language's subtitles and their links
        '''
        movie_response = rq.get(movie_link)
        lang = lang.title()

        if movie_response.status_code == 200:
            soup = BeautifulSoup(movie_response.content, 'html.parser')
            rows = soup.find_all('tr', class_='high-rating')

            for row in rows:
                td = row.find('td', class_='flag-cell')                
                sub_link_tag = row.find('td', class_='download-cell')
                sub_link = sub_link_tag.find('a', class_='subtitle-download').get('href')
                sub_link = f'{self.base_url}{sub_link}'
                sub_name_tag = row.find('td', class_=None)
                sub_name = str(sub_name_tag.find('a').text).replace('subtitle', '').replace('\n', '')
                language = td.find('span', class_='sub-lang').text
                sub = {'sub_name':sub_name, 'link':sub_link}
                
                if lang == 'All':
                    self.subtitles.append(sub)

                elif language == lang:
                    self.subtitles.append(sub)

            return self.subtitles

        else:
            raise Exception('Subtitle Request Failed')


    def download_subtitle(self, sub_link : str):
        '''
        Get subtitle's page link(not direct subtitle download link)
        and download subtitle
        '''
        subtitle_response = rq.get(sub_link)

        if subtitle_response.status_code == 200:
            soup = BeautifulSoup(subtitle_response.content, 'html.parser')
            link = soup.find('a', class_='btn-icon download-subtitle').get('href')
            sub_name = soup.find('div', style='margin-bottom:15px;').text.strip()
            
            final_response = rq.get(link, stream=True)

            if final_response.status_code == 200:                
                with open(f'{self.save_path}\\{sub_name}.zip', 'wb') as sfile:
                    for byte in final_response.iter_content(chunk_size=128):
                        sfile.write(byte)
                print(f'[!] {sub_name}.zip downloaded. Check downloads directory.\n')
            
            else:
                raise Exception('Subtitle Download Failed')

        else:
            raise Exception('Subtitle Request Failed')


    def download_all_subtitles(self, movie_link : str, lang='All'):
        '''
        Download Specific movie's all subtitle belongs to 
        specific language

        params
            movie_link : Movie's link to download subtitles
            lang : Subtitle language. Default is all languages
        '''
        sub_links : list[dict[str, str]] = self.get_subtitles(movie_link, lang)
        for sub in sub_links:
            self.download_subtitle(sub['link'])



# yify = YIFY()

# movie = input('Movie: ').strip()
# movies = yify.search(movie)

# for i,item in enumerate(movies):
#     print(f"{i}.{item['title']}")

# ui = int(input('Sub: ').strip())
# yify.download_all_subtitles(movies[ui]['link'])

