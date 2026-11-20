//! The Rust port of `rust/harness/dbaccess.py`: runs a scenario against the accessors in
//! `ultroid-db` and reports it the way the harness reports the original.
//!
//! The accessors themselves are in the `ultroid-db` crate (ADR-014). What is here is the part
//! that belongs to the scenario: the steps that are not calls, and the shape of the report.

#![forbid(unsafe_code)]

use serde_json::{Value, json};
use ultroid_db::bridge::from_bridge;
use ultroid_db::{
    Database, DateTime, MemoryStore, PyError, PyResult, PyValue, Store, call, canon, has_set_order,
    read_stored,
};

/// A database in memory and the moment the scenario says it is.
struct Session {
    db: Database<MemoryStore>,
    start: DateTime,
    now: DateTime,
}

/// `"" + value`: the text, or the `TypeError` of adding something else to text.
fn text(value: &PyValue) -> PyResult<&str> {
    match value {
        PyValue::Str(text) => Ok(text),
        other => Err(PyError::type_error(format!(
            "can only concatenate str (not \"{}\") to str",
            other.type_name()
        ))),
    }
}

/// `operator.index(value)`: an int, or a bool as one.
fn index(value: &PyValue) -> PyResult<i64> {
    let whole = match value {
        PyValue::Int(whole) => i64::try_from(whole).ok(),
        PyValue::Bool(flag) => Some(i64::from(*flag)),
        other => {
            return Err(PyError::type_error(format!(
                "'{}' object cannot be interpreted as an integer",
                other.type_name()
            )));
        }
    };
    whole.ok_or_else(|| PyError::new("OverflowError", "date value out of range"))
}

/// One step: a list of a name and its arguments.
fn step(session: &mut Session, one: &Value) -> PyResult<PyValue> {
    let PyValue::List(parts) = from_bridge(one)? else {
        return Err(PyError::type_error("a step is a list"));
    };
    let [name, args @ ..] = parts.as_slice() else {
        return Err(PyError::value_error("a step starts with a name"));
    };
    let name = text(name)?;
    // The harness splits a name at its first dot, so `$restart.` is `$restart` too.
    match (name.split_once('.').unwrap_or((name, "")), args) {
        (("$restart", ""), []) => session.db.restart(),
        (("$raw", ""), [key, stored]) => {
            let (stored, key) = (text(stored)?, text(key)?);
            session.db.store_mut().set(key, stored)?;
            session.db.forget(key);
        }
        (("$clock", ""), [seconds]) => {
            session.now = session.start.plus_seconds(index(seconds)?)?;
        }
        (("$restart" | "$raw" | "$clock", ""), _) => {
            return Err(PyError::type_error("wrong number of arguments"));
        }
        _ => return call(&mut session.db, &session.now, name, args),
    }
    Ok(PyValue::None)
}

/// Port of `run` (`rust/harness/dbaccess.py:122`).
pub fn run(steps: Vec<serde_json::Value>) -> Result<Vec<serde_json::Value>, String> {
    let start = DateTime::new(2000, 1, 1, 0, 0, 0).map_err(|error| error.to_string())?;
    let mut session = Session {
        db: Database::new(MemoryStore::new()),
        start,
        now: start,
    };
    let mut results: Vec<Value> = steps
        .iter()
        .map(|one| {
            let done = step(&mut session, one)
                .and_then(|value| Ok(json!(["ok", value.type_name(), canon(&value)?])));
            done.unwrap_or_else(|error| json!(["error", error.kind]))
        })
        .collect();
    let mut stored = vec![json!("stored")];
    for (key, text) in session.db.store().entries() {
        // A set of several members has no fixed order in CPython, so it is shown sorted.
        let value = read_stored(text);
        let shown = if has_set_order(&value) {
            canon(&value).map_err(|error| error.to_string())?
        } else {
            text.to_string()
        };
        stored.push(json!([key, shown]));
    }
    results.push(Value::Array(stored));
    Ok(results)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn report(steps: Value) -> Value {
        Value::Array(run(steps.as_array().cloned().unwrap_or_default()).unwrap_or_default())
    }

    #[test]
    fn a_scenario_end_to_end() {
        // Recorded from the Python original by `rust/harness/dbaccess.py`.
        let got = report(json!([
            ["blacklist_db.add_blacklist", -1001, "spam"],
            ["blacklist_db.add_blacklist", -1001, "eggs ham spam"],
            ["$restart"],
            ["blacklist_db.rem_blacklist", -1001, "eggs"],
            ["blacklist_db.list_blacklist", -1001],
            ["afk_db.add_afk", "brb", null, null],
            ["$clock", 90061],
            ["afk_db.is_afk"],
            ["KeyManager.add", "PMPERMIT", "bad", 777],
            ["nope.nothing"],
            [],
            5,
        ]));
        let want = json!([
            ["ok", "bool", "True"],
            ["ok", "bool", "True"],
            ["ok", "NoneType", "None"],
            ["ok", "bool", "True"],
            ["ok", "str", "'👉`spam`\\n👉`ham`\\n'"],
            ["ok", "NoneType", "None"],
            ["ok", "NoneType", "None"],
            ["ok", "tuple", "('brb', None, None, '1 day, 1:01:01')"],
            ["error", "KeyError"],
            ["error", "KeyError"],
            ["error", "ValueError"],
            ["error", "TypeError"],
            [
                "stored",
                ["BLACKLIST_DB", "{-1001: ['spam', 'ham']}"],
                ["AFK_DB", "['brb', None, None, 'Jan 01 2000 12:00:00AM']"]
            ],
        ]);
        assert_eq!(got, want);
    }
}
