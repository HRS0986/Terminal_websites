# python 3.9
# By Hirusha Fernando
# Unofficial Sarigama.LK API

import re
import os
import eyed3
import requests as r
from tqdm import tqdm


class Track:
    def __init__(self, title:str, tid:str, downloads:int, visits:int, released:str, downloadable:bool, url:str, artists):
        self.title = title
        self.downloads = downloads
        self.tid = tid
        self.visits = visits
        self.released = released
        self.downloadable = downloadable
        self.url = url
        self.artists = artists

    def __str__(self):
        return f'<Sarigama.LK Track Object>'


class Artist:
    def __init__(self, aid:str, name:str, stage_name:str, songs:int, url:str):
        self.aid = aid
        self.name = name
        self.stage_name = stage_name
        self.songs = songs
        self.url = url

    def __str__(self):
        return f'<Sarigama.LK Artist Object>'


class Playlist:
    def __init__(self, songs_count:int, name:str, tracks:list):
        self.songs_count = songs_count
        self.name = name
        self.tracks = tracks

    def __str__(self):
        return f'<Sarigama.LK Playlist Object>'


class Sarigama:
    __PATH : str = os.getcwd()
    '''
    Samples
    Album Art - https://sarigama.lk/img/songs/appsong-68gtxkku5a5ovgfz.jpg
    Playlist - https://sarigama.lk/playlist/appachchi-thaththa/a35b4d46-0632-458d-88c5-6ef41c39413f
    Artist - https://sarigama.lk/artist/sanuka-wickramasinghe/a22b4ecf-c1c1-4bed-b6aa-77df464bf02d
    Song - https://sarigama.lk/sinhala-song/sanuka-wickramasinghe/dewliye-theme-song/de7c1755-7539-4b9b-966e-2f1f82b914d7
    Search - https://sarigama.lk/api/v1/search/mas/{query}
    '''

    def __init__(self):
        self.__HOME = 'https://sarigama.lk'
        self.__LATEST = f'{self.__HOME}/playlist/latest/1a08d372-f979-4654-b180-f04e5e10c336'
        self.__TRENDING = f'{self.__HOME}/playlist/trending/22adef1a-18c7-40a4-96d5-8f93ea1d7708'
        self.__DEFAULT_ART = f'{self.__HOME}/img/default/song.png'
        self.__SEARCH_BASE = f'{self.__HOME}/api/v1/search/mas/'
        
        self.__album_art_path = ''       


    def __repr__(self):
        return f'Sarigama Object'


    def download(self, link:str, art=True, path=__PATH):
        BLOCK_SIZE: int = 1024
        SONG_PTN = r'(https://sarigama\.lk/files/[a-z0-9=\-\?/]+)'
        SONG_REGEX = re.compile(SONG_PTN, flags=re.I)        
        
        track_data: list[str] = link.split('/')
        artist: str = ' '.join(track_data[4].split('-')).title()
        title: str = ' '.join(track_data[5].split('-')).title()
        track_name: str = f'{title} - {artist}.mp3'      
        
        res = r.get(link)
        if res.status_code != 200:
            raise Exception('Song Request failed.')

        else:
            songlink: str = SONG_REGEX.findall(res.text)[0]
            cookies: list[str] = res.headers['Set-Cookie'].split(';')
            XSRF: str = cookies[0]
            LRVL: str = cookies[3].split()[1]
            cookies: str = f'{XSRF};{LRVL};'
            headers: dict[str, str] = {'cookie': cookies}

            mp3_res = r.get(songlink, headers=headers, stream=True)
            if mp3_res.status_code == 200:
                mp3_length = int(mp3_res.headers['content-length'])
                
                bar = tqdm(total=mp3_length, unit='iB', unit_scale=True)
                track_name: str = f'{self.__PATH}\\{track_name}'
               
                with open(track_name, 'wb') as song:
                    for data in mp3.iter_content(BLOCK_SIZE):
                        bar.update(len(data))
                        song.write(data)
                    bar.close()
                
                if mp3_length != 0 and bar.n != mp3_length:
                    raise Exception('Download unsuccessful.')
                else:
                    if art:
                        self.__download_album_art(res.text)
                        art_path = self.__album_art_path
                        self.__set_ID3(track_name, title, artist, art_path)

            else:
                raise Exception('Download failed.')


    def __download_album_art(self, song_page:str):
        ART_PTN = r' <meta name="thumbnail" content="([a-z:0-9//\-\.]+)"'
        ART_REGEX = re.compile(ART_PTN, flags=re.I)
        artlink: str = ART_REGEX.findall(song_page)[0]       
        
        self.__album_art_path = self.__PATH+'coverart.jpg'
        if artlink != self.__DEFAULT_ART_URL:
            art = r.get(artlink)
            if art.status_code == 200:
                with open(self.__album_art_path, 'wb') as cover:
                    cover.write(art.content)
            else:
                raise Exception('Album art download failed.')


    def __set_ID3(self, mp3_path:str, title:str, artist:str, art_path=''):
        mp3 = eyed3.load(mp3_path)
        mp3.tag._images.remove('')   
        mp3.tag.title = title
        mp3.tag.artist = artist
        mp3.tag.album = title

        if cover_art_path:
            # 3 is for front cover
            mp3.tag.images.set(3, open(cover_art_path,'rb').read(), 'image/jpeg')

        mp3.tag.save()


    def __search(self, term:str, s_type:str) -> list:
        querylink = self.__SEARCH_BASE + term
        
        search_response = r.get(querylink)
        if search_response.status_code == 200:
            
            json_res = search_response.json()
            if s_type == 'S':
                songs: list[dict[str, str]] = json_res['songs']['hits']['hits']
                return songs
            else:
                artists: list[dict[str, str]] = json_res['artists']['hits']['hits']
                return artists
        else:
            return False
    

    def search_song(self, term : str) -> Track:
        songs = self.__search(term, 'S')        
        if songs:            
            for song in songs:
                track_info: dict = song['_source']
                title: str = track_info['title']
                url: str = track_info['url']
                tid: str = track_info['id']
                downloads = int(track_info['download_count'])
                visits = int(track_info['visit_count'])
                released: str = track_info['released_at']
                downloadable = bool(int(track_info['download_enabled']))

                track_artists = track_info['main_artists']
                artists: list[str] = [artist['name'] for artist in track_artists]

                track = Track(title, tid, downloads, visits, released, downloadable, url, artists)
                yield track            

        else:
            raise Exception('Search request failed.')


    def search_artist(self, term : str) -> Artist:
        artists = self.__search(term, 'A')        
        if artists:            
            for artist in artists:
                artist_info: dict = artist['_source']
                name: str = track_info['name']
                stage_name:str = track_info['stage_name']
                url: str = track_info['url']
                aid: str = track_info['id']
                songs = int(track_info['songs_count'])
                artist = Artist(aid, name, stage_name, songs, url)
                yield artist            

        else:
            raise Exception('Search request failed.')


    def __get_playlist(self, name:str, link:str) -> Playlist:
        trend_res = r.get(link)

        if trend_res.status_code == 200:
            SONG_PATTERN = r'<a target="_blank" href="(https://sarigama.lk/sinhala-song/[a-z0-9\.:\/-]+)'
            SONG_REGEX = re.compile(SONG_PATTERN, flags=re.I)
            songlinks = SONG_REGEX.finditer(trend_res.text)

            songs_count = 0
            playlist_name = name
            tracks = []

            for link in songlinks:
                title1: str = link.groups()[0]
                title2: str = title1.split('/')[5]
                title: str = ' '.join(title2.split('-')).title()
                track = next(self.search_song(title))
                tracks.append(track)
                songs_count += 1

            playlist = Playlist(songs_count, playlist_name, tracks)
            return playlist

        else:
            raise Exception('Playlist request failed')


    def get_latest(self) -> Playlist:
        latest = self.__get_playlist('Latest', self.__LATEST)
        return latest


    def get_trending(self) -> Playlist:
        trending = self.__get_playlist('Trending', self.__TRENDING)
        return trending
      

    def search_playlist(self, term : str) -> dict[str, str]:
        pass


sarigama = Sarigama()
# res = sarigama.get_trending()

# print(res.name)
# print(res.songs_count)
# for track in res.tracks:
#     print(track.title)
