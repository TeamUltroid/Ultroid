//! Ultroid's database layer in Rust.
//!
//! Ultroid keeps all its state in a key-value database (Redis, MongoDB, PostgreSQL or a local
//! file). Whatever the backend, a value is stored as the text of Python's `str(value)` and read
//! back with `ast.literal_eval`. A Rust Ultroid has to read and write that same text, or every
//! existing deployment loses its data. This crate is that format, proven against the Python
//! original case by case (`rust/dbvalue-rs`).

#![forbid(unsafe_code)]

pub mod bridge;
pub mod literal;
pub mod repr;
pub mod tables;
pub mod value;

pub use literal::parse_literal;
pub use repr::{canon, repr, to_str};
pub use value::{Key, PyDict, PyError, PyResult, PySet, PyValue};

/// What `get_key` makes of stored text: the literal it reads as, or the text itself.
pub fn read_stored(text: &str) -> PyValue {
    parse_literal(text).unwrap_or_else(|| PyValue::Str(text.to_string()))
}

/// What `set_key` keeps for a value. Text that reads as a literal becomes that literal, so
/// storing `"+919876543210"` keeps the int `919876543210`.
pub fn normalize(value: PyValue) -> PyValue {
    match value {
        PyValue::Str(text) => read_stored(&text),
        other => other,
    }
}
