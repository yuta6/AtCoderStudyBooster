import os
from typing import Optional

import requests

from atcdr.util.i18n import _


def set_api_key() -> Optional[str]:
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key and validate_api_key(api_key):
        return api_key
    elif api_key:
        print(_('api_key_validation_failed'))
    else:
        pass

    api_key = input(_('get_api_key_prompt'))
    if validate_api_key(api_key):
        print(_('api_key_test_success'))
        print(_('save_api_key_prompt'))
        if input() == 'y':
            zshrc_path = os.path.expanduser('~/.zshrc')
            with open(zshrc_path, 'a') as f:
                f.write(f'export OPENAI_API_KEY={api_key}\n')
            print(_('api_key_saved', zshrc_path))
        os.environ['OPENAI_API_KEY'] = api_key
        return api_key
    else:
        print(_('api_key_required'))
        return None


def validate_api_key(api_key: str) -> bool:
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}',
    }

    response = requests.get('https://api.openai.com/v1/models', headers=headers)
    if response.status_code == 200:
        return True
    else:
        print(_('api_key_validation_error'))
        return False
