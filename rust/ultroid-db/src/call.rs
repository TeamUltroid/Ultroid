//! Calls the database by the names Python code knows: `udB.get_key`, `notes_db.add_note`,
//! `KeyManager.add`. Arguments and results are Python values, which is the form a bridge to
//! Python, a test or a scenario needs. Rust code calls [`crate::access`] directly.

use crate::access::*;
use crate::clock::DateTime;
use crate::database::{Database, Store};
use crate::value::{PyError, PyResult, PyValue};

fn wrong_count(name: &str, given: usize) -> PyError {
    PyError::type_error(format!("{name}() does not take {given} arguments"))
}

/// A database key from a Python value: only text is a key here.
fn text(key: &PyValue) -> PyResult<&str> {
    match key {
        PyValue::Str(key) => Ok(key),
        other => Err(PyError::type_error(format!(
            "a database key is text, not '{}'",
            other.type_name()
        ))),
    }
}

/// One arm per function: its Python name, its arguments, and the call.
macro_rules! route {
    ($name:ident, $args:ident; $($label:literal => [$($arg:ident),*] $call:expr,)*) => {
        match $name {
            $($label => match $args {
                [$($arg),*] => $call,
                _ => Err(wrong_count($label, $args.len())),
            },)*
            _ => Err(PyError::new("KeyError", format!("no function {}", $name))),
        }
    };
}

fn manager<S: Store>(db: &mut Database<S>, name: &str, args: &[PyValue]) -> PyResult<PyValue> {
    let [key, cast, rest @ ..] = args else {
        return Err(wrong_count(name, args.len()));
    };
    let keys = KeyManager::from_values(key, cast)?;
    route! { name, rest;
        "KeyManager.get" => [] keys.get(db),
        "KeyManager.count" => [] keys.count(db),
        "KeyManager.get_child" => [key] keys.get_child(db, key),
        "KeyManager.add" => [item] keys.add(db, item),
        "KeyManager.remove" => [item] keys.remove(db, item),
        "KeyManager.contains" => [item] keys.contains(db, item),
    }
}

