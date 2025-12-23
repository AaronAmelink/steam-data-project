import os


class Settings:
    def __init__(self):
        for key, value in os.environ.items():
            if value.lower() in ("true", "false"):
                value = value.lower() == "true"
            setattr(self, key.lower(), value)

    def __getitem__(self, key):
        return getattr(self, key.lower())


settings = Settings()
