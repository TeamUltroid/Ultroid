//! The Rust port of `rust/harness/command.py`: how a command is recognised.
//!
//! The logic is in the `ultroid-core` crate, which has no Python in it. This crate holds it
//! against the original: Ultroid's `compile_pattern` and Python's `re`.

#![forbid(unsafe_code)]

use serde_json::{Map, Value, json};
use ultroid_core::command::{Pattern, PatternError, assistant_pattern, command_pattern};

/// What the harness reports for a pattern on a text.
fn report(pattern: &str, text: &str) -> Result<Vec<Value>, String> {
    let compiled = match Pattern::new(pattern) {
        Ok(compiled) => compiled,
        Err(PatternError::Bad(_)) => return Ok(vec![json!("bad pattern")]),
        // No claim is made for these, so no answer is given either.
        Err(error) => return Err(format!("NotImplementedError: {error}")),
    };
    let Some(found) = compiled.match_start(text) else {
        return Ok(vec![json!("no")]);
    };
    let named: Map<String, Value> = found
        .named
        .into_iter()
        .map(|(name, value)| (name, json!(value)))
        .collect();
    Ok(vec![
        json!("match"),
        json!(found.end),
        json!(found.groups),
        Value::Object(named),
    ])
}

/// Port of `command` (`rust/harness/command.py:23`).
pub fn command(
    pattern: String,
    handler: String,
    text: String,
) -> Result<Vec<serde_json::Value>, String> {
    if pattern.is_empty() {
        return Ok(vec![json!("always")]);
    }
    report(&command_pattern(&pattern, &handler), &text)
}

/// Port of `assistant` (`rust/harness/command.py:36`).
pub fn assistant(pattern: String, text: String) -> Result<Vec<serde_json::Value>, String> {
    if pattern.is_empty() {
        return Ok(vec![json!("always")]);
    }
    report(&assistant_pattern(&pattern), &text)
}

/// Port of `inline` (`rust/harness/command.py:48`).
pub fn inline(pattern: String, text: String) -> Result<Vec<serde_json::Value>, String> {
    report(&pattern, &text)
}
