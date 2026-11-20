//! The accessors of `pyUltroid/dB`: one module per Python module and one function per function,
//! under the same names.
//!
//! Each does what the original does to the letter: the order things are looked up and
//! converted in, what comes back, and the exception when a value has another shape. The slips
//! of the original are kept and marked where they are; the README lists them.

use crate::clock::DateTime;
use crate::database::{Database, Store};
use crate::ops::{
    append, as_dict, contains, format_each, int, item, len, method, pop, remove, split, update,
    with_item,
};
use crate::value::{PyDict, PyError, PyResult, PyValue};
use std::borrow::Cow;

type Out = PyResult<PyValue>;

const NONE: Out = Ok(PyValue::None);

fn dict() -> PyValue {
    PyValue::Dict(PyDict::new())
}

fn list() -> PyValue {
    PyValue::List(Vec::new())
}

fn flag(value: bool) -> PyValue {
    PyValue::Bool(value)
}

/// `int(value)`.
fn whole(value: &PyValue) -> Out {
    int(value).map(PyValue::Int)
}

/// `{key: value}`.
fn pair(key: &PyValue, value: PyValue) -> Out {
    let mut made = PyDict::new();
    made.set(key.clone(), value)?;
    Ok(PyValue::Dict(made))
}

/// A dict with text keys, as the reply records are: `{"msg": ..., "media": ..., "button": ...}`.
fn record(first: &str, msg: &PyValue, media: &PyValue, button: &PyValue) -> PyValue {
    let mut made = PyDict::new();
    for (name, value) in [(first, msg), ("media", media), ("button", button)] {
        // INFALLIBLE: a text key is always hashable.
        let _ = made.set(PyValue::str(name), value.clone());
    }
    PyValue::Dict(made)
}

/// `mapping.get(key)` when that is truthy: what `if mapping.get(key):` lets through.
fn found<'a>(mapping: &'a PyValue, key: &PyValue) -> PyResult<Option<&'a PyValue>> {
    Ok(as_dict(mapping, "get")?
        .get(key)?
        .filter(|value| value.truthy()))
}

/// `int(chat)` for an accessor that starts with `stored.get(int(chat))`: the `get` is looked up
/// first, so a stored value that is no dict fails before a bad `chat` does.
fn int_key<S: Store>(db: &mut Database<S>, key: &str, chat: &PyValue) -> Out {
    let empty = dict();
    method(db.read(key, &empty)?, "get")?;
    whole(chat)
}

/// `stored.update({name: value})`, saved.
fn put<S: Store>(db: &mut Database<S>, key: &str, name: &PyValue, value: PyValue) -> Out {
    let mut held = db.hold(key, dict())?;
    update(held.value(), name.clone(), value)?;
    held.save()
}

/// `if stored.get(name): stored.pop(name)`, saved. `None` when there was nothing to drop.
fn drop_found<S: Store>(db: &mut Database<S>, key: &str, name: &PyValue) -> Out {
    let mut held = db.hold(key, dict())?;
    if found(held.value(), name)?.is_none() {
        return NONE;
    }
    pop(held.value(), name)?;
    held.save()
}

/// `if stored.get(name): return stored[name]`.
fn lookup<S: Store>(db: &mut Database<S>, key: &str, name: &PyValue) -> Out {
    let empty = dict();
    let hit = found(db.read(key, &empty)?, name)?;
    Ok(hit.cloned().unwrap_or(PyValue::None))
}

/// `stored.get(name)`, falsy values included.
fn peek<S: Store>(db: &mut Database<S>, key: &str, name: &PyValue) -> Out {
    let empty = dict();
    let hit = as_dict(db.read(key, &empty)?, "get")?.get(name)?;
    Ok(hit.cloned().unwrap_or(PyValue::None))
}

/// `if name in stored.keys(): return stored[name]`.
fn keyed<S: Store>(db: &mut Database<S>, key: &str, name: &PyValue) -> Out {
    let empty = dict();
    let hit = as_dict(db.read(key, &empty)?, "keys")?.get(name)?;
    Ok(hit.cloned().unwrap_or(PyValue::None))
}

/// `if name in stored.keys(): del stored[name]`, saved.
fn drop_keyed<S: Store>(db: &mut Database<S>, key: &str, name: &PyValue) -> Out {
    let mut held = db.hold(key, dict())?;
    if !as_dict(held.value(), "keys")?.contains(name)? {
        return NONE;
    }
    pop(held.value(), name)?;
    held.save()
}

/// `list(stored.keys())`.
fn names<S: Store>(db: &mut Database<S>, key: &str) -> Out {
    let empty = dict();
    let stored = as_dict(db.read(key, &empty)?, "keys")?;
    Ok(PyValue::List(stored.keys().cloned().collect()))
}

