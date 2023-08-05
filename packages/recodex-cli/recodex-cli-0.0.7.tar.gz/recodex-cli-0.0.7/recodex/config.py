from functools import lru_cache

import jwt
from ruamel import yaml
from typing import NamedTuple, Optional

from pathlib import Path


class UserContext(NamedTuple):
    api_url: Optional[str] = None
    api_token: Optional[str] = None

    @property
    @lru_cache()
    def token_data(self):
        if self.api_token is None:
            raise RuntimeError("The API token is not set")

        return jwt.decode(self.api_token, verify=False)

    @property
    def user_id(self):
        return self.token_data["sub"]

    @classmethod
    def load(cls, config_path: Path):
        config = yaml.safe_load(config_path.open("r"))
        return cls(**config)

    def store(self, config_path: Path):
        config_path.parent.mkdir(parents=True, exist_ok=True)
        yaml.dump(dict(self._asdict()), config_path.open("w"))
