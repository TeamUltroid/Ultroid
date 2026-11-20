//! The parts of Python's object model the database code leans on: what `in`, `[]`, `int()`,
//! `len()`, `.get()`, `.update()`, `.pop()`, `.remove()`, `.append()` and `.split()` do to a
//! value, and which exception each raises on the wrong type.
//!
//! The accessors of `pyUltroid/dB` never check what they read from the database. A key holding a
//! value of another shape fails inside one of these operations, so they fail the same way here.

use crate::repr::{MAX_INT_DIGITS, repr};
use crate::tables::{DECIMAL_ZEROS, SPACES};
use crate::value::{PyDict, PyError, PyResult, PyValue};
use num_bigint::BigInt;
use num_traits::{FromPrimitive, ToPrimitive};
use std::borrow::Cow;

/// `AttributeError`: the value has no method of that name.
pub fn no_method(value: &PyValue, method: &str) -> PyError {
    let kind = value.type_name();
    PyError::new(
        "AttributeError",
        format!("'{kind}' object has no attribute '{method}'"),
    )
}

fn key_error(key: &PyValue) -> PyError {
    PyError::new("KeyError", repr(key).unwrap_or_default())
}

/// Looks a method up on a value. Python does this before it works out the arguments of the
/// call, so `x.append(int(y))` on a dict is an `AttributeError` whatever `y` is.
pub fn method(receiver: &PyValue, name: &str) -> PyResult<()> {
    let has = match receiver {
        PyValue::Dict(_) => matches!(name, "get" | "keys" | "update" | "pop"),
        PyValue::List(_) => matches!(name, "append" | "remove" | "pop"),
        PyValue::Set(_) => matches!(name, "update" | "remove" | "pop"),
        PyValue::Str(_) | PyValue::Surrogates(_) | PyValue::Bytes(_) => name == "split",
        _ => false,
    };
    has.then_some(()).ok_or_else(|| no_method(receiver, name))
}

/// The dict a dict method (`get`, `keys`) is called on.
pub fn as_dict<'a>(value: &'a PyValue, method: &str) -> PyResult<&'a PyDict> {
    match value {
        PyValue::Dict(dict) => Ok(dict),
        other => Err(no_method(other, method)),
    }
}

/// `str.isspace()` for one character: what `split()` and `strip()` treat as blank.
pub fn is_space(code: u32) -> bool {
    matches!(code, 0x09..=0x0d | 0x1c..=0x20) || SPACES.iter().any(|&(a, b)| a <= code && code <= b)
}

/// The value of a decimal digit of any script.
pub fn decimal(code: u32) -> Option<u32> {
    if (0x30..=0x39).contains(&code) {
        return Some(code - 0x30);
    }
    let after = DECIMAL_ZEROS.partition_point(|&zero| zero <= code);
    let zero = *DECIMAL_ZEROS.get(after.checked_sub(1)?)?;
    Some(code - zero).filter(|&value| value < 10)
}

/// The code points of a `str`; `None` for any other value.
pub fn code_points(value: &PyValue) -> Option<Cow<'_, [u32]>> {
    match value {
        PyValue::Str(text) => Some(Cow::Owned(text.chars().map(u32::from).collect())),
        PyValue::Surrogates(points) => Some(Cow::Borrowed(points)),
        _ => None,
    }
}

/// A `str` from code points. One that holds a lone surrogate is not text Rust can hold.
pub fn text(points: Vec<u32>) -> PyValue {
    match points.iter().map(|&code| char::from_u32(code)).collect() {
        Some(text) => PyValue::Str(text),
        None => PyValue::Surrogates(points),
    }
}

