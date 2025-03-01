from __future__ import annotations
from enum import Enum
from collections.abc import Iterable
from datetime import datetime
import logging
import requests
from .exceptions import GenerationError, ServiceError
from .types import GenerationStatus, ExtendDirection


class OperationGet(Enum):
    status = 'status'
    data = 'data'


class OperationPost(Enum):
    generate = 'generate'
    extend = 'extend'
    inpaint = 'inpaint'


class InpaintParams:
    def __init__(self, json: dict):
        self.sections: list[list[float]] = json['sections']
        self.selection_crop: bool = json['selection_crop']
        self.audio_url: str = json['audio_url']
        self.lyrics: str = json['lyrics']


class ExtendParams:
    def __init__(self, json: dict):
        self.side = ExtendDirection.left if json['side'] == 'left' else ExtendDirection.right
        self.crop_duration = json['crop_duration']
        self.audio_url: str = json['audio_url']
        self.duration = json['duration']
        self.lyrics: str = json['lyrics']


class Data:
    def __init__(self, api: SonautoApi, json: dict):
        self.api = api
        self.json = json
        self._created_at: datetime | None = None
        self._inpaint_params: InpaintParams | None= None
        self._extend_params: ExtendParams | None = None

    @property
    def id(self) -> str:
        return self.json['id']

    @property
    def created_at(self) -> datetime:
        if self._created_at is None:
            self._created_at = datetime.fromisoformat(self.json['created_at'])
        return self._created_at

    @property
    def status(self) -> GenerationStatus:
        s = self.json['status']
        return GenerationStatus(s if s in SonautoApi._GenerationStatus_values else '')

    @property
    def song_paths(self) -> list[str]:
        return self.json['song_paths']

    @property
    def lyrics(self) -> str:
        return self.json['lyrics']

    @property
    def prompt(self) -> str | None:
        return self.json['prompt']

    @property
    def tags(self) -> list[str]:
        return self.json['tags']

    @property
    def seed(self) -> int:
        return int(self.json['seed'])

    @property
    def inpaint_params(self) -> InpaintParams | None:
        if self._inpaint_params is None:
            p = self.json['inpaint_params']
            if p is not None:
                self._inpaint_params = InpaintParams(p)
        return self._inpaint_params

    @property
    def extend_params(self) -> ExtendParams | None:
        if self._extend_params is None:
            p = self.json['extend_params']
            if p is not None:
                self._extend_params = ExtendParams(p)
        return self._extend_params


class Task:
    def __init__(self, api: SonautoApi, taskid: str):
        self.api = api
        self.taskid = taskid

    def fetch_status(self) -> GenerationStatus:
        return self.api.get_status(self.taskid)

    def fetch_data(self) -> Data:
        return Data(self.api, self.api.get_data_as_json(self.taskid))


