//! The Rust port of `rust/harness/launch.py`: which clients `multi_client.py` starts.
//!
//! The logic is in the `ultroid-core` crate, which has no Python in it. This crate holds it
//! against the original script.

#![forbid(unsafe_code)]

use serde_json::{Value, json};
use std::collections::HashMap;
use ultroid_core::launch::{clients, nothing_configured};
use ultroid_db::PyValue;
use ultroid_db::bridge::from_bridge;

/// What the harness makes of a name or a value: text, or the failure of adding it to text.
fn text(value: &PyValue) -> Result<&str, String> {
    match value {
        PyValue::Str(text) => Ok(text),
        PyValue::Surrogates(_) => Err("NotImplementedError: half of a surrogate pair".to_string()),
        other => Err(format!(
            "TypeError: can only concatenate str (not \"{}\") to str",
            other.type_name()
        )),
    }
}

/// Port of `plan` (`rust/harness/launch.py:30`).
pub fn plan(environment: serde_json::Value) -> Result<Vec<serde_json::Value>, String> {
    let given = from_bridge(&environment).map_err(|error| error.to_string())?;
    let PyValue::Dict(given) = &given else {
        return Err(format!(
            "AttributeError: '{}' object has no attribute 'items'",
            given.type_name()
        ));
    };
    let mut variables = HashMap::new();
    for (name, value) in given.iter() {
        variables.insert(text(name)?, text(value)?);
    }
    let found = clients(|name| variables.get(name).copied());
    if found.is_empty() {
        return Ok(vec![json!("exit"), json!(nothing_configured())]);
    }
    let arguments = |arguments: Vec<std::ffi::OsString>| -> Value {
        let texts = arguments.iter().map(|argument| argument.to_string_lossy());
        json!(texts.collect::<Vec<_>>())
    };
    let started = found.iter().map(|client| arguments(client.arguments()));
    Ok([json!("start")].into_iter().chain(started).collect())
}
