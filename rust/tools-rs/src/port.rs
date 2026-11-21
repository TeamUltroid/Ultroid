//! The Rust port of `pyUltroid/fns/tools.py`.
//!
//! Only the functions that take text or numbers and return data are ported. Everything in that
//! file that reaches the network, the filesystem, a subprocess or Telegram stays in Python
//! (`rust-anything.json` lists each one with its reason).

#![forbid(unsafe_code)]

use crate::pynum::Num;
use regex::Regex;
use serde_json::{Value, json};
use std::sync::LazyLock;

/// Rows of buttons as `get_msg_button` returns them; a button is `[label, url]`.
type ButtonRows = Vec<Vec<Vec<String>>>;

fn pattern(source: &str) -> Regex {
    // INFALLIBLE: every pattern below is a constant that parses.
    Regex::new(source).expect("constant pattern")
}

static BUTTON: LazyLock<Regex> = LazyLock::new(|| pattern(r"\[(.*?)\|(.*?)\]"));
static MARKUP: LazyLock<Regex> = LazyLock::new(|| pattern(r"\[.+?\|.+?\]"));
static MESSAGE_LINK: LazyLock<Regex> = LazyLock::new(|| pattern(r"t\.me/(c/)?([^/]+)/(\d+)"));
static OPEN_MESSAGE: LazyLock<Regex> = LazyLock::new(|| pattern(r"user_id=(\d+)&message_id=(\d+)"));
static DIGIT: LazyLock<Regex> = LazyLock::new(|| pattern(r"^\d$"));

/// The parts `cmd_regex_replace` removes, in the original's order. The order matters: by the
/// time `?(\d+)` is tried the brackets are gone, so it never matches.
const PATTERN_NOISE: [&str; 11] = [
    "$",
    "?(.*)",
    "(.*)",
    "(?: |)",
    "| ",
    "( |)",
    "?((.|//)*)",
    "?P<shortname>\\w+",
    "(",
    ")",
    "?(\\d+)",
];

/// Python's `str.strip()`: Unicode whitespace plus the four ASCII separators U+001C to U+001F.
fn py_strip(text: &str) -> &str {
    text.trim_matches(|c: char| c.is_whitespace() || ('\u{1c}'..='\u{1f}').contains(&c))
}

fn is_decimal(c: char) -> bool {
    DIGIT.is_match(c.encode_utf8(&mut [0; 4]))
}

/// The value of a decimal digit of any script. Unicode lays digits out in runs of ten, so the
/// distance from the start of the run gives the value.
fn decimal_value(c: char) -> Option<u8> {
    if let Some(digit) = c.to_digit(10) {
        return u8::try_from(digit).ok();
    }
    if !is_decimal(c) {
        return None;
    }
    let mut start = u32::from(c);
    while char::from_u32(start - 1).is_some_and(is_decimal) {
        start -= 1;
    }
    u8::try_from((u32::from(c) - start) % 10).ok()
}

/// Python's `int(text)`: whitespace around, an optional sign, decimal digits of any script and
/// single underscores between digits. Python ints have no size limit, so a value beyond 64 bits
/// travels as `$int`.
fn py_int(text: &str) -> Result<Value, String> {
    let invalid = || format!("ValueError: invalid literal for int() with base 10: {text:?}");
    let body = text.trim_matches(char::is_whitespace);
    let (negative, digits) = match body.strip_prefix('-') {
        Some(rest) => (true, rest),
        None => (false, body.strip_prefix('+').unwrap_or(body)),
    };
    let mut value = String::new();
    let mut after_digit = false;
    for c in digits.chars() {
        match decimal_value(c) {
            Some(digit) => {
                value.push(char::from(b'0' + digit));
                after_digit = true;
            }
            None if c == '_' && after_digit => after_digit = false,
            None => return Err(invalid()),
        }
    }
    if !after_digit {
        return Err(invalid());
    }
    let value = match value.trim_start_matches('0') {
        "" => "0".to_string(),
        value if negative => format!("-{value}"),
        value => value.to_string(),
    };
    Ok(value
        .parse::<i64>()
        .map_or_else(|_| json!({ "$int": value }), |small| json!(small)))
}

