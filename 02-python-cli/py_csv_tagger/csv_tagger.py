#!/usr/bin/env python3

# Data Driven Python
from typing import Optional, List, Dict, Callable, Tuple
from pydantic import BaseModel, parse_obj_as, parse_raw_as
import datetime

# calendar printing
import calendar

# Paths, csv's
from pathlib import Path
import csv
import json

# Command Line Interface
import click

import requests


#
#
# Structuration of the code is as follows.
#
# The first objects correspond to the data this CLI program
# manages. This data is a (tagged) spreadsheet, with extra information
# such as column mappings, statistics, and event log.
#
# The following conversion functions are given
# CSV -> State
# State -> String
# String -> State
#
# In order to maintain compatibility with
# other systems, the State is serialised into a CSV file
# with the extra information added on a first line prepended.

DATE_FORMAT = "%d/%m/%Y"

class CSVLine(BaseModel):
    _content: List[str]
    dates: Dict[str, datetime.date]
    tag: Optional[str]
    infos: Dict[str, str]
    debit: float
    credit: float


class CSVMapping(BaseModel):
    dates: Dict[str, int]
    tag: int
    infos: Dict[str, int]
    debit: int
    credit: int


class CSVFile(BaseModel):
    content: List[List[str]]
    start: int
    path: Path


class State(BaseModel):
    cursor: int
    mapping: CSVMapping
    data: List[CSVLine]


def parse_csv(p: Path, delimiter=";", quotechar="|") -> CSVFile:
    with open(p, "r", newline="") as f:
        r = csv.reader(f, delimiter=delimiter, quotechar=quotechar)
        return CSVFile(path=p, start=0, content=[list(row) for row in r])


def render_csv_line(l: List[str]) -> str:
    return "\n".join(f"\t- [{i}] {v}" for (i, v) in enumerate(l))


def interactive_parse_csv(p: Path) -> CSVFile:
    sep = ","
    quo = "|"
    start = 1
    cont = False
    c = None
    while True:
        print(
            f"Parsing {p} with separator {sep} and delimiter {quo} starting from line {start}"
        )
        c = parse_csv(p, delimiter=sep, quotechar=quo)
        c.start = start
        l0 = c.content[0]
        n0 = len(l0)
        print(f"The first line has {n0} elements:")
        print(render_csv_line(l0))
        print(f"The selected start is {start} and contains the following line:")
        print(sep.join(c.content[start]))

        cont = input("Does it seem okay? [yes/no]: ")
        if cont == "yes":
            return c

        sep = input("Please enter a separator [\\n \\t ; ,]: ") or sep
        quo = input("Please enter a quote character [' \" |]: ") or quo
        start = min(
            max(0, int(input("Please enter a starting line [0,1,..]: ") or start)),
            len(c.content) - 1,
        )


def parse_csv_line(ctn: List[str], mapping: CSVMapping) -> CSVLine:
    try:
        debit = float(ctn[mapping.debit])
    except ValueError:
        debit = 0

    try:
        credit = float(ctn[mapping.credit])
    except ValueError:
        credit = 0

    return CSVLine(
        _content=ctn,
        dates={
            datename: datetime.datetime.strptime(ctn[datecolumn], DATE_FORMAT)
            for (datename, datecolumn) in mapping.dates.items()
        },
        tag=None,
        infos={
            infoname: ctn[infocolumn]
            for (infoname, infocolumn) in mapping.infos.items()
        },
        debit=credit,
        credit=debit,
    )


def interactive_define_mapping(c: CSVFile) -> CSVMapping:
    # TODO: allow iterative constructions
    mapping = CSVMapping(dates={}, tag=0, infos={}, debit=0, credit=0)
    first_line = c.content[c.start]
    for (i, (a, b)) in enumerate(zip(c.content[0], first_line)):
        print(f"- [{i}] {a} / {b} ")
        name = input("\t name [_ to ignore, credit, debit, custom]: ") or a
        # Bunch of early returns to avoid too many questions
        if name == a:
            mapping.infos[name] = i
            continue
        elif name == "_":
            continue
        elif name == "credit":
            mapping.credit = i
            continue
        elif name == "debit":
            mapping.debit = i
            continue

        # In corner cases, we have to ask the user what they mean
        dtyp = input("\t type [f s d]: ") or "s"
        if dtyp == "s":
            mapping.infos[name] = i
        elif dtyp == "d":
            mapping.dates[name] = i
        else:
            print(f"I don't know what to do with {name} and {dtyp}... Ignored.")

    fake_line = [f"{a} / {b}" for (a, b) in zip(c.content[0], c.content[c.start])]
    print(render_csv_line(fake_line))
    parsed_line = parse_csv_line(first_line, mapping)
    print(parsed_line)
    return mapping


# def open_with_template( p : Path, s : State) -> State:
# --> opens the CSV file with the same parameters as state.
# --> this is useful if we keep receiving CSV files with similar
# --> formatting.


def upgrade_csv(c: CSVFile, m: CSVMapping) -> State:
    return State(
        cursor=0,
        mapping=m,
        data=[parse_csv_line(line, m) for line in c.content[c.start :]],
    )


def read_state(p : Path) -> State:
    with open(p, "r") as f:
        return State.parse_obj(json.load(f))

def write_state(s : State, p : Path):
    with open(p, "w") as f:
        f.write(s.json())


def one_character_summary(s: State, pos: int, l: CSVLine) -> str:
    out = ""
    if l.tag is not None:
        out = "#"
    else:
        out = "_"
    if pos == s.cursor:
        return f"[{out}]"
    else:
        return out


