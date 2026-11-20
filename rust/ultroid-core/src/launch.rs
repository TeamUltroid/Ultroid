//! Which clients to start: the launch logic of `multi_client.py`. Proven in `rust/launch-rs`.
//!
//! `multi_client.py` runs up to five Ultroid clients from one environment. Each client is
//! `python3 -m pyUltroid` with five values and its number as arguments, and the values come from
//! five environment variables: plain for the first client, with the suffix `1` to `4` for the
//! second to the fifth.

use std::ffi::{OsStr, OsString};

/// The variables a client needs, in the order their values are passed to it.
pub const VARIABLES: [&str; 5] = [
    "API_ID",
    "API_HASH",
    "SESSION",
    "REDIS_URI",
    "REDIS_PASSWORD",
];

/// The suffix of each client's variables, by the client's number less one.
const SUFFIXES: [&str; 5] = ["", "1", "2", "3", "4"];

/// One client to start.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Client<V> {
    /// 1 to 5. The client names its log file after it.
    pub number: usize,
    /// The values of [`VARIABLES`], in that order.
    pub values: [V; 5],
}

impl<V: AsRef<OsStr>> Client<V> {
    /// What follows the interpreter on the command line: `-m pyUltroid`, the five values and
    /// the number.
    pub fn arguments(&self) -> Vec<OsString> {
        let values = self
            .values
            .iter()
            .map(|value| value.as_ref().to_os_string());
        let number = OsString::from(self.number.to_string());
        let module = ["-m", "pyUltroid"].map(OsString::from);
        module.into_iter().chain(values).chain([number]).collect()
    }
}

/// The clients `multi_client.py` starts for an environment, in the order it starts them.
///
/// `variable` gives the value of an environment variable, as `os.environ.get` does. A client is
/// started when all five of its variables are there and none is empty. One that is not
/// configured is skipped, so the third can run without the second.
pub fn clients<V: AsRef<OsStr>>(variable: impl Fn(&str) -> Option<V>) -> Vec<Client<V>> {
    let configured = |(at, suffix): (usize, &&str)| {
        let value = |name: &&str| {
            let value = variable(&format!("{name}{suffix}"))?;
            (!value.as_ref().is_empty()).then_some(value)
        };
        let values: Vec<V> = VARIABLES.iter().map_while(value).collect();
        let values = values.try_into().ok()?;
        Some(Client {
            number: at + 1,
            values,
        })
    };
    SUFFIXES.iter().enumerate().filter_map(configured).collect()
}

/// What `multi_client.py` leaves with when no client is configured. Python prints it to the
/// error output and ends with status 1.
pub fn nothing_configured() -> String {
    let variables = VARIABLES.join(", ");
    format!("No client configured: set {variables} (suffix 1-4 for extra clients).")
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::collections::HashMap;

    fn started(environment: &[(&str, &str)]) -> Vec<(usize, Vec<String>)> {
        let environment: HashMap<&str, &str> = environment.iter().copied().collect();
        let found = clients(|name| environment.get(name).copied());
        let values = |client: Client<&str>| client.values.map(str::to_string).to_vec();
        found
            .into_iter()
            .map(|client| (client.number, values(client)))
            .collect()
    }

    const FIRST: [(&str, &str); 5] = [
        ("API_ID", "1"),
        ("API_HASH", "h"),
        ("SESSION", "s"),
        ("REDIS_URI", "u"),
        ("REDIS_PASSWORD", "p"),
    ];

    #[test]
    fn the_first_client_has_no_suffix() {
        let values = ["1", "h", "s", "u", "p"].map(str::to_string).to_vec();
        assert_eq!(started(&FIRST), [(1, values)]);
        assert_eq!(started(&[]), []);
    }

    #[test]
    fn a_missing_or_empty_variable_is_no_client() {
        for skip in 0..FIRST.len() {
            let mut environment = FIRST.to_vec();
            environment.remove(skip);
            assert_eq!(started(&environment), [], "without {}", FIRST[skip].0);
            let mut environment = FIRST.to_vec();
            environment[skip].1 = "";
            assert_eq!(started(&environment), [], "empty {}", FIRST[skip].0);
        }
    }

    #[test]
    fn the_suffix_is_one_less_than_the_number() {
        let environment = [
            ("API_ID2", "3"),
            ("API_HASH2", "h"),
            ("SESSION2", "s"),
            ("REDIS_URI2", "u"),
            ("REDIS_PASSWORD2", "p"),
            // A suffix of 5 is no client, and neither is one of 0.
            ("API_ID5", "6"),
            ("API_HASH5", "h"),
            ("SESSION5", "s"),
            ("REDIS_URI5", "u"),
            ("REDIS_PASSWORD5", "p"),
        ];
        let values = ["3", "h", "s", "u", "p"].map(str::to_string).to_vec();
        assert_eq!(started(&environment), [(3, values)]);
    }

    #[test]
    fn the_command_line_of_a_client() {
        let client = Client {
            number: 2,
            values: ["1", "h", "s", "u", "p"],
        };
        let arguments = ["-m", "pyUltroid", "1", "h", "s", "u", "p", "2"].map(OsString::from);
        assert_eq!(client.arguments(), arguments);
        assert_eq!(
            nothing_configured(),
            "No client configured: set API_ID, API_HASH, SESSION, REDIS_URI, REDIS_PASSWORD \
             (suffix 1-4 for extra clients)."
        );
    }
}