/// Python's `repr` of a float: the shortest digits that read back the same, in exponent form
/// below 1e-4 and from 1e16 up.
fn repr_float(x: f64) -> String {
    if x.is_nan() {
        return "nan".into();
    }
    if x.is_infinite() {
        return if x > 0.0 { "inf" } else { "-inf" }.into();
    }
    let size = x.abs();
    let mut scientific = format!("{size:e}");
    // 16.0000152587890625 reads back from both ...062 and ...063. Rust prints the upper one;
    // CPython rounds the exact value half to even, which is what a fixed precision does.
    let count = scientific
        .bytes()
        .take_while(|&b| b != b'e')
        .filter(u8::is_ascii_digit)
        .count();
    let rounded = format!("{:.*e}", count.saturating_sub(1), size);
    if rounded.parse() == Ok(size) {
        scientific = rounded;
    }
    let (mantissa, exponent) = scientific.split_once('e').unwrap_or((&scientific, "0"));
    let exponent: i32 = exponent.parse().unwrap_or(0);
    let digits: String = mantissa.chars().filter(char::is_ascii_digit).collect();
    let body = if !(-4..16).contains(&exponent) {
        let (first, rest) = digits.split_at(1);
        let point = if rest.is_empty() { "" } else { "." };
        let sign = if exponent < 0 { '-' } else { '+' };
        format!("{first}{point}{rest}e{sign}{:02}", exponent.abs())
    } else if exponent < 0 {
        format!(
            "0.{}{digits}",
            "0".repeat(exponent.unsigned_abs() as usize - 1)
        )
    } else {
        let whole = exponent.unsigned_abs() as usize + 1;
        match digits.len().checked_sub(whole) {
            Some(0) | None => format!("{digits:0<whole$}.0"),
            Some(_) => format!("{}.{}", &digits[..whole], &digits[whole..]),
        }
    };
    format!("{}{body}", if x.is_sign_negative() { "-" } else { "" })
}

/// Python's `divmod(x, y)` for floats, step for step as CPython computes it.
fn float_divmod(x: f64, y: f64) -> (f64, f64) {
    let mut remainder = x % y;
    let mut quotient = (x - remainder) / y;
    if remainder == 0.0 {
        remainder = 0.0_f64.copysign(y);
    } else if (y < 0.0) != (remainder < 0.0) {
        remainder += y;
        quotient -= 1.0;
    }
    if quotient == 0.0 {
        return (0.0_f64.copysign(x / y), remainder);
    }
    let floor = quotient.floor();
    let floor = if quotient - floor > 0.5 {
        floor + 1.0
    } else {
        floor
    };
    (floor, remainder)
}

/// Hours, minutes and seconds of `stdr`. Python keeps ints and floats apart all the way.
fn clock(seconds: Num) -> [Num; 3] {
    match seconds {
        Num::Int(total) => {
            let (minutes, seconds) = (total.div_euclid(60), total.rem_euclid(60));
            let (hours, minutes) = (minutes.div_euclid(60), minutes.rem_euclid(60));
            [Num::Int(hours), Num::Int(minutes), Num::Int(seconds)]
        }
        Num::Float(total) => {
            let (minutes, seconds) = float_divmod(total, 60.0);
            let (hours, minutes) = float_divmod(minutes, 60.0);
            [Num::Float(hours), Num::Float(minutes), Num::Float(seconds)]
        }
    }
}

/// One field of `stdr`. A single character gets a leading zero; a number that is still zero
/// after that (only `0.0` can be) prints as `empty`.
fn clock_field(value: Num, tail: &str, empty: &str) -> String {
    let text = match value {
        Num::Int(whole) => whole.to_string(),
        Num::Float(x) => repr_float(x),
    };
    if text.len() == 1 {
        format!("0{text}{tail}")
    } else if value == Num::Int(0) {
        empty.to_string()
    } else {
        format!("{text}{tail}")
    }
}

/// Python's `len()` of a value that is not text, as the bridge encodes it.
fn sized_len(value: &Value) -> Result<usize, String> {
    let marker = value.as_object().filter(|o| o.len() == 1);
    match (value, marker.and_then(|o| o.iter().next())) {
        (_, Some((key, Value::Array(items))))
            if ["$tuple", "$set", "$bytes", "$dict"].contains(&key.as_str()) =>
        {
            Ok(items.len())
        }
        (_, Some((key, _))) if ["$int", "$num", "$float"].contains(&key.as_str()) => {
            Err("TypeError: object of type 'number' has no len()".into())
        }
        (Value::Array(items), _) => Ok(items.len()),
        (Value::Object(entries), _) => Ok(entries.len()),
        _ => Err("TypeError: object has no len()".into()),
    }
}

/// The text left once the button markup is taken out, and the buttons row by row.
fn parse_buttons(texts: &str) -> Result<(String, ButtonRows), String> {
    let mut rows = ButtonRows::new();
    for found in BUTTON.captures_iter(texts) {
        let mut targets = found[2].split('|');
        let button = vec![
            found[1].to_string(),
            targets.next().unwrap_or_default().to_string(),
        ];
        if targets.next().is_some() {
            // `|same` joins the row above; with no row yet the original fails on `btn[-1]`.
            rows.last_mut()
                .ok_or("IndexError: list index out of range")?
                .push(button);
        } else {
            rows.push(vec![button]);
        }
    }
    let mut text = texts.to_string();
    for found in MARKUP.find_iter(texts) {
        text = text.replace(found.as_str(), "");
    }
    Ok((py_strip(&text).to_string(), rows))
}