/// `stored[outer][name] = entry`, starting `stored[outer]` when it is missing or empty; saved.
fn put_nested<S: Store>(
    db: &mut Database<S>,
    key: &str,
    outer: &PyValue,
    name: &PyValue,
    entry: PyValue,
) -> Out {
    let mut held = db.hold(key, dict())?;
    let stored = held.value();
    if found(stored, outer)?.is_some() {
        with_item(stored, outer, |inner| update(inner, name.clone(), entry))?;
    } else {
        update(stored, outer.clone(), pair(name, entry)?)?;
    }
    held.save()
}

/// `stored.get(outer) and stored[outer].get(name)`, when both are truthy.
fn found_nested<'a>(
    stored: &'a PyValue,
    outer: &PyValue,
    name: &PyValue,
) -> PyResult<Option<&'a PyValue>> {
    match found(stored, outer)? {
        Some(inner) => found(inner, name),
        None => Ok(None),
    }
}

/// `if stored.get(outer) and stored[outer].get(name): stored[outer].pop(name)`, saved.
fn drop_nested<S: Store>(db: &mut Database<S>, key: &str, outer: &PyValue, name: &PyValue) -> Out {
    let mut held = db.hold(key, dict())?;
    if found_nested(held.value(), outer, name)?.is_none() {
        return NONE;
    }
    with_item(held.value(), outer, |inner| pop(inner, name))?;
    held.save()
}

/// `stored.get(outer) and item in stored[outer]`.
fn listed(stored: &PyValue, outer: &PyValue, item: &PyValue) -> PyResult<bool> {
    match found(stored, outer)? {
        Some(members) => contains(members, item),
        None => Ok(false),
    }
}

pub mod afk_db {
    use super::*;

    const KEY: &str = "AFK_DB";

    pub fn get_stuff<S: Store>(db: &mut Database<S>) -> Out {
        db.get_or(KEY, list())
    }

    pub fn add_afk<S: Store>(
        db: &mut Database<S>,
        now: &DateTime,
        msg: &PyValue,
        media_type: &PyValue,
        media: &PyValue,
    ) -> Out {
        let time = PyValue::Str(now.afk_text());
        let entry = vec![msg.clone(), media_type.clone(), media.clone(), time];
        db.set_key(KEY, PyValue::List(entry))?;
        NONE
    }

    /// `(msg, media_type, media, how long ago)`, or `False` when not away.
    pub fn is_afk<S: Store>(db: &mut Database<S>, now: &DateTime) -> Out {
        let empty = list();
        let afk = db.read(KEY, &empty)?;
        if !afk.truthy() {
            return Ok(flag(false));
        }
        let part = |at: u8| item(afk, &PyValue::int(at)).map(Cow::into_owned);
        let start = DateTime::from_afk_text(&part(3)?)?;
        let since = PyValue::Str(now.since(&start));
        Ok(PyValue::Tuple(vec![part(0)?, part(1)?, part(2)?, since]))
    }

    pub fn del_afk<S: Store>(db: &mut Database<S>) -> Out {
        db.del_key(KEY)?;
        Ok(flag(true))
    }
}

pub mod antiflood_db {
    use super::*;

    const KEY: &str = "ANTIFLOOD";

    pub fn get_flood<S: Store>(db: &mut Database<S>) -> Out {
        db.get_or(KEY, dict())
    }

    pub fn set_flood<S: Store>(db: &mut Database<S>, chat_id: &PyValue, limit: &PyValue) -> Out {
        put(db, KEY, chat_id, limit.clone())
    }

    pub fn get_flood_limit<S: Store>(db: &mut Database<S>, chat_id: &PyValue) -> Out {
        keyed(db, KEY, chat_id)
    }

    pub fn rem_flood<S: Store>(db: &mut Database<S>, chat_id: &PyValue) -> Out {
        drop_keyed(db, KEY, chat_id)
    }
}

pub mod asstcmd_db {
    use super::*;

    const KEY: &str = "ASST_CMDS";

    pub fn get_stuff<S: Store>(db: &mut Database<S>) -> Out {
        db.get_or(KEY, dict())
    }

    pub fn add_cmd<S: Store>(
        db: &mut Database<S>,
        cmd: &PyValue,
        msg: &PyValue,
        media: &PyValue,
        button: &PyValue,
    ) -> Out {
        put(db, KEY, cmd, record("msg", msg, media, button))
    }

    pub fn rem_cmd<S: Store>(db: &mut Database<S>, cmd: &PyValue) -> Out {
        drop_found(db, KEY, cmd)
    }

