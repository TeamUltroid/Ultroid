//! The Rust port of `rust/harness/dbvalue.py`: the database value format.
//!
//! The format itself lives in the `ultroid-db` crate, which has no Python in it. This crate is
//! the bridge that holds it against the original.

#![forbid(unsafe_code)]

use ultroid_db::bridge::from_bridge;
use ultroid_db::{PyValue, canon, has_set_order, normalize, to_str};

/// The type name and `repr` of a value, the way `fixture.describe` reports them.
fn describe(value: &PyValue) -> Result<Vec<String>, String> {
    let text = canon(value).map_err(|error| error.to_string())?;
    Ok(vec![value.type_name().to_string(), text])
}

/// Port of `read_stored` (`rust/harness/dbvalue.py:11`).
pub fn read_stored(text: String) -> Result<Vec<String>, String> {
    describe(&ultroid_db::read_stored(&text))
}

/// Port of `write_value` (`rust/harness/dbvalue.py:18`): what is kept, and the text stored.
pub fn write_value(value: serde_json::Value) -> Result<Vec<String>, String> {
    let kept = normalize(from_bridge(&value).map_err(|error| error.to_string())?);
    let stored = match to_str(&kept) {
        Ok(text) => text,
        // Text with a lone surrogate: the cache keeps it, no backend takes it.
        Err(error) if error.kind == "UnicodeEncodeError" => format!("refused: {}", error.kind),
        Err(error) => return Err(error.to_string()),
    };
    let mut described = describe(&kept)?;
    // As in the original's harness: where set order shows, both sides print sets sorted.
    described.push(if has_set_order(&kept) {
        canon(&kept).map_err(|error| error.to_string())?
    } else {
        stored
    });
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