/// Python's int grammar for base 10: blanks around, one sign, digits with single underscores
/// between them.
fn parse_int(
    points: &[u32],
    blank: fn(u32) -> bool,
    digit: fn(u32) -> Option<u32>,
) -> PyResult<BigInt> {
    let invalid = || PyError::value_error("invalid literal for int() with base 10");
    let body = points
        .iter()
        .position(|&code| !blank(code))
        .zip(points.iter().rposition(|&code| !blank(code)))
        .and_then(|(first, last)| points.get(first..=last))
        .ok_or_else(invalid)?;
    let (negative, body) = match body.split_first() {
        Some((&code, rest)) if code == u32::from('-') => (true, rest),
        Some((&code, rest)) if code == u32::from('+') => (false, rest),
        _ => (false, body),
    };
    // A number neither starts nor ends with an underscore, and never has two in a row.
    let mut after_underscore = true;
    let mut digits = Vec::with_capacity(body.len());
    for &code in body {
        if code == u32::from('_') {
            if after_underscore {
                return Err(invalid());
            }
        } else {
            let value = digit(code).and_then(|value| u8::try_from(value).ok());
            digits.push(b'0' + value.ok_or_else(invalid)?);
        }
        after_underscore = code == u32::from('_');
    }
    if after_underscore {
        return Err(invalid());
    }
    if digits.len() > MAX_INT_DIGITS {
        return Err(PyError::value_error(format!(
            "Exceeds the limit ({MAX_INT_DIGITS} digits) for integer string conversion"
        )));
    }
    let value = BigInt::parse_bytes(&digits, 10).ok_or_else(invalid)?;
    Ok(if negative { -value } else { value })
}

/// `int(value)`.
pub fn int(value: &PyValue) -> PyResult<BigInt> {
    match value {
        PyValue::Bool(flag) => Ok(BigInt::from(u8::from(*flag))),
        PyValue::Int(whole) => Ok(whole.clone()),
        PyValue::Float(x) if x.is_nan() => {
            Err(PyError::value_error("cannot convert float NaN to integer"))
        }
        PyValue::Float(x) => BigInt::from_f64(x.trunc()).ok_or_else(|| {
            PyError::new("OverflowError", "cannot convert float infinity to integer")
        }),
        // `int()` goes by the C notion of a blank for ASCII, which leaves out U+001C to U+001F.
        PyValue::Str(_) | PyValue::Surrogates(_) => parse_int(
            &code_points(value).unwrap_or_default(),
            |code| code != 0x1c && code != 0x1d && code != 0x1e && code != 0x1f && is_space(code),
            decimal,
        ),
        PyValue::Bytes(bytes) => parse_int(
            &bytes
                .iter()
                .map(|&byte| u32::from(byte))
                .collect::<Vec<_>>(),
            |code| matches!(code, 0x09..=0x0d | 0x20),
            |code| decimal(code).filter(|_| code < 0x80),
        ),
        other => Err(PyError::type_error(format!(
            "int() argument must be a string, a bytes-like object or a real number, not '{}'",
            other.type_name()
        ))),
    }
}

/// `value.split()`: the pieces between runs of blanks.
pub fn split(value: &PyValue) -> PyResult<Vec<PyValue>> {
    match value {
        PyValue::Str(_) | PyValue::Surrogates(_) => Ok(code_points(value)
            .unwrap_or_default()
            .split(|&code| is_space(code))
            .filter(|piece| !piece.is_empty())
            .map(|piece| text(piece.to_vec()))
            .collect()),
        PyValue::Bytes(bytes) => Ok(bytes
            .split(|byte| matches!(byte, 0x09..=0x0d | 0x20))
            .filter(|piece| !piece.is_empty())
            .map(|piece| PyValue::Bytes(piece.to_vec()))
            .collect()),
        other => Err(no_method(other, "split")),
    }
}

fn holds<T: PartialEq>(hay: &[T], needle: &[T]) -> bool {
    needle.is_empty() || hay.windows(needle.len()).any(|window| window == needle)
}