    /// `(msg, media, button)`. The button comes back only while a command called `button`
    /// exists: the original asks the table of commands, not this command, whether it has one.
    pub fn cmd_reply<S: Store>(db: &mut Database<S>, cmd: &PyValue) -> Out {
        let empty = dict();
        let stored = db.read(KEY, &empty)?;
        let Some(reply) = found(stored, cmd)? else {
            return NONE;
        };
        let part = |name: &str| item(reply, &PyValue::str(name)).map(Cow::into_owned);
        let (msg, media) = (part("msg")?, part("media")?);
        let button = match found(stored, &PyValue::str("button"))? {
            Some(_) => part("button")?,
            None => PyValue::None,
        };
        Ok(PyValue::Tuple(vec![msg, media, button]))
    }

    /// The command names. A `dict_keys` view in the original, a list here.
    pub fn list_cmds<S: Store>(db: &mut Database<S>) -> Out {
        names(db, KEY)
    }
}

pub mod blacklist_chat_db {
    use super::*;

    const KEY: &str = "BLACKLIST_CHATS";

    pub fn add_black_chat<S: Store>(db: &mut Database<S>, chat_id: &PyValue) -> Out {
        let mut held = db.hold(KEY, list())?;
        if contains(held.value(), chat_id)? {
            return NONE;
        }
        append(held.value(), chat_id.clone())?;
        held.save()
    }

    pub fn rem_black_chat<S: Store>(db: &mut Database<S>, chat_id: &PyValue) -> Out {
        let mut held = db.hold(KEY, list())?;
        if !contains(held.value(), chat_id)? {
            return NONE;
        }
        remove(held.value(), chat_id)?;
        held.save()
    }
}

pub mod blacklist_db {
    use super::*;

    const KEY: &str = "BLACKLIST_DB";

    pub fn get_stuff<S: Store>(db: &mut Database<S>) -> Out {
        db.get_or(KEY, dict())
    }

    /// The first word for a chat is stored whole; later ones are split on blanks.
    pub fn add_blacklist<S: Store>(db: &mut Database<S>, chat: &PyValue, word: &PyValue) -> Out {
        let mut held = db.hold(KEY, dict())?;
        let stored = held.value();
        if found(stored, chat)?.is_some() {
            let pieces = split(word)?;
            with_item(stored, chat, |words| {
                for piece in pieces {
                    if !contains(words, &piece)? {
                        append(words, piece)?;
                    }
                }
                Ok(())
            })?;
        } else {
            update(stored, chat.clone(), PyValue::List(vec![word.clone()]))?;
        }
        held.save()
    }

    pub fn rem_blacklist<S: Store>(db: &mut Database<S>, chat: &PyValue, word: &PyValue) -> Out {
        let mut held = db.hold(KEY, dict())?;
        if !listed(held.value(), chat, word)? {
            return NONE;
        }
        with_item(held.value(), chat, |words| remove(words, word))?;
        held.save()
    }

    pub fn list_blacklist<S: Store>(db: &mut Database<S>, chat: &PyValue) -> Out {
        let empty = dict();
        let Some(words) = found(db.read(KEY, &empty)?, chat)? else {
            return NONE;
        };
        let text = format_each(words, "👉`", "`\n")?;
        Ok(if text.truthy() { text } else { PyValue::None })
    }

    pub fn get_blacklist<S: Store>(db: &mut Database<S>, chat: &PyValue) -> Out {
        lookup(db, KEY, chat)
    }
}

pub mod botchat_db {
    use super::*;

    const KEY: &str = "BOTCHAT";

    pub fn get_stuff<S: Store>(db: &mut Database<S>) -> Out {
        db.get_or(KEY, dict())
    }

    pub fn add_stuff<S: Store>(db: &mut Database<S>, msg_id: &PyValue, user_id: &PyValue) -> Out {
        put(db, KEY, msg_id, user_id.clone())
    }

    pub fn get_who<S: Store>(db: &mut Database<S>, msg_id: &PyValue) -> Out {
        lookup(db, KEY, msg_id)
    }

    /// Tags live under the name `TAG` in the same dict as the message ids of `add_stuff`.
    pub fn tag_add<S: Store>(
        db: &mut Database<S>,
        msg: &PyValue,
        chat: &PyValue,
        user: &PyValue,
    ) -> Out {
        put_nested(
            db,
            KEY,
            &PyValue::str("TAG"),
            msg,
            PyValue::List(vec![chat.clone(), user.clone()]),
        )
    }

