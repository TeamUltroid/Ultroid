//! Python's `repr()` and `str()`, character for character as CPython 3.11 prints them. This is
//! the text every backend stores, so it has to be exact.

use crate::tables::NONPRINTABLE;
use crate::value::{PyError, PyResult, PyValue};
use num_bigint::BigInt;

/// CPython refuses to print an int with more digits than this (`sys.get_int_max_str_digits()`).
pub const MAX_INT_DIGITS: usize = 4300;

/// `str.isprintable()` for one character.
pub fn is_printable(c: char) -> bool {
    let code = u32::from(c);
    if code < 0x80 {
        return (0x20..0x7f).contains(&code);
    }
    let after = NONPRINTABLE.partition_point(|&(_, last)| last < code);
    NONPRINTABLE
        .get(after)
        .is_none_or(|&(first, _)| code < first)
}

/// The digits and the power of ten of the first digit, from Rust's `1.5e2` form.
fn split_scientific(text: &str) -> (String, i32) {
    let (mantissa, exponent) = text.split_once('e').unwrap_or((text, "0"));
    (
        mantissa.chars().filter(char::is_ascii_digit).collect(),
        exponent.parse().unwrap_or(0),
    )
}

/// The shortest digits that read back as `x`, and the power of ten of the first digit.
fn digits(x: f64) -> (String, i32) {
    let x = x.abs();
    let shortest = split_scientific(&format!("{x:e}"));
    // 900719925474099.25 reads back from both ...099.2 and ...099.3. Rust prints the upper one;
    // CPython rounds the exact value half to even, which is what a fixed precision does here.
    let rounded = format!("{:.*e}", shortest.0.len() - 1, x);
    if rounded.parse() == Ok(x) {
        split_scientific(&rounded)
    } else {
        shortest
    }
}

/// CPython's `'r'` float format. `dot_zero` is what `repr(float)` adds to a whole number;
/// `complex` leaves it out. `sign` forces a `+`.
fn format_float(x: f64, dot_zero: bool, sign: bool) -> String {
    let prefix = match (x.is_sign_negative() && !x.is_nan(), sign) {
        (true, _) => "-",
        (false, true) => "+",
        (false, false) => "",
    };
    if x.is_nan() {
        return format!("{prefix}nan");
    }
    if x.is_infinite() {
        return format!("{prefix}inf");
    }
    let (digits, exponent) = digits(x);
    let body = if !(-4..16).contains(&exponent) {
        let (first, rest) = digits.split_at(1);
        let point = if rest.is_empty() { "" } else { "." };
        let direction = if exponent < 0 { '-' } else { '+' };
        format!("{first}{point}{rest}e{direction}{:02}", exponent.abs())
    } else if exponent < 0 {
        format!(
            "0.{}{digits}",
            "0".repeat(exponent.unsigned_abs() as usize - 1)
        )
    } else {
        let whole = exponent.unsigned_abs() as usize + 1;
        match digits.len().checked_sub(whole) {
            Some(0) | None if dot_zero => format!("{digits:0<whole$}.0"),
            Some(0) | None => format!("{digits:0<whole$}"),
            Some(_) => format!("{}.{}", &digits[..whole], &digits[whole..]),
        }
    };
    format!("{prefix}{body}")
}

/// `repr(x)` of a float.
pub fn repr_float(x: f64) -> String {
    format_float(x, true, false)
}

fn repr_complex(re: f64, im: f64) -> String {
    if re == 0.0 && re.is_sign_positive() {
        return format!("{}j", format_float(im, false, false));
    }
    format!(
        "({}{}j)",
        format_float(re, false, false),
        format_float(im, false, true)
    )
}

fn repr_int(whole: &BigInt) -> PyResult<String> {
    let text = whole.to_string();
    if text.trim_start_matches('-').len() > MAX_INT_DIGITS {
        return Err(PyError::value_error(format!(
            "Exceeds the limit ({MAX_INT_DIGITS} digits) for integer string conversion"
        )));
    }
    Ok(text)
}

/// Python picks double quotes only for text that holds a single quote and no double quote.
fn quote_for(has_single: bool, has_double: bool) -> char {
    if has_single && !has_double { '"' } else { '\'' }
}

fn push_code_point(out: &mut String, code: u32, quote: char) {
    match char::from_u32(code) {
        Some(c) if c == quote || c == '\\' => out.extend(['\\', c]),
        Some('\t') => out.push_str("\\t"),
        Some('\n') => out.push_str("\\n"),
        Some('\r') => out.push_str("\\r"),
        Some(c) if is_printable(c) => out.push(c),
        _ if code <= 0xff => out.push_str(&format!("\\x{code:02x}")),
        _ if code <= 0xffff => out.push_str(&format!("\\u{code:04x}")),
        _ => out.push_str(&format!("\\U{code:08x}")),
    }
}

