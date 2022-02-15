from devtools import debug
import yaml
from ekklesia_notify.settings_models import EkklesiaNotifySettings

with open("settings.yml") as f:
    yaml = yaml.safe_load(f)

settings = EkklesiaNotifySettings.parse_obj(yaml)
debug(settings)
