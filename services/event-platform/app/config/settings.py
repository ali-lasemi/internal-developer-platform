import os


class Settings:
    def __init__(self):
        self.redis_url = os.getenv(
            "REDIS_URL",
            "redis://redis:6379/0"
        )

        self.event_stream = os.getenv(
            "EVENT_STREAM",
            "idp-events"
        )


settings = Settings()
