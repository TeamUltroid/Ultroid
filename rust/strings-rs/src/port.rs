//! The Rust port of `rust/harness/language.py`: runs a scenario against the language strings in
//! `ultroid-core` and reports it the way the harness reports the original.
//!
//! The lookup itself is in the `ultroid-core` crate, which has no Python in it. What is here
//! is the scenario: the files it says are there, what it has the translator answer, and the
//! shape of the report.

#![forbid(unsafe_code)]

use serde_json::{Value, json};
use std::collections::VecDeque;
use ultroid_core::strings::{Host, Strings};
use ultroid_db::bridge::from_bridge;
use ultroid_db::ops::{add, contains, item, no_method};
use ultroid_db::{Database, MemoryStore, PyError, PyResult, PyValue, Store, canon, repr, to_str};

/// The files, the translator and the log of one scenario.
struct Scene {
    /// What is in `strings/strings`, in the order it is listed: a name, and what reading the
    /// file gives, or nothing for a name that cannot be read (a folder).
    entries: Vec<(String, Option<PyValue>)>,
    /// What each call to the translator does, in turn.
    script: VecDeque<PyValue>,
    events: Vec<Value>,
}

/// Where a path leads.
enum Place<'a> {
    /// A folder, by how far it is below the one the scenario runs in: `strings`,
    /// `strings/strings`, or an unreadable name in there.
    Folder(usize),
    File(&'a PyValue),
}

impl Scene {
    /// Follows a path from the folder the scenario runs in, the way the system does.
    fn find(&self, path: &str) -> Option<Place<'_>> {
        // The system takes no path with a NUL in it and none of 4096 bytes or more.
        if path.contains('\0') || path.len() >= 4096 {
            return None;
        }
        let mut place = Place::Folder(0);
        for part in path.split('/') {
            let Place::Folder(depth) = place else {
                return None;
            };
            place = match (part, depth) {
                ("" | ".", _) => Place::Folder(depth),
                // Above the scenario's folder is the machine's own, which is not looked into.
                ("..", _) => Place::Folder(depth.checked_sub(1)?),
                ("strings", 0 | 1) => Place::Folder(depth + 1),
                (name, 2) => match &self.entries.iter().find(|(entry, _)| entry == name)?.1 {
                    Some(held) => Place::File(held),
                    None => Place::Folder(3),
                },
                _ => return None,
            };
        }
        Some(place)
    }
}

/// `text.replace("{}", "", 1)`.
fn drop_one(text: &PyValue) -> PyResult<PyValue> {
    match text {
        PyValue::Str(text) => Ok(PyValue::str(text.replacen("{}", "", 1))),
        PyValue::Bytes(_) => Err(PyError::type_error("a bytes-like object is required")),
        other => Err(no_method(other, "replace")),
    }
}

impl Host for Scene {
    fn exists(&self, path: &str) -> bool {
        self.find(path).is_some()
    }

    fn read(&mut self, path: &str) -> PyResult<PyValue> {
        match self.find(path) {
            Some(Place::File(held)) => Ok(held.clone()),
            Some(Place::Folder(_)) => Err(PyError::new("IsADirectoryError", path)),
            None => Err(PyError::new("FileNotFoundError", path)),
        }
    }

    fn names(&self) -> Vec<String> {
        self.entries.iter().map(|(name, _)| name.clone()).collect()
    }

    fn translate(&mut self, text: &PyValue, lang: &PyValue) -> PyResult<PyValue> {
        let shown = |value| canon(value).unwrap_or_default();
        self.events
            .push(json!(["translate", shown(text), shown(lang)]));
        let way = self.script.pop_front().unwrap_or(PyValue::str("tag"));
        // The harness looks the way up in a dict: one it does not know is a `KeyError`.
        way.key()?;
        match &way {
            PyValue::Str(way) => match way.as_str() {
                "same" => Ok(text.clone()),
                "tag" => Ok(PyValue::str(format!(
                    "[{}] {}",
                    to_str(lang)?,
                    to_str(text)?
                ))),
                "empty" => Ok(PyValue::str("")),
                "drop" => drop_one(text),
                "extra" => add(text, &PyValue::str(" {}")),
                "break" => add(text, &PyValue::str("\\ Nx")),
                "none" => Ok(PyValue::None),
                "type" => Err(PyError::type_error("can only concatenate str to str")),
                "value" => Err(PyError::value_error("invalid literal for int()")),
                _ => Err(PyError::new("KeyError", way.as_str())),
            },
            other => Err(PyError::new("KeyError", repr(other).unwrap_or_default())),
        }
    }

    fn info(&mut self, message: &str) {
        self.events.push(json!(["log", "info", message]));
    }

    fn exception(&mut self, error: &PyError) {
        self.events.push(json!(["log", "exception", error.kind]));
    }
}

/// `"" + value`, for a value that may also be `None`.
fn text_or_none(value: &PyValue) -> PyResult<Option<&str>> {
    match value {
        PyValue::None => Ok(None),
        PyValue::Str(text) => Ok(Some(text)),
        other => Err(PyError::type_error(format!(
            "can only concatenate str (not \"{}\") to str",
            other.type_name()
        ))),
    }
}

