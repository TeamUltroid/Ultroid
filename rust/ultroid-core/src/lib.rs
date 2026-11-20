//! Ultroid's start-up logic in Rust: the parts of `pyUltroid/startup` and its neighbours that
//! take data and give data, with no Telegram and no network in them.
//!
//! - [`session`]: what a `SESSION` string is: Telethon's string session, and the Pyrogram
//!   strings Ultroid converts on the way in.
//! - [`command`]: how a command is recognised: the pattern a plugin registers, the handler
//!   prefix, and what Python's `re` makes of the two on a message.
//!
//! Each part is proven against the Python original case by case, in the bridge crate named in
//! its module.
//!
//! ```
//! use ultroid_core::session::validate_session;
//!
//! // No session at all: the original logs `py_c2` and leaves.
//! let checked = validate_session(None, true)?;
//! assert_eq!((checked.session, checked.logged, checked.exits), (None, vec!["py_c2"], true));
//! # Ok::<(), ultroid_core::session::SessionError>(())
//! ```

#![forbid(unsafe_code)]

pub mod command;
pub mod session;
mod tables;
