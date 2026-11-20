//! The clock arithmetic of `afk_db`: one text format, written with `strftime` and read back with
//! `strptime`, and the text of the time between two moments.
//!
//! The moment "now" is handed in by the caller. Reading the local time is the application's job.

use crate::ops::{code_points, decimal, int, is_space, text};
use crate::value::{PyError, PyResult, PyValue};
use num_traits::ToPrimitive;

const MONTHS: [&str; 12] = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
];
const DAY: i64 = 86_400;

/// A naive local date and time to the second, as Python's `datetime` holds it.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct DateTime {
    year: i64,
    month: i64,
    day: i64,
    second_of_day: i64,
}

fn days_in_month(year: i64, month: i64) -> i64 {
    let leap = year % 4 == 0 && (year % 100 != 0 || year % 400 == 0);
    match month {
        2 if leap => 29,
        2 => 28,
        4 | 6 | 9 | 11 => 30,
        _ => 31,
    }
}

/// Days from 1970-01-01 to a date of the Gregorian calendar.
fn days_from_civil(year: i64, month: i64, day: i64) -> i64 {
    let year = if month <= 2 { year - 1 } else { year };
    let era = year.div_euclid(400);
    let year_of_era = year.rem_euclid(400);
    let day_of_year = (153 * ((month + 9) % 12) + 2) / 5 + day - 1;
    let day_of_era = year_of_era * 365 + year_of_era / 4 - year_of_era / 100 + day_of_year;
    era * 146_097 + day_of_era - 719_468
}

/// The date that many days after 1970-01-01.
fn civil_from_days(days: i64) -> (i64, i64, i64) {
    let days = days + 719_468;
    let era = days.div_euclid(146_097);
    let day_of_era = days.rem_euclid(146_097);
    let year_of_era =
        (day_of_era - day_of_era / 1_460 + day_of_era / 36_524 - day_of_era / 146_096) / 365;
    let day_of_year = day_of_era - (365 * year_of_era + year_of_era / 4 - year_of_era / 100);
    let shifted_month = (5 * day_of_year + 2) / 153;
    let day = day_of_year - (153 * shifted_month + 2) / 5 + 1;
    let month = if shifted_month < 10 {
        shifted_month + 3
    } else {
        shifted_month - 9
    };
    let year = year_of_era + era * 400 + i64::from(month <= 2);
    (year, month, day)
}

/// One step of reading the text: the characters not yet read.
struct Reader<'a>(&'a [u32]);

impl Reader<'_> {
    /// Takes characters while `wanted` holds, and says how many there were.
    fn run(&mut self, wanted: impl Fn(u32) -> bool) -> &[u32] {
        let length = self.0.iter().take_while(|&&code| wanted(code)).count();
        let (run, rest) = self.0.split_at(length);
        self.0 = rest;
        run
    }

    fn blanks(&mut self) -> Option<()> {
        (!self.run(is_space).is_empty()).then_some(())
    }

    /// Everything up to `stop`, which is read too.
    fn until(&mut self, stop: char) -> Option<&[u32]> {
        let length = self.0.iter().position(|&code| code == u32::from(stop))?;
        let (run, rest) = self.0.split_at(length);
        self.0 = rest.get(1..)?;
        Some(run)
    }
}

/// The number a run of digits stands for, when it has the shape one field allows. `shapes` lists,
/// for a two-digit field, the first digits that may be followed by any digit, then the pairs
/// allowed besides; a single digit from `single` is always a field of its own.
fn field(run: &[u32], firsts: &str, pairs: &[&str], single: fn(u32) -> bool) -> Option<i64> {
    let ascii = |code: u32| char::from_u32(code).filter(char::is_ascii);
    let allowed = match *run {
        [one] => single(one),
        [first, second] => {
            let pair: Option<String> = [ascii(first), ascii(second)].into_iter().collect();
            ascii(first).is_some_and(|c| firsts.contains(c)) && decimal(second).is_some()
                || pair.is_some_and(|pair| pairs.contains(&pair.as_str()))
        }
        _ => false,
    };
    // `int()` reads digits of any script, which is what `strptime` hands it.
    allowed
        .then(|| int(&text(run.to_vec())).ok()?.to_i64())
        .flatten()
}