/// A name the folder can hold: text without `/` or NUL, not `.` or `..`, of 200 bytes at most.
/// Anything else fails as the harness's check fails on it.
fn file_name(name: &PyValue) -> PyResult<String> {
    let has = |part: &str| contains(name, &PyValue::str(part));
    let plain = !has("/")? && !has("\0")? && !["", ".", ".."].iter().any(|odd| has_eq(name, odd));
    if !plain {
        return Err(PyError::new("KeyError", "False"));
    }
    match name {
        PyValue::Str(name) if name.len() <= 200 => Ok(name.clone()),
        PyValue::Str(_) => Err(PyError::new("KeyError", "False")),
        PyValue::Bytes(_) => Err(PyError::type_error("a bytes-like object is required")),
        other => Err(no_method(other, "encode")),
    }
}

fn has_eq(name: &PyValue, text: &str) -> bool {
    name.py_eq(&PyValue::str(text))
}

/// The scenario's setting: the scene, the stored language and the `LANGUAGE` variable.
type Setting = (Scene, Option<String>, Option<String>);

fn setting(setup: &PyValue) -> PyResult<Setting> {
    let part = |name: &str| item(setup, &PyValue::str(name)).map(|part| part.into_owned());
    let empty = PyValue::List(Vec::new());
    let files = match part("files")? {
        PyValue::Dict(files) => files,
        other => {
            let kind = other.type_name();
            return Err(PyError::type_error(format!(
                "'{kind}' object is not a mapping"
            )));
        }
    };
    let (broken, script) = (
        add(&part("broken")?, &empty)?,
        add(&part("translate")?, &empty)?,
    );
    let (stored, env) = (part("stored")?, part("env")?);
    let (PyValue::List(broken), PyValue::List(script)) = (broken, script) else {
        return Err(PyError::type_error("a list plus a list is a list"));
    };
    let mut entries: Vec<(String, Option<PyValue>)> = Vec::new();
    for name in &broken {
        let name = file_name(name)?;
        if !entries.iter().any(|(entry, _)| *entry == name) {
            entries.push((name, None));
        }
    }
    for (name, held) in files.iter() {
        let name = file_name(name)?;
        if !entries.iter().any(|(entry, _)| *entry == name) {
            entries.push((name, Some(held.clone())));
        }
    }
    let stored = text_or_none(&stored)?.map(str::to_string);
    let env = text_or_none(&env)?.map(str::to_string);
    if env.as_deref().is_some_and(|env| env.contains('\0')) {
        return Err(PyError::new("KeyError", "False"));
    }
    let scene = Scene {
        entries,
        script: script.into(),
        events: Vec::new(),
    };
    Ok((scene, stored, env))
}

/// One step on the module: the call it names, with the arguments Python would take.
fn call(strings: &mut Strings<Scene>, name: &str, arguments: &[PyValue]) -> PyResult<PyValue> {
    let wrong = || PyError::type_error(format!("{name}() takes other arguments"));
    match (name, arguments) {
        ("get_string", [key]) => strings.get_string(key, true),
        ("get_string", [key, res]) => strings.get_string(key, res.truthy()),
        ("get_help", [key]) => strings.get_help(key),
        ("get_languages", []) => strings.get_languages(),
        ("language", [value]) => {
            strings.lang = value.clone();
            Ok(PyValue::None)
        }
        _ => Err(wrong()),
    }
}

fn scenario(setup: &Value, steps: &[Value]) -> PyResult<Vec<Value>> {
    let (scene, stored, env) = setting(&from_bridge(setup)?)?;
    let mut db = Database::new(MemoryStore::new());
    if let Some(stored) = &stored {
        db.store_mut().set("language", stored)?;
    }
    let mut strings = Strings::start(&mut db, env.as_deref(), scene)?;
    let mut report = std::mem::take(&mut strings.host_mut().events);
    for step in steps {
        let step = add(&from_bridge(step)?, &PyValue::List(Vec::new()))?;
        let PyValue::List(parts) = &step else {
            return Err(PyError::type_error("a list plus a list is a list"));
        };
        let Some((name, arguments)) = parts.split_first() else {
            return Err(PyError::value_error("not enough values to unpack"));
        };
        name.key()?;
        let known = ["get_string", "get_help", "get_languages", "language"];
        let name = match name {
            PyValue::Str(name) if known.contains(&name.as_str()) => name.as_str(),
            other => return Err(PyError::new("KeyError", repr(other).unwrap_or_default())),
        };
        let outcome = match call(&mut strings, name, arguments) {
            Ok(value) => json!(["ok", value.type_name(), canon(&value)?]),
            Err(error) => json!(["error", error.kind]),
        };
        report.append(&mut strings.host_mut().events);
        report.push(outcome);
    }
    let mut loaded = Vec::new();
    for (code, held) in strings.languages().iter() {
        loaded.push(json!([canon(code)?, canon(held)?]));
    }
    report.push(json!(["state", canon(&strings.lang)?, loaded]));
    Ok(report)
}

/// Port of `run` (`rust/harness/language.py:80`).
pub fn run(
    setup: serde_json::Value,
    steps: Vec<serde_json::Value>,
) -> Result<Vec<serde_json::Value>, String> {
    scenario(&setup, &steps).map_err(|error| error.to_string())
}
