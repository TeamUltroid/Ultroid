//! Python bindings for `rust/harness/dbvalue.py`: generated from the signatures in `port.rs` by rust-anything.
//! Regenerate with `rust-anything refresh` after changing them.

use pyo3::prelude::*;

pub mod js;
pub mod port;
pub mod pyconv;
pub mod pynum;

#[allow(unused_imports)]
use pynum::Num;

fn error(message: String) -> PyErr {
    use pyo3::exceptions as e;
    let (kind, text) = message.split_once(": ").unwrap_or(("", message.as_str()));
    let text = text.to_string();
    match kind {
        "TypeError" => e::PyTypeError::new_err(text),
        "KeyError" => e::PyKeyError::new_err(text),
        "IndexError" => e::PyIndexError::new_err(text),
        "OverflowError" => e::PyOverflowError::new_err(text),
        "ZeroDivisionError" => e::PyZeroDivisionError::new_err(text),
        "AttributeError" => e::PyAttributeError::new_err(text),
        "RuntimeError" => e::PyRuntimeError::new_err(text),
        "NotImplementedError" => e::PyNotImplementedError::new_err(text),
        "LookupError" => e::PyLookupError::new_err(text),
        "ArithmeticError" => e::PyArithmeticError::new_err(text),
        "UnicodeError" => e::PyUnicodeError::new_err(text),
        "ValueError" => e::PyValueError::new_err(text),
        _ => e::PyValueError::new_err(message),
    }
}

fn read_stored_inner(text: String) -> Result<Vec<String>, String> {
    let out = port::read_stored(text)?;
    Ok(out)
}

/// `read_stored`.
#[pyfunction]
#[pyo3(name = "read_stored", signature = (text))]
fn read_stored(text: String) -> PyResult<Vec<String>> {
    read_stored_inner(text).map_err(error)
}

fn write_value_inner(value: Bound<'_, PyAny>) -> Result<Vec<String>, String> {
    let value: serde_json::Value = crate::pyconv::FromPy::from_py(&value)?;
    let out = port::write_value(value)?;
    Ok(out)
}

/// `write_value`.
#[pyfunction]
#[pyo3(name = "write_value", signature = (value))]
fn write_value(value: Bound<'_, PyAny>) -> PyResult<Vec<String>> {
    write_value_inner(value).map_err(error)
}

#[pymodule]
#[pyo3(name = "_native")]
fn native_module(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(read_stored, m)?)?;
    m.add_function(wrap_pyfunction!(write_value, m)?)?;
    Ok(())
}