impl DateTime {
    /// `datetime(year, month, day, hour, minute, second)`, refusing what Python refuses.
    pub fn new(
        year: i64,
        month: i64,
        day: i64,
        hour: i64,
        minute: i64,
        second: i64,
    ) -> PyResult<Self> {
        let valid = (1..=9999).contains(&year)
            && (1..=12).contains(&month)
            && (1..=days_in_month(year, month)).contains(&day)
            && (0..24).contains(&hour)
            && (0..60).contains(&minute)
            && (0..60).contains(&second);
        if !valid {
            return Err(PyError::value_error("date or time field out of range"));
        }
        Ok(Self {
            year,
            month,
            day,
            second_of_day: hour * 3600 + minute * 60 + second,
        })
    }

    /// Seconds since 1970-01-01 00:00:00, read as the same naive clock.
    fn seconds(&self) -> i64 {
        days_from_civil(self.year, self.month, self.day) * DAY + self.second_of_day
    }

    /// The moment `seconds` later (earlier when negative).
    pub fn plus_seconds(&self, seconds: i64) -> PyResult<Self> {
        let out_of_range = || PyError::new("OverflowError", "date value out of range");
        let total = self
            .seconds()
            .checked_add(seconds)
            .ok_or_else(out_of_range)?;
        let days = total.div_euclid(DAY);
        // The calendar arithmetic below is exact far beyond the years a `datetime` can hold.
        if days.abs() > 4_000_000 {
            return Err(out_of_range());
        }
        let (year, month, day) = civil_from_days(days);
        let second_of_day = total.rem_euclid(DAY);
        let (hour, minute) = (second_of_day / 3600, second_of_day % 3600 / 60);
        Self::new(year, month, day, hour, minute, second_of_day % 60).map_err(|_| out_of_range())
    }

    /// `strftime("%b %d %Y %I:%M:%S%p")` in the C locale: `Nov 20 2026 08:51:44PM`. The year is
    /// not padded, as glibc does not pad it, so a year before 1000 does not read back.
    pub fn afk_text(&self) -> String {
        let (hour, minute) = (self.second_of_day / 3600, self.second_of_day % 3600 / 60);
        let month = usize::try_from(self.month - 1).ok();
        format!(
            "{} {:02} {} {:02}:{:02}:{:02}{}",
            month
                .and_then(|at| MONTHS.get(at))
                .copied()
                .unwrap_or_default(),
            self.day,
            self.year,
            if hour % 12 == 0 { 12 } else { hour % 12 },
            minute,
            self.second_of_day % 60,
            if hour < 12 { "AM" } else { "PM" },
        )
    }

