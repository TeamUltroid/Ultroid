//! Ultroid's database layer in Rust.
//!
//! Ultroid keeps all its state in a key-value database (Redis, MongoDB, PostgreSQL or a local
//! file). Whatever the backend, a value is stored as the text of Python's `str(value)` and read
//! back with `ast.literal_eval`. A Rust Ultroid has to read and write that same text, or every
//! existing deployment loses its data.
//!
//! - [`value`], [`literal`], [`repr`]: Python values, and the text they are stored as.
//! - [`database`]: `udB`, the cache over a store of that text.
//! - [`ops`], [`clock`]: what Python does to those values when the accessors work on them.
//! - [`access`]: the accessors of `pyUltroid/dB`, function for function.
//! - [`call`]: the same by their Python names, for a bridge or a test.
//!
//! Each part is proven against the Python original case by case, in `rust/dbvalue-rs` and
//! `rust/dbaccess-rs`.
//!
//! ```
//! use ultroid_db::access::notes_db;
//! use ultroid_db::{Database, MemoryStore, PyValue, repr};
//!
//! let mut db = Database::new(MemoryStore::new());
//! let (chat, word) = (PyValue::int(-1001234567890_i64), PyValue::str("rules"));
//! let (msg, none) = (PyValue::str("be kind"), PyValue::None);
//! notes_db::add_note(&mut db, &chat, &word, &msg, &none, &none)?;
//! let note = notes_db::get_notes(&mut db, &chat, &word)?;
//! assert_eq!(repr(&note)?, "{'msg': 'be kind', 'media': None, 'button': None}");
//! assert_eq!(
//!     db.store().entries().collect::<Vec<_>>(),
//!     [("NOTE", "{-1001234567890: {'rules': {'msg': 'be kind', 'media': None, 'button': None}}}")]
//! );
//! # Ok::<(), ultroid_db::PyError>(())
//! ```

#![forbid(unsafe_code)]

pub mod access;
pub mod bridge;
pub mod call;
pub mod clock;
pub mod database;
pub mod literal;
pub mod ops;
pub mod repr;
pub mod tables;
pub mod value;

pub use call::call;
pub use clock::DateTime;
pub use database::{Database, MemoryStore, Store};
pub use literal::parse_literal;
pub use num_bigint::BigInt;
pub use repr::{canon, has_set_order, repr, to_str};
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
