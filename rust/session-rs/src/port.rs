//! The Rust port of `rust/harness/session.py`: session strings.
//!
//! The logic is in the `ultroid-core` crate, which has no Python in it. This crate holds it
//! against the original: Ultroid's `validate_session` and Telethon's `StringSession`.

#![forbid(unsafe_code)]

use serde_json::{Value, json};
use ultroid_core::session::{StringSession, validate_session};
use ultroid_db::PyValue;
use ultroid_db::bridge::from_bridge;

/// The harness takes a session that is text or nothing; anything else fails as adding it to
/// text fails.
fn text(value: &Value) -> Result<Option<String>, String> {
    match from_bridge(value).map_err(|error| error.to_string())? {
        PyValue::None => Ok(None),
        PyValue::Str(text) => Ok(Some(text)),
        other => Err(format!(
            "TypeError: can only concatenate str (not \"{}\") to str",
            other.type_name()
        )),
    }
}

/// What the harness reads off a session: data centre, address, port, key in hex, and the string
/// Telethon would save.
fn fields(session: &StringSession) -> Vec<Value> {
    let hex = |key: [u8; 256]| {
        key.iter()
            .map(|byte| format!("{byte:02x}"))
            .collect::<String>()
    };
    vec![
        json!(session.dc_id),
        json!(session.server_address.map(|address| address.to_string())),
        json!(session.port),
        json!(session.auth_key.map(hex)),
        json!(session.save()),
    ]
}

/// Port of `check` (`rust/harness/session.py:42`).
pub fn check(
    session: serde_json::Value,
    leave: serde_json::Value,
) -> Result<Vec<serde_json::Value>, String> {
    let session = text(&session)?;
    let leave = from_bridge(&leave)
        .map_err(|error| error.to_string())?
        .truthy();
    Ok(match validate_session(session.as_deref(), leave) {
        // Nothing is logged before a string fails to decode.
        Err(error) => vec![json!("raised"), json!(error.python_name()), json!([])],
        Ok(checked) => match &checked.session {
            Some(session) => {
                let mut report = vec![json!("session")];
                report.extend(fields(session));
                report.push(json!(checked.logged));
                report
            }
            None if checked.exits => vec![json!("exit"), json!(checked.logged)],
            None => vec![json!("none"), json!(checked.logged)],
        },
    })
}

/// Port of `parse` (`rust/harness/session.py:58`).
pub fn parse(text: serde_json::Value) -> Result<Vec<serde_json::Value>, String> {
    let text = self::text(&text)?;
    Ok(
        match StringSession::parse(text.as_deref().unwrap_or_default()) {
            Err(error) => vec![json!("raised"), json!(error.python_name())],
            Ok(session) => {
                let mut report = vec![json!("session")];
                report.extend(fields(&session));
                report
            }
        },
    )
}