    /// The fields `strptime` finds, before any range check. The whole text has to fit the
    /// format: three letters of a month, a day, four digits of a year, then `hour:minute:second`
    /// on a 12-hour clock with `AM` or `PM` straight after, in any letter case.
    fn afk_fields(points: &[u32]) -> Option<[i64; 6]> {
        let folded = |points: &[u32]| -> Option<String> {
            let letters: Option<String> = points.iter().map(|&code| char::from_u32(code)).collect();
            letters.map(|letters| letters.to_ascii_lowercase())
        };
        let mut reader = Reader(points);
        let name = folded(reader.0.get(..3)?)?;
        let month = MONTHS
            .iter()
            .position(|month| month.to_ascii_lowercase() == name)?;
        reader.0 = reader.0.get(3..)?;
        reader.blanks()?;
        let is_nonzero = |code| (0x31..=0x39).contains(&code);
        let day = field(
            reader.run(|code| !is_space(code)),
            "12",
            &[
                "30", "31", "01", "02", "03", "04", "05", "06", "07", "08", "09",
            ],
            is_nonzero,
        )?;
        reader.blanks()?;
        let year = reader.run(|code| !is_space(code));
        let year = (year.len() == 4 && year.iter().all(|&code| decimal(code).is_some()))
            .then(|| int(&text(year.to_vec())).ok()?.to_i64())??;
        reader.blanks()?;
        let hour = field(
            reader.until(':')?,
            "",
            &[
                "10", "11", "12", "01", "02", "03", "04", "05", "06", "07", "08", "09",
            ],
            is_nonzero,
        )?;
        let any_digit = |code| decimal(code).is_some();
        let minute = field(reader.until(':')?, "012345", &[], any_digit)?;
        let half = folded(reader.0.get(reader.0.len().checked_sub(2)?..)?)?;
        let second = field(
            reader.0.get(..reader.0.len() - 2)?,
            "012345",
            &["60", "61"],
            any_digit,
        )?;
        let hour = match half.as_str() {
            "am" => hour % 12,
            "pm" => hour % 12 + 12,
            _ => return None,
        };
        Some([
            year,
            i64::try_from(month).ok()? + 1,
            day,
            hour,
            minute,
            second,
        ])
    }

    /// `datetime.strptime(value, "%b %d %Y %I:%M:%S%p")`.
    pub fn from_afk_text(value: &PyValue) -> PyResult<Self> {
        let points = code_points(value).ok_or_else(|| {
            PyError::type_error(format!(
                "strptime() argument 1 must be str, not {}",
                value.type_name()
            ))
        })?;
        let [year, month, day, hour, minute, second] =
            Self::afk_fields(&points).ok_or_else(|| {
                PyError::value_error("time data does not match format '%b %d %Y %I:%M:%S%p'")
            })?;
        Self::new(year, month, day, hour, minute, second)
    }

