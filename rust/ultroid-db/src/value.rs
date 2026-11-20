//! Python values as Ultroid's database holds them, with the parts of Python's data model the
//! database code relies on: which keys are the same key, what is true, what a type is called.

use indexmap::IndexMap;
use num_bigint::BigInt;
use num_traits::{FromPrimitive, Zero};
use std::fmt;
use std::sync::atomic::{AtomicU64, Ordering};

/// A Python exception: its type name and message. Ports return the type the original raises.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct PyError {
    pub kind: &'static str,
    pub message: String,
}

impl PyError {
    pub fn new(kind: &'static str, message: impl Into<String>) -> Self {
        Self {
            kind,
            message: message.into(),
        }
    }

    pub fn type_error(message: impl Into<String>) -> Self {
        Self::new("TypeError", message)
    }

    pub fn value_error(message: impl Into<String>) -> Self {
        Self::new("ValueError", message)
    }
}

impl fmt::Display for PyError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}: {}", self.kind, self.message)
    }
}

impl std::error::Error for PyError {}

pub type PyResult<T> = Result<T, PyError>;

/// A Python value: everything `ast.literal_eval` can produce, which is everything stored text can
/// turn into.
#[derive(Clone, Debug, PartialEq)]
pub enum PyValue {
    None,
    Ellipsis,
    Bool(bool),
    Int(BigInt),
    Float(f64),
    /// Real and imaginary part.
    Complex(f64, f64),
    Str(String),
    /// A `str` that holds lone surrogates, as code points. Python can hold one; it is not text
    /// and cannot be encoded.
    Surrogates(Vec<u32>),
    Bytes(Vec<u8>),
    List(Vec<PyValue>),
    Tuple(Vec<PyValue>),
    Set(PySet),
    Dict(PyDict),
}

/// What makes two values the same dict key or set member in Python: `1`, `1.0` and `True` are
/// one key, `0.0` and `-0.0` are one key, and a NaN is only ever equal to itself.
#[derive(Clone, Debug, PartialEq, Eq, Hash)]
pub enum Key {
    None,
    Ellipsis,
    Int(BigInt),
    /// The bits of a float that is not a whole number.
    Float(u64),
    Complex(u64, u64),
    Str(String),
    Surrogates(Vec<u32>),
    Bytes(Vec<u8>),
    Tuple(Vec<Key>),
    /// Python finds a NaN key by identity. Values here have no identity, so each NaN is its own
    /// key.
    Nan(u64),
}

static NEXT_NAN: AtomicU64 = AtomicU64::new(0);

fn float_key(x: f64) -> Key {
    if x.is_nan() {
        return Key::Nan(NEXT_NAN.fetch_add(1, Ordering::Relaxed));
    }
    match BigInt::from_f64(x) {
        Some(whole) if x.fract() == 0.0 => Key::Int(whole),
        _ => Key::Float(x.to_bits()),
    }
}

/// A dict: insertion ordered, keyed the way Python keys it. Setting an existing key keeps the
/// key object that was there first.
#[derive(Clone, Debug, Default, PartialEq)]
pub struct PyDict {
    entries: IndexMap<Key, (PyValue, PyValue)>,
}

impl PyDict {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn len(&self) -> usize {
        self.entries.len()
    }

    pub fn is_empty(&self) -> bool {
        self.entries.is_empty()
    }

    pub fn get(&self, key: &PyValue) -> PyResult<Option<&PyValue>> {
        Ok(self.entries.get(&key.key()?).map(|(_, value)| value))
    }

    pub fn get_mut(&mut self, key: &PyValue) -> PyResult<Option<&mut PyValue>> {
        Ok(self.entries.get_mut(&key.key()?).map(|(_, value)| value))
    }

    pub fn contains(&self, key: &PyValue) -> PyResult<bool> {
        Ok(self.entries.contains_key(&key.key()?))
    }