fn repr_code_points(points: impl Iterator<Item = u32> + Clone) -> String {
    let has = |wanted: char| points.clone().any(|code| code == u32::from(wanted));
    let quote = quote_for(has('\''), has('"'));
    let mut out = String::from(quote);
    for code in points {
        push_code_point(&mut out, code, quote);
    }
    out.push(quote);
    out
}

fn repr_bytes(bytes: &[u8]) -> String {
    let quote = quote_for(bytes.contains(&b'\''), bytes.contains(&b'"'));
    let mut out = format!("b{quote}");
    for &byte in bytes {
        match char::from(byte) {
            c if c == quote || c == '\\' => out.extend(['\\', c]),
            '\t' => out.push_str("\\t"),
            '\n' => out.push_str("\\n"),
            '\r' => out.push_str("\\r"),
            c if (' '..'\x7f').contains(&c) => out.push(c),
            _ => out.push_str(&format!("\\x{byte:02x}")),
        }
    }
    out.push(quote);
    out
}

fn join(open: &str, parts: Vec<String>, close: &str) -> String {
    format!("{open}{}{close}", parts.join(", "))
}

fn render(value: &PyValue, sorted_sets: bool) -> PyResult<String> {
    let each = |items: &mut dyn Iterator<Item = &PyValue>| -> PyResult<Vec<String>> {
        items.map(|item| render(item, sorted_sets)).collect()
    };
    Ok(match value {
        PyValue::None => "None".into(),
        PyValue::Ellipsis => "Ellipsis".into(),
        PyValue::Bool(true) => "True".into(),
        PyValue::Bool(false) => "False".into(),
        PyValue::Int(whole) => repr_int(whole)?,
        PyValue::Float(x) => repr_float(*x),
        PyValue::Complex(re, im) => repr_complex(*re, *im),
        PyValue::Str(text) => repr_code_points(text.chars().map(u32::from)),
        PyValue::Surrogates(points) => repr_code_points(points.iter().copied()),
        PyValue::Bytes(bytes) => repr_bytes(bytes),
        PyValue::List(items) => join("[", each(&mut items.iter())?, "]"),
        PyValue::Tuple(items) if items.len() == 1 => join("(", each(&mut items.iter())?, ",)"),
        PyValue::Tuple(items) => join("(", each(&mut items.iter())?, ")"),
        PyValue::Set(set) if set.is_empty() => "set()".into(),
        PyValue::Set(set) => {
            let mut parts = each(&mut set.iter())?;
            if sorted_sets {
                parts.sort();
            }
            join("{", parts, "}")
        }
        PyValue::Dict(dict) => {
            let mut parts = Vec::with_capacity(dict.len());
            for (key, item) in dict.iter() {
                parts.push(format!(
                    "{}: {}",
                    render(key, sorted_sets)?,
                    render(item, sorted_sets)?
                ));
            }
            join("{", parts, "}")
        }
    })
}

/// `repr(value)`. A set prints in insertion order, where CPython prints in hash-table order.
pub fn repr(value: &PyValue) -> PyResult<String> {
    render(value, false)
}

/// `repr(value)` with every set's members sorted by their own text, so two sets with the same
/// members print the same. Used to compare values, never to store them.
pub fn canon(value: &PyValue) -> PyResult<String> {
    render(value, true)
}

/// Whether printing `value` depends on the order a set happens to be in: it holds a set of more
/// than one member. CPython's order follows its hash table and cannot be reproduced (ADR-013).
pub fn has_set_order(value: &PyValue) -> bool {
    match value {
        PyValue::Set(set) => set.len() > 1 || set.iter().any(has_set_order),
        PyValue::List(items) | PyValue::Tuple(items) => items.iter().any(has_set_order),
        PyValue::Dict(dict) => dict
            .iter()
            .any(|(key, item)| has_set_order(key) || has_set_order(item)),
        _ => false,
    }
}

