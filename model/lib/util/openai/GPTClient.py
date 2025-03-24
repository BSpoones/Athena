import logging
import time
import json
import asyncio

import aiofiles
from os import getenv
from ThreadPool import ThreadPool
from asyncio import Queue
from openai import AsyncOpenAI
from openai.types.beta import Assistant, Thread
from openai.types.beta.threads import Run, Message

_NAME = "Athena-Augmentation"
_TIMEOUT_SECS = 300  # 5 mins
_ASSISTANT_ID = "assistant"
_USER_ID = "user"
_BATCH_ID_KEY = "batch_id"
_ERROR_PATH = ".model/logs/failed.json"
_MAX_THREAD_POOL_TRIES = 100


# TODO -> Move elsewhere
def is_valid_dict(response: dict) -> bool:
    return (
            isinstance(response, dict) and all(
        isinstance(k, str) and isinstance(v, list) and all(isinstance(i, str) for i in v)
        for k, v in response.items()
    )
    )


class GPTClient:

    @classmethod
    async def create(cls, name: str, model: str, system_prompt: str, pool_size: int = 25):
        self = cls(name, model, system_prompt, pool_size)

        await self._connect_client()
        await self._create_assistant()
        await self._populate_thread_pool()

        return self

    def __init__(self, name: str, model: str, system_prompt: str, pool_size: int):
        """
        TODO -> Docstring
        """
        self.completed = 0
        self.failed = 0

        self.logger = logging.getLogger(f"GPT CLIENT -  {name}")

        self.name = name
        self.model = model
        self.system_prompt = system_prompt
        self.pool_size = pool_size

        self._client: AsyncOpenAI | None = None
        self._assistant: Assistant | None = None
        self._thread_queue: Queue[ThreadPool] = Queue()

    async def _connect_client(self):
        self.logger.info(f"Connecting {self.name} to OpenAI client!")

        # Any error in connection should count as a breaking stoppage
        self._client = AsyncOpenAI(api_key=getenv("OPENAI_API_KEY"))
        self.logger.info(f"Connection of {self.name} complete!")

    async def _create_assistant(self):
        self.logger.info(f"Looking for existing assistant with name: {self.name}...")

        # List existing assistants and check for a matching name
        assistants = await self._client.beta.assistants.list()
        existing = next((a for a in assistants.data if a.name == self.name), None)

        if existing:
            self.logger.info(f"Found existing assistant '{self.name}' with ID: {existing.id}, reusing it.")

            self._assistant = await self._client.beta.assistants.update(
                assistant_id=existing.id,
                instructions=self.system_prompt,
                model=self.model,
            )
            self.logger.info(f"Updated assistant '{self.name}' with new model/instructions.")
        else:
            self.logger.info(f"Creating new assistant '{self.name}'...")
            self._assistant = await self._client.beta.assistants.create(
                name=self.name,
                instructions=self.system_prompt,
                model=self.model,
            )
            self.logger.info(f"Created new assistant with ID: {self._assistant.id}")

    async def _populate_thread_pool(self):
        if self._client is None:
            raise ValueError("Failed to create thread pool! Client is not initialised!")

        for i in range(self.pool_size):
            await self._create_thread_pool(i, 0)

    async def _create_thread_pool(self, index: int, previous_created_at: int = 0):
        self.logger.info(f"{'Re-c' if previous_created_at != 0 else 'C'}Creating thread pool no.{index:,}")
        pool = await ThreadPool.create(self._client, index, previous_created_at)
        await self._thread_queue.put(pool)

    async def _get_available_thread(self) -> ThreadPool:
        return await self._thread_queue.get()

    async def _release_thread(self, thread: ThreadPool):
        if thread.completion_count >= _MAX_THREAD_POOL_TRIES:
            await self._refresh_thread(thread)
            return

        await self._thread_queue.put(thread)

    async def _refresh_thread(self, thread: ThreadPool):
        self.logger.info(f"Refreshing thread pool no.{thread.pool_id:,}")
        await self._create_thread_pool(thread.pool_id, thread.previous_created_at)

    async def process_batch(self, batch: list[str]) -> dict[str, list[str]] | None:
        if self._client is None:
            raise RuntimeError("Client not initialised!")
        if self._assistant is None:
            raise RuntimeError("Assistant not initialised!")

        prompt = "\n".join(batch)

        try:
            thread_pool = await self._get_available_thread()
            thread = thread_pool.thread
            await self._create_message(thread, prompt)
            run = await self._create_run(thread)
        except Exception as e:
            self.logger.critical(f"FAILED TO START RUN DUE TO {e}")
            return None

        try:
            response = await self._retrieve_run(thread, run, prompt)
            if response:
                self.completed += 1
            return response
        finally:
            thread_pool.completion_count += 1
            thread_pool.previous_created_at = run.created_at
            await self._release_thread(thread_pool)

    async def _create_message(self, thread: Thread, message: str) -> Message:
        return await self._client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=message
        )

    async def _create_run(self, thread: Thread) -> Run:
        return await self._client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=self._assistant.id,
        )

    async def _retrieve_run(self, thread: Thread, run: Run, message: str) -> dict[str, list[str]] | None:
        status = await self._get_response(thread, run, message)
        if not status:
            return None

        response = await self._get_message_response(thread, run, message)
        if not response:
            return None

        dict_response = await self._parse_json(run, response)
        if not dict_response:
            return None

        if is_valid_dict(dict_response):
            return dict_response
        else:
            return None

    async def _get_response(self, thread: Thread, run: Run, prompt: str) -> bool:
        start_time = time.time()
        while True:
            if time.time() - start_time > _TIMEOUT_SECS:
                self.logger.error(f"Run {run.id} timed out.")
                await self._log_failed_batch(run.id, prompt, "Run timed out", None)
                return False

            status = await self._client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id,
            )

            if status.status not in ("queued", "in_progress"):
                break
            await asyncio.sleep(10)

        if status.status != "completed":
            self.logger.error(f"Run {run.id} failed with status: {status.status}")
            await self._log_failed_batch(
                run.id, prompt, f"Response status was {status.status}, not completed", status.status
            )
            return False
        else:
            return True


    async def _get_message_response(self, thread: Thread, run: Run, original_message: str) -> str | None:
        messages = await self._client.beta.threads.messages.list(thread_id=thread.id)
        assistant_message = next(
            (m for m in messages.data if m.role == "assistant" and m.created_at >= run.created_at),
            None
        )

        if not assistant_message:
            response_messages = ', '.join(map(lambda m: str(m.data), messages))
            await self._log_failed_batch(
                run.id, original_message, "No assistant message found", response_messages
            )
            return None

        return assistant_message.content[0].text.value

    async def _parse_json(self, run: Run, content: str) -> dict | None:
        try:
            return json.loads(content)
        except Exception as e:
            self.logger.error(f"Failed to parse JSON: {e}")
            await self._log_failed_batch(run.id, content, "Failed to parse JSON", content)
            return None

    async def _log_failed_batch(self, run_id: str, batch: str, reason: str, raw_response: str | None):

        self.failed += 1
        self.logger.debug(
            f"Preparing to log failed batch request"
            f"\n\tID: {run_id}\n\tBatch: {batch}"
            f"\n\tReason: {reason}\n\tRaw Response`: {raw_response}"
        )
        log = {
            "run_id": run_id,
            "message": batch,
            "reason": reason,
            "raw_response": raw_response,
        }

        try:
            async with aiofiles.open(_ERROR_PATH, mode="r+", encoding="utf-8") as f:
                content = await f.read()
                data = json.loads(content) if content.strip() else {}
                data[run_id] = log
                await f.seek(0)
                await f.write(json.dumps(data, indent=4))
                await f.truncate()
        except Exception as e:
            self.logger.error(f"Failed to log failed batch ({raw_response} due to:\n{e}")
