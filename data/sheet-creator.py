#! /usr/bin/env python3
#
# This program produces sample CSV files
# using typed headers
#
# The header names are taken from the CSV
# export of a French bank account at the "Caisse d'Épargne".
#
import csv
import datetime
from pathlib import Path
from typing import Tuple,List,Optional,Dict,Union
from random import choice,randint,random


def parse_french_date(datestring : str) -> datetime.date:
    return datetime.datetime.strptime(datestring, "%d/%m/%Y").date()

def print_french_date(date : datetime.date) -> str:
    return f"{date.day:02d}/{date.month:02d}/{date.year:04d}"




## Constants for CSV generation (headers)

# Base headers
HEADERS_BASIC = [
        "Libelle operation",
        "Libelle simplifie",
        "Informations complementaires",
        "Type operation",
        "Debit","Credit"]

# Extra information provided by the bank
HEADERS_ANNOT = [
        "Reference",
        "Pointage operation",
        "Categorie",
        "Sous categorie",
        ]

# All the date fields
HEADERS_DATES = [
        "Date de comptabilisation",
        "Date operation",
        "Date de valeur",
        ]

## Constants for CSV generation (data)
CATEGORIES = ["Vacances", "Logement", "Restauration"]
SUBCATEGORIES = ["-"]
WORDS = ["Baguette", "Épice", "Marché", "France", "Pharmacie", "Univ", "DDFIP"]
COMPANIES = [
        f"{first}{last}" for first in WORDS for last in WORDS 
        ]

OP_TYPE = ["Virement", "Carte Bleue", "Prélèvement"]
LIBEL_PREFIX = [
        "VIR",
        "CB",
        "PRV",
        ]

LIBEL_INFIX = [
        "FACT",
        "REMUNERATION"
        ]


def random_date(start: datetime.date, end: datetime.date) -> datetime.date:
    """ Produces a random date between the two endpoints (included) """
    δ : datetime.timedelta = end - start
    Δ : int = randint(0, δ.days)
    return start + datetime.timedelta(days=Δ)


def random_basic_transaction() -> Dict[str,str]:
    (prefix,type_op) = choice(list(zip(LIBEL_PREFIX, OP_TYPE)))
    comp   = choice(COMPANIES)
    amount = randint(-55,50) + 5 * random()
    credit = max(amount, 0)
    debit  = min(amount, 0)
    if amount < 0:
        infix = LIBEL_INFIX[0]
    else:
        infix = LIBEL_INFIX[1]
    return {
            "Libelle operation": f"{prefix} {infix} {comp}",
            "Libelle simplifie": f"{infix} {comp}",
            "Informations complementaires": "-",
            "Type operation": type_op,
            "Debit": f"{debit:.2f}",
            "Credit": f"{credit:.2f}",
            }

def random_annotated_transaction() -> Dict[str,str]:
    transaction = random_basic_transaction()
    return {**transaction,
            "Reference": f"{randint(0,200)}",
            "Pointage operation": "0",
            "Categorie": choice(CATEGORIES),
            "Sous categorie": choice(SUBCATEGORIES),
            }

def random_full_transaction(start: datetime.date, end: datetime.date) -> Dict[str,str]:
    transaction = random_annotated_transaction()

    first_date = random_date(start, end)
    new_start = max(start,first_date - datetime.timedelta(days=5))
    new_end   = min(end, first_date + datetime.timedelta(days=5))
    dates = [ print_french_date(random_date(new_start, new_end))
            for _ in range(3) ]
    dates.sort()

    return {**transaction,
            "Date de comptabilisation": dates[0],
            "Date operation": dates[1],
            "Date de valeur": dates[2],
            }

### CSV GENERATION

CSV_TYPE = Tuple[List[str], List[Dict[str,str]]]

def random_basic_transactions(n : int = 15) -> CSV_TYPE:
    return (HEADERS_BASIC, [ random_basic_transaction() for i in range (n)])

def random_annotated_transactions(n : int = 15) -> CSV_TYPE:
    return (HEADERS_BASIC + HEADERS_ANNOT, [ random_annotated_transaction() for i in range (n)])

def random_full_transactions_month(year = 2024, month = 10, n : int = 15) -> CSV_TYPE:
    start = datetime.date(year, month, 1)
    if month + 1 <= 12:
        end   = datetime.date(year, month + 1, 1)
    else:
        end   = datetime.date(year + 1, 1, 1)
    return (HEADERS_BASIC + HEADERS_ANNOT + HEADERS_DATES, [ random_full_transaction(start, end) for i in range (n)])


def write_csv(csv_data : CSV_TYPE, filepath : Path, delimiter = ","):
    with open(filepath, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_data[0],delimiter = delimiter)

        writer.writeheader()
        writer.writerows(csv_data[1])


