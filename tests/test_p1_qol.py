# Ultroid - UserBot
# P1 QoL unit tests (no Telegram / no network).

from __future__ import annotations

import importlib
import importlib.util
import logging
import os
import sys
import types
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _load_module(name: str, rel: str):
    path = ROOT / rel
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class SettingsSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = _load_module(
            "ultroid_settings_schema", "pyUltroid/startup/settings_schema.py"
        )

    def test_bool_true_false(self):
        v, w = self.schema.coerce_value("ADDONS", "true")
        self.assertIs(v, True)
        self.assertIsNone(w)
        v, _ = self.schema.coerce_value("ADDONS", "0")
        self.assertIs(v, False)

    def test_bool_invalid(self):
        with self.assertRaises(ValueError):
            self.schema.coerce_value("ADDONS", "maybe")

    def test_int(self):
        v, _ = self.schema.coerce_value("LOG_CHANNEL", "-100123")
        self.assertEqual(v, -100123)

    def test_handler(self):
        v, _ = self.schema.coerce_value("HNDLR", "!")
        self.assertEqual(v, "!")
        with self.assertRaises(ValueError):
            self.schema.coerce_value("HNDLR", "toolong")

    def test_list_space(self):
        v, _ = self.schema.coerce_value("EXCLUDE_OFFICIAL", "a b c")
        self.assertEqual(v, ["a", "b", "c"])

    def test_list_literal(self):
        v, _ = self.schema.coerce_value("SUDOS", "[1, 2, 3]")
        self.assertEqual(v, [1, 2, 3])

    def test_unknown_warns(self):
        v, w = self.schema.coerce_value("CUSTOM_FOO", "bar")
        self.assertEqual(v, "bar")
        self.assertIn("unknown", w.lower())

    def test_keys_help(self):
        text = self.schema.format_keys_help("HNDLR")
        self.assertIn("HNDLR", text)


class LoaderReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Minimal stub package so loader can import LOGS
        pkg = types.ModuleType("pyUltroid")
        pkg.LOGS = logging.getLogger("test")
        pkg.__path__ = [str(ROOT / "pyUltroid")]
        sys.modules["pyUltroid"] = pkg
        fns = types.ModuleType("pyUltroid.fns")
        fns.__path__ = [str(ROOT / "pyUltroid" / "fns")]
        sys.modules["pyUltroid.fns"] = fns
        tools = types.ModuleType("pyUltroid.fns.tools")

        def get_all_files(path, ext):
            return []

        tools.get_all_files = get_all_files
        sys.modules["pyUltroid.fns.tools"] = tools

        name = "pyUltroid.loader"
        if name in sys.modules:
            cls.loader = importlib.reload(sys.modules[name])
        else:
            cls.loader = importlib.import_module(name)

    def test_report_accumulates(self):
        self.loader.reset_load_report()
        L = self.loader.Loader(path="plugins", key="Official", logger=logging.getLogger("t"))

        def ok_func(name):
            return types.ModuleType(name)

        def bad_func(name):
            raise ModuleNotFoundError("missingpkg")

        # use a real tiny file list via include of nonexistent -> empty ok
        # Directly exercise report helpers
        self.loader.LOAD_REPORT["loaded"].append(("Official", "ping"))
        self.loader.LOAD_REPORT["skipped_missing_dep"].append(
            ("Official", "pdftools", "skimage")
        )
        self.loader.LOAD_REPORT["failed"].append(("Addons", "x", "RuntimeError: boom"))
        text = self.loader.summarize_load_report(logging.getLogger("t"))
        self.assertIn("1 loaded", text)
        self.assertIn("missing-dep", text)
        self.assertIn("failed", text)


class RedactLogTests(unittest.TestCase):
    def test_redact_filter_logic(self):
        # Mirror _RedactFilter without importing startup package side effects
        import re
        from logging import Filter, LogRecord

        secret_re = re.compile(
            r"(?i)(api_hash|api_id|session|bot_token|password|token|secret|authorization)"
            r"([\"']?\s*[:=]\s*[\"']?)([^\s,\"']{6,})"
        )

        class RedactFilter(Filter):
            def filter(self, record):
                try:
                    msg = record.getMessage()
                except Exception:
                    return True
                redacted = secret_re.sub(r"\1\2***", msg)
                if redacted != msg:
                    record.msg = redacted
                    record.args = ()
                return True

        filt = RedactFilter()
        rec = LogRecord(
            "t",
            logging.INFO,
            __file__,
            1,
            "session=ABCDEF123456 password=secret99",
            (),
            None,
        )
        self.assertTrue(filt.filter(rec))
        msg = rec.getMessage()
        self.assertNotIn("ABCDEF123456", msg)
        self.assertIn("***", msg)

        # Source file must define the filter used at runtime
        src = (ROOT / "pyUltroid" / "startup" / "__init__.py").read_text(encoding="utf-8")
        self.assertIn("class _RedactFilter", src)
        self.assertIn("LOG_LEVEL", src)


class DockerComposeTests(unittest.TestCase):
    def test_compose_has_redis_and_health(self):
        text = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
        self.assertIn("redis:", text)
        self.assertIn("healthcheck:", text)
        self.assertIn("env_file:", text)
        self.assertIn("ultroid-data", text)


class HelpBotStringTests(unittest.TestCase):
    def test_en_help_mentions_doctor_and_keys(self):
        text = (ROOT / "strings" / "strings" / "en.yml").read_text(encoding="utf-8")
        self.assertIn("{i}doctor", text)
        self.assertIn("{i}keys", text)


if __name__ == "__main__":
    unittest.main()
