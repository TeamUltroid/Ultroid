//! Language strings: `strings/__init__.py`. Proven in `rust/strings-rs`.
//!
//! Every message Ultroid sends is looked up by a key in the language the owner chose. The
//! module loads that language's file when it is imported and loads the others only when the
//! list of languages is asked for. A key the language lacks is taken from English, if English
//! happens to be loaded, sent to Google to be translated, and kept.
//!
//! What a file holds is whatever the YAML reader made of it, so the values here are Python's
//! ([`PyValue`]), and a lookup fails the way Python fails when a file holds something else than
//! a mapping of keys to text.

use ultroid_db::ops::{add, as_dict, code_points, item, no_method, text};
use ultroid_db::{Database, PyDict, PyError, PyResult, PyValue, Store, repr, to_str};

/// What `strings` reaches outside itself: the language files, Google's translation and the log.
pub trait Host {
    /// `os.path.exists(path)`.
    fn exists(&self, path: &str) -> bool;
    /// `safe_load(open(path, encoding="UTF-8"))`: what the file holds, or the exception that
    /// opening or reading it ends in.
    fn read(&mut self, path: &str) -> PyResult<PyValue>;
    /// The names in `strings/strings`, in the order the directory lists them.
    fn names(&self) -> Vec<String>;
    /// `translate(text, lang_tgt=lang)`: the translation, or the exception the request ends in.
    fn translate(&mut self, text: &PyValue, lang: &PyValue) -> PyResult<PyValue>;
    /// `LOGS.info(message)`.
    fn info(&mut self, message: &str);
    /// `LOGS.exception(error)`.
    fn exception(&mut self, error: &PyError);
}

/// The module `strings`, once imported.
#[derive(Clone, Debug)]
pub struct Strings<H> {
    host: H,
    /// `ULTConfig.lang`: the language asked for. It is whatever the database holds under
    /// `language`, which need not be the code of a language, nor text.
    pub lang: PyValue,
    languages: PyDict,
}

/// Where the file of a language is.
fn path(code: &str) -> String {
    format!("strings/strings/{code}.yml")
}

fn english() -> PyValue {
    PyValue::str("en")
}

/// `value.replace("\\ N", "\n")`: Google puts a blank into the line breaks it is sent.
fn mend(value: &PyValue) -> PyResult<PyValue> {
    let Some(points) = code_points(value) else {
        return Err(match value {
            PyValue::Bytes(_) => PyError::type_error("a bytes-like object is required, not 'str'"),
            other => no_method(other, "replace"),
        });
    };
    let broken = ['\\', ' ', 'N'].map(u32::from);
    let (mut mended, mut rest) = (Vec::with_capacity(points.len()), &points[..]);
    while let Some((&first, after)) = rest.split_first() {
        if let Some(after) = rest.strip_prefix(&broken) {
            mended.push(u32::from('\n'));
            rest = after;
        } else {
            mended.push(first);
            rest = after;
        }
    }
    Ok(text(mended))
}

/// `value.count("{}")`: the places a message leaves to be filled in.
fn places(value: &PyValue) -> PyResult<usize> {
    let pair = ['{', '}'].map(u32::from);
    if let Some(points) = code_points(value) {
        let (mut count, mut rest) = (0, &points[..]);
        while let Some(at) = rest.windows(2).position(|window| window == pair) {
            count += 1;
            rest = rest.get(at + 2..).unwrap_or_default();
        }
        return Ok(count);
    }
    match value {
        PyValue::List(items) | PyValue::Tuple(items) => {
            let pair = PyValue::str("{}");
            Ok(items.iter().filter(|item| item.py_eq(&pair)).count())
        }
        PyValue::Bytes(_) => Err(PyError::type_error(
            "argument should be integer or bytes-like object, not 'str'",
        )),
        other => Err(no_method(other, "count")),
    }
}

impl<H: Host> Strings<H> {
    /// What importing the module does: the language is the one the database holds under
    /// `language`, or else the `LANGUAGE` variable, or else English, and its file is loaded.
    pub fn start<S: Store>(
        db: &mut Database<S>,
        variable: Option<&str>,
        host: H,
    ) -> PyResult<Self> {
        let stored = db.get_key("language")?;
        let lang = if stored.truthy() {
            stored.clone()
        } else {
            PyValue::str(variable.unwrap_or("en"))
        };
        let file = path(&to_str(&lang)?);
        let languages = PyDict::new();
        let mut strings = Self {
            host,
            lang,
            languages,
        };
        strings.load(&file);
        Ok(strings)
    }

    /// `languages`: what each loaded file holds, by the name of the file.
    pub fn languages(&self) -> &PyDict {
        &self.languages
    }

    pub fn host(&self) -> &H {
        &self.host
    }

    pub fn host_mut(&mut self) -> &mut H {
        &mut self.host
    }

