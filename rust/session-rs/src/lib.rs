//! Python bindings for `rust/harness/session.py`: generated from the signatures in `port.rs` by rust-anything.
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

fn check_inner(
    session: Bound<'_, PyAny>,
    leave: Bound<'_, PyAny>,
) -> Result<Vec<serde_json::Value>, String> {
    let session: serde_json::Value = crate::pyconv::FromPy::from_py(&session)?;
    let leave: serde_json::Value = crate::pyconv::FromPy::from_py(&leave)?;
    let out = port::check(session, leave)?;
    Ok(out)
}

/// `check`.
#[pyfunction]
#[pyo3(name = "check", signature = (session, leave))]
fn check(
    py: Python<'_>,
    session: Bound<'_, PyAny>,
    leave: Bound<'_, PyAny>,
) -> PyResult<Py<PyAny>> {
    check_inner(session, leave)
        .map_err(error)
        .and_then(|v| crate::pyconv::ToPy::to_py(&v, py))
}

fn parse_inner(text: Bound<'_, PyAny>) -> Result<Vec<serde_json::Value>, String> {
    let text: serde_json::Value = crate::pyconv::FromPy::from_py(&text)?;
    let out = port::parse(text)?;
    Ok(out)
}

/// `parse`.
#[pyfunction]
#[pyo3(name = "parse", signature = (text))]
fn parse(py: Python<'_>, text: Bound<'_, PyAny>) -> PyResult<Py<PyAny>> {
    parse_inner(text)
        .map_err(error)
        .and_then(|v| crate::pyconv::ToPy::to_py(&v, py))
}

#[pymodule]
#[pyo3(name = "_native")]
fn native_module(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(check, m)?)?;
    m.add_function(wrap_pyfunction!(parse, m)?)?;
    Ok(())
}
