import ast
import asyncio
import base64
import os
import sys
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from aiohttp import web
from PIL import Image

ROOT = Path(os.environ.get("ULTROID_SOURCE_ROOT", Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(ROOT))

from pyUltroid.fns import misc
from pyUltroid.fns.tools import check_filename


def response(data=None, status=200, body=b""):
    result = MagicMock()
    result.status = status
    result.json = AsyncMock(return_value=data)
    result.read = AsyncMock(return_value=body)
    result.__aenter__ = AsyncMock(return_value=result)
    return result


def load_command(namespace):
    # Importing the plugin registers commands and requires a live session.
    # Compile its actual handler with only those application globals replaced.
    source = ROOT / "plugins/utilities.py"
    tree = ast.parse(source.read_text())
    handler = next(
        node for node in tree.body if getattr(node, "name", "") == "abs_rmbg"
    )
    handler.decorator_list = []
    exec(
        compile(ast.Module(body=[handler], type_ignores=[]), str(source), "exec"),
        namespace,
    )
    return namespace["abs_rmbg"]


class RetrieveFileTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.original_directory = Path.cwd()
        self.directory = tempfile.TemporaryDirectory()
        os.chdir(self.directory.name)
        self.addCleanup(self.directory.cleanup)
        self.addCleanup(os.chdir, self.original_directory)
        self.source = Path("source.png")
        Image.new("RGBA", (2, 2), (12, 34, 56, 0)).save(self.source)
        self.png = self.source.read_bytes()
        self.url = "https://images.example/cutout.png?signature=example"
        self.post = response({"results": [{"url": self.url}]})
        self.get = response(body=self.png)
        self.session = MagicMock()
        self.session.__aenter__ = AsyncMock(return_value=self.session)
        self.session.post.return_value = self.post
        self.session.get.return_value = self.get
        factory_patch = patch.object(misc.aiohttp, "ClientSession")
        self.addCleanup(factory_patch.stop)
        self.factory = factory_patch.start()
        self.factory.return_value = self.session
        database_patch = patch.object(misc, "udB")
        self.addCleanup(database_patch.stop)
        self.database = database_patch.start()
        self.database.get_key.return_value = "example-leonardo-key"

    async def retrieve(self):
        return await misc.ReTrieveFile(str(self.source))

    def assert_error(self, result):
        ok, error = result
        self.assertFalse(ok)
        item = error["errors"][0]
        self.assertIsInstance(item["title"], str)
        self.assertTrue(item["title"])
        self.assertIsInstance(item["detail"], str)
        self.assertEqual(list(Path.cwd().iterdir()), [self.source.resolve()])
        return item

    async def test_success_uses_documented_request_and_preserves_transparency(self):
        ok, filename = await self.retrieve()
        self.assertTrue(ok)
        self.assertEqual(Path(filename).read_bytes(), self.png)
        with Image.open(filename) as result:
            self.assertEqual(result.getpixel((0, 0))[3], 0)
        args, kwargs = self.session.post.call_args
        self.assertEqual(
            args, ("https://cloud.leonardo.ai/api/rest/v2/generationssync",)
        )
        self.assertEqual(
            kwargs["headers"], {"Authorization": "Bearer example-leonardo-key"}
        )
        self.assertEqual(
            kwargs["json"],
            {
                "model": "remove-bg",
                "ephemeral": True,
                "parameters": {
                    "format": "png",
                    "guidances": {
                        "image_reference": [
                            {
                                "image": {
                                    "type": "BASE64",
                                    "data": base64.b64encode(self.png).decode(),
                                }
                            }
                        ]
                    },
                },
            },
        )
        self.session.get.assert_called_once_with(self.url)
        self.assertNotIn("headers", self.factory.call_args.kwargs)
        self.database.get_key.assert_called_once_with("LEONARDO_API_KEY")
        self.post.__aexit__.assert_awaited_once()
        self.get.__aexit__.assert_awaited_once()
        self.session.__aexit__.assert_awaited_once()

    async def test_explicit_timeout_allows_sync_processing(self):
        await self.retrieve()
        timeout = self.factory.call_args.kwargs["timeout"]
        self.assertGreater(timeout.total, 27)
        self.assertLessEqual(timeout.total, 90)

    async def test_existing_output_is_preserved(self):
        Path("ult-rmbg.png").write_bytes(b"existing")
        ok, filename = await self.retrieve()
        self.assertTrue(ok)
        self.assertNotEqual(filename, "ult-rmbg.png")
        self.assertEqual(Path("ult-rmbg.png").read_bytes(), b"existing")
        self.assertEqual(Path(filename).read_bytes(), self.png)

    async def test_missing_key_never_opens_source_or_calls_service(self):
        self.database.get_key.return_value = None
        self.source.unlink()
        ok, error = await self.retrieve()
        self.assertFalse(ok)
        self.assertIn("LEONARDO_API_KEY", str(error))
        self.factory.assert_not_called()

    async def test_missing_dependency_keeps_existing_exception(self):
        with patch.object(misc, "aiohttp", None):
            with self.assertRaises(misc.DependencyMissingError):
                await self.retrieve()

    async def test_http_error_takes_precedence_over_results(self):
        self.post.status = 401
        item = self.assert_error(await self.retrieve())
        self.assertIn("401", str(item))
        self.session.get.assert_not_called()

    async def test_provider_errors_take_precedence_over_results(self):
        self.post.json.return_value["errors"] = [
            {
                "message": "Insufficient credits",
                "extensions": {"code": "PAYMENT_REQUIRED"},
            }
        ]
        item = self.assert_error(await self.retrieve())
        self.assertEqual(
            item, {"title": "Insufficient credits", "detail": "PAYMENT_REQUIRED"}
        )
        self.session.get.assert_not_called()

    async def test_non_json_error_preserves_http_status(self):
        self.post.status = 502
        self.post.json.side_effect = ValueError("HTML response")
        self.assertIn("502", str(self.assert_error(await self.retrieve())))
        self.session.get.assert_not_called()

    async def test_non_json_success_is_an_invalid_response(self):
        self.post.json.side_effect = ValueError("HTML response")
        item = self.assert_error(await self.retrieve())
        self.assertIn("response", item["title"].lower())
        self.assertNotIn("HTTP 200", str(item))

    async def test_malformed_results_do_not_crash(self):
        for results in (
            None,
            {},
            "bad",
            [None],
            [1],
            ["bad"],
            [{}],
            [{"url": 123}],
            [{"url": ""}],
        ):
            with self.subTest(results=results):
                self.post.json.return_value = {"results": results}
                self.assert_error(await self.retrieve())
        self.session.get.assert_not_called()

    async def test_non_object_json_does_not_crash(self):
        for data in (None, [], [1], "bad", 1):
            with self.subTest(data=data):
                self.post.json.return_value = data
                self.assert_error(await self.retrieve())
        self.session.get.assert_not_called()

    async def test_empty_results_are_not_assumed_to_be_moderated(self):
        self.post.json.return_value = {"results": [], "blockedCount": 0}
        item = self.assert_error(await self.retrieve())
        self.assertNotIn("moderation", str(item).lower())
        self.assertIn("No image", item["title"])

    async def test_moderation_is_reported_when_confirmed(self):
        self.post.json.return_value = {"results": [], "blockedCount": 1}
        self.assertIn(
            "moderation", str(self.assert_error(await self.retrieve())).lower()
        )

    async def test_malformed_provider_errors_do_not_crash(self):
        for error in (
            None,
            "bad",
            {"message": None},
            {"message": "Rejected", "extensions": "bad"},
        ):
            with self.subTest(error=error):
                self.post.json.return_value = {"errors": [error]}
                self.assert_error(await self.retrieve())

    async def test_provider_status_code_is_preserved(self):
        self.post.json.return_value = {
            "errors": [{"message": "Unauthorized", "extensions": {"statusCode": 401}}]
        }
        self.assertIn("401", self.assert_error(await self.retrieve())["detail"])

    async def test_top_level_error_message_is_preserved(self):
        self.post.status = 429
        self.post.json.return_value = {"message": "Rate limit exceeded"}
        self.assertIn("Rate limit", self.assert_error(await self.retrieve())["title"])

    async def test_download_failure_is_not_saved(self):
        self.get.status = 403
        self.assertIn("403", str(self.assert_error(await self.retrieve())))

    async def test_empty_or_non_png_download_is_not_saved(self):
        for body in (b"", b"<html>error</html>", b'{"error":"failed"}'):
            with self.subTest(body=body):
                self.get.read.return_value = body
                self.assert_error(await self.retrieve())

    async def test_generation_transport_error_uses_return_contract(self):
        self.session.post.side_effect = misc.aiohttp.ClientConnectionError("offline")
        self.assert_error(await self.retrieve())
        self.session.get.assert_not_called()

    async def test_download_transport_error_uses_return_contract(self):
        self.session.get.side_effect = misc.aiohttp.ClientConnectionError("offline")
        self.assert_error(await self.retrieve())

    async def test_download_read_error_leaves_no_partial_file(self):
        self.get.read.side_effect = misc.aiohttp.ClientPayloadError("truncated")
        self.assert_error(await self.retrieve())

    async def test_disk_write_error_leaves_no_partial_file(self):
        @contextmanager
        def failing_open(filename, mode):
            with open(filename, mode) as file:
                if mode == "wb":

                    def write(content):
                        file.write(content[:8])
                        raise OSError("Disk full")

                    yield SimpleNamespace(write=write)
                else:
                    yield file

        with patch.object(misc, "open", failing_open, create=True):
            with self.assertRaisesRegex(OSError, "Disk full"):
                await self.retrieve()
        self.assertEqual(list(Path.cwd().iterdir()), [self.source.resolve()])

    async def test_timeout_uses_return_contract(self):
        self.post.json.side_effect = asyncio.TimeoutError
        self.assertIn("time", str(self.assert_error(await self.retrieve())).lower())

    async def test_cancellation_is_not_swallowed(self):
        self.get.read.side_effect = asyncio.CancelledError
        with self.assertRaises(asyncio.CancelledError):
            await self.retrieve()
        self.assertEqual(list(Path.cwd().iterdir()), [self.source.resolve()])


class CommandTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.original_directory = Path.cwd()
        self.directory = tempfile.TemporaryDirectory()
        os.chdir(self.directory.name)
        self.addCleanup(self.directory.cleanup)
        self.addCleanup(os.chdir, self.original_directory)
        self.database = MagicMock()
        self.database.get_key.return_value = "example-key"
        self.event = MagicMock()
        self.event.eor = AsyncMock()
        self.progress = MagicMock()
        self.progress.edit = AsyncMock()
        self.progress.delete = AsyncMock()
        self.event.eor.return_value = self.progress
        self.event.get_reply_message = AsyncMock(return_value=None)
        self.event.client.send_file = AsyncMock()
        self.event.pattern_match.group.return_value = " source.png"
        self.source = Path("source.png")
        Image.new("RGBA", (2, 2), (12, 34, 56, 0)).save(self.source)
        self.png = self.source.read_bytes()
        self.output = "ult-rmbg.png"
        self.retrieve = AsyncMock(side_effect=self.create_output)
        self.namespace = {
            "os": os,
            "Image": Image,
            "udB": self.database,
            "HNDLR": ".",
            "eod": AsyncMock(),
            "get_string": lambda key: key,
            "check_filename": check_filename,
            "ReTrieveFile": self.retrieve,
        }
        self.command = load_command(self.namespace)

    async def create_output(self, filename):
        Path(self.output).write_bytes(self.png)
        return True, self.output

    async def test_local_source_is_preserved_and_outputs_are_cleaned(self):
        await self.command(self.event)
        self.assertEqual(self.source.read_bytes(), self.png)
        self.assertEqual(list(Path.cwd().iterdir()), [self.source.resolve()])
        self.assertEqual(self.event.client.send_file.await_count, 2)
        self.progress.delete.assert_awaited_once()

    async def test_png_and_webp_uploads_preserve_transparency(self):
        uploads = []

        async def capture(chat_id, filename, **kwargs):
            with Image.open(filename) as image:
                uploads.append((image.format, image.getpixel((0, 0))[3], kwargs))

        self.event.client.send_file.side_effect = capture
        await self.command(self.event)
        self.assertEqual(
            [(item[0], item[1]) for item in uploads], [("PNG", 0), ("WEBP", 0)]
        )
        self.assertTrue(uploads[0][2]["force_document"])

    async def test_provider_failure_preserves_local_source(self):
        self.retrieve.side_effect = None
        self.retrieve.return_value = False, {
            "errors": [{"title": "Rejected", "detail": "BAD_REQUEST"}]
        }
        await self.command(self.event)
        self.assertEqual(self.source.read_bytes(), self.png)
        self.progress.edit.assert_awaited_once()
        self.event.client.send_file.assert_not_awaited()

    async def test_failed_send_still_cleans_generated_files(self):
        self.event.client.send_file.side_effect = RuntimeError("send failed")
        with self.assertRaisesRegex(RuntimeError, "send failed"):
            await self.command(self.event)
        self.assertEqual(list(Path.cwd().iterdir()), [self.source.resolve()])

    async def test_cancellation_still_cleans_generated_files(self):
        self.event.client.send_file.side_effect = asyncio.CancelledError
        with self.assertRaises(asyncio.CancelledError):
            await self.command(self.event)
        self.assertEqual(list(Path.cwd().iterdir()), [self.source.resolve()])

    async def test_invalid_download_does_not_try_to_unlink_none(self):
        self.event.pattern_match.group.return_value = ""
        self.event.get_reply_message.return_value = SimpleNamespace(
            media=True, document=None, download_media=AsyncMock(return_value=None)
        )
        await self.command(self.event)
        self.retrieve.assert_not_awaited()

    async def test_downloaded_source_is_cleaned_on_service_failure(self):
        self.event.pattern_match.group.return_value = ""
        self.event.get_reply_message.return_value = SimpleNamespace(
            media=True,
            document=None,
            download_media=AsyncMock(return_value=str(self.source)),
        )
        self.retrieve.side_effect = None
        self.retrieve.return_value = False, {
            "errors": [{"title": "Rejected", "detail": ""}]
        }
        await self.command(self.event)
        self.assertFalse(self.source.exists())

    async def test_webp_conversion_preserves_source_and_existing_png(self):
        source = Path("source.webp")
        Image.new("RGBA", (2, 2), (0, 0, 0, 0)).save(source)
        original = source.read_bytes()
        Path("source.webp.png").write_bytes(b"existing")
        self.event.pattern_match.group.return_value = " source.webp"
        await self.command(self.event)
        self.assertEqual(source.read_bytes(), original)
        self.assertEqual(Path("source.webp.png").read_bytes(), b"existing")
        self.assertEqual(
            set(Path.cwd().iterdir()),
            {
                source.resolve(),
                self.source.resolve(),
                Path("source.webp.png").resolve(),
            },
        )

    async def test_invalid_output_is_reported_and_cleaned(self):
        self.png = b"\x89PNG\r\n\x1a\ntruncated"
        await self.command(self.event)
        self.assertEqual(set(Path.cwd().iterdir()), {self.source.resolve()})
        self.event.client.send_file.assert_not_awaited()
        self.progress.edit.assert_awaited_once()

    async def test_key_setup_is_actionable_and_does_not_use_legacy_key(self):
        self.database.get_key.side_effect = lambda key: (
            "legacy-key" if key == "RMBG_API" else None
        )
        await self.command(self.event)
        self.retrieve.assert_not_awaited()
        text = self.event.eor.call_args.args[0]
        self.assertIn(".setdb LEONARDO_API_KEY", text)
        self.assertNotIn("no longer work", text)


class AiohttpTransportTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.original_directory = Path.cwd()
        self.directory = tempfile.TemporaryDirectory()
        os.chdir(self.directory.name)
        self.addCleanup(self.directory.cleanup)
        self.addCleanup(os.chdir, self.original_directory)
        self.source = Path("source.png")
        Image.new("RGBA", (2, 2), (12, 34, 56, 0)).save(self.source)
        self.png = self.source.read_bytes()
        self.requests = []
        self.generation_status = 200
        self.generation_error = None
        self.result_body = self.png
        app = web.Application()
        app.router.add_post("/generate", self.generate)
        app.router.add_get("/cutout.png", self.download)
        runner = web.AppRunner(app)
        await runner.setup()
        self.addAsyncCleanup(runner.cleanup)
        site = web.TCPSite(runner, "127.0.0.1", 0)
        await site.start()
        self.server_url = f"http://127.0.0.1:{site._server.sockets[0].getsockname()[1]}"

    async def generate(self, request):
        self.requests.append(
            (request.path, dict(request.headers), await request.json())
        )
        if self.generation_error is not None:
            return web.json_response(
                self.generation_error, status=self.generation_status
            )
        return web.json_response(
            {"results": [{"url": self.server_url + "/cutout.png"}]},
            status=self.generation_status,
        )

    async def download(self, request):
        self.requests.append((request.path, dict(request.headers), None))
        return web.Response(body=self.result_body, content_type="image/png")

    async def retrieve(self):
        real_session = misc.aiohttp.ClientSession

        def factory(**kwargs):
            session = real_session(**kwargs)
            post = session.post

            def local_post(url, **request_kwargs):
                self.assertEqual(
                    url, "https://cloud.leonardo.ai/api/rest/v2/generationssync"
                )
                return post(self.server_url + "/generate", **request_kwargs)

            session.post = local_post
            return session

        with patch.object(misc, "udB") as database:
            database.get_key.return_value = "example-key"
            with patch.object(misc.aiohttp, "ClientSession", side_effect=factory):
                return await misc.ReTrieveFile(str(self.source))

    async def test_real_http_request_and_result_download(self):
        ok, filename = await self.retrieve()
        self.assertTrue(ok)
        self.assertEqual(Path(filename).read_bytes(), self.png)
        post, get = self.requests
        self.assertEqual(post[1]["Authorization"], "Bearer example-key")
        self.assertEqual(post[1]["Content-Type"], "application/json")
        self.assertEqual(post[2]["model"], "remove-bg")
        self.assertTrue(post[2]["ephemeral"])
        image = post[2]["parameters"]["guidances"]["image_reference"][0]["image"]
        self.assertEqual(base64.b64decode(image["data"]), self.png)
        self.assertNotIn("Authorization", get[1])

    async def test_real_http_200_provider_error(self):
        self.generation_error = {
            "errors": [{"message": "Rejected", "extensions": {"code": "BAD_REQUEST"}}]
        }
        ok, error = await self.retrieve()
        self.assertFalse(ok)
        self.assertEqual(
            error["errors"][0], {"title": "Rejected", "detail": "BAD_REQUEST"}
        )
        self.assertEqual(len(self.requests), 1)

    async def test_real_http_error_with_results_does_not_download(self):
        self.generation_status = 503
        ok, error = await self.retrieve()
        self.assertFalse(ok)
        self.assertIn("503", str(error))
        self.assertEqual(len(self.requests), 1)

    async def test_real_http_200_invalid_image_is_not_saved(self):
        self.result_body = b"<html>upstream unavailable</html>"
        ok, error = await self.retrieve()
        self.assertFalse(ok)
        self.assertIn("PNG", str(error))
        self.assertEqual(list(Path.cwd().iterdir()), [self.source.resolve()])


if __name__ == "__main__":
    unittest.main()