/// Calls `name` with `args`. `now` is the moment the AFK functions take for the present.
/// An unknown name is a `KeyError`, a wrong number of arguments a `TypeError`.
pub fn call<S: Store>(
    db: &mut Database<S>,
    now: &DateTime,
    name: &str,
    args: &[PyValue],
) -> PyResult<PyValue> {
    if name.starts_with("KeyManager.") {
        return manager(db, name, args);
    }
    // These two may be given the name of the key to read.
    if let "greetings_db.get_stuff" | "nsfw_db.get_stuff" = name {
        let key = match args {
            [] => None,
            [key] => Some(text(key)?),
            _ => return Err(wrong_count(name, args.len())),
        };
        return if name == "nsfw_db.get_stuff" {
            nsfw_db::get_stuff(db, key)
        } else {
            greetings_db::get_stuff(db, key)
        };
    }
    let done = |result: PyResult<()>, value: PyValue| result.map(|()| value);
    route! { name, args;
        "udB.get_key" => [key] db.get_key(text(key)?).cloned(),
        "udB.set_key" => [key, value] done(db.set_key(text(key)?, value.clone()), PyValue::Bool(true)),
        "udB.del_key" => [key] done(db.del_key(text(key)?), PyValue::Bool(true)),
        "udB.rename" => [from, to] {
            let (from, to) = (text(from)?, text(to)?);
            db.rename(from, to).map(|moved| PyValue::int(u8::from(!moved)))
        },
        "udB.keys" => [] db.keys().map(|keys| PyValue::List(keys.into_iter().map(PyValue::Str).collect())),
        "udB.re_cache" => [] done(db.re_cache(), PyValue::None),

        "afk_db.get_stuff" => [] afk_db::get_stuff(db),
        "afk_db.add_afk" => [msg, media_type, media] afk_db::add_afk(db, now, msg, media_type, media),
        "afk_db.is_afk" => [] afk_db::is_afk(db, now),
        "afk_db.del_afk" => [] afk_db::del_afk(db),

        "antiflood_db.get_flood" => [] antiflood_db::get_flood(db),
        "antiflood_db.set_flood" => [chat_id, limit] antiflood_db::set_flood(db, chat_id, limit),
        "antiflood_db.get_flood_limit" => [chat_id] antiflood_db::get_flood_limit(db, chat_id),
        "antiflood_db.rem_flood" => [chat_id] antiflood_db::rem_flood(db, chat_id),

        "asstcmd_db.get_stuff" => [] asstcmd_db::get_stuff(db),
        "asstcmd_db.add_cmd" => [cmd, msg, media, button] asstcmd_db::add_cmd(db, cmd, msg, media, button),
        "asstcmd_db.rem_cmd" => [cmd] asstcmd_db::rem_cmd(db, cmd),
        "asstcmd_db.cmd_reply" => [cmd] asstcmd_db::cmd_reply(db, cmd),
        "asstcmd_db.list_cmds" => [] asstcmd_db::list_cmds(db),

        "blacklist_chat_db.add_black_chat" => [chat_id] blacklist_chat_db::add_black_chat(db, chat_id),
        "blacklist_chat_db.rem_black_chat" => [chat_id] blacklist_chat_db::rem_black_chat(db, chat_id),

        "blacklist_db.get_stuff" => [] blacklist_db::get_stuff(db),
        "blacklist_db.add_blacklist" => [chat, word] blacklist_db::add_blacklist(db, chat, word),
        "blacklist_db.rem_blacklist" => [chat, word] blacklist_db::rem_blacklist(db, chat, word),
        "blacklist_db.list_blacklist" => [chat] blacklist_db::list_blacklist(db, chat),
        "blacklist_db.get_blacklist" => [chat] blacklist_db::get_blacklist(db, chat),

        "botchat_db.get_stuff" => [] botchat_db::get_stuff(db),
        "botchat_db.add_stuff" => [msg_id, user_id] botchat_db::add_stuff(db, msg_id, user_id),
        "botchat_db.get_who" => [msg_id] botchat_db::get_who(db, msg_id),
        "botchat_db.tag_add" => [msg, chat, user] botchat_db::tag_add(db, msg, chat, user),
        "botchat_db.who_tag" => [msg] botchat_db::who_tag(db, msg),

        "echo_db.get_stuff" => [] echo_db::get_stuff(db),
        "echo_db.add_echo" => [chat, user] echo_db::add_echo(db, chat, user),
        "echo_db.rem_echo" => [chat, user] echo_db::rem_echo(db, chat, user),
        "echo_db.check_echo" => [chat, user] echo_db::check_echo(db, chat, user),
        "echo_db.list_echo" => [chat] echo_db::list_echo(db, chat),

        "filestore_db.get_stored" => [] filestore_db::get_stored(db),
        "filestore_db.store_msg" => [hash, msg_id] filestore_db::store_msg(db, hash, msg_id),
        "filestore_db.list_all_stored_msgs" => [] filestore_db::list_all_stored_msgs(db),
        "filestore_db.get_stored_msg" => [hash] filestore_db::get_stored_msg(db, hash),
        "filestore_db.del_stored" => [hash] filestore_db::del_stored(db, hash),

        "filter_db.get_stuff" => [] filter_db::get_stuff(db),
        "filter_db.add_filter" => [chat, word, msg, media, button] filter_db::add_filter(db, chat, word, msg, media, button),
        "filter_db.rem_filter" => [chat, word] filter_db::rem_filter(db, chat, word),
        "filter_db.rem_all_filter" => [chat] filter_db::rem_all_filter(db, chat),
        "filter_db.get_filter" => [chat] filter_db::get_filter(db, chat),
        "filter_db.list_filter" => [chat] filter_db::list_filter(db, chat),

        "forcesub_db.get_chats" => [] forcesub_db::get_chats(db),
        "forcesub_db.add_forcesub" => [chat_id, chattojoin] forcesub_db::add_forcesub(db, chat_id, chattojoin),
        "forcesub_db.get_forcesetting" => [chat_id] forcesub_db::get_forcesetting(db, chat_id),
        "forcesub_db.rem_forcesub" => [chat_id] forcesub_db::rem_forcesub(db, chat_id),

        "gban_mute_db.list_gbanned" => [] gban_mute_db::list_gbanned(db),
        "gban_mute_db.gban" => [user, reason] gban_mute_db::gban(db, user, reason),
        "gban_mute_db.ungban" => [user] gban_mute_db::ungban(db, user),
        "gban_mute_db.is_gbanned" => [user] gban_mute_db::is_gbanned(db, user),
        "gban_mute_db.gmute" => [user] gban_mute_db::gmute(db, user),
        "gban_mute_db.ungmute" => [user] gban_mute_db::ungmute(db, user),
        "gban_mute_db.is_gmuted" => [user] gban_mute_db::is_gmuted(db, user),
        "gban_mute_db.list_gmuted" => [] gban_mute_db::list_gmuted(db),

        "greetings_db.add_welcome" => [chat, msg, media, button] greetings_db::add_welcome(db, chat, msg, media, button),
        "greetings_db.get_welcome" => [chat] greetings_db::get_welcome(db, chat),
        "greetings_db.delete_welcome" => [chat] greetings_db::delete_welcome(db, chat),
        "greetings_db.add_goodbye" => [chat, msg, media, button] greetings_db::add_goodbye(db, chat, msg, media, button),
        "greetings_db.get_goodbye" => [chat] greetings_db::get_goodbye(db, chat),
        "greetings_db.delete_goodbye" => [chat] greetings_db::delete_goodbye(db, chat),
        "greetings_db.add_thanks" => [chat] greetings_db::add_thanks(db, chat),
        "greetings_db.remove_thanks" => [chat] greetings_db::remove_thanks(db, chat),
        "greetings_db.must_thank" => [chat] greetings_db::must_thank(db, chat),

        "mute_db.get_muted" => [] mute_db::get_muted(db),
        "mute_db.mute" => [chat, id] mute_db::mute(db, chat, id),
        "mute_db.unmute" => [chat, id] mute_db::unmute(db, chat, id),
        "mute_db.is_muted" => [chat, id] mute_db::is_muted(db, chat, id),

        "notes_db.get_stuff" => [] notes_db::get_stuff(db),
        "notes_db.add_note" => [chat, word, msg, media, button] notes_db::add_note(db, chat, word, msg, media, button),
        "notes_db.rem_note" => [chat, word] notes_db::rem_note(db, chat, word),
        "notes_db.rem_all_note" => [chat] notes_db::rem_all_note(db, chat),
        "notes_db.get_notes" => [chat, word] notes_db::get_notes(db, chat, word),
        "notes_db.list_note" => [chat] notes_db::list_note(db, chat),

        "nsfw_db.nsfw_chat" => [chat, action] nsfw_db::nsfw_chat(db, chat, action),
        "nsfw_db.rem_nsfw" => [chat] nsfw_db::rem_nsfw(db, chat),
        "nsfw_db.is_nsfw" => [chat] nsfw_db::is_nsfw(db, chat),
        "nsfw_db.profan_chat" => [chat, action] nsfw_db::profan_chat(db, chat, action),
        "nsfw_db.rem_profan" => [chat] nsfw_db::rem_profan(db, chat),
        "nsfw_db.is_profan" => [chat] nsfw_db::is_profan(db, chat),

        "snips_db.get_all_snips" => [] snips_db::get_all_snips(db),
        "snips_db.add_snip" => [word, msg, media, button] snips_db::add_snip(db, word, msg, media, button),
        "snips_db.rem_snip" => [word] snips_db::rem_snip(db, word),
        "snips_db.get_snips" => [word] snips_db::get_snips(db, word),
        "snips_db.list_snip" => [] snips_db::list_snip(db),

        "vc_sudos.get_vcsudos" => [] vc_sudos::get_vcsudos(db),
        "vc_sudos.is_vcsudo" => [id] vc_sudos::is_vcsudo(db, id),
        "vc_sudos.add_vcsudo" => [id] vc_sudos::add_vcsudo(db, id),
        "vc_sudos.del_vcsudo" => [id] vc_sudos::del_vcsudo(db, id),

        "warn_db.get_stuff" => [] warn_db::get_stuff(db),
        "warn_db.add_warn" => [chat, user, count, reason] warn_db::add_warn(db, chat, user, count, reason),
        "warn_db.warns" => [chat, user] warn_db::warns(db, chat, user),
        "warn_db.reset_warn" => [chat, user] warn_db::reset_warn(db, chat, user),
    }
}
