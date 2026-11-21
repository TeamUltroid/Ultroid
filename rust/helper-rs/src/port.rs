//! The Rust port of `pyUltroid/fns/helper.py`.
//!
//! Only the functions that take numbers and return text are ported. Everything in that file that
//! talks to Telegram, the network or the process stays in Python (`rust-anything.json` lists
//! each one with its reason).

#![forbid(unsafe_code)]

use crate::pynum::Num;
use num_bigint::BigInt;
use num_integer::Integer;
use num_traits::{FromPrimitive, Zero};

const BYTE_UNITS: [&str; 5] = ["", "K", "M", "G", "T"];
const COUNT_UNITS: [&str; 5] = ["", "K", "M", "B", "T"];

/// Python's `n / d` for two ints: the exact quotient, rounded once (half to even) to a float.
/// Converting `n` to a float first would round twice for ints beyond 2^53.
fn int_div(n: i64, d: u32) -> f64 {
    if n == 0 {
        return 0.0;
    }
    let magnitude = u128::from(n.unsigned_abs());
    // Shifted to the top bit, the quotient keeps far more than 53 bits for any `d`.
    let shift = magnitude.leading_zeros();
    let scaled = magnitude << shift;
    let (quotient, remainder) = (scaled / u128::from(d), scaled % u128::from(d));
    let drop = 128 - quotient.leading_zeros() - 53;
    let (kept, rest) = (quotient >> drop, quotient & ((1 << drop) - 1));
    let half = 1 << (drop - 1);
    let up = rest > half || (rest == half && (remainder != 0 || kept & 1 == 1));
    let value = (kept + u128::from(up)) as f64 * 2f64.powi(drop as i32 - shift as i32);
    if n < 0 { -value } else { value }
}