    /// `load(file)`: reads a language file and keeps what it holds under the file's name. A
    /// file that is not there is read as English, and kept as English.
    pub fn load(&mut self, file: &str) {
        if !file.ends_with(".yml") {
            return;
        }
        let english = path("en");
        let file = if self.host.exists(file) {
            file
        } else {
            &english
        };
        let stem = file.strip_suffix(".yml").unwrap_or(file);
        // The name is what follows the last `/` and the last `\`.
        let code = stem.rsplit(['/', '\\']).next().unwrap_or(stem);
        match self.host.read(file) {
            // Text is always fit to be a key.
            Ok(held) => drop(self.languages.set(PyValue::str(code), held).ok()),
            Err(error) => {
                self.host.info(&format!("Error in {stem} language file"));
                self.host.exception(&error);
            }
        }
    }

    /// `languages[lang][key]`.
    fn held(&self, lang: &PyValue, key: &PyValue) -> PyResult<PyValue> {
        let missing = || PyError::new("KeyError", repr(lang).unwrap_or_default());
        let language = self.languages.get(lang)?.ok_or_else(missing)?;
        item(language, key).map(|found| found.into_owned())
    }

    /// The English string for a key, translated, and kept for the language from then on.
    fn translated(&mut self, lang: &PyValue, key: &PyValue) -> PyResult<PyValue> {
        let english = self.held(&english(), key)?;
        let mut translated = mend(&self.host.translate(&english, lang)?)?;
        // A translation that lost or gained a place to fill in would break the message.
        if places(&english)? != places(&translated)? {
            translated = english;
        }
        match self.languages.get_mut(lang)? {
            Some(PyValue::Dict(language)) if !language.is_empty() => {
                language.set(key.clone(), translated.clone())?;
            }
            Some(other) if other.truthy() => {
                let kind = other.type_name();
                let message = format!("'{kind}' object does not support item assignment");
                return Err(PyError::type_error(message));
            }
            _ => {
                let mut language = PyDict::new();
                language.set(key.clone(), translated.clone())?;
                self.languages.set(lang.clone(), PyValue::Dict(language))?;
            }
        }
        Ok(translated)
    }

    /// `get_string(key, _res)`: the string for a key in the language asked for.
    ///
    /// A key the language lacks goes through English and the translator. When English is not
    /// loaded or lacks the key too, the answer is a warning that names the key, or `None`
    /// without `res`. When the translation fails, it is the English string.
    pub fn get_string(&mut self, key: &PyValue, res: bool) -> PyResult<PyValue> {
        let lang = if self.lang.truthy() {
            self.lang.clone()
        } else {
            english()
        };
        match self.held(&lang, key) {
            Err(error) if error.kind == "KeyError" => {}
            found => return found,
        }
        let warning = "Warning: could not load any string with the key";
        match self.translated(&lang, key) {
            Err(error) if error.kind == "KeyError" => {
                if !res {
                    return Ok(PyValue::None);
                }
                return Ok(PyValue::str(format!("{warning} `{}`", to_str(key)?)));
            }
            Err(error) if error.kind == "TypeError" => {}
            Err(error) => self.host.exception(&error),
            found => return found,
        }
        if !res {
            return Ok(PyValue::None);
        }
        let english = self.held_whole(&english())?;
        let found = as_dict(english, "get")?.get(key)?;
        Ok(match found.filter(|found| found.truthy()) {
            Some(found) => found.clone(),
            None => PyValue::str(format!("Failed to load language string '{}'", to_str(key)?)),
        })
    }

    /// `languages[lang]`.
    fn held_whole(&self, lang: &PyValue) -> PyResult<&PyValue> {
        let missing = || PyError::new("KeyError", repr(lang).unwrap_or_default());
        self.languages.get(lang)?.ok_or_else(missing)
    }

    /// `get_help(key)`: the help text of a plugin under its heading, or `None` when there is
    /// none.
    pub fn get_help(&mut self, key: &PyValue) -> PyResult<PyValue> {
        let name = PyValue::str(format!("help_{}", to_str(key)?));
        let doc = self.get_string(&name, false)?;
        if !doc.truthy() {
            return Ok(PyValue::None);
        }
        add(&self.get_string(&PyValue::str("cmda"), true)?, &doc)
    }