class SonautoApi:
    url_base = "https://api.sonauto.ai/v1"

    _GenerationStatus_values = set(x.value for x in iter(GenerationStatus))

    url_operations = {
        OperationPost.generate: f"{url_base}/generations",
        OperationPost.extend: f"{url_base}/generations/extend",
        OperationPost.inpaint: f"{url_base}/generations/inpaint",
        OperationGet.status:  f"{url_base}/generations/status/",
        OperationGet.data: f"{url_base}/generations/",
    }

    def __init__(self, token: str):
        assert isinstance(token, str)
        header_authorization = f"Bearer {token}"

        self.headers_basic = {
            "Authorization": header_authorization,
        }
        self.headers_json = self.headers_basic.copy()
        self.headers_json['Content-Type'] = "application/json"

    def make_generate_parameters(
            self,
            *,
            tags: Iterable[str] | None = None,
            lyrics: str | None = None,
            prompt: str | None = None,
            instrumental: bool | None = None,
            prompt_strength: float | None = None,
            seed: int | None = None,
            num_steps: int | None = None,
            webhook_url: str | None = None,
            num_songs: int | None = None,
    ) -> dict[str, list[str] | str | float | bool | int]:
        return dict(
            e for e in (
                ('tags', list(tags) if tags is not None else None),
                ('lyrics', lyrics),
                ('prompt', prompt),
                ('instrumental', instrumental),
                ('prompt_strength', prompt_strength),
                ('seed', seed),
                ('num_step', num_steps),
                ('webhook_url', webhook_url),
                ('num_songs', num_songs)
            ) if e[1] is not None
        )

    def make_extend_parameters(
            self,
            audio_url: str,
            side: ExtendDirection = ExtendDirection.right,
            *,
            tags: Iterable[str] | None = None,
            lyrics: str | None = None,
            prompt: str | None = None,
            instrumental: bool | None = None,
            prompt_strength: float | None = None,
            seed: int | None = None,
            num_steps: int | None = None,
            webhook_url: str | None = None,
            num_songs: int | None = None,
            extend_duration: float | None = None,
            crop_duration: float | None = None,
    ) -> dict[str, list[str] | str | float | bool | int]:
        return dict(
            e for e in (
                ('audio_url', audio_url),
                ('side', side.value),
                ('tags', list(tags) if tags is not None else None),
                ('lyrics', lyrics),
                ('prompt', prompt),
                ('instrumental', instrumental),
                ('prompt_strength', prompt_strength),
                ('seed', seed),
                ('num_step', num_steps),
                ('webhook_url', webhook_url),
                ('num_songs', num_songs),
                ('extend_duration', extend_duration),
                ('crop_duration', crop_duration),
            ) if e[1] is not None
        )

    def make_inpaint_parameters(
            self,
            audio_url: str,
            sections: list[list[float]],
            *,
            tags: Iterable[str] | None = None,
            lyrics: str | None = None,
            prompt: str | None = None,
            instrumental: bool | None = None,
            prompt_strength: float | None = None,
            seed: int | None = None,
            num_steps: int | None = None,
            webhook_url: str | None = None,
            num_songs: int | None = None,
            selection_crop: bool | None = None,
    ) -> dict[str, list[str] | str | float | bool | int]:
        return dict(
            e for e in (
                ('audio_url', audio_url),
                ('sections', sections),
                ('tags', list(tags) if tags is not None else None),
                ('lyrics', lyrics),
                ('prompt', prompt),
                ('instrumental', instrumental),
                ('prompt_strength', prompt_strength),
                ('seed', seed),
                ('num_step', num_steps),
                ('webhook_url', webhook_url),
                ('num_songs', num_songs),
                ('selection_crop', selection_crop),
            ) if e[1] is not None
        )

    def get_by_taskid(self, operation: OperationGet, taskid: str) -> str | dict[str, str | list[str] | float | int | dict]:
        assert isinstance(taskid, str)
        url = self.url_operations[operation] + taskid
        response = requests.get(url, headers=self.headers_basic)
        if response.status_code != 200:
            logging.error("Sonauto fetch_status task-id %s: HTTP STATUS %d: %s", taskid, response.status_code, response.text)
            raise ServiceError(f"Fetch status failed for taskid: {taskid}")
        try:
            result = response.json()
        except Exception:
            raise ServiceError("Sonauto get status: missing json response")
        return result

    def post(self, operation: OperationPost, parameters: dict[str, list[str] | str | float | bool | int]) -> str:
        url = self.url_operations[operation]
        response = requests.post(url, json=parameters, headers=self.headers_json)

        if response.status_code != 200:
            logging.error(f"Sonauto %s: HTTP STATUS %d: %s", operation.value, response.status_code, response.text)
            raise GenerationError()
        try:
            taskid = response.json()['task_id']
            logging.info(f"Sonauto %s task-id %s", operation.value,taskid)
        except Exception:
            raise ServiceError(f"Sonauto {operation.value}: json error")
        return taskid

    def get_status(self, taskid: str) -> GenerationStatus:
        result = self.get_by_taskid(OperationGet.status, taskid)
        logging.debug("STATUS: %s", str(result))
        return GenerationStatus(result if result in SonautoApi._GenerationStatus_values else '')

    def get_data_as_json(self, taskid: str) -> dict[str, str | list[str] | float | int | dict]:
        result = self.get_by_taskid(OperationGet.data, taskid)
        return result

    def post_generate(self, parameters: dict[str, list[str] | str | float | bool | int]) -> str:
        return self.post(OperationPost.generate, parameters)

    def post_inpaint(self, parameters: dict[str, list[str] | str | float | bool | int]) -> str:
        return self.post(OperationPost.inpaint, parameters)

    def post_extend(self, parameters: dict[str, list[str] | str | float | bool | int]) -> str:
        return self.post(OperationPost.extend, parameters)

    #
    # CONVENIENCE FUNCTIONS
    #

    def generate_polling(
            self,
            poll_delay:int = 12,
            poll_interval:int = 3,
            *,
            tags: Iterable[str] | None = None,
            lyrics: str | None = None,
            prompt: str | None = None,
            instrumental: bool | None = None,
            prompt_strength: float | None = None,
            seed: int | None = None,
            num_steps: int | None = None,
            webhook_url: str | None = None,
            num_songs: int | None = None,
         ) -> Data:
        from time import sleep
        # TODO: timestamping for debugging purposes
        parameters = self.make_generate_parameters(tags=tags, lyrics=lyrics,prompt=prompt, instrumental=instrumental,
                                                   prompt_strength=prompt_strength, seed=seed,num_steps=num_steps,
                                                   webhook_url=webhook_url, num_songs=num_songs)
        taskid = self.post_generate(parameters)
        sleep(poll_delay)
        status = self.get_status(taskid)
        # old_status = status
        logging.debug('Generating status:', status.value)
        while status != status.generating:
            sleep(poll_delay)
            old_status = status
            status = self.get_status(taskid)
            if status != old_status:
                logging.debug('Generating status:', status.value)
        while status != status.success:
            sleep(poll_interval)
            old_status = status
            status = self.get_status(taskid)
            if status != old_status:
                logging.debug('Generating status:', status.value)
        return Data(self, self.get_data_as_json(taskid))





