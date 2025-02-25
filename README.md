# NetworkMusic V0.0.1 GAMMA

Currently only provides access to AI generated music from Sonauto.

Warning: the code is mostly untested at this point


## Requirements

Uses the `requests` library.


## Usage Example

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


## License

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
