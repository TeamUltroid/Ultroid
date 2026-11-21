//! Python values in the JSON that rust-anything's Python bridge carries them in.
//!
//! JSON has no tuples, sets, bytes, big ints, special floats or non-text keys, so the bridge
//! marks those with one-key objects such as `{"$tuple": [...]}`. This is only used to prove the
//! port against the Python original; a Rust Ultroid never needs it.

use crate::value::{PyDict, PyError, PyResult, PySet, PyValue};
use num_bigint::BigInt;
use serde_json::{Map, Number, Value, json};

fn malformed(what: &str) -> PyError {
    PyError::type_error(format!("malformed bridge value: {what}"))
}

fn list(items: &[Value]) -> PyResult<Vec<PyValue>> {
    items.iter().map(from_bridge).collect()
}

fn marked(name: &str, inner: &Value) -> PyResult<Option<PyValue>> {
    let items = || inner.as_array().ok_or_else(|| malformed(name));
    let text = || inner.as_str().ok_or_else(|| malformed(name));
    Ok(Some(match name {
        "$tuple" => PyValue::Tuple(list(items()?)?),
        "$set" => {
            let mut set = PySet::new();
            for member in list(items()?)? {
                set.add(member)?;
            }
            PyValue::Set(set)
        }
        "$bytes" => PyValue::Bytes(
            items()?
                .iter()
                .map(|byte| byte.as_u64().and_then(|b| u8::try_from(b).ok()))
                .collect::<Option<_>>()
                .ok_or_else(|| malformed(name))?,
        ),
        "$int" => PyValue::Int(text()?.parse::<BigInt>().map_err(|_| malformed(name))?),
        "$float" => PyValue::Float(text()?.parse().map_err(|_| malformed(name))?),
        "$num" => PyValue::Float(match text()? {
            "NaN" => f64::NAN,
            "Infinity" => f64::INFINITY,
            "-Infinity" => f64::NEG_INFINITY,
            "-0" => -0.0,
            _ => return Err(malformed(name)),
        }),
        "$dict" => {
            let mut dict = PyDict::new();
            for pair in items()? {
                let [key, value] = pair.as_array().map(Vec::as_slice).unwrap_or_default() else {
                    return Err(malformed(name));
                };
                dict.set(from_bridge(key)?, from_bridge(value)?)?;
            }
            PyValue::Dict(dict)
        }
        _ => return Ok(None),
    }))
}

/// The Python value a bridge value stands for.
pub fn from_bridge(value: &Value) -> PyResult<PyValue> {
    Ok(match value {
        Value::Null => PyValue::None,
        Value::Bool(flag) => PyValue::Bool(*flag),
        Value::Number(number) => match (number.as_i64(), number.as_u64(), number.as_f64()) {
            _ if number.is_f64() => PyValue::Float(number.as_f64().unwrap_or(f64::NAN)),
            (Some(whole), _, _) => PyValue::int(whole),
            (_, Some(whole), _) => PyValue::int(whole),
            (_, _, other) => PyValue::Float(other.unwrap_or(f64::NAN)),
        },
        Value::String(text) => PyValue::Str(text.clone()),
        Value::Array(items) => PyValue::List(list(items)?),
        Value::Object(entries) => {
            if let (1, Some((name, inner))) = (entries.len(), entries.iter().next())
                && let Some(value) = marked(name, inner)?
            {
                return Ok(value);
            }
            let mut dict = PyDict::new();
            for (key, item) in entries {
                dict.set(PyValue::Str(key.clone()), from_bridge(item)?)?;
            }
            PyValue::Dict(dict)
        }
    })
}

fn float(x: f64) -> Value {
    let special = if x.is_nan() {
        "NaN"
    } else if x == f64::INFINITY {
        "Infinity"
    } else if x == f64::NEG_INFINITY {
        "-Infinity"
    } else if x == 0.0 && x.is_sign_negative() {
        "-0"
    } else {
        return Number::from_f64(x).map_or(Value::Null, Value::Number);
    };
    json!({ "$num": special })
}

/// A Python value as the bridge carries it back. `complex` and `Ellipsis` cannot cross: they come
/// out as `{"$repr": type name}`, which is also what the recorder writes for them.
pub fn to_bridge(value: &PyValue) -> Value {
    let list = |items: &mut dyn Iterator<Item = &PyValue>| -> Vec<Value> {
        items.map(to_bridge).collect()
    };
    match value {
        PyValue::None => Value::Null,
        PyValue::Bool(flag) => json!(flag),
        PyValue::Int(whole) => match i64::try_from(whole) {
            Ok(small) => json!(small),
            Err(_) => json!({ "$int": whole.to_string() }),
        },
        PyValue::Float(x) => float(*x),
        PyValue::Str(text) => json!(text),
        PyValue::Bytes(bytes) => json!({ "$bytes": bytes }),
        PyValue::List(items) => Value::Array(list(&mut items.iter())),
        PyValue::Tuple(items) => json!({ "$tuple": list(&mut items.iter()) }),
        PyValue::Set(set) => json!({ "$set": list(&mut set.iter()) }),
        PyValue::Dict(dict) => {
            // A dict of plain text keys is a JSON object, unless it could be read as a marker.
            let plain = dict
                .keys()
                .all(|key| matches!(key, PyValue::Str(text) if !text.starts_with('$')));
            if plain {
                let mut entries = Map::new();
                for (key, item) in dict.iter() {
                    if let PyValue::Str(text) = key {
                        entries.insert(text.clone(), to_bridge(item));
                    }
                }
                return Value::Object(entries);
            }
            let pairs: Vec<Value> = dict
                .iter()
                .map(|(key, item)| json!([to_bridge(key), to_bridge(item)]))
                .collect();
            json!({ "$dict": pairs })
        }
        PyValue::Complex(..) | PyValue::Ellipsis | PyValue::Surrogates(_) => {
            json!({ "$repr": value.type_name() })
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::repr::repr;

    #[test]
    fn markers_become_python_values() {
        let text = |value: Value| repr(&from_bridge(&value).unwrap()).unwrap();
        assert_eq!(
            text(json!([1, 1.0, "a", null, true])),
            "[1, 1.0, 'a', None, True]"
        );
        assert_eq!(text(json!({"$tuple": [1, {"$tuple": []}]})), "(1, ())");
        assert_eq!(text(json!({"$bytes": [104, 105]})), "b'hi'");
        assert_eq!(
            text(json!({"$int": "18446744073709551616"})),
            "18446744073709551616"
        );
        assert_eq!(text(json!({"$num": "-0"})), "-0.0");
        assert_eq!(
            text(json!({"$dict": [[-100, ["x"]], [{"$tuple": [1, 2]}, null]]})),
            "{-100: ['x'], (1, 2): None}"
        );
        assert_eq!(text(json!({"b": 1, "a": 2})), "{'b': 1, 'a': 2}");
        assert_eq!(text(json!({"$set": [5]})), "{5}");
    }

    #[test]
    fn values_go_back_the_same_way() {
        for value in [
            json!([1, 1.5, "a", null, true]),
            json!({"$tuple": [1, 2]}),
            json!({"$bytes": [0, 255]}),
            json!({"$int": "18446744073709551616"}),
            json!({"$num": "NaN"}),
            json!({"$dict": [[-100, ["x"]]]}),
            json!({"b": 1, "a": {"c": []}}),
        ] {
            assert_eq!(to_bridge(&from_bridge(&value).unwrap()), value);
        }
        // A whole float stays a float.
        assert_eq!(to_bridge(&PyValue::Float(2.0)).to_string(), "2.0");
    }
}