    /// `d[key] = value`.
    pub fn set(&mut self, key: PyValue, value: PyValue) -> PyResult<()> {
        match self.entries.entry(key.key()?) {
            indexmap::map::Entry::Occupied(mut slot) => slot.get_mut().1 = value,
            indexmap::map::Entry::Vacant(slot) => {
                slot.insert((key, value));
            }
        }
        Ok(())
    }

    /// `d.pop(key, None)`: the value, if the key was there.
    pub fn remove(&mut self, key: &PyValue) -> PyResult<Option<PyValue>> {
        Ok(self
            .entries
            .shift_remove(&key.key()?)
            .map(|(_, value)| value))
    }

    pub fn iter(&self) -> impl Iterator<Item = (&PyValue, &PyValue)> {
        self.entries.values().map(|(key, value)| (key, value))
    }

    pub fn keys(&self) -> impl Iterator<Item = &PyValue> {
        self.entries.values().map(|(key, _)| key)
    }
}

/// A set: members are unique the way dict keys are. Kept in insertion order, which is not the
/// order CPython iterates in (that follows its hash table).
#[derive(Clone, Debug, Default, PartialEq)]
pub struct PySet {
    members: IndexMap<Key, PyValue>,
}

impl PySet {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn len(&self) -> usize {
        self.members.len()
    }

    pub fn is_empty(&self) -> bool {
        self.members.is_empty()
    }

    pub fn contains(&self, member: &PyValue) -> PyResult<bool> {
        Ok(self.members.contains_key(&member.key()?))
    }

    /// `s.add(member)`: the member that was there first stays.
    pub fn add(&mut self, member: PyValue) -> PyResult<()> {
        self.members.entry(member.key()?).or_insert(member);
        Ok(())
    }

    pub fn iter(&self) -> impl Iterator<Item = &PyValue> {
        self.members.values()
    }
}

impl PyValue {
    pub fn int(value: impl Into<BigInt>) -> Self {
        Self::Int(value.into())
    }

    pub fn str(value: impl Into<String>) -> Self {
        Self::Str(value.into())
    }