/// Port of `get_msg_button` (`pyUltroid/fns/tools.py:176`). The original returns a tuple.
pub fn get_msg_button(texts: String) -> Result<serde_json::Value, String> {
    let (text, rows) = parse_buttons(&texts)?;
    Ok(json!({ "$tuple": [text, rows] }))
}

/// Port of `text_set` (`pyUltroid/fns/tools.py:319`).
pub fn text_set(text: serde_json::Value) -> Result<serde_json::Value, String> {
    let Value::String(text) = &text else {
        // The original only asks for a length, so any short sized value comes back as one line.
        return match sized_len(&text)? {
            0..=55 => Ok(json!([text])),
            _ if text.get("$bytes").is_some() => Err("TypeError: a bytes-like object".into()),
            _ => Err("AttributeError: object has no attribute 'split'".into()),
        };
    };
    let chars: Vec<char> = text.chars().collect();
    let mut lines: Vec<String> = Vec::new();
    if chars.len() <= 55 {
        lines.push(text.clone());
    } else {
        for line in chars.split(|&c| c == '\n') {
            if line.len() <= 55 {
                lines.push(line.iter().collect());
                continue;
            }
            // One slice more than needed: a line of exactly 110 characters ends with "".
            for piece in 0..=line.len() / 55 {
                lines.push(line.iter().skip(piece * 55).take(55).collect());
            }
        }
    }
    lines.truncate(25);
    Ok(json!(lines))
}

/// Port of `stdr` (`pyUltroid/fns/tools.py:543`).
pub fn stdr(seconds: Num) -> Result<String, String> {
    let [hours, minutes, seconds] = clock(seconds);
    Ok(clock_field(hours, ":", "00:")
        + &clock_field(minutes, ":", "00:")
        + &clock_field(seconds, "", ""))
}

/// Port of `cmd_regex_replace` (`pyUltroid/fns/tools.py:730`).
pub fn cmd_regex_replace(cmd: String) -> Result<String, String> {
    Ok(PATTERN_NOISE
        .iter()
        .fold(cmd, |text, part| text.replace(part, "")))
}

