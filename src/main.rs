extern crate getopts;

use getopts::Options;
use std::env;

#[derive(Debug)]
enum Mode {
    Split(String),
    Extract(String),
    CSV,
    TSV,
}


fn parse_options(args: &[String]) -> (Mode, Vec<String>) {
    let mut opts = Options::new();
    opts.optopt("d", "delimiter", "set the field delimiter", "DELIMITER");
    opts.optopt("e", "extract", "extract fields from a pattern", "PATTERN");
    opts.optflag("", "csv", "extract from CSV");
    opts.optflag("", "tsv", "extract from TSV");
    opts.optopt("f", "fields", "set the fields to select", "FIELDS");

    let matches = opts.parse(&args[..]).unwrap();
    if matches.opt_present("d") {
        return (Mode::Split(matches.opt_str("d").unwrap()), matches.free);
    }
    if matches.opt_present("e") {
        return (Mode::Extract(matches.opt_str("e").unwrap()), matches.free);
    }
    if matches.opt_present("csv") {
        return (Mode::CSV, matches.free);
    }
    if matches.opt_present("tsv") {
        return (Mode::TSV, matches.free);
    }
    panic!("No valid option");
}

fn main() {
    let args: Vec<String> = env::args().skip(1).collect();
    let (mode, free) = parse_options(&args[..]);

    println!("Hello, world!");
    println!("Args: {:?}", args);
    println!("Mode: {:?}", mode);
    println!("Free: {:?}", free);
}
