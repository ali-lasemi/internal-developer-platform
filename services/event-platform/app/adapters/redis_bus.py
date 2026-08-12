import json

from redis.asyncio import Redis

from app.config.settings import settings
from app.models.event import PlatformEvent


class RedisEventBus:
    def __init__(self):
        self.client = Redis.from_url(
            settings.redis_url,
            decode_responses=True
        )

    async def publish(
        self,
        event: PlatformEvent
    ) -> str:
        payload = json.dumps(
            event.model_dump(
                mode="json"
            )
        )

        message_id = await self.client.xadd(
            settings.event_stream,
            {
                "event": payload
            }
        )

        return message_id

    async def ping(
        self
    ) -> bool:
        return bool(
            await self.client.ping()
        )


event_bus = RedisEventBus()