/// Port of `get_chat_and_msgid` (`pyUltroid/fns/tools.py:1085`).
pub fn get_chat_and_msgid(link: String) -> Result<(serde_json::Value, serde_json::Value), String> {
    if let Some(found) = MESSAGE_LINK.captures(&link) {
        let chat = match found.get(1) {
            // A `/c/` link names a channel by its bare id; the original builds `-100<id>`.
            Some(_) => py_int(&format!("-100{}", &found[2]))?,
            None => json!(&found[2]),
        };
        return Ok((chat, py_int(&found[3])?));
    }
    if let Some(found) = OPEN_MESSAGE.captures(&link) {
        return Ok((py_int(&found[1])?, py_int(&found[2])?));
    }
    Ok((Value::Null, Value::Null))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn float_repr_follows_python() {
        // Expected values are CPython's `repr(x)`.
        for (x, text) in [
            (0.0, "0.0"),
            (-0.0, "-0.0"),
            (42.0, "42.0"),
            (0.5, "0.5"),
            (0.0001, "0.0001"),
            (1e-5, "1e-05"),
            (1e15, "1000000000000000.0"),
            (1e16, "1e+16"),
            (36.789_000_000_004_31, "36.78900000000431"),
            (2.777_777_777_777_777_6e17, "2.7777777777777776e+17"),
            (5e-324, "5e-324"),
            (-61.5, "-61.5"),
            // Exactly halfway between two shortest forms: CPython takes the even digit.
            (16.0 + 1.0 / 65536.0, "16.000015258789062"),
            (16.0 + 3.0 / 65536.0, "16.000045776367188"),
            (7_205_759_403_792_794.0 / 8.0, "900719925474099.2"),
            (-(8.0 + 1.0 / 65536.0), "-8.000015258789062"),
        ] {
            assert_eq!(repr_float(x), text);
        }
        assert_eq!(repr_float(f64::NAN), "nan");
        assert_eq!(repr_float(f64::NEG_INFINITY), "-inf");
    }

    #[test]
    fn int_parsing_follows_python() {
        assert_eq!(py_int("-100123"), Ok(json!(-100_123)));
        assert_eq!(py_int(" 12_3\t"), Ok(json!(123)));
        assert_eq!(py_int("-100_12"), Ok(json!(-10_012)));
        assert_eq!(py_int("007"), Ok(json!(7)));
        assert_eq!(py_int("-0"), Ok(json!(0)));
        assert_eq!(py_int("\u{661}\u{662}\u{663}"), Ok(json!(123)));
        assert_eq!(py_int("\u{1d7d7}\u{1d7ec}"), Ok(json!(90)));
        assert_eq!(
            py_int("99999999999999999999"),
            Ok(json!({"$int": "99999999999999999999"}))
        );
        for bad in [
            "", "-", "_1", "1_", "1__2", "1 2", "1\u{1f}", "+-1", "1\u{b2}", "abc",
        ] {
            assert!(py_int(bad).is_err(), "{bad:?} must be refused");
        }
    }

    #[test]
    fn clock_text() {
        let text = |n| stdr(n).unwrap_or_else(|e| e);
        assert_eq!(text(Num::Int(0)), "00:00:00");
        assert_eq!(text(Num::Int(3661)), "01:01:01");
        assert_eq!(text(Num::Int(360_000)), "100:00:00");
        assert_eq!(text(Num::Int(-1)), "-1:59:59");
        // A float zero is not padded, so it drops out instead of printing "00".
        assert_eq!(text(Num::Float(60.0)), "00:1.0:");
        assert_eq!(text(Num::Float(-0.0)), "00:00:");
        assert_eq!(text(Num::Float(-2.5)), "-1.0:59.0:57.5");
        assert_eq!(text(Num::Float(f64::INFINITY)), "nan:nan:nan");
    }

    #[test]
    fn buttons() {
        let rows = |pairs: &[&[[&str; 2]]]| -> ButtonRows {
            pairs
                .iter()
                .map(|row| {
                    row.iter()
                        .map(|pair| pair.map(String::from).to_vec())
                        .collect()
                })
                .collect()
        };
        assert_eq!(
            parse_buttons("text [A|a.com] middle [B|b.com|same] end"),
            Ok((
                "text  middle  end".into(),
                rows(&[&[["A", "a.com"], ["B", "b.com"]]])
            ))
        );
        assert_eq!(
            parse_buttons("[[x|y]]"),
            Ok(("]".into(), rows(&[&[["[x", "y"]]])))
        );
        // An empty label or target is a button, but the markup is not removed from the text.
        assert_eq!(
            parse_buttons("[|]"),
            Ok(("[|]".into(), rows(&[&[["", ""]]])))
        );
        assert_eq!(
            parse_buttons("\u{1f}text\u{1c}"),
            Ok(("text".into(), Vec::new()))
        );
        assert!(parse_buttons("[A|a.com|same]").is_err());
        assert_eq!(
            get_msg_button("[A|a.com]".into()),
            Ok(json!({"$tuple": ["", [[["A", "a.com"]]]]}))
        );
    }

    #[test]
    fn wrapping() {
        let lines = |text: &str| text_set(json!(text)).unwrap_or_default();
        assert_eq!(lines("hello"), json!(["hello"]));
        assert_eq!(
            lines(&"a".repeat(110)),
            json!(["a".repeat(55), "a".repeat(55), ""])
        );
        assert_eq!(
            lines(&"\u{1f600}".repeat(56)),
            json!(["\u{1f600}".repeat(55), "\u{1f600}"])
        );
        assert_eq!(lines(&"a".repeat(2000)).as_array().map(Vec::len), Some(25));
        assert_eq!(text_set(json!(["a", 1])), Ok(json!([["a", 1]])));
        assert!(text_set(json!(0)).is_err());
    }

    #[test]
    fn links() {
        assert_eq!(
            get_chat_and_msgid("https://t.me/c/1234567890/42".into()),
            Ok((json!(-1_001_234_567_890_i64), json!(42)))
        );
        assert_eq!(
            get_chat_and_msgid("https://t.me/TeamUltroid/123".into()),
            Ok((json!("TeamUltroid"), json!(123)))
        );
        // Without a message id after it, `c` is read as the chat name.
        assert_eq!(
            get_chat_and_msgid("t.me/c/123".into()),
            Ok((json!("c"), json!(123)))
        );
        assert_eq!(
            get_chat_and_msgid("tg://openmessage?user_id=777000&message_id=456".into()),
            Ok((json!(777_000), json!(456)))
        );
        assert_eq!(
            get_chat_and_msgid("no link".into()),
            Ok((Value::Null, Value::Null))
        );
        assert!(get_chat_and_msgid("https://t.me/c/abc/5".into()).is_err());
    }

    #[test]
    fn pattern_cleaning() {
        let clean = |text: &str| cmd_regex_replace(text.into()).unwrap_or_default();
        assert_eq!(clean("purgeme( (.*)|$)"), "purgeme");
        assert_eq!(clean("delstored ?(.*)"), "delstored ");
        assert_eq!(clean("purge ?(\\d+)"), "purge ?\\d+");
    }
}