    /// `str(self - start)`, the text of a `timedelta`: `0:05:00`, `1 day, 0:00:00`,
    /// `-1 day, 23:59:55`.
    pub fn since(&self, start: &Self) -> String {
        let total = self.seconds() - start.seconds();
        let (days, rest) = (total.div_euclid(DAY), total.rem_euclid(DAY));
        let clock = format!("{}:{:02}:{:02}", rest / 3600, rest % 3600 / 60, rest % 60);
        match days {
            0 => clock,
            1 | -1 => format!("{days} day, {clock}"),
            _ => format!("{days} days, {clock}"),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn at(year: i64, month: i64, day: i64, hour: i64, minute: i64, second: i64) -> DateTime {
        DateTime::new(year, month, day, hour, minute, second).unwrap()
    }

    fn read(text: &str) -> PyResult<DateTime> {
        DateTime::from_afk_text(&PyValue::str(text))
    }

    #[test]
    fn writes_the_afk_format() {
        // Expected values are CPython's `strftime("%b %d %Y %I:%M:%S%p")`.
        assert_eq!(
            at(2026, 11, 20, 20, 51, 44).afk_text(),
            "Nov 20 2026 08:51:44PM"
        );
        assert_eq!(at(2026, 1, 5, 0, 0, 9).afk_text(), "Jan 05 2026 12:00:09AM");
        assert_eq!(
            at(2024, 2, 29, 12, 30, 0).afk_text(),
            "Feb 29 2024 12:30:00PM"
        );
    }

    #[test]
    fn reads_what_it_writes() {
        for moment in [
            at(2026, 11, 20, 20, 51, 44),
            at(2026, 1, 5, 0, 0, 9),
            at(2024, 2, 29, 12, 30, 0),
            at(1999, 12, 31, 23, 59, 59),
        ] {
            assert_eq!(read(&moment.afk_text()).unwrap(), moment);
        }
    }

    #[test]
    fn reads_as_strptime_does() {
        // Each of these parses in CPython to the same moment.
        let moment = at(2026, 11, 5, 8, 1, 4);
        for text in [
            "Nov 05 2026 08:01:04AM",
            "nov 5 2026 8:1:4am",
            "NOV\t 5\u{3000}2026  08:01:04Am",
            "Nov 5 \u{662}\u{660}\u{662}\u{666} 08:0\u{661}:\u{664}AM",
            "Nov\u{1c}5\u{1f}2026\u{1d}08:\u{661}:0\u{664}AM",
        ] {
            assert_eq!(read(text).unwrap(), moment, "{text:?}");
        }
        // And each of these is a ValueError there.
        for text in [
            "",
            "Nov 05 2026 08:01:04",
            " Nov 05 2026 08:01:04AM",
            "Nov 05 2026 08:01:04AM ",
            "Nov 05 2026 08:01:04 AM",
            "Nov 5 26 08:01:04AM",
            "Nov 5 20260 08:01:04AM",
            "Nov 35 2026 08:01:04AM",
            "Nov 00 2026 08:01:04AM",
            "Nov 005 2026 08:01:04AM",
            "Nov 31 2026 08:01:04AM",
            "Feb 29 2026 08:01:04AM",
            "Nov 05 0000 08:01:04AM",
            "Nov 05 2026 13:01:04AM",
            "Nov 05 2026 00:01:04AM",
            "Nov 05 2026 08:60:04AM",
            "Nov 05 2026 08:01:61AM",
            "Nov 05 2026 08:01:075AM",
            "November 05 2026 08:01:04AM",
            "Nov 05 2026 08-01-04AM",
            "20 Nov 2026 08:01:04AM",
            // Digits of other scripts count only where the pattern says "any digit".
            "Nov \u{665} 2026 08:01:04AM",
            "Nov 0\u{665} 2026 08:01:04AM",
            "Nov 3\u{660} 2026 08:01:04AM",
            "Nov 5 2026 0\u{668}:01:04AM",
            "Nov 5 2026 08:01:6\u{661}AM",
            "\u{17f}ep 5 2026 08:01:04AM",
            "Nov 5 2026 08:01:04\u{ff21}M",
        ] {
            assert_eq!(
                read(text).map_err(|error| error.kind),
                Err("ValueError"),
                "{text:?}"
            );
        }
        assert_eq!(
            read("Nov 2\u{665} 2026 12:00:00am").unwrap(),
            at(2026, 11, 25, 0, 0, 0)
        );
        assert_eq!(
            read("Nov 5 2026 12:00:00PM").unwrap(),
            at(2026, 11, 5, 12, 0, 0)
        );
        assert_eq!(
            DateTime::from_afk_text(&PyValue::int(5)).unwrap_err().kind,
            "TypeError"
        );
    }

    #[test]
    fn time_between() {
        let start = at(2026, 11, 20, 20, 51, 44);
        // Expected values are CPython's `str(later - start)`.
        assert_eq!(start.plus_seconds(5).unwrap().since(&start), "0:00:05");
        assert_eq!(start.plus_seconds(3_725).unwrap().since(&start), "1:02:05");
        assert_eq!(
            start.plus_seconds(DAY).unwrap().since(&start),
            "1 day, 0:00:00"
        );
        assert_eq!(
            start.plus_seconds(3 * DAY + 61).unwrap().since(&start),
            "3 days, 0:01:01"
        );
        assert_eq!(
            start.plus_seconds(-5).unwrap().since(&start),
            "-1 day, 23:59:55"
        );
        assert_eq!(
            start.plus_seconds(-2 * DAY).unwrap().since(&start),
            "-2 days, 0:00:00"
        );
        assert_eq!(
            at(2027, 1, 1, 0, 0, 0).since(&at(2026, 12, 31, 23, 59, 59)),
            "0:00:01"
        );
        assert_eq!(
            at(2000, 3, 1, 0, 0, 0).since(&at(2000, 2, 28, 0, 0, 0)),
            "2 days, 0:00:00"
        );
        assert_eq!(
            at(2000, 1, 1, 0, 0, 0)
                .plus_seconds(4_000_000_000)
                .unwrap()
                .afk_text(),
            "Oct 03 2126 07:06:40AM"
        );
    }
}
