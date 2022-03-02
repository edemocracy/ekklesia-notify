from devtools import debug
import yaml
import os
from ekklesia_notify.settings_models import EkklesiaNotifySettings

settings_filepath = os.environ.get('EKKLESIA_NOTIFY_CONFIG', "settings.yml")
with open(settings_filepath) as f:
    yaml = yaml.safe_load(f)

settings = EkklesiaNotifySettings.parse_obj(yaml)
debug(settings)
