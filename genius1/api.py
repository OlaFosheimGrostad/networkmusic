from __future__ import annotations
import datetime
from enum import Enum
import logging
import json
import requests
from .exceptions import ServiceError
from .utility import strip_lyrics_webpage

class OperationGet(Enum):
    songlist = 'songlist'


class SongEntry:
    def __init__(self, api: GeniusApi, json_data: dict):
        self.api = api
        self.json = json_data
        self._primary_artists_ids: tuple[int, ...] | None = None
        self._primary_artists: tuple[tuple[int, str], ...] | None = None
        self._featured_artists: tuple[tuple[int, str], ...] | None = None
        self._release_date_iso: str | None = None

    @property
    def primary_artists_ids(self) -> tuple[int, ...]:
        if self._primary_artists_ids is None:
            self._primary_artists_ids = tuple(
                int(e['id']) for e in self.json['primary_artists']
            )
        return self._primary_artists_ids

    @property
    def primary_artists(self) -> tuple[tuple[int, str], ...] :
        if self._primary_artists is None:
            self._primary_artists = tuple(
                (int(e['id']), str(e['name'])) for e in self.json['primary_artists']
            )
        return self._primary_artists

    @property
    def featured_artists(self) -> tuple[tuple[int, str], ...] :
        if self._featured_artists is None:
            self._featured_artists = tuple(
                (int(e['id']), str(e['name'])) for e in self.json['featured_artists']
            )
        return self._featured_artists


    @property
    def id(self) -> int:
        return self.json['id']

    @property
    def url(self) -> str:
        return self.json['url']

    @property
    def lyrics_complete(self) -> bool:
        return self.json['lyrics_state'] == 'complete'

    @property
    def release_date_iso(self) -> str | None:
        if self._release_date_iso is None:
            d = self.json.get('release_date_components')
            if d is not None:
                if d['month'] is None:
                    self._release_date_iso = str(d['year'])
                elif d['day'] is None:
                    self._release_date_iso = f"{d['year']:04}-{d['month']:02}"
                else:
                    self._release_date_iso = f"{d['year']:04}-{d['month']:02}-{d['day']:02}"
        return self._release_date_iso

    @property
    def title(self) -> str:
        return self.json['title']

    def fetch_lyrics(self) -> str:
        response = requests.get(self.url)
        if response.status_code != 200:
            logging.error("GeniusApi: fetch lyrics failed, HTTP Status %d: ", response.status_code, self.url)
            raise ServiceError()
        return strip_lyrics_webpage(response.text)

class SongsPage:
    def __init__(self, api: GeniusApi, json: dict):
        self.api = api
        self.json = json
        self._songs: list[SongEntry] | None = None

    @property
    def next_page(self) -> int | None:
        p = self.json.get('next_page')
        return p if p is None else int(p)

    @property
    def songs(self) -> list[SongEntry]:
        if self._songs is None:
            self._songs = [
                SongEntry(self.api, e)
                for e in self.json.get('songs', tuple())
            ]
        return self._songs


class GeniusApi:
    def __init__(self, token: str):
        autorization = f"Bearer {token}"
        self.headers_get = {"Authorization": autorization}

    def get_songs_page(self, artist_id: int, *, per_page: int = 50, page: int = 1) -> SongsPage:
        url = f"https://api.genius.com/artists/{artist_id}/songs?per_page={per_page}&page={page}"
        response = requests.get(url, headers=self.headers_get)
        data = response.json()
        if response.status_code != 200:
            msg = data['meta'].get('message', '')
            logging.error("GeniusApi: artist %d page %d failed, HTTP status %d: %s", artist_id, page, response.status_code, msg)
            raise ServiceError(msg)
        return SongsPage(self, data['response'])

    def fetch_artist_song_entries(self, artist_id: int):
        next_page: int | None = 1
        while next_page is not None:
            page = self.get_songs_page(artist_id, page=next_page)
            next_page = page.next_page
            if len(page.songs) == 0:
                break
            # logging.debug("next_page = %s",str(next_page))
            for entry in page.songs:
                yield entry

    def fetch_artist_song_entries_by_popularity(self, artist_id: int):
        next_page: int | None = 1
        while next_page is not None:
            url = f"https://api.genius.com/artists/{artist_id}/songs?&sort=popularity&page={next_page}"
            response = requests.get(url, headers=self.headers_get)
            data = response.json()
            if response.status_code != 200:
                msg = data['meta'].get('message', '')
                logging.error("GeniusApi: artist %d page %d failed, HTTP status %d: %s", artist_id, next_page,
                              response.status_code, msg)
                raise ServiceError(msg)
            page = SongsPage(self, data['response'])
            next_page = page.next_page
            if len(page.songs) == 0:
                break
            # logging.debug("next_page = %s",str(next_page))
            for entry in page.songs:
                yield entry

