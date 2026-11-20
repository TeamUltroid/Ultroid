use std::ffi::OsString;
use std::io::Write;
use std::path::Path;
use std::process::{Command, ExitCode, ExitStatus};

const ROOT: &str = concat!(env!("CARGO_MANIFEST_DIR"), "/../..");
const RUN: &[&str] = &["python3", "multi_client.py"];
const FALLBACK_LOG: &str = "RUST_ANYTHING_FALLBACK_LOG";

fn resolve(word: &str) -> OsString {
    if word.starts_with('-') {
        return word.into();
    }
    let path = Path::new(ROOT).join(word);
    let looks_like_path = word.contains('/') || word.contains('\\') || path.is_file();
    if looks_like_path && path.exists() {
        return std::path::absolute(&path).unwrap_or(path).into_os_string();
    }
    word.into()
}

fn log() -> Option<std::fs::File> {
    let path = std::env::var_os(FALLBACK_LOG)?;
    std::fs::OpenOptions::new()
        .create(true)
        .append(true)
        .open(path)
        .ok()
}

/// Tells `rust-anything app replay` this build counts its fallbacks, even when it makes none.
pub fn report_fallbacks() {
    let _ = log();
}

/// Runs the original with the same arguments, stdin and environment, and passes its output and
/// exit code through. Each call is one fallback.
pub fn run(args: &[OsString]) -> ExitCode {
    run_with(args, None)
}

/// For glue that read stdin and then declines the case: runs the original with `input` as its
/// stdin. Each call is one fallback.
#[allow(dead_code)]
pub fn run_with_stdin(args: &[OsString], input: &[u8]) -> ExitCode {
    run_with(args, Some(input))
}

fn run_with(args: &[OsString], input: Option<&[u8]>) -> ExitCode {
    if let Some(mut file) = log() {
        let line: Vec<String> = args
            .iter()
            .map(|a| a.to_string_lossy().into_owned())
            .collect();
        let _ = writeln!(file, "{}", line.join(" "));
    }
    let Some((program, rest)) = RUN.split_first() else {
        return ExitCode::from(127);
    };
    let mut command = Command::new(resolve(program));
    command.args(rest.iter().map(|w| resolve(w))).args(args);
    #[cfg(windows)]
    if Path::new(program)
        .file_stem()
        .and_then(|name| name.to_str())
        .is_some_and(|name| {
            ["python", "python3", "py"]
                .iter()
                .any(|candidate| name.eq_ignore_ascii_case(candidate))
        })
        && std::env::var_os("PYTHONIOENCODING").is_none()
    {
        command.env("PYTHONIOENCODING", "utf-8");
    }
    let status = match input {
        None => command.status(),
        Some(input) => command
            .stdin(std::process::Stdio::piped())
            .spawn()
            .and_then(|mut child| {
                if let Some(mut pipe) = child.stdin.take() {
                    let _ = pipe.write_all(input);
                }
                child.wait()
            }),
    };
    match status {
        Ok(status) => ExitCode::from(exit_code(status)),
        Err(e) => {
            eprintln!(
                "front door: cannot run the original `{}`: {e}",
                RUN.join(" ")
            );
            ExitCode::from(127)
        }
    }
}

fn exit_code(status: ExitStatus) -> u8 {
    if let Some(code) = status.code() {
        return (code & 0xff) as u8;
    }
    #[cfg(unix)]
    {
        use std::os::unix::process::ExitStatusExt;
        if let Some(signal) = status.signal() {
            return (128 + signal) as u8;
        }
    }
    1
}