/// `item in container`.
pub fn contains(container: &PyValue, item: &PyValue) -> PyResult<bool> {
    match container {
        PyValue::List(items) | PyValue::Tuple(items) => {
            Ok(items.iter().any(|member| member.py_eq(item)))
        }
        PyValue::Dict(dict) => dict.contains(item),
        // Python looks a set up in a set as a frozenset, and no stored set holds one.
        PyValue::Set(_) if matches!(item, PyValue::Set(_)) => Ok(false),
        PyValue::Set(set) => set.contains(item),
        PyValue::Str(_) | PyValue::Surrogates(_) => {
            let needle = code_points(item).ok_or_else(|| {
                PyError::type_error("'in <string>' requires string as left operand")
            })?;
            Ok(holds(&code_points(container).unwrap_or_default(), &needle))
        }
        PyValue::Bytes(bytes) => match item {
            PyValue::Bytes(needle) => Ok(holds(bytes, needle)),
            PyValue::Int(_) | PyValue::Bool(_) => {
                let byte = int(item)?.to_u8();
                let byte =
                    byte.ok_or_else(|| PyError::value_error("byte must be in range(0, 256)"))?;
                Ok(bytes.contains(&byte))
            }
            _ => Err(PyError::type_error("a bytes-like object is required")),
        },
        other => Err(PyError::type_error(format!(
            "argument of type '{}' is not iterable",
            other.type_name()
        ))),
    }
}

/// `len(container)`.
pub fn len(container: &PyValue) -> PyResult<usize> {
    Ok(match container {
        PyValue::Str(text) => text.chars().count(),
        PyValue::Surrogates(points) => points.len(),
        PyValue::Bytes(bytes) => bytes.len(),
        PyValue::List(items) | PyValue::Tuple(items) => items.len(),
        PyValue::Set(set) => set.len(),
        PyValue::Dict(dict) => dict.len(),
        other => {
            return Err(PyError::type_error(format!(
                "object of type '{}' has no len()",
                other.type_name()
            )));
        }
    })
}

/// Where a sequence index points: negative counts from the end, a bool is an int.
fn position(key: &PyValue, length: usize, kind: &str) -> PyResult<usize> {
    if !matches!(key, PyValue::Int(_) | PyValue::Bool(_)) {
        return Err(PyError::type_error(format!(
            "{kind} indices must be integers or slices, not {}",
            key.type_name()
        )));
    }
    let from_end = BigInt::from(length);
    let wanted = int(key)?;
    let wanted = if wanted < BigInt::from(0) {
        wanted + from_end
    } else {
        wanted
    };
    (wanted.to_usize().filter(|&at| at < length))
        .ok_or_else(|| PyError::new("IndexError", format!("{kind} index out of range")))
}

/// `container[key]`.
pub fn item<'a>(container: &'a PyValue, key: &PyValue) -> PyResult<Cow<'a, PyValue>> {
    let kind = container.type_name();
    let at = |length| position(key, length, kind);
    let found = match container {
        PyValue::Dict(dict) => {
            return dict
                .get(key)?
                .map(Cow::Borrowed)
                .ok_or_else(|| key_error(key));
        }
        PyValue::List(items) | PyValue::Tuple(items) => {
            items.get(at(items.len())?).map(Cow::Borrowed)
        }
        PyValue::Str(text) => {
            let found = text.chars().nth(at(text.chars().count())?);
            found.map(|c| Cow::Owned(PyValue::Str(c.into())))
        }
        PyValue::Surrogates(points) => {
            let found = points.get(at(points.len())?);
            found.map(|&code| Cow::Owned(self::text(vec![code])))
        }
        PyValue::Bytes(bytes) => {
            let found = bytes.get(at(bytes.len())?);
            found.map(|&byte| Cow::Owned(PyValue::int(byte)))
        }
        other => {
            return Err(PyError::type_error(format!(
                "'{}' object is not subscriptable",
                other.type_name()
            )));
        }
    };
    found.ok_or_else(|| PyError::new("IndexError", format!("{kind} index out of range")))
}

/// Does something to `container[key]` in place, as `container[key].append(x)` does. A dict, list
/// or tuple hands out the member it holds; a `str` or `bytes` hands out a new object each time.
pub fn with_item<T>(
    container: &mut PyValue,
    key: &PyValue,
    act: impl FnOnce(&mut PyValue) -> PyResult<T>,
) -> PyResult<T> {
    let kind = container.type_name();
    match container {
        PyValue::Dict(dict) => act(dict.get_mut(key)?.ok_or_else(|| key_error(key))?),
        PyValue::List(items) | PyValue::Tuple(items) => {
            let at = position(key, items.len(), kind)?;
            let out_of_range = || PyError::new("IndexError", format!("{kind} index out of range"));
            act(items.get_mut(at).ok_or_else(out_of_range)?)
        }
        other => act(&mut item(other, key)?.into_owned()),
    }
}

