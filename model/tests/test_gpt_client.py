import time
import unittest
import pytest

from unittest.mock import patch, AsyncMock
from lib.util.openai.GPTClient import GPTClient, parse_list_response
from lib.util.openai.ThreadPool import ThreadPool

#############################################
# Dummy Classes and Async Helper Functions
#############################################

class DummyAssistant:
    def __init__(self, id, name=None):
        self.id = id
        self.name = name


class DummyThread:
    def __init__(self, id):
        self.id = id

    def __eq__(self, other):
        return isinstance(other, DummyThread) and self.id == other.id

    def __repr__(self):
        return f"DummyThread(id={self.id!r})"


class DummyRun:
    def __init__(self, id, created_at, status="completed"):
        self.id = id
        self.created_at = created_at
        self.status = status


class DummyText:
    def __init__(self, value):
        self.value = value


class DummyMessageContent:
    def __init__(self, text):
        self.text = DummyText(text)


class DummyMessage:
    def __init__(self, role, created_at, content_text):
        self.role = role
        self.created_at = created_at
        self.content = [DummyMessageContent(content_text)]


class DummyResponse:
    def __init__(self, data):
        self.data = data

    def __iter__(self):
        return iter(self.data)


class DummyAssistants:
    def __init__(self, existing_assistants=None):
        self.existing_assistants = existing_assistants or []

    async def list(self):
        return DummyResponse(self.existing_assistants)

    async def update(self, assistant_id, instructions, model):
        return DummyAssistant(assistant_id)

    async def create(self, name, instructions, model):
        return DummyAssistant("new-dummy-assistant", name)


class DummyThreads:
    async def create(self):
        return DummyThread("dummy-thread-id")

    class messages:
        @staticmethod
        async def create(thread_id, role, content):
            return DummyMessage(role, time.time(), content)

        @staticmethod
        async def list(thread_id):
            return DummyResponse([])

    class runs:
        @staticmethod
        async def create(thread_id, assistant_id):
            return DummyRun("dummy-run-id", time.time(), status="completed")

        @staticmethod
        async def retrieve(thread_id, run_id):
            return DummyRun(run_id, time.time(), status="completed")


class DummyBeta:
    def __init__(self, existing_assistants=None):
        self.assistants = DummyAssistants(existing_assistants)
        self.threads = DummyThreads()


class DummyClient:
    def __init__(self, existing_assistants=None):
        self.beta = DummyBeta(existing_assistants)


async def dummy_connect_client(self):
    self._client = DummyClient()


async def dummy_create_assistant(self):
    self._assistant = DummyAssistant("dummy-assistant-id", self.name)


async def dummy_populate_thread_pool(self):
    for i in range(self.pool_size):
        pool = ThreadPool(
            pool_id=i,
            thread=DummyThread(f"dummy-thread-{i}"),
            completion_count=0,
            previous_created_at=0,
        )
        await self._thread_queue.put(pool)


class DummyFile:
    def __init__(self, initial_content=""):
        self.content = initial_content

    async def seek(self, pos):
        pass

    async def read(self):
        return self.content

    async def write(self, data):
        self.content = data

    async def truncate(self):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass


def dummy_aiofiles_open_file_not_found(path, mode, encoding):
    if mode == "r+":
        raise FileNotFoundError
    return DummyFile()


def dummy_aiofiles_open_exception(path, mode, encoding):
    raise Exception("Dummy file error")

