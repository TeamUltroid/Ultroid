//! Python bindings for `pyUltroid/fns/helper.py`: generated from the signatures in `port.rs` by rust-anything.
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

fn time_formatter_inner(milliseconds: Bound<'_, PyAny>) -> Result<String, String> {
    let milliseconds: Num = crate::pyconv::FromPy::from_py(&milliseconds)?;
    let out = port::time_formatter(milliseconds)?;
    Ok(out)
}

/// `time_formatter`.
#[pyfunction]
#[pyo3(name = "time_formatter", signature = (milliseconds))]
fn time_formatter(milliseconds: Bound<'_, PyAny>) -> PyResult<String> {
    time_formatter_inner(milliseconds).map_err(error)
}

fn humanbytes_inner(size: Option<Bound<'_, PyAny>>) -> Result<String, String> {
    let size: Option<Num> = match &size {
        None => None,
        Some(v) => Some(crate::pyconv::FromPy::from_py(v)?),
    };
    let out = port::humanbytes(size)?;
    Ok(out)
}

/// `humanbytes`.
#[pyfunction]
#[pyo3(name = "humanbytes", signature = (size))]
fn humanbytes(size: Option<Bound<'_, PyAny>>) -> PyResult<String> {
    humanbytes_inner(size).map_err(error)
}

fn numerize_inner(number: Option<Bound<'_, PyAny>>) -> Result<Option<String>, String> {
    let number: Option<Num> = match &number {
        None => None,
        Some(v) => Some(crate::pyconv::FromPy::from_py(v)?),
    };
    let out = port::numerize(number)?;
    Ok(out)
}

/// `numerize`.
#[pyfunction]
#[pyo3(name = "numerize", signature = (number))]
fn numerize(number: Option<Bound<'_, PyAny>>) -> PyResult<Option<String>> {
    numerize_inner(number).map_err(error)
}

#[pymodule]
#[pyo3(name = "_native")]
fn native_module(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(time_formatter, m)?)?;
    m.add_function(wrap_pyfunction!(humanbytes, m)?)?;
    m.add_function(wrap_pyfunction!(numerize, m)?)?;
    Ok(())
}