def print_summary(s: State):
    status = "".join(one_character_summary(s, i, l) for (i, l) in enumerate(s.data))
    total = len(s.data)
    tagged = len(list(filter(lambda x: x.tag is not None, s.data)))
    skipped = len(list(filter(lambda x: x.tag is None, s.data[: s.cursor])))
    print(f"N: {tagged} / {total}. {skipped} items skipped.")
    print(status)

class DayInMonthHighlightingCalendar(calendar.TextCalendar):
    def __init__(self, days_to_highlight : List[datetime.date]):
        super().__init__()
        self._days_to_highlight = days_to_highlight

    def formatday(self, day: int, weekday: int, width: int, year: int, month: int) -> str:
        s = super().formatday(day, weekday, width)
        if day != 0 and datetime.date(year, month, day) in self._days_to_highlight:
            s = f"\033[7m{s}\033[0m"
        return s

    def formatweek(self, theweek : List[Tuple[int,int]], width : int, year: int, month : int):
        print(f"{theweek} / {year} / {month}", flush=True)
        return ' '.join(self.formatday(d, wd, width, year, month) for (d,wd) in theweek)

    def formatmonth(self, theyear, themonth, w=0, l=0):
        w = max(2, w)
        l = max(1, l)
        s = self.formatmonthname(theyear, themonth, 7 * (w + 1) - 1)
        s = s.rstrip()
        s += '\n' * l
        s += self.formatweekheader(w).rstrip()
        s += '\n' * l
        for week in self.monthdays2calendar(theyear, themonth):
            s += self.formatweek(week, w, theyear, themonth).rstrip()
            s += '\n' * l
        return s

def print_line_calendar(s: State):
    dates = s.data[s.cursor].dates
    min_date = min(dates.values())
    max_date = max(dates.values())
    cal = DayInMonthHighlightingCalendar(days_to_highlight=list(dates.values()))
    cal.prmonth(min_date.year, min_date.month)
    # This assumes that we do not have HUGE timespans between min and max
    # (at most a month)
    if min_date.year != max_date.year or min_date.month != max_date.month:
        cal.prmonth(max_date.year, max_date.month)


def print_line_summary(s: State):
    for infoname, infovalue in s.data[s.cursor].infos.items():
        print(f"\t [{infoname}] \t {infovalue}")


def print_line_balance(s: State):
    pos = s.data[s.cursor].credit
    neg = s.data[s.cursor].debit
    print(f"\t +{pos} / {neg} \t {pos - neg}")


def print_line_status(s: State):
    tag = s.data[s.cursor].tag
    if tag is None:
        tag = "UNTAGGED"
    print(f"\t [tag] \t {tag}")


def next_line(s: State):
    s.cursor = (s.cursor + 1) % len(s.data)


def prev_line(s: State):
    s.cursor = (s.cursor - 1) % len(s.data)


def next_tag(s: State):
    for i, v in enumerate(s.data[s.cursor + 1 :]):
        if v.tag is None:
            s.cursor = 1 + i + s.cursor
            return


def prev_tag(s: State):
    for i, v in enumerate(reversed(s.data[: s.cursor])):
        if v.tag is None:
            s.cursor = s.cursor - i - 1
            return


def update_tag(name: str) -> Callable[[State], None]:
    def _update(s: State):
        s.data[s.cursor].tag = name
        next_tag(s)

    return _update


actions = {
    "<": prev_line,
    ">": next_line,
    "": next_line,
    "«": prev_tag,
    "»": next_tag,
}

def interactive_modify(s : State, p : Path):
    while True:
        print("")
        print_summary(s)
        print_line_calendar(s)
        print_line_summary(s)
        print_line_balance(s)
        print_line_status(s)
        i_action = input("Action: ")
        if i_action == "q" or i_action == "quit":
            break
        action = actions.get(i_action, update_tag(i_action))
        action(s)
        write_state(s, p)

def print_global_summary(s : State):
    tags_credit : Dict[str,float] = {}
    tags_debit  : Dict[str,float] = {}
    tags_count  : Dict[str, int] = {}
    for line in s.data:
        t = line.tag or "UNTAGGED"
        tags_credit[t] = tags_credit.get(t, 0) + line.credit
        tags_debit[t] = tags_debit.get(t, 0) + line.debit
        tags_count[t] = tags_count.get(t, 0) + 1
    for tag,count in tags_count.items():
        pos = tags_credit[tag]
        neg = tags_debit[tag]
        print(f"\t [{tag}] \t {count} items \t +{pos}€ \t {neg}€")


@click.group()
@click.option('--debug/--no-debug', default=False)
def cli(debug):
    click.echo(f"Debug mode is {'on' if debug else 'off'}")


@cli.command()
@click.argument("file", type=Path, required=True)
@click.option(
    "--save",
    "-s",
    type=Path,
    required=False,
    help="the path where state is saved",
)
def new(save: Optional[Path], file : Path):
    # STEP 1: we acquire the data
    c = interactive_parse_csv(file)
    m = interactive_define_mapping(c)
    s = upgrade_csv(c, m)
    save = save or file.with_suffix(".csvt")
    # STEP 2: we update in a loop
    interactive_modify(s, save)
    # STEP 3: we display the results
    print_global_summary(s)

@cli.command()
@click.argument("file", type=Path, required=True)
def resume(file : Path):
    # STEP 1: we acquire the data
    s = read_state(file)
    # STEP 2: we update in a loop
    interactive_modify(s, file)
    # STEP 3: we display the results
    print_summary(s)


if __name__ == "__main__":
    cli()