/// The loop `humanbytes` and `numerize` share: divide by `base` until the value is below it or
/// the units run out. Like the original, a value that is still too large after the last unit is
/// divided once more, so 1024 TB prints as `1.00TB`.
fn scale(mut value: Num, base: u32, units: [&'static str; 5]) -> String {
    let mut unit = "";
    for next in units {
        unit = next;
        if value < Num::Int(i64::from(base)) {
            break;
        }
        value = Num::Float(match value {
            Num::Int(i) => int_div(i, base),
            Num::Float(x) => x / f64::from(base),
        });
    }
    match value {
        Num::Int(i) => format!("{i}{unit}"),
        Num::Float(x) if x.is_nan() => format!("nan{unit}"),
        Num::Float(x) => format!("{x:.2}{unit}"),
    }
}

/// Python's truth test for a number: zero of either sign is false, NaN is true.
fn truthy(value: &Num) -> bool {
    *value != Num::Int(0)
}

/// Port of `time_formatter` (`pyUltroid/fns/helper.py:501`).
pub fn time_formatter(milliseconds: Num) -> Result<String, String> {
    let seconds = match milliseconds {
        Num::Int(i) => int_div(i, 1000),
        Num::Float(x) => x / 1000.0,
    };
    if seconds.is_nan() {
        return Err("ValueError: cannot convert float NaN to integer".into());
    }
    // Python's int is unbounded: 1.7e308 ms is a 300-digit count of weeks, not an overflow.
    let total = BigInt::from_f64(seconds.trunc())
        .ok_or("OverflowError: cannot convert float infinity to integer")?;
    let (minutes, seconds) = total.div_mod_floor(&BigInt::from(60));
    let (hours, minutes) = minutes.div_mod_floor(&BigInt::from(60));
    let (days, hours) = hours.div_mod_floor(&BigInt::from(24));
    let (weeks, days) = days.div_mod_floor(&BigInt::from(7));
    let parts = [
        (weeks, "w:"),
        (days, "d:"),
        (hours, "h:"),
        (minutes, "m:"),
        (seconds, "s"),
    ];
    let mut text = String::new();
    for (value, unit) in parts {
        if !value.is_zero() {
            text += &format!("{value}{unit}");
        }
    }
    if text.is_empty() {
        return Ok("0s".into());
    }
    Ok(text.strip_suffix(':').unwrap_or(&text).to_string())
}

/// Port of `humanbytes` (`pyUltroid/fns/helper.py:521`).
pub fn humanbytes(size: Option<Num>) -> Result<String, String> {
    Ok(match size.filter(truthy) {
        Some(size) => scale(size, 1024, BYTE_UNITS) + "B",
        None => "0 B".into(),
    })
}

/// Port of `numerize` (`pyUltroid/fns/helper.py:535`).
pub fn numerize(number: Option<Num>) -> Result<Option<String>, String> {
    Ok(number
        .filter(truthy)
        .map(|number| scale(number, 1000, COUNT_UNITS)))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn int_div_rounds_once() {
        // Expected values are CPython's `n / d`.
        assert_eq!(int_div(1, 1000), 0.001);
        assert_eq!(int_div(-5000, 1000), -5.0);
        assert_eq!(
            int_div(9_223_372_036_854_775_807, 1000),
            9_223_372_036_854_776.0
        );
        assert_eq!(int_div(9_007_199_254_740_993, 1000), 9_007_199_254_740.992);
        assert_eq!(int_div(i64::MIN, 1000), -9_223_372_036_854_776.0);
        assert_eq!(
            int_div(1_152_921_504_606_846_976, 1024),
            1_125_899_906_842_624.0
        );
    }

    #[test]
    fn durations() {
        let text = |n| time_formatter(n).unwrap_or_else(|e| e);
        assert_eq!(text(Num::Int(0)), "0s");
        assert_eq!(text(Num::Int(694_861_000)), "1w:1d:1h:1m:1s");
        assert_eq!(text(Num::Int(604_800_000)), "1w");
        assert_eq!(text(Num::Float(3_600_000.5)), "1h");
        // Floor division carries a negative duration into every unit.
        assert_eq!(text(Num::Int(-5000)), "-1w:6d:23h:59m:55s");
        assert_eq!(text(Num::Float(1e21)), "1653439153439w:1d:1h:46m:40s");
        assert_eq!(
            text(Num::Float(f64::NAN)),
            "ValueError: cannot convert float NaN to integer"
        );
        assert_eq!(
            text(Num::Float(f64::INFINITY)),
            "OverflowError: cannot convert float infinity to integer"
        );
    }

    #[test]
    fn sizes() {
        let text = |n| humanbytes(n).unwrap_or_else(|e| e);
        assert_eq!(text(None), "0 B");
        assert_eq!(text(Some(Num::Float(-0.0))), "0 B");
        assert_eq!(text(Some(Num::Int(1023))), "1023B");
        assert_eq!(text(Some(Num::Int(1024))), "1.00KB");
        assert_eq!(text(Some(Num::Int(1_048_575))), "1024.00KB");
        // Ties round half to even, as Python's `:.2f` does.
        assert_eq!(text(Some(Num::Int(1152))), "1.12KB");
        assert_eq!(text(Some(Num::Int(1408))), "1.38KB");
        assert_eq!(text(Some(Num::Float(0.125))), "0.12B");
        // The original's extra division past the last unit.
        assert_eq!(text(Some(Num::Int(1_125_899_906_842_624))), "1.00TB");
        assert_eq!(text(Some(Num::Float(f64::NAN))), "nanTB");
        assert_eq!(text(Some(Num::Float(f64::NEG_INFINITY))), "-infB");
        assert_eq!(text(Some(Num::Float(-0.001))), "-0.00B");
    }

    #[test]
    fn counts() {
        let text = |n| numerize(n).unwrap_or_default();
        assert_eq!(text(None), None);
        assert_eq!(text(Some(Num::Int(0))), None);
        assert_eq!(text(Some(Num::Int(999))).as_deref(), Some("999"));
        assert_eq!(text(Some(Num::Int(1000))).as_deref(), Some("1.00K"));
        assert_eq!(text(Some(Num::Int(1_234_567))).as_deref(), Some("1.23M"));
        assert_eq!(text(Some(Num::Float(999.995))).as_deref(), Some("1000.00"));
        assert_eq!(text(Some(Num::Int(-1000))).as_deref(), Some("-1000"));
        assert_eq!(text(Some(Num::Int(i64::MAX))).as_deref(), Some("9223.37T"));
    }
}