    pub fn who_tag<S: Store>(db: &mut Database<S>, msg: &PyValue) -> Out {
        let empty = dict();
        let hit = found_nested(db.read(KEY, &empty)?, &PyValue::str("TAG"), msg)?;
        Ok(hit
            .cloned()
            .unwrap_or_else(|| PyValue::Tuple(vec![flag(false), flag(false)])))
    }
}

pub mod echo_db {
    use super::*;

    const KEY: &str = "ECHO";

    pub fn get_stuff<S: Store>(db: &mut Database<S>) -> Out {
        db.get_or(KEY, dict())
    }

    pub fn add_echo<S: Store>(db: &mut Database<S>, chat: &PyValue, user: &PyValue) -> Out {
        let mut held = db.hold(KEY, dict())?;
        let stored = held.value();
        method(stored, "get")?;
        let chat = whole(chat)?;
        if found(stored, &chat)?.is_some() {
            with_item(stored, &chat, |users| {
                if !contains(users, user)? {
                    method(users, "append")?;
                    append(users, whole(user)?)?;
                }
                Ok(())
            })?;
        } else {
            update(stored, chat, PyValue::List(vec![whole(user)?]))?;
        }
        held.save()
    }

    /// Looks for `user` as given, then removes `int(user)`.
    pub fn rem_echo<S: Store>(db: &mut Database<S>, chat: &PyValue, user: &PyValue) -> Out {
        let mut held = db.hold(KEY, dict())?;
        let stored = held.value();
        method(stored, "get")?;
        let chat = whole(chat)?;
        if found(stored, &chat)?.is_some() {
            with_item(stored, &chat, |users| {
                if contains(users, user)? {
                    method(users, "remove")?;
                    remove(users, &whole(user)?)?;
                }
                Ok(())
            })?;
        }
        held.save()
    }

    /// `True`, or `None` where one would expect `False`.
    pub fn check_echo<S: Store>(db: &mut Database<S>, chat: &PyValue, user: &PyValue) -> Out {
        let chat = int_key(db, KEY, chat)?;
        let empty = dict();
        let Some(users) = found(db.read(KEY, &empty)?, &chat)? else {
            return NONE;
        };
        Ok(if contains(users, &whole(user)?)? {
            flag(true)
        } else {
            PyValue::None
        })
    }

    pub fn list_echo<S: Store>(db: &mut Database<S>, chat: &PyValue) -> Out {
        let chat = int_key(db, KEY, chat)?;
        peek(db, KEY, &chat)
    }
}

pub mod filestore_db {
    use super::*;

    const KEY: &str = "FILE_STORE";

    pub fn get_stored<S: Store>(db: &mut Database<S>) -> Out {
        db.get_or(KEY, dict())
    }

    pub fn store_msg<S: Store>(db: &mut Database<S>, hash: &PyValue, msg_id: &PyValue) -> Out {
        put(db, KEY, hash, msg_id.clone())
    }

    pub fn list_all_stored_msgs<S: Store>(db: &mut Database<S>) -> Out {
        names(db, KEY)
    }

    pub fn get_stored_msg<S: Store>(db: &mut Database<S>, hash: &PyValue) -> Out {
        lookup(db, KEY, hash)
    }

    /// A hash that is not stored is a `KeyError`.
    pub fn del_stored<S: Store>(db: &mut Database<S>, hash: &PyValue) -> Out {
        let mut held = db.hold(KEY, dict())?;
        pop(held.value(), hash)?;
        held.save()
    }
}

pub mod filter_db {
    use super::*;

    const KEY: &str = "FILTERS";

    pub fn get_stuff<S: Store>(db: &mut Database<S>) -> Out {
        db.get_or(KEY, dict())
    }

    pub fn add_filter<S: Store>(
        db: &mut Database<S>,
        chat: &PyValue,
        word: &PyValue,
        msg: &PyValue,
        media: &PyValue,
        button: &PyValue,
    ) -> Out {
        put_nested(db, KEY, chat, word, record("msg", msg, media, button))?;
        NONE
    }

    pub fn rem_filter<S: Store>(db: &mut Database<S>, chat: &PyValue, word: &PyValue) -> Out {
        drop_nested(db, KEY, chat, word)?;
        NONE
    }

    pub fn rem_all_filter<S: Store>(db: &mut Database<S>, chat: &PyValue) -> Out {
        drop_found(db, KEY, chat)?;
        NONE
    }

    pub fn get_filter<S: Store>(db: &mut Database<S>, chat: &PyValue) -> Out {
        lookup(db, KEY, chat)
    }

    pub fn list_filter<S: Store>(db: &mut Database<S>, chat: &PyValue) -> Out {
        let empty = dict();
        match found(db.read(KEY, &empty)?, chat)? {
            Some(words) => format_each(words, "👉 `", "`\n"),
            None => NONE,
        }
    }
}

