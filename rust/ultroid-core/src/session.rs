//! Session strings: `validate_session` of `pyUltroid/startup/connections.py` and the
//! `StringSession` of Telethon it returns. Proven in `rust/session-rs`.
//!
//! A Telethon string session is the digit `1` followed by URL-safe base64 of the data centre
//! (one byte), its address (4 or 16 bytes), its port (two bytes) and the 256-byte key. Ultroid
//! also takes the three layouts Pyrogram has used, and makes a Telethon session of each.

use base64::Engine;
use base64::engine::general_purpose::URL_SAFE;
use std::fmt;
use std::net::{IpAddr, Ipv4Addr, Ipv6Addr};

/// The version digit every Telethon string session starts with.
pub const CURRENT_VERSION: char = '1';
/// Bytes in an authorization key.
pub const KEY_LEN: usize = 256;
/// The address Ultroid gives a session converted from Pyrogram, by data centre.
const DC_IPV4: [(u8, Ipv4Addr); 5] = [
    (1, Ipv4Addr::new(149, 154, 175, 53)),
    (2, Ipv4Addr::new(149, 154, 167, 51)),
    (3, Ipv4Addr::new(149, 154, 175, 100)),
    (4, Ipv4Addr::new(149, 154, 167, 91)),
    (5, Ipv4Addr::new(91, 108, 56, 130)),
];

/// Why a string is no session. Each is the exception the Python code raises at the same point.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum SessionError {
    /// `ValueError`: the first character is not the version digit.
    NotThisVersion,
    /// `ValueError`: base64 text has to be ASCII.
    NotAscii,
    /// `binascii.Error`: the base64 text is cut short.
    BadBase64,
    /// `struct.error`: the decoded bytes are not the length of the layout.
    WrongLength,
    /// `KeyError`: a Pyrogram session of a data centre Ultroid has no address for.
    UnknownDataCentre(u8),
}

impl SessionError {
    /// The exception as Python names it: module, dot, class.
    pub fn python_name(&self) -> &'static str {
        match self {
            Self::NotThisVersion | Self::NotAscii => "builtins.ValueError",
            Self::BadBase64 => "binascii.Error",
            Self::WrongLength => "struct.error",
            Self::UnknownDataCentre(_) => "builtins.KeyError",
        }
    }
}

impl fmt::Display for SessionError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::NotThisVersion => f.write_str("not a valid string session"),
            Self::NotAscii => f.write_str("a session string holds only ASCII characters"),
            Self::BadBase64 => f.write_str("the session string is cut short"),
            Self::WrongLength => f.write_str("the session string has the wrong length"),
            Self::UnknownDataCentre(dc) => write!(f, "no address for data centre {dc}"),
        }
    }
}

impl std::error::Error for SessionError {}

/// `base64.urlsafe_b64decode(text)` as Python does it: `-` and `_` stand for `+` and `/`, any
/// other character outside the alphabet is skipped, and nothing after complete padding is read.
/// Stricter decoders refuse strings Python accepts, such as one with a line break in it.
pub fn urlsafe_b64decode(text: &str) -> Result<Vec<u8>, SessionError> {
    if !text.is_ascii() {
        return Err(SessionError::NotAscii);
    }
    let mut out = Vec::with_capacity(text.len() / 4 * 3);
    let (mut quad, mut left, mut pads) = (0_u8, 0_u8, 0_u8);
    for byte in text.bytes() {
        let six = match byte {
            b'=' => {
                // Padding ends the data once it completes a group of four.
                if quad >= 2 {
                    pads += 1;
                    if quad + pads >= 4 {
                        return Ok(out);
                    }
                }
                continue;
            }
            b'A'..=b'Z' => byte - b'A',
            b'a'..=b'z' => byte - b'a' + 26,
            b'0'..=b'9' => byte - b'0' + 52,
            b'+' | b'-' => 62,
            b'/' | b'_' => 63,
            _ => continue,
        };
        pads = 0;
        match quad {
            0 => {}
            1 => out.push(left << 2 | six >> 4),
            2 => out.push(left << 4 | six >> 2),
            _ => out.push(left << 6 | six),
        }
        left = six;
        quad = (quad + 1) % 4;
    }
    if quad == 0 {
        Ok(out)
    } else {
        Err(SessionError::BadBase64)
    }
}

