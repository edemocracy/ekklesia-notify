from typing import Dict, Any
from eliot import log_call, Message
from jinja2 import FileSystemLoader
from jinja2 import Environment, FileSystemLoader
from jinja2.exceptions import TemplateNotFound

from ekklesia_notify.api_models import TemplatedMessage
from ekklesia_notify.settings import settings
from ekklesia_notify.settings_models import ClientSettings

Message.log(msg="templating", template_dir=settings.template_dir)
env = Environment(loader=FileSystemLoader(settings.template_dir))


@log_call
def render_template(msg: TemplatedMessage, transport_name: str, client_settings: ClientSettings) -> str:

    if msg.template not in client_settings.allowed_templates:
        raise ValueError("Template not allowed for this client")

    template_name = f"{transport_name}_{msg.template}.j2"
    try:
        template = env.get_template(template_name)
    except TemplateNotFound:
        Message.log(msg="not found", template=template_name)
        template = env.get_template(f"{msg.template}.j2")

    context = {"sender": msg.sender, **msg.variables}
    return template.render(context)
