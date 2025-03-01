# NetworkMusic V0.0.1 GAMMA

This preliminary version of the library provides a wrapper for the
[Sonauto API](https://sonauto.ai/developers) and a very limited wrapper for the
[Genius API](https://genius.com/developers).

Warning: the code is mostly untested at this point


## Requirements

Uses the `requests` library.


## Usage Examples

### Example Sonauto

```python
from networkmusic.sonauto1 import SonautoApi, tags

# access token obtained from https://sonauto.ai/developers
token = "sksonauto_012345678901234567890"

# create an object that provides API access
api = SonautoApi(token)

# pick the four folk genre tags that have been trained the most
prompt = list(filter(lambda s: s.startswith("folk") or s.endswith("folk"), tags.all))[:4]

print(prompt)

# Generate audio, wait 15 seconds before checking if the track is done
data = api.generate_polling(poll_delay=15, poll_interval=3, tags=prompt, instrumental=True)

print(data.song_paths)
```


### Example Genius

```python
import itertools
from networkmusic.genius1 import GeniusApi
from networkmusic.genius1.content import artist_ids

# access token obtained from https://genius.com/api-clients
token = r"9D2g3FEGGerer_4759t234523453245"

# create an object that provides API access
api = GeniusApi(token)

# Look up the genius artist id (the current list is very limited)
artist_id = artist_ids["Dua Lipa"]

# Fetch and print the 10 most popular song titles by Dua Lipa
for song in itertools.islice(api.fetch_artist_song_entries_by_popularity(artist_id), 10):
    print(song.title, '(', song.release_date, ')')
```


## License

You can choose either the Apache 2.0 or the LGPL3 licensing terms for the files in this repository.

### License alternative 1: LPGL3
All files in this repository are governed by the following license.

Copyright 2025 Ola Fosheim Grøstad

Licensed under the GNU LESSER GENERAL PUBLIC LICENSE Version 3 (the "License");
you may not use any files in this repository except in compliance with the License.
You may obtain a copy of the License at

https://www.gnu.org/licenses/lgpl-3.0.html#license-text

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

### License alternative 2: Apacahe 2.0
All files in this repository are governed by the following license.

Copyright 2025 Ola Fosheim Grøstad

Licensed under the Apache License, Version 2.0 (the "License");
you may not use any files in this repository except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
