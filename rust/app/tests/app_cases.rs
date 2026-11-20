//! Replays `rust/app-cases` against the binary built from this crate: what
//! `rust-anything app replay` does, with nothing but cargo. The cases were recorded from
//! `python3 multi_client.py`. Those that start clients start a stand-in for the bot with
//! `python3`, which therefore has to be on `PATH`.

#[test]
fn the_recorded_cases() {
    trycmd::TestCases::new().case("../app-cases/*.toml");
}