    /// `get_languages()`: loads every language file in the directory, and gives each loaded
    /// language's `name`, `natively` and `authors`.
    pub fn get_languages(&mut self) -> PyResult<PyValue> {
        // `glob("strings/strings/*yml")`: no dot is asked for before `yml`, and a name that
        // starts with a dot is not listed.
        for name in self.host.names() {
            if name.ends_with("yml") && !name.starts_with('.') {
                self.load(&format!("strings/strings/{name}"));
            }
        }
        let mut listed = PyDict::new();
        for (code, language) in self.languages.iter() {
            let mut entry = PyDict::new();
            for field in ["name", "natively", "authors"].map(PyValue::str) {
                let value = item(language, &field)?.into_owned();
                entry.set(field, value)?;
            }
            listed.set(code.clone(), PyValue::Dict(entry))?;
        }
        Ok(PyValue::Dict(listed))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use ultroid_db::{MemoryStore, parse_literal};

    const EN: &str = "{'name': 'English', 'natively': 'English', 'authors': ['a', 'b'], \
        'py_c1': 'Wrong session!', 'cmda': 'Commands', 'help_ping': ': ping', 'fmt': 'a {} b {}'}";
    const HI: &str = "{'name': 'Hindi', 'natively': 'हिन्दी', 'authors': ['x'], 'py_c1': 'गलत'}";

    /// A folder of files written as Python would print what they hold, a translator that puts
    /// the language in front, and a note of what was translated and logged.
    #[derive(Default)]
    struct Folder {
        files: Vec<(&'static str, &'static str)>,
        asked: Vec<String>,
        logged: Vec<String>,
    }

    impl Folder {
        fn file(&self, path: &str) -> Option<&'static str> {
            let name = path.strip_prefix("strings/strings/")?;
            let found = self.files.iter().find(|(file, _)| *file == name)?;
            Some(found.1)
        }
    }

    impl Host for Folder {
        fn exists(&self, path: &str) -> bool {
            self.file(path).is_some()
        }

        fn read(&mut self, path: &str) -> PyResult<PyValue> {
            let missing = || PyError::new("FileNotFoundError", path);
            let unread = || PyError::value_error("no literal");
            parse_literal(self.file(path).ok_or_else(missing)?).ok_or_else(unread)
        }

        fn names(&self) -> Vec<String> {
            self.files
                .iter()
                .map(|(name, _)| name.to_string())
                .collect()
        }

        fn translate(&mut self, text: &PyValue, lang: &PyValue) -> PyResult<PyValue> {
            self.asked.push(to_str(text)?);
            Ok(PyValue::str(format!(
                "[{}] {}",
                to_str(lang)?,
                to_str(text)?
            )))
        }

        fn info(&mut self, message: &str) {
            self.logged.push(message.to_string());
        }

        fn exception(&mut self, error: &PyError) {
            self.logged.push(error.kind.to_string());
        }
    }

    fn started(stored: Option<&str>, variable: Option<&str>) -> Strings<Folder> {
        let mut db = Database::new(MemoryStore::new());
        if let Some(stored) = stored {
            db.store_mut().set("language", stored).unwrap();
        }
        let files = vec![("en.yml", EN), ("hi.yml", HI)];
        let folder = Folder {
            files,
            ..Folder::default()
        };
        Strings::start(&mut db, variable, folder).unwrap()
    }

    fn string(strings: &mut Strings<Folder>, key: &str) -> PyValue {
        strings.get_string(&PyValue::str(key), true).unwrap()
    }

    // What is expected below is what the original gives for the same files (CPython 3.11).

    #[test]
    fn english_is_only_there_when_something_loaded_it() {
        let mut strings = started(Some("hi"), None);
        assert_eq!(string(&mut strings, "py_c1"), PyValue::str("गलत"));
        let warning = "Warning: could not load any string with the key `fmt`";
        assert_eq!(string(&mut strings, "fmt"), PyValue::str(warning));
        let listed = strings.get_languages().unwrap();
        let both = "{'hi': {'name': 'Hindi', 'natively': 'हिन्दी', 'authors': ['x']}, \
            'en': {'name': 'English', 'natively': 'English', 'authors': ['a', 'b']}}";
        assert_eq!(repr(&listed).unwrap(), both);
        // Now English is there, and the string comes through the translator, once.
        assert_eq!(string(&mut strings, "fmt"), PyValue::str("[hi] a {} b {}"));
        assert_eq!(string(&mut strings, "fmt"), PyValue::str("[hi] a {} b {}"));
        assert_eq!(strings.host().asked, ["a {} b {}"]);
        assert!(strings.host().logged.is_empty());
    }

    #[test]
    fn a_language_with_no_file_is_read_as_english() {
        // What a desktop Linux has in `LANGUAGE` for its own messages.
        let mut strings = started(None, Some("en_US:en"));
        assert_eq!(strings.lang, PyValue::str("en_US:en"));
        let translated = "[en_US:en] Wrong session!";
        assert_eq!(string(&mut strings, "py_c1"), PyValue::str(translated));
        assert_eq!(strings.host().asked, ["Wrong session!"]);
        // The database comes first, and what it holds is read as `get_key` reads it.
        assert_eq!(started(Some("hi"), Some("en")).lang, PyValue::str("hi"));
        assert_eq!(started(Some("5"), Some("en")).lang, PyValue::int(5));
        assert_eq!(started(Some("None"), None).lang, PyValue::str("en"));
        assert_eq!(started(Some("0"), Some("")).lang, PyValue::str(""));
    }

    #[test]
    fn help_under_its_heading() {
        let mut strings = started(None, None);
        let help = strings.get_help(&PyValue::str("ping")).unwrap();
        assert_eq!(help, PyValue::str("Commands: ping"));
        assert_eq!(strings.get_help(&PyValue::str("x")).unwrap(), PyValue::None);
        assert!(strings.host().asked.is_empty());
    }
}
