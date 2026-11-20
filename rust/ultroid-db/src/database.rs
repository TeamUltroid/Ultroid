//! The key-value database every part of Ultroid reads and writes (`udB`): the cache and the
//! value handling of `_BaseDatabase` in `pyUltroid/startup/_database.py`, over any store of text.

use crate::value::{PyResult, PyValue};
use crate::{normalize, read_stored, to_str};
use indexmap::IndexMap;
use std::collections::HashMap;
use std::collections::hash_map::Entry;

/// Where the text lives: Redis, MongoDB, PostgreSQL or a file in the original. A backend that
/// fails reports the exception its Python driver would raise.
pub trait Store {
    fn get(&mut self, key: &str) -> PyResult<Option<String>>;
    fn set(&mut self, key: &str, value: &str) -> PyResult<()>;
    fn delete(&mut self, key: &str) -> PyResult<()>;
    fn keys(&mut self) -> PyResult<Vec<String>>;
}

/// A store in memory, listing keys in the order they were first written.
#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct MemoryStore {
    entries: IndexMap<String, String>,
}

impl MemoryStore {
    pub fn new() -> Self {
        Self::default()
    }

    /// Every key with its stored text.
    pub fn entries(&self) -> impl Iterator<Item = (&str, &str)> {
        self.entries
            .iter()
            .map(|(key, text)| (key.as_str(), text.as_str()))
    }
}

impl Store for MemoryStore {
    fn get(&mut self, key: &str) -> PyResult<Option<String>> {
        Ok(self.entries.get(key).cloned())
    }

    fn set(&mut self, key: &str, value: &str) -> PyResult<()> {
        self.entries.insert(key.to_string(), value.to_string());
        Ok(())
    }

    fn delete(&mut self, key: &str) -> PyResult<()> {
        self.entries.shift_remove(key);
        Ok(())
    }

    fn keys(&mut self) -> PyResult<Vec<String>> {
        Ok(self.entries.keys().cloned().collect())
    }
}

/// `udB`: a store of text behind a cache of the values that text reads as.
#[derive(Clone, Debug, Default)]
pub struct Database<S> {
    store: S,
    cache: HashMap<String, PyValue>,
}

/// What the cache holds for a key, reading the store the first time. A key that is missing is
/// remembered as `None`, and the empty key is never looked up.
fn cached<'a, S: Store>(
    cache: &'a mut HashMap<String, PyValue>,
    store: &mut S,
    key: &str,
) -> PyResult<&'a mut PyValue> {
    match cache.entry(key.to_string()) {
        Entry::Occupied(slot) => Ok(slot.into_mut()),
        Entry::Vacant(slot) => {
            let stored = if key.is_empty() {
                None
            } else {
                store.get(key)?
            };
            Ok(slot.insert(stored.map_or(PyValue::None, |text| read_stored(&text))))
        }
    }
}

impl<S: Store> Database<S> {
    pub fn new(store: S) -> Self {
        Self {
            store,
            cache: HashMap::new(),
        }
    }

    pub fn store(&self) -> &S {
        &self.store
    }

    pub fn store_mut(&mut self) -> &mut S {
        &mut self.store
    }

    /// `get_key(key)`: the cached value, or what the stored text reads as.
    pub fn get_key(&mut self, key: &str) -> PyResult<&PyValue> {
        cached(&mut self.cache, &mut self.store, key).map(|value| &*value)
    }

    /// `get_key(key) or empty`, by reference.
    pub fn read<'a>(&'a mut self, key: &str, empty: &'a PyValue) -> PyResult<&'a PyValue> {
        let value = self.get_key(key)?;
        Ok(if value.truthy() { value } else { empty })
    }

    /// `get_key(key) or empty`, as a value of its own.
    pub fn get_or(&mut self, key: &str, empty: PyValue) -> PyResult<PyValue> {
        let value = self.get_key(key)?;
        Ok(if value.truthy() { value.clone() } else { empty })
    }

    /// `value = get_key(key) or empty`, kept for changing and saving. See [`Held`].
    pub fn hold<'a>(&'a mut self, key: &'a str, empty: PyValue) -> PyResult<Held<'a, S>> {
        let cached = cached(&mut self.cache, &mut self.store, key)?;
        let fresh = (!cached.truthy()).then_some(empty);
        Ok(Held {
            store: &mut self.store,
            key,
            cached,
            fresh,
        })
    }

    /// `set_key(key, value)`. Text that reads as a literal is kept as that literal. The cache
    /// has the value before the store is asked, so it keeps it when the store fails.
    pub fn set_key(&mut self, key: &str, value: PyValue) -> PyResult<()> {
        let value = normalize(value);
        let kept = match self.cache.entry(key.to_string()) {
            Entry::Occupied(mut slot) => {
                slot.insert(value);
                slot.into_mut()
            }
            Entry::Vacant(slot) => slot.insert(value),
        };
        self.store.set(key, &to_str(kept)?)
    }

    /// `del_key(key)`.
    pub fn del_key(&mut self, key: &str) -> PyResult<()> {
        self.cache.remove(key);
        self.store.delete(key)
    }

    /// `rename(from, to)`: moves a value that is truthy, and says whether it did. The value goes
    /// through `set_key`, so text stored as `'5'` arrives as the int `5`.
    pub fn rename(&mut self, from: &str, to: &str) -> PyResult<bool> {
        let value = self.get_key(from)?.clone();
        if !value.truthy() {
            return Ok(false);
        }
        self.del_key(from)?;
        self.set_key(to, value)?;
        Ok(true)
    }

    /// `keys()`: the keys the store holds.
    pub fn keys(&mut self) -> PyResult<Vec<String>> {
        self.store.keys()
    }