/// What a string session holds: Telethon's `StringSession`.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct StringSession {
    pub dc_id: u8,
    /// `None` only in the session made from no string at all.
    pub server_address: Option<IpAddr>,
    pub port: Option<u16>,
    /// `None` when the key is all zeros, which Telethon takes for no key.
    pub auth_key: Option<[u8; KEY_LEN]>,
}

impl StringSession {
    /// `StringSession()`: no data centre, no key.
    pub fn empty() -> Self {
        Self {
            dc_id: 0,
            server_address: None,
            port: None,
            auth_key: None,
        }
    }

    /// `StringSession(text)`. The address is taken to be IPv4 when exactly 352 characters
    /// follow the version digit, and IPv6 otherwise, whatever those characters are.
    pub fn parse(text: &str) -> Result<Self, SessionError> {
        let Some(first) = text.chars().next() else {
            return Ok(Self::empty());
        };
        if first != CURRENT_VERSION {
            return Err(SessionError::NotThisVersion);
        }
        let body = &text[first.len_utf8()..];
        let address_len = if body.chars().count() == 352 { 4 } else { 16 };
        let bytes = urlsafe_b64decode(body)?;
        // `>B{}sH256s`: data centre, address, port, key.
        if bytes.len() != 1 + address_len + 2 + KEY_LEN {
            return Err(SessionError::WrongLength);
        }
        let (head, key) = bytes.split_at(bytes.len() - KEY_LEN);
        let (address, port) = head[1..].split_at(address_len);
        let address = match <[u8; 4]>::try_from(address) {
            Ok(v4) => IpAddr::V4(Ipv4Addr::from(v4)),
            Err(_) => {
                let v6 = <[u8; 16]>::try_from(address).map_err(|_| SessionError::WrongLength)?;
                IpAddr::V6(Ipv6Addr::from(v6))
            }
        };
        let key = <[u8; KEY_LEN]>::try_from(key).map_err(|_| SessionError::WrongLength)?;
        Ok(Self {
            dc_id: head[0],
            server_address: Some(address),
            port: Some(u16::from_be_bytes([port[0], port[1]])),
            auth_key: key.iter().any(|&byte| byte != 0).then_some(key),
        })
    }

    /// A session at one of Telegram's data centres, the way Ultroid builds one from a Pyrogram
    /// session: the data centre's IPv4 address and port 443.
    pub fn at_data_centre(dc_id: u8, key: [u8; KEY_LEN]) -> Result<Self, SessionError> {
        let address = DC_IPV4.iter().find(|(dc, _)| *dc == dc_id);
        let (_, address) = address.ok_or(SessionError::UnknownDataCentre(dc_id))?;
        Ok(Self {
            dc_id,
            server_address: Some(IpAddr::V4(*address)),
            port: Some(443),
            auth_key: key.iter().any(|&byte| byte != 0).then_some(key),
        })
    }

    /// `save()`: the string for this session, or the empty string when there is no key.
    pub fn save(&self) -> String {
        let (Some(key), Some(address), Some(port)) =
            (self.auth_key, self.server_address, self.port)
        else {
            return String::new();
        };
        let mut bytes = vec![self.dc_id];
        match address {
            IpAddr::V4(v4) => bytes.extend(v4.octets()),
            IpAddr::V6(v6) => bytes.extend(v6.octets()),
        }
        bytes.extend(port.to_be_bytes());
        bytes.extend(key);
        format!("{CURRENT_VERSION}{}", URL_SAFE.encode(bytes))
    }
}

/// What `validate_session` did with a string.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Checked {
    /// The session to log in with, when the string was one.
    pub session: Option<StringSession>,
    /// The keys of the messages logged: `py_c1` (wrong string session), `py_c2` (none given).
    pub logged: Vec<&'static str>,
    /// Whether the original calls `sys.exit()` at this point.
    pub exits: bool,
}

/// Where the data centre and the key sit in a Pyrogram session of a given length in characters:
/// the offset of the key, and the length in bytes of the whole.
fn pyrogram_layout(characters: usize) -> Option<(usize, usize)> {
    match characters {
        351 => Some((2, 263)), // >B?256sI?   dc, test, key, user id (32 bits), bot
        356 => Some((2, 267)), // >B?256sQ?   the same with a 64-bit user id
        362 => Some((6, 271)), // >BI?256sQ?  dc, api id, test, key, user id, bot
        _ => None,
    }
}

