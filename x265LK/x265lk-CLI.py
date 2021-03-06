from art import tprint
import requests as rq 
from colorama import init, Fore
import random
import os
from tqdm import tqdm
from bs4 import BeautifulSoup
from PyInquirer import prompt
from examples import custom_style_2


init(convert=True)

CWD: str = os.getcwd()

class x265LK:

    def __init__(self):        
        self.__URL = 'https://x265lk.com/wp-json/dooplay/search/?keyword='        
        self.__seasons = []
        self.__episodes = []

    
    # Statring function
    def display_title(self):
        os.system('CLS')
        print(random.choice([Fore.LIGHTMAGENTA_EX, Fore.LIGHTBLUE_EX, Fore.LIGHTCYAN_EX]))
        tprint('x265LK', random.choice(["clossal", "banner3-d", "georgiall"]))
        print(Fore.RESET)

    
    def search(self, term:str, type='TV') -> list:
        search_url = f'{self.__URL}{term}&nonce=deec18d3b5'

        r = rq.get(search_url)
        
        if r.status_code == 200:
            search_result = r.json()
            query_data = []
            
            if 'error' in search_result.keys():               
                return -1

            for id, v in search_result.items():
                if 'tvshows' in v['url']:
                    item = { 'id': id, 'title': v['title'], 'url': v['url'] }
                    query_data.append(item)
            return query_data
        
        return (-9, r.status_code)

    
    def select_series(self, seriesList:list) -> dict:
        question = {
            'type': 'input',
            'name': 'series_no',
            'message': 'Enter Series Number:',
            'validate': lambda val: val in [*[str(i) for i in range(1, len(seriesList)+1)], '-1', '-9' ]
        }
        print(Fore.LIGHTYELLOW_EX + '[+] Search Result:')
        for ind, series in enumerate(seriesList, 1):
            print(Fore.LIGHTYELLOW_EX + f"\t{ind}. {series['title']}")
        print(Fore.RESET)

        print('[+] Enter -1 to go back')
        print('[+] Enter -9 To Exit')
        number = prompt(question, style=custom_style_2)['series_no']  

        if number == '-9':
            os.system('CLS')
            exit()

        if number.isdigit():
            series_ind = int(number) - 1                   
            return seriesList[series_ind]
        
        return number

    
    def select_season(self, series:dict) -> tuple:       
        print(Fore.LIGHTYELLOW_EX + f"[+] {series['title']} Seasons: ")
        r = rq.get(series['url'])

        if r.status_code == 200:
            html = r.text
            soup = BeautifulSoup(html, 'html.parser')
            seasonsDiv = soup.find('div', {'id': 'seasons'})
            seasons = seasonsDiv.findAll('div', {'class': 'se-c'})
            seasonCount = len(seasons)
                        
            for i, season in enumerate(seasons, 1):
                self.__seasons.append(str(season))
                print(f'\t{i}.', season.div.find('span', {'class' : 'title'}).text)
            print(Fore.RESET)

            print('[+] Enter Number To Select Episodes. Or,')
            print('[+] Enter 0<Number> to download all episodes in season.Or,')
            print('[+] Enter 0 to download all seasons')
            print('[+] Enter -1 for search again')
            print('[+] Enter -9 To Exit')
            nums = []

            try:
                question = {
                    'type': 'input',
                    'name': 'season_no',
                    'message': 'Enter Season Number:',
                    'validate': lambda val: all([int(v) in [*[i for i in range(seasonCount+1)], -1, -9] for v in val.split()])
                }
                season_number = prompt(question, style=custom_style_2)['season_no']
                nums = season_number.split()
            
            except Exception as e:
                self.display_title()
                self.select_season(series)

            # Download All Seasons
            if int(nums[0]) == 0:
                return (seasonCount, series['title'], 'A')
            
            # Go Back
            if int(nums[0]) == -1:
                return (-1, ' ', '-1')
            
            elif int(nums[0]) == -9:
                os.system('CLS')
                exit()

            # Download Full Single Season
            elif len(nums) == 1 and nums[0][0] == '0' :
                return (int(season_number), series['title'], 'a')

            # Go To Episode Selection
            elif len(nums) == 1:
                return (int(season_number), series['title'], 'e')

            else:
                full_seasons = [int(i) for i in nums]
                return (full_seasons, series['title'], 'm')

        return (-9, r.status_code, 0)

        
    def select_episode(self, season_no:int, series_name:str, ask=True) -> list[int]:
        season = self.__seasons[season_no - 1]
        soup = BeautifulSoup(season, 'html.parser')
        episodesList = soup.find('div', {'class': 'se-a'}).find('ul')

        print(Fore.LIGHTYELLOW_EX + f"[+] {series_name} Season {season_no} Episodes: ")
        for i, episode in enumerate(episodesList, 1):
            epiData = episode.find('div',{'class':'episodiotitle'}).a
            epi = {'page_url': epiData['href'], 'title':epiData.text}
            self.__episodes.append(epi)
            print(f"\t{i}. {epi['title']}")
        print(Fore.RESET)

        if not ask:
            return [i for i in range(1, len(self.__seasons)+1)]

        print('[+] Enter Episode Number. Or')
        print('[+] Enter Episode Numbers Space Seperated. Or')
        print('[+] Enter 0 To Download All')
        print('[+] Enter -2 To Go Back')
        print('[+] Enter -1 To Search TV Series')
        print('[+] Enter -9 To Exit')
        question = {
            'type': 'input',
            'name': 'epi_no',
            'message': 'Enter Episode Number:',
            'validate': lambda val: all([v in [*[str(i) for i in range(len(episodesList)+1)], str(-1), str(-2)] for v in val.split()])
        }

        epis = prompt(question, style=custom_style_2)['epi_no'].strip().split()

        if int(epis[0]) == 0:
            return [i for i in range(1, len(self.__seasons)+1)]

        if int(epis[0]) == -1:
            return [-1]

        if int(epis[0]) == -2:
            return [-2]

        epi_numbers = [int(ep) for ep in epis]
        return epi_numbers

        
    def get_ep_link(self, epi_no:int) -> str:
        r = rq.get(self.__episodes[epi_no-1]['page_url'])

        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            download_div = soup.find('div', {'id':'download'})
            link_data = download_div.find('tbody').findAll('td')[0]
            download_page_link = link_data.a['href']
            self.__episodes[epi_no]['download_page_url'] = download_page_link

            r2 = rq.get(download_page_link)

            if r2.status_code == 200:
                sp = BeautifulSoup(r2.text, 'html.parser')
                Link = sp.find('div', {'class':'inside'}).a['href']
                self.__episodes[epi_no-1]['download_url'] = Link
                print(Fore.LIGHTYELLOW_EX + f'\nLink: {Link}' + Fore.RESET)

                return (Link, epi_no-1)
            
            return (-9, r2.status_code)

        return (-9, r.status_code)


    def download(self, link:str, path:str):
        r = rq.get(link, stream=True)
        
        if r.status_code == 200:            
            ep_name = link.split('/')[-1]
            removed_site_name = ep_name.split('.')[3:]
            removed_site_name = '.'.join(removed_site_name)            
            filename = f'{path}\\{removed_site_name}'

            epi_length = int(r.headers['content-length'])
            block_size: int = 1024

            print(Fore.CYAN+f'Downloading {removed_site_name}')
            bar = tqdm(total=epi_length, unit='iB', unit_scale=True)

            with open(filename, 'wb') as episode:
                for data in r.iter_content(block_size):
                    bar.update(len(data))
                    episode.write(data)
                bar.close()
            
            if epi_length != 0 and bar.n != epi_length:
                print(Fore.RED+"ERROR, Something went wrong"+Fore.RESET)            
            else:
                print(Fore.GREEN+f'Downloaded {filename} \n'+Fore.RESET)

        else:
            print(Fore.LIGHTRED_EX + f'[!] Connection Error : {r.status_code}' + Fore.RESET)
            input('Press Any Key To Exit...')
            exit()
    
    # Get download path from user
    def get_save_path(self) -> str:

        try:
            print(Fore.LIGHTYELLOW_EX + '\n[!] Enter path to save episode. Just press enter to save episode in current directory.')
            path: str = input(Fore.YELLOW + '?' + Fore.RESET +' Save Path (without file name) :').strip()

            if not path:
                return CWD

            is_valid_path = os.path.isdir(path)

            if not is_valid_path:
                os.mkdir(path)
            
            return path

        except KeyboardInterrupt:
            os.system('CLS')
            exit()

        except OSError as e:
            print(Fore.RED+'Error : {e}\n'+Fore.RESET)
            save_path()