    /// `re_cache()`: forgets everything and reads every key again.
    pub fn re_cache(&mut self) -> PyResult<()> {
        self.cache.clear();
        for key in self.store.keys()? {
            self.get_key(&key)?;
        }
        Ok(())
    }

    /// Forgets what is cached for one key, as when something else wrote to the store.
    pub fn forget(&mut self, key: &str) {
        self.cache.remove(key);
    }

    /// What a restart leaves: the stored text and an empty cache.
    pub fn restart(&mut self) {
        self.cache.clear();
    }
}

/// What an accessor works on after `value = udB.get_key(key) or <empty>`.
///
/// When the cached value is truthy, Python hands out that very object, and a change to it is in
/// the cache whether or not it is saved. Otherwise the accessor starts from a new empty value,
/// which reaches the cache only when it is saved. Both are kept apart here.
pub struct Held<'a, S> {
    store: &'a mut S,
    key: &'a str,
    cached: &'a mut PyValue,
    fresh: Option<PyValue>,
}

impl<S: Store> Held<'_, S> {
    /// The value to read and change.
    pub fn value(&mut self) -> &mut PyValue {
        match &mut self.fresh {
            Some(value) => value,
            None => self.cached,
        }
    }

    /// `udB.set_key(key, value)`: the cache has the value, the store gets its text. Gives what
    /// the original's backends give for a write, `True`.
    pub fn save(self) -> PyResult<PyValue> {
        if let Some(value) = self.fresh {
            *self.cached = value;
        }
        self.store.set(self.key, &to_str(self.cached)?)?;
        Ok(PyValue::Bool(true))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::value::PyDict;

    fn stored(db: &Database<MemoryStore>) -> Vec<(&str, &str)> {
        db.store().entries().collect()
    }

    #[test]
    fn values_are_stored_as_text_and_read_back() {
        let mut db = Database::new(MemoryStore::new());
        db.set_key("PHONE", PyValue::str("+919876543210")).unwrap();
        db.set_key("NAME", PyValue::str("007")).unwrap();
        db.set_key(
            "IDS",
            PyValue::List(vec![PyValue::int(1), PyValue::str("a")]),
        )
        .unwrap();
        assert_eq!(
            stored(&db),
            [
                ("PHONE", "919876543210"),
                ("NAME", "007"),
                ("IDS", "[1, 'a']")
            ]
        );
        db.restart();
        assert_eq!(
            *db.get_key("PHONE").unwrap(),
            PyValue::int(919_876_543_210_i64)
        );
        assert_eq!(*db.get_key("NAME").unwrap(), PyValue::str("007"));
        assert_eq!(*db.get_key("MISSING").unwrap(), PyValue::None);
        assert_eq!(*db.get_key("").unwrap(), PyValue::None);
    }

    #[test]
    fn a_missing_key_stays_missing_until_forgotten() {
        let mut db = Database::new(MemoryStore::new());
        assert_eq!(*db.get_key("K").unwrap(), PyValue::None);
        db.store_mut().set("K", "5").unwrap();
        assert_eq!(*db.get_key("K").unwrap(), PyValue::None);
        db.forget("K");
        assert_eq!(*db.get_key("K").unwrap(), PyValue::int(5));
        db.store_mut().set("L", "[1]").unwrap();
        db.re_cache().unwrap();
        assert_eq!(db.keys().unwrap(), ["K", "L"]);
    }

    #[test]
    fn rename_goes_through_set_key() {
        let mut db = Database::new(MemoryStore::new());
        db.store_mut().set("A", "'5'").unwrap();
        assert_eq!(*db.get_key("A").unwrap(), PyValue::str("5"));
        assert!(db.rename("A", "B").unwrap());
        assert_eq!(*db.get_key("B").unwrap(), PyValue::int(5));
        assert_eq!(stored(&db), [("B", "5")]);
        assert!(!db.rename("A", "C").unwrap());
        db.set_key("ZERO", PyValue::int(0)).unwrap();
        assert!(!db.rename("ZERO", "C").unwrap());
    }

    #[test]
    fn a_held_value_is_the_cached_one_only_when_truthy() {
        let mut db = Database::new(MemoryStore::new());
        let empty = || PyValue::Dict(PyDict::new());
        // Nothing stored: the change is to a new dict, and is lost unless saved.
        let mut held = db.hold("K", empty()).unwrap();
        crate::ops::update(held.value(), PyValue::int(1), PyValue::int(2)).unwrap();
        drop(held);
        assert_eq!(*db.get_key("K").unwrap(), PyValue::None);
        let mut held = db.hold("K", empty()).unwrap();
        crate::ops::update(held.value(), PyValue::int(1), PyValue::int(2)).unwrap();
        assert_eq!(held.save().unwrap(), PyValue::Bool(true));
        assert_eq!(stored(&db), [("K", "{1: 2}")]);
        // Something stored: the change is to the cached dict, saved or not.
        let mut held = db.hold("K", empty()).unwrap();
        crate::ops::update(held.value(), PyValue::int(3), PyValue::int(4)).unwrap();
        drop(held);
        assert_eq!(
            crate::repr(db.get_key("K").unwrap()).unwrap(),
            "{1: 2, 3: 4}"
        );
        assert_eq!(stored(&db), [("K", "{1: 2}")]);
    }

    #[test]
    fn the_cache_keeps_what_the_store_refused() {
        let mut db = Database::new(MemoryStore::new());
        let lone = PyValue::Surrogates(vec![0xd83d]);
        assert_eq!(
            db.set_key("K", lone.clone()).unwrap_err().kind,
            "UnicodeEncodeError"
        );
        assert_eq!(*db.get_key("K").unwrap(), lone);
        assert_eq!(stored(&db), []);
    }
}