#############################################
# Unit Tests Using unittest Module
#############################################
@pytest.mark.asyncio
class TestGPTClient(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        # Patch only _connect_client and _populate_thread_pool globally.
        # We *do not* patch _create_assistant for tests that want to test its full logic.
        self.connect_patch = patch("lib.util.openai.GPTClient.GPTClient._connect_client", dummy_connect_client)
        self.thread_pool_patch = patch("lib.util.openai.GPTClient.GPTClient._populate_thread_pool",
                                       dummy_populate_thread_pool)
        self.connect_patch.start()
        self.thread_pool_patch.start()
        # Create a dummy GPTClient instance.
        # For tests that use _create_assistant logic, we will later stop the dummy _create_assistant patch.
        self.assistant_patch = patch("lib.util.openai.GPTClient.GPTClient._create_assistant", dummy_create_assistant)
        self.assistant_patch.start()
        self.client = await GPTClient.create("dummy", "dummy-model", "dummy-system", pool_size=3)

    async def asyncTearDown(self):
        patch.stopall()

    # 1. GPTClient Initialization
    async def test_gptclient_initialization(self):
        self.assertIsNotNone(self.client._client)
        self.assertIsNotNone(self.client._assistant)
        count = 0
        while not self.client._thread_queue.empty():
            await self.client._thread_queue.get()
            count += 1
        self.assertEqual(count, self.client.pool_size)

    # 2. Client Connection (_connect_client)
    async def test_connect_client(self):
        client = GPTClient("test", "model", "system", pool_size=1)
        await dummy_connect_client(client)
        self.assertIsInstance(client._client, DummyClient)

    # 3. Assistant Creation – Existing Assistant
    async def test_create_assistant_existing(self):
        # Stop the dummy patch so we exercise the real _create_assistant logic.
        self.assistant_patch.stop()
        client = GPTClient("dummy", "model", "system", pool_size=1)
        # Setup so that an assistant with matching name exists.
        client._client = DummyClient(existing_assistants=[DummyAssistant("existing-id", "dummy")])

        async def fake_list():
            return DummyResponse([DummyAssistant("existing-id", "dummy")])

        with patch.object(client._client.beta.assistants, "list", fake_list):
            async def fake_update(assistant_id, instructions, model):
                return DummyAssistant(assistant_id)

            with patch.object(client._client.beta.assistants, "update", fake_update):
                await client._create_assistant()
                self.assertEqual(client._assistant.id, "existing-id")

    # 4. Assistant Creation – New Assistant
    async def test_create_assistant_new(self):
        # Stop the dummy patch to test real _create_assistant logic
        self.assistant_patch.stop()

        # Instantiate a GPTClient with a unique name to simulate new assistant creation
        client = GPTClient("new_dummy", "model", "system", pool_size=1)

        # Patch the instance methods correctly (include 'self' as the first argument)
        async def fake_list(_self):
            return DummyResponse([])  # Simulate no existing assistants

        async def fake_create(_self, name, instructions, model):
            return DummyAssistant("created-id", name)

        # Inject patched methods into the instance's beta.assistants
        client._client = DummyClient()
        with patch.object(client._client.beta.assistants.__class__, "list", fake_list), \
                patch.object(client._client.beta.assistants.__class__, "create", fake_create):
            await client._create_assistant()
            self.assertEqual(client._assistant.id, "created-id")
            self.assertEqual(client._assistant.name, "new_dummy")

    # 5. Thread Pool Population
    async def test_thread_pool_population(self):
        count = 0
        while not self.client._thread_queue.empty():
            await self.client._thread_queue.get()
            count += 1
        self.assertEqual(count, self.client.pool_size)

    # 6. Creating a Thread Pool
    async def test_create_thread_pool(self):
        while not self.client._thread_queue.empty():
            await self.client._thread_queue.get()
        await self.client._create_thread_pool(99, 123456)
        pool = await self.client._get_available_thread()
        self.assertEqual(pool.pool_id, 99)
        # Flip order: expected value first.
        self.assertEqual(123456, pool.previous_created_at)

    # 7. Getting an Available Thread
    async def test_get_available_thread(self):
        dummy_pool = ThreadPool(0, DummyThread("dummy-thread-0"))
        await self.client._thread_queue.put(dummy_pool)
        pool = await self.client._get_available_thread()
        # Use equality check instead of identity.
        self.assertEqual(pool, dummy_pool)

    # 8. Releasing a Thread (Without Refresh)
    async def test_release_thread_without_refresh(self):
        dummy_pool = ThreadPool(0, DummyThread("dummy-thread-0"), completion_count=2, previous_created_at=0)
        while not self.client._thread_queue.empty():
            await self.client._thread_queue.get()
        await self.client._release_thread(dummy_pool)
        pool = await self.client._get_available_thread()
        self.assertEqual(pool, dummy_pool)

    # 9. Releasing a Thread (With Refresh)
    async def test_release_thread_with_refresh(self):
        dummy_pool = ThreadPool(1, DummyThread("dummy-thread-1"), completion_count=10, previous_created_at=111)
        refreshed = False

        async def fake_create_thread_pool(index, previous_created_at):
            nonlocal refreshed
            refreshed = True
            return ThreadPool(index, DummyThread(f"refreshed-thread-{index}"), 0, previous_created_at)

        with patch.object(self.client, "_create_thread_pool", fake_create_thread_pool):
            while not self.client._thread_queue.empty():
                await self.client._thread_queue.get()
            await self.client._release_thread(dummy_pool)
            self.assertTrue(refreshed)

    # 10. Processing Batch – Successful Response
    async def test_process_batch_success(self):
        # Dummy function to simulate creating a message
        async def fake_create_message(thread, message):
            return DummyMessage("user", time.time(), message)

        # Dummy function to simulate starting a run
        async def fake_create_run(thread):
            return DummyRun("run-id", time.time())

        # Simulate a successful run completion
        async def fake_get_response(thread, run, message):
            return True

        # Simulate the assistant's raw text response (multi-line, double newline separated)
        async def fake_get_message_response(thread, run, message):
            return "response1\n\nresponse2"

        with patch.object(self.client, "_create_message", fake_create_message), \
                patch.object(self.client, "_create_run", fake_create_run), \
                patch.object(self.client, "_get_response", fake_get_response), \
                patch.object(self.client, "_get_message_response", fake_get_message_response):
            pool = ThreadPool(0, DummyThread("dummy-thread-0"))
            await self.client._thread_queue.put(pool)

            batch = ["prompt1", "prompt2"]
            response = await self.client.process_batch(batch)

            expected = {
                "prompt1": ["response1"],
                "prompt2": ["response2"]
            }

            self.assertEqual(response, expected)

    # 11. Processing Batch – Timeout Scenario
    async def test_process_batch_timeout(self):
        async def fake_get_response(thread, run, prompt):
            return False

        with patch.object(self.client, "_get_response", fake_get_response):
            pool = ThreadPool(0, DummyThread("dummy-thread-timeout"))
            await self.client._thread_queue.put(pool)
            batch = ["prompt timeout"]
            response = await self.client.process_batch(batch)
            self.assertIsNone(response)

    # 12. Processing Batch – Non-Completed Run Status
    async def test_process_batch_non_completed(self):
        async def fake_get_response(thread, run, prompt):
            return False

        with patch.object(self.client, "_get_response", fake_get_response):
            pool = ThreadPool(0, DummyThread("dummy-thread-noncomplete"))
            await self.client._thread_queue.put(pool)
            batch = ["prompt noncompleted"]
            response = await self.client.process_batch(batch)
            self.assertIsNone(response)

    # 13. Creating a Message (_create_message)
    async def test_create_message(self):
        self.client._client = DummyClient()
        thread = DummyThread("thread-13")
        message = "Test message"
        msg = await self.client._create_message(thread, message)
        self.assertIsInstance(msg, DummyMessage)
        self.assertEqual(msg.role, "user")
        self.assertEqual(msg.content[0].text.value, message)

    # 14. Creating a Run (_create_run)
    async def test_create_run(self):
        self.client._assistant = DummyAssistant("assistant-14")
        self.client._client = DummyClient()
        thread = DummyThread("thread-14")
        run = await self.client._create_run(thread)
        self.assertIsInstance(run, DummyRun)
        self.assertTrue(hasattr(run, "created_at"))

    # 15. Retrieving Run Successfully (_retrieve_run)
    async def test_retrieve_run_success(self):
        async def fake_get_response(thread, run, prompt):
            return True

        # Simulate model returning plain text with rewrites per sentence separated by double newlines
        async def fake_get_message_response(thread, run, prompt):
            return "msg1\n\nmsg2"

        with patch.object(self.client, "_get_response", fake_get_response), \
                patch.object(self.client, "_get_message_response", fake_get_message_response):
            thread = DummyThread("thread-15")
            run = DummyRun("run-15", time.time())
            prompt = "sentence1\nsentence2"

            mapping = await self.client._retrieve_run(thread, run, prompt)

            expected = {
                "sentence1": ["msg1"],
                "sentence2": ["msg2"]
            }

            self.assertEqual(mapping, expected)

    # 16. Retrieving Run with Invalid Response Format
    async def test_retrieve_run_invalid_response_format(self):
        async def fake_get_response(thread, run, prompt):
            return True

        # Simulate assistant returning a single string response without double-newlines
        async def fake_get_message_response(thread, run, prompt):
            return "rewrite1\nrewrite2"  # Single group, no double-newline

        with patch.object(self.client, "_get_response", fake_get_response), \
                patch.object(self.client, "_get_message_response", fake_get_message_response):
            thread = DummyThread("thread-16")
            run = DummyRun("run-16", time.time())
            prompt = "sentence1\nsentence2"

            mapping = await self.client._retrieve_run(thread, run, prompt)

            # Should return None due to mismatch in lengths (2 prompts, only 1 group)
            self.assertIsNone(mapping)

    # 17. Getting Response – Successful Loop (_get_response)
    async def test_get_response_success(self):
        call_count = 0
        start_time = time.time()

        async def fake_retrieve(thread_id, run_id):
            nonlocal call_count
            call_count += 1
            status = "queued" if call_count < 3 else "completed"
            return DummyRun(run_id, time.time(), status=status)

        async def fake_sleep(_):
            return  # no-op to avoid delay

        with patch.object(self.client._client.beta.threads.runs, "retrieve", fake_retrieve), \
                patch("asyncio.sleep", new=fake_sleep):
            result = await self.client._get_response(
                DummyThread("thread-17"),
                DummyRun("run-17", start_time),
                "prompt"
            )
            self.assertTrue(result)

    # 18. Getting Response – Failure Loop (_get_response)
    async def test_get_response_failure(self):
        # Fake retrieve always returns a failed run
        async def fake_retrieve(thread_id, run_id):
            return DummyRun(run_id, time.time(), status="failed")

        # Freeze time to simulate timeout
        original_time = time.time

        def fake_time():
            # Simulate future timeout by advancing time
            return original_time() + 1000

        with patch.object(self.client._client.beta.threads.runs, "retrieve", fake_retrieve), \
                patch("time.time", fake_time), \
                patch.object(self.client, "_log_failed_batch", new=AsyncMock()):  # prevent file IO
            result = await self.client._get_response(
                DummyThread("thread-18"),
                DummyRun("run-18", original_time()),
                "prompt"
            )
            self.assertFalse(result)

    # 19. Getting Message Response – Success (_get_message_response)
    async def test_get_message_response_success(self):
        run_created = time.time() - 1
        valid_msg = DummyMessage("assistant", time.time(), "Valid response")

        async def fake_list(thread_id):
            return DummyResponse([valid_msg])

        with patch.object(self.client._client.beta.threads.messages, "list", fake_list):
            thread = DummyThread("thread-19")
            run = DummyRun("run-19", run_created)
            response = await self.client._get_message_response(thread, run, "prompt")
            self.assertEqual(response, "Valid response")

    # 20. Getting Message Response – Failure (_get_message_response)
    async def test_get_message_response_failure(self):
        async def fake_list(thread_id):
            return DummyResponse([])  # Simulate no messages returned

        with patch.object(self.client._client.beta.threads.messages, "list", fake_list), \
                patch.object(self.client, "_log_failed_batch", new=AsyncMock()):  # Prevent file access
            thread = DummyThread("thread-20")
            run = DummyRun("run-20", time.time())
            response = await self.client._get_message_response(thread, run, "prompt")
            self.assertIsNone(response)

    # 21. Parsing Model Response – Flat List Scenario
    async def test_parse_model_response_flat_list(self):
        response_text = "a\nb\nc"
        result = parse_list_response(response_text)
        expected = [["a", "b", "c"]]
        self.assertEqual(result, expected)

    # 22. Parsing Model Response – List-of-Lists Scenario
    async def test_parse_model_response_list_of_lists(self):
        response_text = "a\nb\n\nc"
        result = parse_list_response(response_text)
        expected = [["a", "b"], ["c"]]
        self.assertEqual(result, expected)

    # 23. Parsing Model Response – Invalid / Null Entries
    async def test_parse_model_response_invalid_and_null_entries(self):
        response_text = "null\n\n \n\nvalid\n\n"
        result = parse_list_response(response_text)
        expected = [[], [], ["valid"]]
        self.assertEqual(result, expected)

    # 24. Logging Failed Batch – File Not Found
    async def test_log_failed_batch_file_not_found(self):
        with patch("aiofiles.open", new=dummy_aiofiles_open_file_not_found):
            try:
                await self.client._log_failed_batch("run-24", "batch", "reason", "raw")
            except Exception as e:
                self.fail(f"Failed with exception: {e}")

    # 25. Logging Failed Batch – General File Operation Exception
    async def test_log_failed_batch_exception(self):
        # Instead of expecting an exception (since the method swallows errors),
        # we check that the failed counter is incremented.
        original_failed = self.client.failed
        with patch("aiofiles.open", new=dummy_aiofiles_open_exception):
            await self.client._log_failed_batch("run-25", "batch", "reason", "raw")
            self.assertGreater(self.client.failed, original_failed)

    # 1. Simulated Exception in _create_message (API failure)
    async def test_exception_in_create_message(self):
        async def fake_create_message_exception(thread, message):
            raise Exception("Simulated create message failure")

        with patch.object(self.client, "_create_message", fake_create_message_exception), \
                patch.object(self.client, "_log_failed_batch", new=AsyncMock()):
            # Ensure a thread is available
            pool = __import__("lib.util.openai.ThreadPool", fromlist=["ThreadPool"]).ThreadPool(0, DummyThread(
                "dummy-thread-exc"))
            await self.client._thread_queue.put(pool)
            response = await self.client.process_batch(["test prompt"])
            self.assertIsNone(response)

    # 2. Simulated Exception in _create_run (API failure)
    async def test_exception_in_create_run(self):
        async def fake_create_run_exception(thread):
            raise Exception("Simulated create run failure")

        with patch.object(self.client, "_create_run", fake_create_run_exception), \
                patch.object(self.client, "_log_failed_batch", new=AsyncMock()):
            pool = __import__("lib.util.openai.ThreadPool", fromlist=["ThreadPool"]).ThreadPool(0, DummyThread(
                "dummy-thread-exc-run"))
            await self.client._thread_queue.put(pool)
            response = await self.client.process_batch(["test prompt"])
            self.assertIsNone(response)

        # 3. _log_failed_batch with malformed JSON in the log file

    class DummyFileMalformed:
        def __init__(self, initial_content="malformed json"):
            self.content = initial_content

        async def seek(self, pos):
            pass

        async def read(self):
            return self.content

        async def write(self, data):
            self.content = data

        async def truncate(self):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

    async def test_log_failed_batch_malformed_json(self):
        with patch("aiofiles.open",
                   new=lambda path, mode, encoding: TestGPTClient.DummyFileMalformed("malformed json")):
            original_failed = self.client.failed
            await self.client._log_failed_batch("run-malformed", "batch", "reason", "raw")
            self.assertGreater(self.client.failed, original_failed)

    # 4. Parsing Unexpected Structure (dictionary-like content instead of groups)
    async def test_parse_model_response_unexpected_structure(self):
        response_text = '{"key": "value"}'  # Malformed in the context of plain-text groups
        result = parse_list_response(response_text)
        # It will treat this as one string group
        expected = [['{"key": "value"}']]
        self.assertEqual(result, expected)

    # 5. Parsing Empty String
    async def test_parse_model_response_empty_string(self):
        response_text = ""
        result = parse_list_response(response_text)
        expected = [[]]
        self.assertEqual(result, expected)

def main():
    unittest.main()


if __name__ == "__main__":
    main()
