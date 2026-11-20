//! Python bindings for `pyUltroid/fns/tools.py`: generated from the signatures in `port.rs` by rust-anything.
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

fn get_msg_button_inner(texts: String) -> Result<serde_json::Value, String> {
    let out = port::get_msg_button(texts)?;
    Ok(out)
}

/// `get_msg_button`.
#[pyfunction]
#[pyo3(name = "get_msg_button", signature = (texts))]
fn get_msg_button(py: Python<'_>, texts: String) -> PyResult<Py<PyAny>> {
    get_msg_button_inner(texts)
        .map_err(error)
        .and_then(|v| crate::pyconv::ToPy::to_py(&v, py))
}

fn text_set_inner(text: Bound<'_, PyAny>) -> Result<serde_json::Value, String> {
    let text: serde_json::Value = crate::pyconv::FromPy::from_py(&text)?;
    let out = port::text_set(text)?;
    Ok(out)
}

/// `text_set`.
#[pyfunction]
#[pyo3(name = "text_set", signature = (text))]
fn text_set(py: Python<'_>, text: Bound<'_, PyAny>) -> PyResult<Py<PyAny>> {
    text_set_inner(text)
        .map_err(error)
        .and_then(|v| crate::pyconv::ToPy::to_py(&v, py))
}

fn stdr_inner(seconds: Bound<'_, PyAny>) -> Result<String, String> {
    let seconds: Num = crate::pyconv::FromPy::from_py(&seconds)?;
    let out = port::stdr(seconds)?;
    Ok(out)
}

/// `stdr`.
#[pyfunction]
#[pyo3(name = "stdr", signature = (seconds))]
fn stdr(seconds: Bound<'_, PyAny>) -> PyResult<String> {
    stdr_inner(seconds).map_err(error)
}

fn cmd_regex_replace_inner(cmd: String) -> Result<String, String> {
    let out = port::cmd_regex_replace(cmd)?;
    Ok(out)
}

/// `cmd_regex_replace`.
#[pyfunction]
#[pyo3(name = "cmd_regex_replace", signature = (cmd))]
fn cmd_regex_replace(cmd: String) -> PyResult<String> {
    cmd_regex_replace_inner(cmd).map_err(error)
}

fn get_chat_and_msgid_inner(
    link: String,
) -> Result<(serde_json::Value, serde_json::Value), String> {
    let out = port::get_chat_and_msgid(link)?;
    Ok(out)
}

/// `get_chat_and_msgid`.
#[pyfunction]
#[pyo3(name = "get_chat_and_msgid", signature = (link))]
fn get_chat_and_msgid(py: Python<'_>, link: String) -> PyResult<Py<PyAny>> {
    get_chat_and_msgid_inner(link)
        .map_err(error)
        .and_then(|v| crate::pyconv::ToPy::to_py(&v, py))
}

#[pymodule]
#[pyo3(name = "_native")]
fn native_module(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(get_msg_button, m)?)?;
    m.add_function(wrap_pyfunction!(text_set, m)?)?;
    m.add_function(wrap_pyfunction!(stdr, m)?)?;
    m.add_function(wrap_pyfunction!(cmd_regex_replace, m)?)?;
    m.add_function(wrap_pyfunction!(get_chat_and_msgid, m)?)?;
    Ok(())
}