pub mod forcesub_db {
    use super::*;

    const KEY: &str = "FORCESUB";

    pub fn get_chats<S: Store>(db: &mut Database<S>) -> Out {
        db.get_or(KEY, dict())
    }

    pub fn add_forcesub<S: Store>(
        db: &mut Database<S>,
        chat_id: &PyValue,
        chattojoin: &PyValue,
    ) -> Out {
        put(db, KEY, chat_id, chattojoin.clone())
    }

    pub fn get_forcesetting<S: Store>(db: &mut Database<S>, chat_id: &PyValue) -> Out {
        keyed(db, KEY, chat_id)
    }

    pub fn rem_forcesub<S: Store>(db: &mut Database<S>, chat_id: &PyValue) -> Out {
        drop_keyed(db, KEY, chat_id)
    }
}

pub mod gban_mute_db {
    use super::*;

    const GBAN: &str = "GBAN";
    const GMUTE: &str = "GMUTE";

    pub fn list_gbanned<S: Store>(db: &mut Database<S>) -> Out {
        db.get_or(GBAN, dict())
    }

    pub fn gban<S: Store>(db: &mut Database<S>, user: &PyValue, reason: &PyValue) -> Out {
        let mut held = db.hold(GBAN, dict())?;
        method(held.value(), "update")?;
        let reason = if reason.truthy() {
            reason.clone()
        } else {
            PyValue::str("No Reason. ")
        };
        update(held.value(), whole(user)?, reason)?;
        held.save()
    }

    pub fn ungban<S: Store>(db: &mut Database<S>, user: &PyValue) -> Out {
        let user = int_key(db, GBAN, user)?;
        drop_found(db, GBAN, &user)
    }

    /// The reason, or `None`.
    pub fn is_gbanned<S: Store>(db: &mut Database<S>, user: &PyValue) -> Out {
        let user = int_key(db, GBAN, user)?;
        lookup(db, GBAN, &user)
    }

    /// Adds without looking: muting twice lists the user twice.
    pub fn gmute<S: Store>(db: &mut Database<S>, user: &PyValue) -> Out {
        let mut held = db.hold(GMUTE, list())?;
        method(held.value(), "append")?;
        append(held.value(), whole(user)?)?;
        held.save()
    }

    /// Looks for `user` as given, so an id passed as text is never found.
    pub fn ungmute<S: Store>(db: &mut Database<S>, user: &PyValue) -> Out {
        let mut held = db.hold(GMUTE, list())?;
        if !contains(held.value(), user)? {
            return NONE;
        }
        method(held.value(), "remove")?;
        remove(held.value(), &whole(user)?)?;
        held.save()
    }

    pub fn is_gmuted<S: Store>(db: &mut Database<S>, user: &PyValue) -> Out {
        let user = whole(user)?;
        let empty = list();
        Ok(flag(contains(db.read(GMUTE, &empty)?, &user)?))
    }

    pub fn list_gmuted<S: Store>(db: &mut Database<S>) -> Out {
        db.get_or(GMUTE, list())
    }
}

pub mod greetings_db {
    use super::*;

    const WELCOME: &str = "WELCOME";
    const GOODBYE: &str = "GOODBYE";
    const THANKS: &str = "THANK_MEMBERS";

    /// `get_stuff(key)`; with no key the original reads nothing and gives `{}`.
    pub fn get_stuff<S: Store>(db: &mut Database<S>, key: Option<&str>) -> Out {
        match key {
            Some(key) => db.get_or(key, dict()),
            None => Ok(dict()),
        }
    }

    pub fn add_welcome<S: Store>(
        db: &mut Database<S>,
        chat: &PyValue,
        msg: &PyValue,
        media: &PyValue,
        button: &PyValue,
    ) -> Out {
        put(db, WELCOME, chat, record("welcome", msg, media, button))
    }

    pub fn get_welcome<S: Store>(db: &mut Database<S>, chat: &PyValue) -> Out {
        peek(db, WELCOME, chat)
    }

    pub fn delete_welcome<S: Store>(db: &mut Database<S>, chat: &PyValue) -> Out {
        drop_found(db, WELCOME, chat)
    }

    pub fn add_goodbye<S: Store>(
        db: &mut Database<S>,
        chat: &PyValue,
        msg: &PyValue,
        media: &PyValue,
        button: &PyValue,
    ) -> Out {
        put(db, GOODBYE, chat, record("goodbye", msg, media, button))
    }

