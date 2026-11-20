//! The Rust port of `rust/harness/dbvalue.py`: the database value format.
//!
//! The format itself lives in the `ultroid-db` crate, which has no Python in it. This crate is
//! the bridge that holds it against the original.

#![forbid(unsafe_code)]

use ultroid_db::bridge::from_bridge;
use ultroid_db::{PyValue, canon, normalize, to_str};

/// The type name and `repr` of a value, the way `fixture.describe` reports them.
fn describe(value: &PyValue) -> Result<Vec<String>, String> {
    let text = canon(value).map_err(|error| error.to_string())?;
    Ok(vec![value.type_name().to_string(), text])
}

/// Port of `read_stored` (`rust/harness/dbvalue.py:11`).
pub fn read_stored(text: String) -> Result<Vec<String>, String> {
    describe(&ultroid_db::read_stored(&text))
}

/// Whether printing a value depends on the order a set is iterated in. CPython follows its hash
/// table, this port follows insertion; each reads what the other writes.
fn has_set_order(value: &PyValue) -> bool {
    match value {
        PyValue::Set(set) => set.len() > 1 || set.iter().any(has_set_order),
        PyValue::List(items) | PyValue::Tuple(items) => items.iter().any(has_set_order),
        PyValue::Dict(dict) => dict
            .iter()
            .any(|(key, item)| has_set_order(key) || has_set_order(item)),
        _ => false,
    }
}

/// Port of `write_value` (`rust/harness/dbvalue.py:18`).
pub fn write_value(value: serde_json::Value) -> Result<Vec<String>, String> {
    let kept = normalize(from_bridge(&value).map_err(|error| error.to_string())?);
    let mut described = describe(&kept)?;
    // As in the original's harness: where set order shows, both sides print sets sorted.
    let stored = if has_set_order(&kept) {
        canon(&kept)
    } else {
        to_str(&kept)
    };
    described.push(stored.map_err(|error| error.to_string())?);
    Ok(described)
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    fn list(items: &[&str]) -> Result<Vec<String>, String> {
        Ok(items.iter().map(|item| item.to_string()).collect())
    }

    #[test]
    fn stored_text_reads_as_python_reads_it() {
        assert_eq!(
            read_stored("{-100: ['x']}".into()),
            list(&["dict", "{-100: ['x']}"])
        );
        assert_eq!(
            read_stored("+919876543210".into()),
            list(&["int", "919876543210"])
        );
        assert_eq!(
            read_stored("hello world".into()),
            list(&["str", "'hello world'"])
        );
        assert_eq!(read_stored(String::new()), list(&["str", "''"]));
    }

    #[test]
    fn values_are_stored_as_python_stores_them() {
        assert_eq!(write_value(json!("abc")), list(&["str", "'abc'", "abc"]));
        assert_eq!(
            write_value(json!("1e5")),
            list(&["float", "100000.0", "100000.0"])
        );
        assert_eq!(
            write_value(json!({"$dict": [[-100, ["it's"]]]})),
            list(&["dict", "{-100: [\"it's\"]}", "{-100: [\"it's\"]}"])
        );
        assert_eq!(
            write_value(json!(null)),
            list(&["NoneType", "None", "None"])
        );
    }
}
