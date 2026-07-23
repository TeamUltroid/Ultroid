# Ultroid - UserBot
# P0 QoL unit tests (no Telegram / no network).

from __future__ import annotations

import importlib
import os
import sys
import types
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _load_validate():
    """Import config_validate without booting the full package."""
    # Ensure pyUltroid is a package path without running __init__ side effects
    pkg = types.ModuleType("pyUltroid")
    pkg.__path__ = [str(ROOT / "pyUltroid")]
    pkg.__file__ = str(ROOT / "pyUltroid" / "__init__.py")
    sys.modules.setdefault("pyUltroid", pkg)

    startup = types.ModuleType("pyUltroid.startup")
    startup.__path__ = [str(ROOT / "pyUltroid" / "startup")]
    startup.__file__ = str(ROOT / "pyUltroid" / "startup" / "__init__.py")
    sys.modules.setdefault("pyUltroid.startup", startup)

    name = "pyUltroid.startup.config_validate"
    if name in sys.modules:
        return importlib.reload(sys.modules[name])
    return importlib.import_module(name)


class _V:
    def __init__(self, **kw):
        defaults = dict(
            API_ID=12345,
            API_HASH="0123456789abcdef0123456789abcdef",
            SESSION="1" * 353,
            REDIS_URI=None,
            REDISHOST=None,
            REDISPORT=None,
            MONGO_URI=None,
            DATABASE_URL=None,
            BOT_TOKEN=None,
        )
        defaults.update(kw)
        for k, v in defaults.items():
            setattr(self, k, v)


class ConfigValidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cv = _load_validate()

    def test_rejects_default_api_credentials(self):
        v = _V(API_ID=6, API_HASH="eb06d4abfb49dc3eeb1aeb98ae0f581e")
        errors, _ = self.cv.collect_config_issues(v)
        self.assertTrue(any("defaults" in e.lower() or "API_ID" in e for e in errors))

    def test_accepts_custom_api(self):
        v = _V(REDIS_URI="127.0.0.1:6379")
        errors, warnings = self.cv.collect_config_issues(v)
        self.assertEqual(errors, [])

    def test_redis_uri_rejects_scheme(self):
        errs = self.cv.validate_redis_uri("redis://host:6379")
        self.assertTrue(errs)
        errs = self.cv.validate_redis_uri("https://host:6379")
        self.assertTrue(errs)

    def test_redis_uri_requires_port(self):
        errs = self.cv.validate_redis_uri("only-host")
        self.assertTrue(errs)

    def test_redis_uri_ok(self):
        self.assertEqual(self.cv.validate_redis_uri("redis-123.c1.example.com:12345"), [])

    def test_mongo_uri(self):
        self.assertTrue(self.cv.validate_mongo_uri("http://bad"))
        self.assertEqual(
            self.cv.validate_mongo_uri("mongodb+srv://u:p@cluster/db"), []
        )

    def test_database_url(self):
        self.assertTrue(self.cv.validate_database_url("mysql://x"))
        self.assertEqual(
            self.cv.validate_database_url("postgres://u:p@h:5432/db"), []
        )

    def test_missing_session_errors(self):
        v = _V(SESSION=None, BOT_TOKEN=None, REDIS_URI="h:1")
        errors, _ = self.cv.collect_config_issues(v)
        self.assertTrue(any("SESSION" in e for e in errors))

    def test_localdb_warning_without_strict(self):
        with mock.patch.dict(os.environ, {"ULTROID_STRICT_CONFIG": "0"}, clear=False):
            # reload truthy path
            v = _V(SESSION="x" * 353)
            errors, warnings = self.cv.collect_config_issues(v)
            self.assertFalse(any("Strict mode" in e for e in errors))
            self.assertTrue(any("LocalDB" in w or "remote database" in w for w in warnings))

    def test_strict_requires_remote_db(self):
        with mock.patch.dict(os.environ, {"ULTROID_STRICT_CONFIG": "1"}, clear=False):
            # force re-read of env inside strict_config
            v = _V(SESSION="x" * 353)
            errors, _ = self.cv.collect_config_issues(v)
            self.assertTrue(any("Strict mode" in e or "remote" in e.lower() for e in errors))

    def test_auto_pip_default_on(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("ULTROID_AUTO_PIP", None)
            self.assertTrue(self.cv.auto_pip_enabled())

    def test_auto_pip_off(self):
        with mock.patch.dict(os.environ, {"ULTROID_AUTO_PIP": "0"}):
            self.assertFalse(self.cv.auto_pip_enabled())

    def test_validate_or_exit_ok(self):
        v = _V(REDIS_URI="127.0.0.1:6379")
        log = mock.Mock()
        self.cv.validate_config_or_exit(v, log)

    def test_validate_or_exit_fails(self):
        v = _V(API_ID=6, API_HASH="eb06d4abfb49dc3eeb1aeb98ae0f581e")
        log = mock.Mock()
        with self.assertRaises(SystemExit) as ctx:
            self.cv.validate_config_or_exit(v, log)
        self.assertEqual(ctx.exception.code, 1)


class SetupCliTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Load setup_cli similarly isolated
        pkg = types.ModuleType("pyUltroid")
        pkg.__path__ = [str(ROOT / "pyUltroid")]
        sys.modules.setdefault("pyUltroid", pkg)
        startup = types.ModuleType("pyUltroid.startup")
        startup.__path__ = [str(ROOT / "pyUltroid" / "startup")]
        sys.modules.setdefault("pyUltroid.startup", startup)
        name = "pyUltroid.startup.setup_cli"
        if name in sys.modules:
            cls.cli = importlib.reload(sys.modules[name])
        else:
            cls.cli = importlib.import_module(name)

    def test_help(self):
        rc = self.cli.main(["--help"])
        self.assertEqual(rc, 0)

    def test_unknown(self):
        rc = self.cli.main(["nope"])
        self.assertEqual(rc, 2)

    def test_setup_noninteractive(self):
        tmp = ROOT / ".env_test_tmp_setup"
        if tmp.exists():
            tmp.unlink()
        with mock.patch.object(self.cli, "_is_interactive", return_value=False):
            with mock.patch.object(self.cli, "ENV_PATH", tmp):
                with mock.patch.object(self.cli, "ENV_SAMPLE", ROOT / ".env.sample"):
                    # avoid copying over a real path; sample exists
                    rc = self.cli.cmd_setup()
        self.assertEqual(rc, 0)
        if tmp.exists():
            tmp.unlink()

    def test_profiles_exist(self):
        for reqs in self.cli.PROFILES.values():
            for r in reqs:
                path = ROOT / r
                # termux/minimal only need requirements.txt
                if r == "requirements.txt":
                    self.assertTrue(path.exists(), r)


class EnvSampleTests(unittest.TestCase):
    def test_sample_has_required_keys(self):
        text = (ROOT / ".env.sample").read_text(encoding="utf-8")
        for key in (
            "API_ID",
            "API_HASH",
            "SESSION",
            "REDIS_URI",
            "ULTROID_AUTO_PIP",
            "SKIP_AUTOPILOT",
            "SKIP_AUTOJOIN",
        ):
            self.assertIn(key, text)

    def test_db_requirement_files(self):
        for name in (
            "requirements-db-redis.txt",
            "requirements-db-mongo.txt",
            "requirements-db-postgres.txt",
            "requirements-full.txt",
        ):
            self.assertTrue((ROOT / name).exists(), name)


if __name__ == "__main__":
    unittest.main()