    pub fn get_goodbye<S: Store>(db: &mut Database<S>, chat: &PyValue) -> Out {
        peek(db, GOODBYE, chat)
    }

    pub fn delete_goodbye<S: Store>(db: &mut Database<S>, chat: &PyValue) -> Out {
        drop_found(db, GOODBYE, chat)
    }

    pub fn add_thanks<S: Store>(db: &mut Database<S>, chat: &PyValue) -> Out {
        put(db, THANKS, chat, flag(true))
    }

    pub fn remove_thanks<S: Store>(db: &mut Database<S>, chat: &PyValue) -> Out {
        drop_found(db, THANKS, chat)
    }

    pub fn must_thank<S: Store>(db: &mut Database<S>, chat: &PyValue) -> Out {
        peek(db, THANKS, chat)
    }
}

pub mod mute_db {
    use super::*;

    const KEY: &str = "MUTE";

    pub fn get_muted<S: Store>(db: &mut Database<S>) -> Out {
        db.get_or(KEY, dict())
    }

    pub fn mute<S: Store>(db: &mut Database<S>, chat: &PyValue, id: &PyValue) -> Out {
        let mut held = db.hold(KEY, dict())?;
        let stored = held.value();
        if found(stored, chat)?.is_some() {
            with_item(stored, chat, |ids| {
                if !contains(ids, id)? {
                    append(ids, id.clone())?;
                }
                Ok(())
            })?;
        } else {
            update(stored, chat.clone(), PyValue::List(vec![id.clone()]))?;
        }
        held.save()
    }

    /// Writes the key even when there was nothing to remove.
    pub fn unmute<S: Store>(db: &mut Database<S>, chat: &PyValue, id: &PyValue) -> Out {
        let mut held = db.hold(KEY, dict())?;
        if listed(held.value(), chat, id)? {
            with_item(held.value(), chat, |ids| remove(ids, id))?;
        }
        held.save()
    }

    pub fn is_muted<S: Store>(db: &mut Database<S>, chat: &PyValue, id: &PyValue) -> Out {
        let empty = dict();
        Ok(flag(listed(db.read(KEY, &empty)?, chat, id)?))
    }
}

pub mod notes_db {
    use super::*;

    const KEY: &str = "NOTE";

    pub fn get_stuff<S: Store>(db: &mut Database<S>) -> Out {
        db.get_or(KEY, dict())
    }

    pub fn add_note<S: Store>(
        db: &mut Database<S>,
        chat: &PyValue,
        word: &PyValue,
        msg: &PyValue,
        media: &PyValue,
        button: &PyValue,
    ) -> Out {
        let chat = int_key(db, KEY, chat)?;
        put_nested(db, KEY, &chat, word, record("msg", msg, media, button))?;
        NONE
    }

    pub fn rem_note<S: Store>(db: &mut Database<S>, chat: &PyValue, word: &PyValue) -> Out {
        let chat = int_key(db, KEY, chat)?;
        drop_nested(db, KEY, &chat, word)
    }

    pub fn rem_all_note<S: Store>(db: &mut Database<S>, chat: &PyValue) -> Out {
        let chat = int_key(db, KEY, chat)?;
        drop_found(db, KEY, &chat)
    }

    pub fn get_notes<S: Store>(db: &mut Database<S>, chat: &PyValue, word: &PyValue) -> Out {
        let chat = int_key(db, KEY, chat)?;
        let empty = dict();
        let hit = found_nested(db.read(KEY, &empty)?, &chat, word)?;
        Ok(hit.cloned().unwrap_or(PyValue::None))
    }

    /// Finds the chat by `int(chat)` and then lists `stored[chat]` as given, so a chat passed
    /// as text is a `KeyError`.
    pub fn list_note<S: Store>(db: &mut Database<S>, chat: &PyValue) -> Out {
        let number = int_key(db, KEY, chat)?;
        let empty = dict();
        let stored = db.read(KEY, &empty)?;
        if found(stored, &number)?.is_none() {
            return NONE;
        }
        format_each(item(stored, chat)?.as_ref(), "👉 #", "\n")
    }
}

pub mod nsfw_db {
    use super::*;

    const NSFW: &str = "NSFW";
    const PROFANITY: &str = "PROFANITY";

    pub fn get_stuff<S: Store>(db: &mut Database<S>, key: Option<&str>) -> Out {
        db.get_or(key.unwrap_or(NSFW), dict())
    }

    pub fn nsfw_chat<S: Store>(db: &mut Database<S>, chat: &PyValue, action: &PyValue) -> Out {
        put(db, NSFW, chat, action.clone())
    }

    pub fn rem_nsfw<S: Store>(db: &mut Database<S>, chat: &PyValue) -> Out {
        drop_found(db, NSFW, chat)
    }