/// `str.strip()`'s idea of a blank, for the characters a session string can meet.
fn is_blank(c: char) -> bool {
    matches!(c, '\t'..='\r' | '\u{1c}'..=' ' | '\u{85}' | '\u{a0}' | '\u{1680}' | '\u{2000}'..='\u{200a}')
        || matches!(
            c,
            '\u{2028}' | '\u{2029}' | '\u{202f}' | '\u{205f}' | '\u{3000}'
        )
}

/// `validate_session(session, _exit=leave)`.
///
/// A string that starts with `1` is a Telethon session: it must be 353 characters once blanks
/// around it are dropped, or the program exits, whatever `leave` says. It is then read with the
/// blanks still on, so a session with a line break after it passes the check and fails to
/// parse. A string of 351, 356 or 362 characters is a Pyrogram session. Anything else is logged
/// as a wrong session, and then as a missing one too.
pub fn validate_session(session: Option<&str>, leave: bool) -> Result<Checked, SessionError> {
    let mut logged = Vec::new();
    let done = |session, logged, exits| {
        Ok(Checked {
            session,
            logged,
            exits,
        })
    };
    let session = session.unwrap_or_default();
    if session.starts_with(CURRENT_VERSION) {
        if session.trim_matches(is_blank).chars().count() != 353 {
            logged.push("py_c1");
            return done(None, logged, true);
        }
        return done(Some(StringSession::parse(session)?), logged, false);
    }
    let characters = session.chars().count();
    if let Some((key_at, length)) = pyrogram_layout(characters) {
        // Pyrogram leaves the padding off; the original puts it back before decoding.
        let padding = "=".repeat((4 - characters % 4) % 4);
        let bytes = urlsafe_b64decode(&format!("{session}{padding}"))?;
        let key = bytes
            .get(key_at..key_at + KEY_LEN)
            .filter(|_| bytes.len() == length);
        let key = key.and_then(|key| <[u8; KEY_LEN]>::try_from(key).ok());
        let key = key.ok_or(SessionError::WrongLength)?;
        return done(
            Some(StringSession::at_data_centre(bytes[0], key)?),
            logged,
            false,
        );
    }
    if !session.is_empty() {
        logged.push("py_c1");
        if leave {
            return done(None, logged, true);
        }
    }
    logged.push("py_c2");
    done(None, logged, leave)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn key() -> [u8; KEY_LEN] {
        let mut key = [0; KEY_LEN];
        for (at, byte) in key.iter_mut().enumerate() {
            *byte = u8::try_from(at % 251 + 1).unwrap();
        }
        key
    }

    fn telethon(dc: u8, address: &[u8], port: u16) -> String {
        let mut bytes = vec![dc];
        bytes.extend(address);
        bytes.extend(port.to_be_bytes());
        bytes.extend(key());
        format!("1{}", URL_SAFE.encode(bytes))
    }

    #[test]
    fn decodes_base64_the_way_python_does() {
        // Expected values are CPython's `base64.urlsafe_b64decode`.
        assert_eq!(urlsafe_b64decode("aGk=").unwrap(), b"hi");
        assert_eq!(
            urlsafe_b64decode("aGk").unwrap_err(),
            SessionError::BadBase64
        );
        assert_eq!(urlsafe_b64decode("a").unwrap_err(), SessionError::BadBase64);
        assert_eq!(urlsafe_b64decode("aG\nk=\n").unwrap(), b"hi");
        assert_eq!(urlsafe_b64decode("aGk=aGk=").unwrap(), b"hi");
        assert_eq!(urlsafe_b64decode("a=Gk=").unwrap(), b"hi");
        assert_eq!(urlsafe_b64decode("-_+/").unwrap(), [0xfb, 0xff, 0xbf]);
        assert_eq!(urlsafe_b64decode("").unwrap(), b"");
        assert_eq!(urlsafe_b64decode("====").unwrap(), b"");
        assert_eq!(urlsafe_b64decode("é").unwrap_err(), SessionError::NotAscii);
    }

    #[test]
    fn a_telethon_session_round_trips() {
        let text = telethon(2, &[149, 154, 167, 51], 443);
        assert_eq!(text.chars().count(), 353);
        let session = StringSession::parse(&text).unwrap();
        assert_eq!(session.dc_id, 2);
        assert_eq!(
            session.server_address.unwrap().to_string(),
            "149.154.167.51"
        );
        assert_eq!(session.port, Some(443));
        assert_eq!(session.auth_key, Some(key()));
        assert_eq!(session.save(), text);
        let checked = validate_session(Some(&text), true).unwrap();
        assert_eq!((checked.session, checked.exits), (Some(session), false));
    }

    #[test]
    fn an_ipv6_session_parses_but_does_not_validate() {
        let mut address = [0; 16];
        address[10..].copy_from_slice(&[0xff, 0xff, 1, 2, 3, 4]);
        let text = telethon(2, &address, 443);
        let session = StringSession::parse(&text).unwrap();
        assert_eq!(
            session.server_address.unwrap().to_string(),
            "::ffff:1.2.3.4"
        );
        assert_eq!(session.save(), text);
        let checked = validate_session(Some(&text), false).unwrap();
        assert_eq!(
            (checked.session, checked.logged, checked.exits),
            (None, vec!["py_c1"], true)
        );
    }

    #[test]
    fn blanks_around_a_session() {
        let text = telethon(2, &[149, 154, 167, 51], 443);
        // A line break after it passes the length check and then fails to parse.
        let after = validate_session(Some(&format!("{text}\n")), true);
        assert_eq!(after.unwrap_err(), SessionError::WrongLength);
        // A blank before it means it does not start with the version digit.
        let before = validate_session(Some(&format!(" {text}")), false).unwrap();
        assert_eq!(
            (before.logged, before.exits),
            (vec!["py_c1", "py_c2"], false)
        );
    }

    #[test]
    fn nothing_and_nonsense() {
        let none = validate_session(None, true).unwrap();
        assert_eq!(
            (none.session, none.logged, none.exits),
            (None, vec!["py_c2"], true)
        );
        let empty = validate_session(Some(""), false).unwrap();
        assert_eq!((empty.logged, empty.exits), (vec!["py_c2"], false));
        let wrong = validate_session(Some("hello"), true).unwrap();
        assert_eq!((wrong.logged, wrong.exits), (vec!["py_c1"], true));
        assert_eq!(StringSession::parse("").unwrap(), StringSession::empty());
        assert_eq!(
            StringSession::parse("2abc").unwrap_err(),
            SessionError::NotThisVersion
        );
        assert_eq!(
            StringSession::parse("1abc").unwrap_err(),
            SessionError::BadBase64
        );
        assert_eq!(
            StringSession::parse("1").unwrap_err(),
            SessionError::WrongLength
        );
    }

    #[test]
    fn pyrogram_sessions_are_converted() {
        let pack = |parts: &[&[u8]]| {
            URL_SAFE
                .encode(parts.concat())
                .trim_end_matches('=')
                .to_string()
        };
        let old = pack(&[&[4, 0], &key(), &123_456_u32.to_be_bytes(), &[0]]);
        let newer = pack(&[&[5, 1], &key(), &(1_u64 << 40).to_be_bytes(), &[1]]);
        let newest = pack(&[
            &[1],
            &6_u32.to_be_bytes(),
            &[0],
            &key(),
            &777_u64.to_be_bytes(),
            &[0],
        ]);
        for (text, length, dc, address) in [
            (&old, 351, 4, "149.154.167.91"),
            (&newer, 356, 5, "91.108.56.130"),
            (&newest, 362, 1, "149.154.175.53"),
        ] {
            assert_eq!(text.len(), length);
            let session = validate_session(Some(text), true).unwrap().session.unwrap();
            assert_eq!(session.dc_id, dc);
            assert_eq!(session.server_address.unwrap().to_string(), address);
            assert_eq!((session.port, session.auth_key), (Some(443), Some(key())));
            assert_eq!(StringSession::parse(&session.save()).unwrap(), session);
        }
        let unknown = pack(&[&[9, 0], &key(), &1_u32.to_be_bytes(), &[0]]);
        let error = validate_session(Some(&unknown), true).unwrap_err();
        assert_eq!(error, SessionError::UnknownDataCentre(9));
        // 351 characters that decode to 263 bytes of zeros: data centre 0 is not one of the five.
        let zeros = validate_session(Some(&"A".repeat(351)), true).unwrap_err();
        assert_eq!(zeros, SessionError::UnknownDataCentre(0));
        // 351 characters of which none is base64: nothing decodes.
        let noise = validate_session(Some(&"!".repeat(351)), true).unwrap_err();
        assert_eq!(noise, SessionError::WrongLength);
    }
}
