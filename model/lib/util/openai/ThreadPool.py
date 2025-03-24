from dataclasses import dataclass

from openai import AsyncOpenAI
from openai.types.beta import Thread


@dataclass
class ThreadPool:
    pool_id: int
    thread: Thread
    completion_count: int = 0
    previous_created_at: int = 0

    @classmethod
    async def create(cls, client: AsyncOpenAI, pool_id: int, previous_created_at: int):
        thread = await client.beta.threads.create()
        return cls(pool_id, thread, previous_created_at)
