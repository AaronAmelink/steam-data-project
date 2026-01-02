import os


class Config:
    def __init__(self):
        for key, value in os.environ.items():
            if value.lower() in ("true", "false"):
                value = value.lower() == "true"
            setattr(self, key.upper(), value)

    def __getitem__(self, key):
        return getattr(self, key.upper())


config = Config()
