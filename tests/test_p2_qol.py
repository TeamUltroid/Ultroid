# Ultroid - UserBot
# P2 QoL unit tests (no Telegram / no network).

from __future__ import annotations

import ast
import importlib.util
import os
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class MultiClientTests(unittest.TestCase):
    def test_source_has_no_oob_indexes(self):
        src = (ROOT / "multi_client.py").read_text(encoding="utf-8")
        # Old bug used out[3], out[4] with only 3 auth values
        self.assertNotIn("out[3]", src)
        self.assertNotIn("out[4]", src)
        self.assertIn("REDIS", src)
        self.assertIn("SESSION1", src)

    def test_client_env_helper(self):
        spec = importlib.util.spec_from_file_location("mc", ROOT / "multi_client.py")
        mod = importlib.util.module_from_spec(spec)
        # don't run main
        code = compile((ROOT / "multi_client.py").read_text(), "multi_client.py", "exec")
        # exec only functions by loading module with blocked main
        with mock.patch.dict(os.environ, {}, clear=True):
            spec.loader.exec_module(mod)
            self.assertIsNone(mod._client_env(""))
        env = {
            "API_ID": "1",
            "API_HASH": "h",
            "SESSION": "s",
            "API_ID1": "2",
            "API_HASH1": "h1",
            "SESSION1": "s1",
            "REDIS_URI": "localhost:6379",
            "REDIS_PASSWORD": "pw",
        }
        with mock.patch.dict(os.environ, env, clear=True):
            self.assertEqual(mod._client_env(""), ["1", "h", "s"])
            self.assertEqual(mod._client_env("1"), ["2", "h1", "s1"])
            self.assertEqual(mod._redis_pair(), ("localhost:6379", "pw"))


class I18nScriptTests(unittest.TestCase):
    def test_script_runs(self):
        import subprocess

        rc = subprocess.call(
            [sys.executable, str(ROOT / "scripts" / "check_i18n_keys.py")],
            cwd=str(ROOT),
            stdout=subprocess.DEVNULL,
        )
        self.assertEqual(rc, 0)


class AddonModeTests(unittest.TestCase):
    def test_schema_has_addons_mode(self):
        schema = (ROOT / "pyUltroid" / "startup" / "settings_schema.py").read_text()
        self.assertIn("ADDONS_MODE", schema)

    def test_plug_mentions_mode(self):
        src = (ROOT / "pyUltroid" / "startup" / "funcs.py").read_text()
        self.assertIn("ADDONS_MODE", src)
        self.assertIn("official-only", src)


class FloodWaitTests(unittest.TestCase):
    def test_no_unconditional_disconnect(self):
        src = (ROOT / "pyUltroid" / "_misc" / "_decorators.py").read_text()
        self.assertIn("wait_for > 120", src)


class ReadyFileTests(unittest.TestCase):
    def test_main_writes_ready(self):
        src = (ROOT / "pyUltroid" / "__main__.py").read_text()
        self.assertIn("ULTROID_READY_FILE", src)
        self.assertIn("ultroid.ready", src)


class PluginsCtlTests(unittest.TestCase):
    def test_plugin_exists(self):
        self.assertTrue((ROOT / "plugins" / "pluginsctl.py").exists())
        src = (ROOT / "plugins" / "pluginsctl.py").read_text()
        # parseable
        ast.parse(src)
        self.assertIn("disableplugin", src)
        self.assertIn("reload", src)


class DocsTests(unittest.TestCase):
    def test_multi_client_doc(self):
        self.assertTrue((ROOT / "docs" / "MULTI_CLIENT.md").exists())

    def test_readme_docker_first(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("Docker Compose (recommended)", text)
        self.assertIn("Legacy hosts", text)


if __name__ == "__main__":
    unittest.main()