/// `receiver.update({key: value})`. A set has `update` too: it takes the dict's keys.
pub fn update(receiver: &mut PyValue, key: PyValue, value: PyValue) -> PyResult<()> {
    match receiver {
        PyValue::Dict(dict) => dict.set(key, value),
        PyValue::Set(set) => set.add(key),
        other => Err(no_method(other, "update")),
    }
}

/// `receiver.append(item)`.
pub fn append(receiver: &mut PyValue, item: PyValue) -> PyResult<()> {
    match receiver {
        PyValue::List(items) => {
            items.push(item);
            Ok(())
        }
        other => Err(no_method(other, "append")),
    }
}

/// `receiver.pop(key)`: a key of a dict, or an index into a list.
pub fn pop(receiver: &mut PyValue, key: &PyValue) -> PyResult<PyValue> {
    match receiver {
        // An empty dict has nothing to pop, and says so before it looks at the key at all.
        PyValue::Dict(dict) if dict.is_empty() => Err(key_error(key)),
        PyValue::Dict(dict) => dict.remove(key)?.ok_or_else(|| key_error(key)),
        PyValue::List(items) => {
            if !matches!(key, PyValue::Int(_) | PyValue::Bool(_)) {
                return Err(PyError::type_error(format!(
                    "'{}' object cannot be interpreted as an integer",
                    key.type_name()
                )));
            }
            let at = position(key, items.len(), "pop")?;
            Ok(items.remove(at))
        }
        PyValue::Set(_) => Err(PyError::type_error(
            "set.pop() takes no arguments (1 given)",
        )),
        other => Err(no_method(other, "pop")),
    }
}

/// `receiver.remove(item)`: the first equal member of a list, or a member of a set.
pub fn remove(receiver: &mut PyValue, item: &PyValue) -> PyResult<()> {
    match receiver {
        PyValue::List(items) => {
            let found = items.iter().position(|member| member.py_eq(item));
            let at = found.ok_or_else(|| PyError::value_error("list.remove(x): x not in list"))?;
            items.remove(at);
            Ok(())
        }
        PyValue::Set(set) => {
            let found = !matches!(item, PyValue::Set(_)) && set.remove(item)?;
            found.then_some(()).ok_or_else(|| key_error(item))
        }
        other => Err(no_method(other, "remove")),
    }
}

/// The code points of `str(value)`.
fn str_points(value: &PyValue) -> PyResult<Cow<'_, [u32]>> {
    match code_points(value) {
        Some(points) => Ok(points),
        None => Ok(Cow::Owned(repr(value)?.chars().map(u32::from).collect())),
    }
}

