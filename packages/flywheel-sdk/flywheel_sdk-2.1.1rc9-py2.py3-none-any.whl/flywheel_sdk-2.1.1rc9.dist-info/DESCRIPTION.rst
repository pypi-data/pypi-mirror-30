# Flywheel SDK

An SDK for interaction with a remote Flywheel instance.

# Getting Started

```python
import flywheel
from pprint import pprint

fw = flywheel.Flywheel('api-key')

user = fw.get_current_user()
pprint(user)

fw.upload_file_to_project('project-id', '/path/to/file.txt')
```