x265 = x265LK()
series = dict()

def get_search():
    question = {
        'type': 'input',
        'name': 'search_term',
        'message': 'Enter Title To Search:',        
        'validate': lambda val: val != ''
    }
    x265.display_title()
    search_term: str = prompt(question, style=custom_style_2)['search_term']
    search_result: list = x265.search(search_term)
    
    if search_result == -1:
        print(Fore.LIGHTRED_EX + '[!] Nothing Found' + Fore.RESET)
        os.system('PAUSE')
        get_search()

    if search_result[0] == -9:
        print(Fore.LIGHTRED_EX + f'[!] Connection Error : {search_result[1]}' + Fore.RESET)
        input('Press Any Key To Exit...')
        exit()
    

    x265.display_title()
    ui = x265.select_series(search_result) 

    if ui == '-1':
        get_search()
    
    else:   
        global series
        series = ui
        get_season()


def get_season():
    x265.display_title()
    season_no, series_name, dtype = x265.select_season(series)
    
    if season_no == -9:
        print(Fore.LIGHTRED_EX + f'[!] Connection Error : {series_name}' + Fore.RESET)
        input('Press Any Key To Exit...')
        exit()

    get_episode(season_no, series_name, dtype)


def get_episode(season_no, series_name, dtype):

    x265.display_title()
    if dtype == 'e':    # Go To Episode Selection
        epi_nums: list[int] = x265.select_episode(season_no, series_name)
        
        if epi_nums[0] == -1:
            get_search()

        elif epi_nums[0] == -2:
            get_season()

        path:str = x265.get_save_path()

        for epi in epi_nums:
            link, epi_no = x265.get_ep_link(epi)
            if link == -9:
                print(Fore.LIGHTRED_EX + f'[!] Connection Error : {epi_no}' + Fore.RESET)
                input('Press Any Key To Exit...')
                exit()
            x265.download(link, path)

    elif dtype == 'A':
        for i in range(season_no):
            epi_nums: list[int] = x265.select_episode(i+1, series_name, False)
            path:str = x265.get_save_path()

            for epi in epi_nums:
                link, epi_no = x265.get_ep_link(epi)
                if link == -9:
                    print(Fore.LIGHTRED_EX + f'[!] Connection Error : {epi_no}' + Fore.RESET)
                    input('Press Any Key To Exit...')
                    exit()
                x265.download(link, path)

    elif dtype == 'a':
        epi_nums: list[int] = x265.select_episode(season_no, series_name, False)
        path:str = x265.get_save_path()

        for epi in epi_nums:
            link, epi_no = x265.get_ep_link(epi)
            if link == -9:
                print(Fore.LIGHTRED_EX + f'[!] Connection Error : {epi_no}' + Fore.RESET)
                input('Press Any Key To Exit...')
                exit()
            x265.download(link, path)

    elif dtype == '-1':
        get_search()

    else:   # Download Full Multiple Seasons
        for n in season_no:
            epi_nums: list[int] = x265.select_episode(n, series_name, False)
            path:str = x265.get_save_path()

            for epi in epi_nums:
                link, epi_no = x265.get_ep_link(epi)
                if link == -9:
                    print(Fore.LIGHTRED_EX + f'[!] Connection Error : {epi_no}' + Fore.RESET)
                    input('Press Any Key To Exit...')
                    exit()
                x265.download(link, path)

    question =  {
        'type': 'list',
        'name': 'ui',
        'message': 'What to do next?',
        'choices': [
            'Download Another Episode',
            'Change Season',
            'Search TV Series',
            'Exit'
        ],
        'filter': lambda val: val.lower()
    }
    answer = prompt(question, style=custom_style_2)['name']
    
    if answer[0] == 'd':
        get_episode(season_no, series_name, dtype)
    elif answer[0] == 'c':
        get_season()
    elif answer[0] == 's':
        get_search()
    else:
        exit()


get_search()