    /// `type(value).__name__`.
    pub fn type_name(&self) -> &'static str {
        match self {
            Self::None => "NoneType",
            Self::Ellipsis => "ellipsis",
            Self::Bool(_) => "bool",
            Self::Int(_) => "int",
            Self::Float(_) => "float",
            Self::Complex(..) => "complex",
            Self::Str(_) | Self::Surrogates(_) => "str",
            Self::Bytes(_) => "bytes",
            Self::List(_) => "list",
            Self::Tuple(_) => "tuple",
            Self::Set(_) => "set",
            Self::Dict(_) => "dict",
        }
    }

    /// `bool(value)`.
    pub fn truthy(&self) -> bool {
        match self {
            Self::None => false,
            Self::Ellipsis => true,
            Self::Bool(flag) => *flag,
            Self::Int(whole) => !whole.is_zero(),
            Self::Float(x) => *x != 0.0,
            Self::Complex(re, im) => *re != 0.0 || *im != 0.0,
            Self::Str(text) => !text.is_empty(),
            Self::Surrogates(points) => !points.is_empty(),
            Self::Bytes(bytes) => !bytes.is_empty(),
            Self::List(items) | Self::Tuple(items) => !items.is_empty(),
            Self::Set(set) => !set.is_empty(),
            Self::Dict(dict) => !dict.is_empty(),
        }
    }

    /// The value as a dict key or set member; `TypeError` for a list, dict or set, as in Python.
    pub fn key(&self) -> PyResult<Key> {
        Ok(match self {
            Self::None => Key::None,
            Self::Ellipsis => Key::Ellipsis,
            Self::Bool(flag) => Key::Int(BigInt::from(u8::from(*flag))),
            Self::Int(whole) => Key::Int(whole.clone()),
            Self::Float(x) => float_key(*x),
            // A complex with no imaginary part is the same key as its real part.
            Self::Complex(re, im) if *im == 0.0 => float_key(*re),
            Self::Complex(re, im) if re.is_nan() || im.is_nan() => float_key(f64::NAN),
            Self::Complex(re, im) => Key::Complex((re + 0.0).to_bits(), (im + 0.0).to_bits()),
            Self::Str(text) => Key::Str(text.clone()),
            Self::Surrogates(points) => Key::Surrogates(points.clone()),
            Self::Bytes(bytes) => Key::Bytes(bytes.clone()),
            Self::Tuple(items) => Key::Tuple(items.iter().map(Self::key).collect::<PyResult<_>>()?),
            Self::List(_) | Self::Set(_) | Self::Dict(_) => {
                return Err(PyError::type_error(format!(
                    "unhashable type: '{}'",
                    self.type_name()
                )));
            }
        })
    }

    /// Python's `==`. Numbers compare by value across `bool`, `int`, `float` and `complex`;
    /// containers compare member by member; dicts and sets ignore order.
    pub fn py_eq(&self, other: &Self) -> bool {
        match (self, other) {
            (Self::List(a), Self::List(b)) | (Self::Tuple(a), Self::Tuple(b)) => {
                a.len() == b.len() && a.iter().zip(b).all(|(x, y)| x.py_eq(y))
            }
            (Self::Dict(a), Self::Dict(b)) => {
                a.len() == b.len()
                    && a.iter().all(
                        |(key, value)| matches!(b.get(key), Ok(Some(found)) if found.py_eq(value)),
                    )
            }
            (Self::Set(a), Self::Set(b)) => {
                a.len() == b.len() && a.iter().all(|member| b.contains(member) == Ok(true))
            }
            _ => matches!((self.key(), other.key()), (Ok(a), Ok(b)) if a == b),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn one_key_for_equal_numbers() {
        let mut dict = PyDict::new();
        dict.set(PyValue::int(1), PyValue::str("a")).unwrap();
        dict.set(PyValue::Float(1.0), PyValue::str("b")).unwrap();
        dict.set(PyValue::Bool(true), PyValue::str("c")).unwrap();
        dict.set(PyValue::Complex(1.0, 0.0), PyValue::str("d"))
            .unwrap();
        // One entry, the first key object, the last value.
        assert_eq!(dict.len(), 1);
        assert_eq!(
            dict.iter().next(),
            Some((&PyValue::int(1), &PyValue::str("d")))
        );
        assert_eq!(PyValue::Float(-0.0).key(), PyValue::int(0).key());
        assert_ne!(PyValue::str("1").key(), PyValue::int(1).key());
        assert_ne!(PyValue::str("a").key(), PyValue::Bytes(b"a".to_vec()).key());
        assert_ne!(
            PyValue::Float(f64::NAN).key(),
            PyValue::Float(f64::NAN).key()
        );
    }

    #[test]
    fn unhashable_values_are_refused() {
        assert_eq!(PyValue::List(vec![]).key().unwrap_err().kind, "TypeError");
        assert_eq!(
            PyValue::Dict(PyDict::new()).key().unwrap_err().kind,
            "TypeError"
        );
        let nested = PyValue::Tuple(vec![PyValue::int(1), PyValue::List(vec![])]);
        assert_eq!(nested.key().unwrap_err().kind, "TypeError");
    }

    #[test]
    fn equality_follows_python() {
        let list = |items: &[i32]| PyValue::List(items.iter().map(|&i| PyValue::int(i)).collect());
        let mixed = PyValue::List(vec![PyValue::Float(1.0), PyValue::Bool(false)]);
        assert!(!list(&[1, 2]).py_eq(&mixed));
        assert!(list(&[1, 0]).py_eq(&mixed));
        assert!(!list(&[1]).py_eq(&PyValue::Tuple(vec![PyValue::int(1)])));
        assert!(!PyValue::Float(f64::NAN).py_eq(&PyValue::Float(f64::NAN)));
        assert!(!PyValue::None.py_eq(&PyValue::Bool(false)));
    }

    #[test]
    fn truth() {
        assert!(!PyValue::Float(-0.0).truthy());
        assert!(PyValue::Float(f64::NAN).truthy());
        assert!(!PyValue::str("").truthy());
        assert!(PyValue::Ellipsis.truthy());
        assert!(!PyValue::Tuple(vec![]).truthy());
    }
}