/// `str(value)` as a backend stores it: text is itself, everything else is its `repr`. Text
/// that holds a lone surrogate cannot be encoded, so no backend takes it.
pub fn to_str(value: &PyValue) -> PyResult<String> {
    match value {
        PyValue::Str(text) => Ok(text.clone()),
        PyValue::Surrogates(_) => Err(PyError::new(
            "UnicodeEncodeError",
            "'utf-8' codec can't encode character: surrogates not allowed",
        )),
        other => repr(other),
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::value::{PyDict, PySet};

    #[test]
    fn floats() {
        // Expected values are CPython's `repr(x)`.
        for (x, text) in [
            (0.0, "0.0"),
            (-0.0, "-0.0"),
            (1.5, "1.5"),
            (1e16, "1e+16"),
            (1e15, "1000000000000000.0"),
            (1e-5, "1e-05"),
            (0.0001, "0.0001"),
            (123456789.123, "123456789.123"),
            (5e-324, "5e-324"),
            (1e300, "1e+300"),
            (f64::INFINITY, "inf"),
            (f64::NEG_INFINITY, "-inf"),
            // Halfway between two shortest forms (...099.25, ...099.75, ...955.25): the even
            // digit wins. Written as divisions because the decimal form has no exact literal.
            (7_205_759_403_792_794.0 / 8.0, "900719925474099.2"),
            (3_602_879_701_896_399.0 / 4.0, "900719925474099.8"),
            (7_378_697_629_483_821.0 / 4.0, "1844674407370955.2"),
        ] {
            assert_eq!(repr_float(x), text);
        }
        assert_eq!(repr_float(f64::NAN), "nan");
    }

    #[test]
    fn complex_numbers() {
        // Expected values are CPython's `repr(z)`.
        for ((re, im), text) in [
            ((0.0, 1.0), "1j"),
            ((0.0, -1.0), "-1j"),
            ((-0.0, -1.0), "(-0-1j)"),
            ((1.0, 2.0), "(1+2j)"),
            ((1.5, -2.5), "(1.5-2.5j)"),
            ((f64::INFINITY, 1.0), "(inf+1j)"),
            ((1.0, f64::INFINITY), "(1+infj)"),
            ((0.0, 0.0), "0j"),
            ((0.0, 1e16), "1e+16j"),
            ((1.0, f64::NAN), "(1+nanj)"),
        ] {
            assert_eq!(repr_complex(re, im), text);
        }
    }

    #[test]
    fn text_quotes_and_escapes() {
        let text = |s: &str| repr(&PyValue::str(s)).unwrap();
        assert_eq!(text("abc"), "'abc'");
        assert_eq!(text("it's"), "\"it's\"");
        assert_eq!(text("say \"hi\""), "'say \"hi\"'");
        assert_eq!(text("both ' and \""), "'both \\' and \"'");
        assert_eq!(text("a\\b\n\t\r"), "'a\\\\b\\n\\t\\r'");
        assert_eq!(text("\x01\x7f\u{85}\u{a0}"), "'\\x01\\x7f\\x85\\xa0'");
        assert_eq!(text("é 日本 😀"), "'é 日本 😀'");
        assert_eq!(text("\u{200d}\u{2028}\u{e000}"), "'\\u200d\\u2028\\ue000'");
        // Assigned after Unicode 14, so CPython 3.11 does not count them as printable.
        assert_eq!(text("\u{1fae8}"), "'\\U0001fae8'");
        assert_eq!(
            repr(&PyValue::Surrogates(vec![0xd83d, 0x61])).unwrap(),
            "'\\ud83da'"
        );
    }

    #[test]
    fn bytes() {
        let text = |b: &[u8]| repr(&PyValue::Bytes(b.to_vec())).unwrap();
        assert_eq!(text(b"abc"), "b'abc'");
        assert_eq!(text(b"it's"), "b\"it's\"");
        assert_eq!(text(b"\x00\xff\n"), "b'\\x00\\xff\\n'");
    }

    #[test]
    fn containers() {
        let one = || PyValue::int(1);
        assert_eq!(repr(&PyValue::Tuple(vec![])).unwrap(), "()");
        assert_eq!(repr(&PyValue::Tuple(vec![one()])).unwrap(), "(1,)");
        assert_eq!(repr(&PyValue::Tuple(vec![one(), one()])).unwrap(), "(1, 1)");
        assert_eq!(
            repr(&PyValue::List(vec![PyValue::None, PyValue::Bool(true)])).unwrap(),
            "[None, True]"
        );
        assert_eq!(repr(&PyValue::Set(PySet::new())).unwrap(), "set()");
        let mut set = PySet::new();
        set.add(PyValue::int(3)).unwrap();
        set.add(PyValue::int(10)).unwrap();
        assert_eq!(repr(&PyValue::Set(set.clone())).unwrap(), "{3, 10}");
        assert_eq!(canon(&PyValue::Set(set)).unwrap(), "{10, 3}");
        let mut dict = PyDict::new();
        dict.set(PyValue::int(-100), PyValue::List(vec![PyValue::str("x")]))
            .unwrap();
        assert_eq!(repr(&PyValue::Dict(dict)).unwrap(), "{-100: ['x']}");
        assert_eq!(to_str(&PyValue::str("plain")).unwrap(), "plain");
    }

    #[test]
    fn huge_ints_are_refused() {
        let big = |digits: usize| PyValue::Int("9".repeat(digits).parse().unwrap());
        assert_eq!(repr(&big(MAX_INT_DIGITS)).unwrap().len(), MAX_INT_DIGITS);
        assert_eq!(
            repr(&big(MAX_INT_DIGITS + 1)).unwrap_err().kind,
            "ValueError"
        );
    }
}
