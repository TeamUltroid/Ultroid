//! Python bindings for `rust/harness/command.py`: generated from the signatures in `port.rs` by rust-anything.
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

fn command_inner(
    pattern: String,
    handler: String,
    text: String,
) -> Result<Vec<serde_json::Value>, String> {
    let out = port::command(pattern, handler, text)?;
    Ok(out)
}

/// `command`.
#[pyfunction]
#[pyo3(name = "command", signature = (pattern, handler, text))]
fn command(py: Python<'_>, pattern: String, handler: String, text: String) -> PyResult<Py<PyAny>> {
    command_inner(pattern, handler, text)
        .map_err(error)
        .and_then(|v| crate::pyconv::ToPy::to_py(&v, py))
}

fn assistant_inner(pattern: String, text: String) -> Result<Vec<serde_json::Value>, String> {
    let out = port::assistant(pattern, text)?;
    Ok(out)
}

/// `assistant`.
#[pyfunction]
#[pyo3(name = "assistant", signature = (pattern, text))]
fn assistant(py: Python<'_>, pattern: String, text: String) -> PyResult<Py<PyAny>> {
    assistant_inner(pattern, text)
        .map_err(error)
        .and_then(|v| crate::pyconv::ToPy::to_py(&v, py))
}

fn inline_inner(pattern: String, text: String) -> Result<Vec<serde_json::Value>, String> {
    let out = port::inline(pattern, text)?;
    Ok(out)
}

/// `inline`.
#[pyfunction]
#[pyo3(name = "inline", signature = (pattern, text))]
fn inline(py: Python<'_>, pattern: String, text: String) -> PyResult<Py<PyAny>> {
    inline_inner(pattern, text)
        .map_err(error)
        .and_then(|v| crate::pyconv::ToPy::to_py(&v, py))
}

#[pymodule]
#[pyo3(name = "_native")]
fn native_module(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(command, m)?)?;
    m.add_function(wrap_pyfunction!(assistant, m)?)?;
    m.add_function(wrap_pyfunction!(inline, m)?)?;
    Ok(())
}
