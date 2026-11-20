//! `multi_client.py` in Rust: starts every client the environment configures and waits for
//! them. Which clients those are is `ultroid_core::launch`, proven in `launch-rs`; this file is
//! the part that starts processes.
//!
//! The original starts each client with the interpreter it runs under itself. There is no such
//! interpreter here, so the clients are started with `python3` from `PATH`, or with what the
//! `PYTHON` variable names.

use std::process::{Command, ExitCode};

use clap::ArgMatches;
use ultroid_core::launch::{clients, nothing_configured};

/// The arguments on the command line are not looked at, as in the original.
pub fn run(_command: &str, _matches: &ArgMatches) -> ExitCode {
    let found = clients(|name| std::env::var_os(name));
    if found.is_empty() {
        eprintln!("{}", nothing_configured());
        return ExitCode::FAILURE;
    }
    let python = std::env::var_os("PYTHON").unwrap_or_else(|| "python3".into());
    let mut started = Vec::new();
    let mut code = ExitCode::SUCCESS;
    for client in &found {
        match Command::new(&python).args(client.arguments()).spawn() {
            Ok(process) => started.push(process),
            Err(error) => {
                // The original cannot fail here: its interpreter is the one already running.
                let python = python.to_string_lossy();
                eprintln!(
                    "cannot start client {} with {python}: {error}",
                    client.number
                );
                code = ExitCode::FAILURE;
                break;
            }
        }
    }
    // However a client ends, the original waits for the next and then ends with 0.
    for mut process in started {
        let _ = process.wait();
    }
    code
}