/// `"".join(f"{before}{member}{after}" for member in container)`: the listings the accessors
/// build. A dict gives its keys, a `str` its characters, `bytes` its numbers.
pub fn format_each(container: &PyValue, before: &str, after: &str) -> PyResult<PyValue> {
    let mut out: Vec<u32> = Vec::new();
    let mut line = |member: &PyValue| -> PyResult<()> {
        out.extend(before.chars().map(u32::from));
        out.extend(str_points(member)?.iter());
        out.extend(after.chars().map(u32::from));
        Ok(())
    };
    match container {
        PyValue::List(items) | PyValue::Tuple(items) => items.iter().try_for_each(&mut line)?,
        PyValue::Dict(dict) => dict.keys().try_for_each(&mut line)?,
        PyValue::Set(set) => set.iter().try_for_each(&mut line)?,
        PyValue::Str(_) | PyValue::Surrogates(_) | PyValue::Bytes(_) => {
            for at in 0..len(container)? {
                line(item(container, &PyValue::int(at))?.as_ref())?;
            }
        }
        other => {
            return Err(PyError::type_error(format!(
                "'{}' object is not iterable",
                other.type_name()
            )));
        }
    }
    Ok(text(out))
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::value::PySet;

    fn kind<T: std::fmt::Debug>(result: PyResult<T>) -> &'static str {
        result.map_or_else(
            |error| error.kind,
            |value| panic!("no error, got {value:?}"),
        )
    }

    fn ints(items: &[i64]) -> PyValue {
        PyValue::List(items.iter().map(|&i| PyValue::int(i)).collect())
    }

    #[test]
    fn int_follows_python() {
        let of = |text: &str| int(&PyValue::str(text)).map(|whole| whole.to_string());
        // Expected values are CPython's `int(text)`.
        assert_eq!(of(" -1001234567890\n").unwrap(), "-1001234567890");
        assert_eq!(of("+007").unwrap(), "7");
        assert_eq!(of("1_000").unwrap(), "1000");
        assert_eq!(of("\u{a0}\u{663}\u{1d7d7}\u{3000}").unwrap(), "39");
        for bad in [
            "", " ", "1__0", "_1", "1_", "+-1", "+ 1", "1 2", "0x10", "1.0", "1\u{1f}",
        ] {
            assert_eq!(kind(of(bad)), "ValueError", "{bad:?}");
        }
        assert_eq!(kind(of(&"9".repeat(MAX_INT_DIGITS + 1))), "ValueError");
        assert_eq!(int(&PyValue::Float(-2.9)).unwrap(), BigInt::from(-2));
        assert_eq!(int(&PyValue::Bool(true)).unwrap(), BigInt::from(1));
        assert_eq!(
            int(&PyValue::Bytes(b" 12\t".to_vec())).unwrap(),
            BigInt::from(12)
        );
        assert_eq!(
            kind(int(&PyValue::Bytes(b"\xd9\xa3".to_vec()))),
            "ValueError"
        );
        assert_eq!(kind(int(&PyValue::Float(f64::NAN))), "ValueError");
        assert_eq!(kind(int(&PyValue::Float(f64::INFINITY))), "OverflowError");
        assert_eq!(kind(int(&PyValue::None)), "TypeError");
        assert_eq!(kind(int(&ints(&[1]))), "TypeError");
    }

    #[test]
    fn split_follows_python() {
        let pieces = split(&PyValue::str(" a\u{1f}b\u{3000}c\td ")).unwrap();
        assert_eq!(pieces, ["a", "b", "c", "d"].map(PyValue::str));
        assert_eq!(split(&PyValue::str(" \n")).unwrap(), []);
        let bytes = split(&PyValue::Bytes(b"a\x1fb c".to_vec())).unwrap();
        assert_eq!(
            bytes,
            [b"a\x1fb".to_vec(), b"c".to_vec()].map(PyValue::Bytes)
        );
        assert_eq!(kind(split(&PyValue::int(5))), "AttributeError");
    }

    #[test]
    fn membership() {
        assert!(contains(&ints(&[1, 2]), &PyValue::Float(2.0)).unwrap());
        assert!(!contains(&ints(&[1, 2]), &PyValue::str("2")).unwrap());
        assert!(contains(&PyValue::str("héllo"), &PyValue::str("él")).unwrap());
        assert!(contains(&PyValue::str("abc"), &PyValue::str("")).unwrap());
        assert_eq!(
            kind(contains(&PyValue::str("abc"), &PyValue::int(1))),
            "TypeError"
        );
        assert!(contains(&PyValue::Bytes(b"abc".to_vec()), &PyValue::int(98)).unwrap());
        assert_eq!(
            kind(contains(&PyValue::Bytes(vec![]), &PyValue::int(256))),
            "ValueError"
        );
        assert_eq!(
            kind(contains(&PyValue::int(5), &PyValue::int(5))),
            "TypeError"
        );
        let mut set = PySet::new();
        set.add(PyValue::int(1)).unwrap();
        let set = PyValue::Set(set);
        assert!(contains(&set, &PyValue::Bool(true)).unwrap());
        assert!(!contains(&set, &set.clone()).unwrap());
        assert_eq!(kind(contains(&set, &ints(&[1]))), "TypeError");
    }

    #[test]
    fn subscripts() {
        let list = ints(&[10, 20, 30]);
        assert_eq!(*item(&list, &PyValue::int(-1)).unwrap(), PyValue::int(30));
        assert_eq!(
            *item(&list, &PyValue::Bool(true)).unwrap(),
            PyValue::int(20)
        );
        assert_eq!(kind(item(&list, &PyValue::int(3))), "IndexError");
        assert_eq!(kind(item(&list, &PyValue::int(-4))), "IndexError");
        assert_eq!(kind(item(&list, &PyValue::Float(0.0))), "TypeError");
        assert_eq!(
            *item(&PyValue::str("héllo"), &PyValue::int(1)).unwrap(),
            PyValue::str("é")
        );
        assert_eq!(
            *item(&PyValue::Bytes(b"a".to_vec()), &PyValue::int(0)).unwrap(),
            PyValue::int(97)
        );
        assert_eq!(kind(item(&PyValue::None, &PyValue::int(0))), "TypeError");
        let mut dict = PyDict::new();
        dict.set(PyValue::int(1), PyValue::str("x")).unwrap();
        let dict = PyValue::Dict(dict);
        assert_eq!(
            *item(&dict, &PyValue::Float(1.0)).unwrap(),
            PyValue::str("x")
        );
        assert_eq!(kind(item(&dict, &PyValue::int(2))), "KeyError");
        assert_eq!(kind(item(&dict, &list)), "TypeError");
    }

    #[test]
    fn methods_on_the_wrong_type() {
        let mut number = PyValue::int(5);
        assert_eq!(
            kind(update(&mut number, PyValue::None, PyValue::None)),
            "AttributeError"
        );
        assert_eq!(kind(append(&mut number, PyValue::None)), "AttributeError");
        assert_eq!(kind(pop(&mut number, &PyValue::None)), "AttributeError");
        assert_eq!(kind(remove(&mut number, &PyValue::None)), "AttributeError");
        assert_eq!(kind(as_dict(&number, "get")), "AttributeError");
        let mut list = ints(&[1, 2, 1]);
        remove(&mut list, &PyValue::Bool(true)).unwrap();
        assert_eq!(list, ints(&[2, 1]));
        assert_eq!(kind(remove(&mut list, &PyValue::int(7))), "ValueError");
        assert_eq!(pop(&mut list, &PyValue::int(-1)).unwrap(), PyValue::int(1));
        assert_eq!(kind(pop(&mut list, &PyValue::str("a"))), "TypeError");
        assert_eq!(kind(pop(&mut list, &PyValue::int(5))), "IndexError");
        // An empty dict refuses before it hashes the key; one with members hashes first.
        let mut dict = PyValue::Dict(PyDict::new());
        assert_eq!(kind(pop(&mut dict, &ints(&[1]))), "KeyError");
        update(&mut dict, PyValue::int(1), PyValue::None).unwrap();
        assert_eq!(kind(pop(&mut dict, &ints(&[1]))), "TypeError");
        let mut set = PyValue::Set(PySet::new());
        update(&mut set, PyValue::int(1), PyValue::None).unwrap();
        assert_eq!(kind(pop(&mut set, &PyValue::int(1))), "TypeError");
        assert_eq!(kind(remove(&mut set, &PyValue::int(2))), "KeyError");
        remove(&mut set, &PyValue::int(1)).unwrap();
        assert_eq!(len(&set).unwrap(), 0);
    }

    #[test]
    fn listings() {
        let words = PyValue::List(vec![PyValue::str("a"), PyValue::int(5), PyValue::None]);
        let listed = format_each(&words, "> `", "`\n").unwrap();
        assert_eq!(listed, PyValue::str("> `a`\n> `5`\n> `None`\n"));
        assert_eq!(
            format_each(&PyValue::str("ab"), "", ",").unwrap(),
            PyValue::str("a,b,")
        );
        assert_eq!(kind(format_each(&PyValue::int(5), "", "")), "TypeError");
        let lone = PyValue::List(vec![PyValue::Surrogates(vec![0xd83d])]);
        assert_eq!(
            format_each(&lone, "<", ">").unwrap(),
            PyValue::Surrogates(vec![0x3c, 0xd83d, 0x3e])
        );
    }
}