    pub fn is_nsfw<S: Store>(db: &mut Database<S>, chat: &PyValue) -> Out {
        lookup(db, NSFW, chat)
    }

    pub fn profan_chat<S: Store>(db: &mut Database<S>, chat: &PyValue, action: &PyValue) -> Out {
        put(db, PROFANITY, chat, action.clone())
    }

    pub fn rem_profan<S: Store>(db: &mut Database<S>, chat: &PyValue) -> Out {
        drop_found(db, PROFANITY, chat)
    }

    pub fn is_profan<S: Store>(db: &mut Database<S>, chat: &PyValue) -> Out {
        lookup(db, PROFANITY, chat)
    }
}

pub mod snips_db {
    use super::*;

    const KEY: &str = "SNIP";

    pub fn get_all_snips<S: Store>(db: &mut Database<S>) -> Out {
        db.get_or(KEY, dict())
    }

    pub fn add_snip<S: Store>(
        db: &mut Database<S>,
        word: &PyValue,
        msg: &PyValue,
        media: &PyValue,
        button: &PyValue,
    ) -> Out {
        put(db, KEY, word, record("msg", msg, media, button))?;
        NONE
    }

    pub fn rem_snip<S: Store>(db: &mut Database<S>, word: &PyValue) -> Out {
        drop_found(db, KEY, word)?;
        NONE
    }

    /// The snip, or `False`.
    pub fn get_snips<S: Store>(db: &mut Database<S>, word: &PyValue) -> Out {
        let empty = dict();
        let hit = found(db.read(KEY, &empty)?, word)?;
        Ok(hit.cloned().unwrap_or(flag(false)))
    }

    pub fn list_snip<S: Store>(db: &mut Database<S>) -> Out {
        let empty = dict();
        format_each(db.read(KEY, &empty)?, "👉 $", "\n")
    }
}

pub mod vc_sudos {
    use super::*;

    const KEY: &str = "VC_SUDOS";

    pub fn get_vcsudos<S: Store>(db: &mut Database<S>) -> Out {
        db.get_or(KEY, list())
    }

    pub fn is_vcsudo<S: Store>(db: &mut Database<S>, id: &PyValue) -> Out {
        let empty = list();
        Ok(flag(contains(db.read(KEY, &empty)?, id)?))
    }

    /// Adds without looking, like `gmute`.
    pub fn add_vcsudo<S: Store>(db: &mut Database<S>, id: &PyValue) -> Out {
        let mut held = db.hold(KEY, list())?;
        append(held.value(), id.clone())?;
        held.save()
    }

    pub fn del_vcsudo<S: Store>(db: &mut Database<S>, id: &PyValue) -> Out {
        let mut held = db.hold(KEY, list())?;
        if !contains(held.value(), id)? {
            return NONE;
        }
        remove(held.value(), id)?;
        held.save()
    }
}

pub mod warn_db {
    use super::*;

    const KEY: &str = "WARNS";

    pub fn get_stuff<S: Store>(db: &mut Database<S>) -> Out {
        db.get_or(KEY, dict())
    }

    /// Whatever goes wrong adding to the chat's warnings, the chat starts over with this one.
    pub fn add_warn<S: Store>(
        db: &mut Database<S>,
        chat: &PyValue,
        user: &PyValue,
        count: &PyValue,
        reason: &PyValue,
    ) -> Out {
        let mut held = db.hold(KEY, dict())?;
        let stored = held.value();
        let warning = || PyValue::List(vec![count.clone(), reason.clone()]);
        let added = with_item(stored, chat, |users| update(users, user.clone(), warning()));
        if added.is_err() {
            method(stored, "update")?;
            update(stored, chat.clone(), pair(user, warning())?)?;
        }
        held.save()
    }

    /// `(count, reason)`, and `(0, None)` for anything that cannot be read as that.
    pub fn warns<S: Store>(db: &mut Database<S>, chat: &PyValue, user: &PyValue) -> Out {
        let empty = dict();
        let stored = db.read(KEY, &empty)?;
        let part = |at: u8| -> Out {
            let warning = item(stored, chat)?;
            let warning = item(&warning, user)?;
            item(&warning, &PyValue::int(at)).map(Cow::into_owned)
        };
        let read = part(0).and_then(|count| Ok(vec![count, part(1)?]));
        Ok(PyValue::Tuple(
            read.unwrap_or_else(|_| vec![PyValue::int(0), PyValue::None]),
        ))
    }

