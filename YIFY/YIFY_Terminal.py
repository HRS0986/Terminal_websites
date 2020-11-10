import os
import art
from colorama import init, Fore
import requests as rq
from bs4 import BeautifulSoup

if os.name == 'nt':
    SAVE_PATH = os.popen('ECHO %USERPROFILE%').read().replace('\n', '') + r'\Downloads'
else:
    SAVE_PATH = os.path.join(os.path.expanduser('~'), 'downloads')

init(convert=True)
print(Fore.BLUE + art.text2art('YIFY Subtitles'))

print(Fore.YELLOW)
keyword = input('[+] Enter Movie Name: ').strip()
print(Fore.RESET)

# Search URL
URL = f'https://yts-subs.com/search/ajax?mov={keyword}'

try:
    search_response = rq.get(URL)

    if search_response.status_code == 200:
        search_result : list = search_response.json()

        if search_result:

            # Display search result
            print(Fore.CYAN + '\n[!] Search Result:')
            for ind,movie in enumerate(search_result, 1):
                title = movie['mv_mainTitle']
                print(f'\t{ind}.{title}')

            # User input a number from displayed movies
            print(Fore.YELLOW)
            indx = int(input('\n[+] Enter Movie Number: ').strip()) - 1
            print(Fore.RESET)

            movie_code : str = search_result[indx]['mv_imdbCode']
            movie_url = f'https://yts-subs.com/movie-imdb/{movie_code}'

            movie_response = rq.get(movie_url)

            if movie_response.status_code == 200:

                subtitles, i = [], 1

                print(Fore.CYAN + '\n[!] English Subtitles:' + Fore.RESET)

                # Scraping Data From Page Source
                soup1 = BeautifulSoup(movie_response.content, 'html.parser')
                rows = soup1.find_all('tr', class_='high-rating')

                for row in rows:
                    td = row.find('td', class_='flag-cell')
                    lang = td.find('span', class_='sub-lang').text
                    # Filter English Subtitles
                    if lang == 'English':
                        sub_link_tag = row.find('td', class_='download-cell')
                        sub_link = sub_link_tag.find('a', class_='subtitle-download').get('href')
                        sub_link = f'https://yts-subs.com/{sub_link}'
                        sub_name_tag = row.find('td', class_=None)
                        sub_name = str(sub_name_tag.find('a').text).replace('subtitle', '').replace('\n', '')       
                        sub = (sub_name, sub_link)
                        subtitles.append(sub)
                        print(Fore.CYAN + f'\t{i}.{sub_name}' + Fore.RESET)
                        i += 1

                print(Fore.YELLOW)
                sub_no = int(input('\n[+] Enter Subtitle Number To Download: ').strip()) - 1
                print(Fore.RESET)
                selected_sub_link = subtitles[sub_no][1]
                selected_sub_name = subtitles[sub_no][0]

                sub_response = rq.get(selected_sub_link)

                if sub_response.status_code == 200:

                    soup2 = BeautifulSoup(sub_response.content, 'html.parser')
                    link = soup2.find('a', class_='btn-icon download-subtitle').get('href')

                    final_response = rq.get(link, stream=True)

                    if final_response.status_code == 200:

                        # Download Subtitle
                        with open(f'{SAVE_PATH}\\{selected_sub_name}.zip', 'wb') as sfile:
                            for byte in final_response.iter_content(chunk_size=128):
                                sfile.write(byte)

                        print(Fore.GREEN + '[!] Subtitle Downloaded. Check Downloads Directory\n' + Fore.RESET)
                    
                    else:
                        print(Fore.RED + f'Error : Status Code - {search_response.status_code}\n' + Fore.RESET)

                else:
                    print(Fore.RED + f'Error : Status Code - {search_response.status_code}\n' + Fore.RESET)
                
            else:
                print(Fore.RED + f'Error : Status Code - {search_response.status_code}\n' + Fore.RESET)
        
        else:
            print(Fore.RED + '[!] Not Found.\n' + Fore.RESET)

    else:
        print(Fore.RED + f'Error : Status Code - {search_response.status_code}\n' + Fore.RESET)

except Exception as e:
    print(Fore.RED + f'Error : {e}' + Fore.RESET)