    /// `None` when there was nothing to reset, and also when saving failed.
    pub fn reset_warn<S: Store>(db: &mut Database<S>, chat: &PyValue, user: &PyValue) -> Out {
        let mut held = db.hold(KEY, dict())?;
        if with_item(held.value(), chat, |users| pop(users, user)).is_err() {
            return NONE;
        }
        held.save().or(NONE)
    }
}

/// What `KeyManager(key, cast)` casts a stored value to. The code base only ever passes `list`.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Cast {
    None,
    List,
}

/// `KeyManager` of `pyUltroid/dB/base.py`: one key holding a list (or a dict) of items.
#[derive(Clone, Copy, Debug)]
pub struct KeyManager<'a> {
    pub key: &'a str,
    pub cast: Cast,
}

/// `type(item)()`: the empty value of an item's type.
fn empty_like(item: &PyValue) -> PyValue {
    match item {
        PyValue::None => PyValue::None,
        PyValue::Ellipsis => PyValue::Ellipsis,
        PyValue::Bool(_) => flag(false),
        PyValue::Int(_) => PyValue::int(0),
        PyValue::Float(_) => PyValue::Float(0.0),
        PyValue::Complex(..) => PyValue::Complex(0.0, 0.0),
        PyValue::Str(_) | PyValue::Surrogates(_) => PyValue::str(""),
        PyValue::Bytes(_) => PyValue::Bytes(Vec::new()),
        PyValue::List(_) => list(),
        PyValue::Tuple(_) => PyValue::Tuple(Vec::new()),
        PyValue::Set(_) => PyValue::Set(Default::default()),
        PyValue::Dict(_) => dict(),
    }
}

impl KeyManager<'_> {
    /// `get()`. With `cast=list`, a stored value that is no list comes back as a list of it.
    pub fn get<S: Store>(&self, db: &mut Database<S>) -> Out {
        let data = db.get_key(self.key)?;
        Ok(match (self.cast, data) {
            (Cast::List, PyValue::None) => list(),
            (Cast::List, PyValue::List(_)) | (Cast::None, _) if data.truthy() => data.clone(),
            (Cast::List, PyValue::List(_)) => list(),
            (Cast::List, other) => PyValue::List(vec![other.clone()]),
            (Cast::None, _) => PyValue::None,
        })
    }

    pub fn get_child<S: Store>(&self, db: &mut Database<S>, key: &PyValue) -> Out {
        item(&self.get(db)?, key).map(Cow::into_owned)
    }

    pub fn count<S: Store>(&self, db: &mut Database<S>) -> Out {
        len(&self.get(db)?).map(PyValue::int)
    }

    pub fn contains<S: Store>(&self, db: &mut Database<S>, item: &PyValue) -> Out {
        contains(&self.get(db)?, item).map(flag)
    }

    /// Adds an item to a list unless it is there, or the items of a dict to a dict. Anything
    /// else is left alone without a word.
    pub fn add<S: Store>(&self, db: &mut Database<S>, item: &PyValue) -> Out {
        let mut content = self.get(db)?;
        if content == PyValue::None {
            content = empty_like(item);
        }
        match (&mut content, item) {
            (PyValue::Dict(held), PyValue::Dict(more)) => {
                for (key, value) in more.iter() {
                    held.set(key.clone(), value.clone())?;
                }
            }
            (PyValue::List(held), _) if !held.iter().any(|member| member.py_eq(item)) => {
                held.push(item.clone());
            }
            _ => return NONE,
        }
        db.set_key(self.key, content)?;
        NONE
    }

    /// Removes an item from a list, or a key with a truthy value from a dict.
    pub fn remove<S: Store>(&self, db: &mut Database<S>, item: &PyValue) -> Out {
        let mut content = self.get(db)?;
        let in_list = matches!(&content, PyValue::List(_)) && contains(&content, item)?;
        if in_list {
            remove(&mut content, item)?;
        } else if matches!(&content, PyValue::Dict(_)) && found(&content, item)?.is_some() {
            pop(&mut content, item)?;
        } else {
            return NONE;
        }
        db.set_key(self.key, content)?;
        NONE
    }
}

impl<'a> KeyManager<'a> {
    /// A manager from the Python values of its arguments: `cast` is `None` or the name `list`.
    pub fn from_values(key: &'a PyValue, cast: &PyValue) -> PyResult<Self> {
        let PyValue::Str(key) = key else {
            return Err(PyError::type_error("a database key is text"));
        };
        cast.key()?;
        let cast = match cast {
            PyValue::None => Cast::None,
            PyValue::Str(name) if name == "list" => Cast::List,
            other => return Err(PyError::new("KeyError", format!("no cast {other:?}"))),
        };
        Ok(Self { key, cast })
    }
}
