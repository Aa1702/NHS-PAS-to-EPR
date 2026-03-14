import csv
import random
import string
from datetime import date, timedelta

random.seed(42)

FIRST_NAMES = [
    "Oliver","Amelia","George","Isla","Harry","Poppy","Jack","Ava","Jacob","Lily",
    "Charlie","Sophie","Alfie","Grace","Freddie","Emily","Archie","Jessica","Oscar",
    "Mia","James","Ruby","William","Evie","Thomas","Chloe","Henry","Ella","Joshua",
    "Scarlett","Noah","Isabella","Mohammed","Layla","Ethan","Sienna","Lucas","Rosie",
    "Mason","Freya","Logan","Alice","Elijah","Millie","Daniel","Daisy","Isaac","Phoebe",
    "Adam","Zoe","Priya","Ravi","Sunita","Deepa","Aisha","Tariq","Fatima","Hassan",
    "Mei","Wei","Yuki","Hana","Sven","Ingrid","Aleksander","Natasha","Ciarán","Aoife",
]

LAST_NAMES = [
    "Smith","Jones","Williams","Taylor","Brown","Davies","Evans","Wilson","Thomas",
    "Roberts","Johnson","Lewis","Walker","Robinson","Wood","Thompson","White","Watson",
    "Jackson","Wright","Green","Harris","Cooper","King","Lee","Martin","Clarke","Scott",
    "Edwards","Turner","Morris","Mitchell","Bell","Ward","Hughes","Harrison","Collins",
    "Carter","Phillips","Patel","Khan","Singh","Ali","Ahmed","Hussain","Begum","Malik",
    "O'Brien","Murphy","Walsh","Ryan","McCarthy","Kowalski","Nowak","Fischer","Müller",
]

BLOOD_TYPES = ["A+","A-","B+","B-","AB+","AB-","O+","O-"]

CORRUPT_DATE_FORMATS = [
    lambda d: d.strftime("%d/%m/%Y"),          # wrong separator style (should be ISO)
    lambda d: d.strftime("%m-%d-%Y"),           # US format
    lambda d: d.strftime("%Y/%m/%d"),           # slash instead of dash
    lambda d: d.strftime("%d %b %Y"),           # e.g. 23 Mar 1985
    lambda d: d.strftime("%Y-%m-") + "00",      # impossible day
    lambda d: d.strftime("%Y-13-%d"),           # impossible month
    lambda d: d.strftime("%Y-%m-%d") + "T00:00",# datetime bleed-in
    lambda d: "",                               # blank date
    lambda d: "NULL",                           # legacy NULL string
    lambda d: "N/A",                            # free-text
    lambda d: str(random.randint(10000, 99999)),# random number instead of date
    lambda d: d.strftime("%Y-%m-%d").replace(
        str(d.year), str(d.year + random.randint(50, 200))
    ),                                          # year far in future
]

BASE_DATE   = date(1930, 1, 1)
LATEST_DOB  = date(2010, 12, 31)
VISIT_START = date(2010, 1, 1)
VISIT_END   = date(2024, 12, 31)

TARGET_BASE = 98_000   

def random_date(start: date, end: date) -> date:
    return start + timedelta(days=random.randint(0, (end - start).days))

def nhs_number() -> str:
    """10-digit NHS number (not Luhn-validated – intentionally loose)."""
    return "".join(random.choices(string.digits, k=10))

def generate_patient() -> dict:
    dob        = random_date(BASE_DATE, LATEST_DOB)
    last_visit = random_date(max(VISIT_START, dob + timedelta(days=1)), VISIT_END)
    return {
        "patient_name": f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
        "nhs_number":   nhs_number(),
        "dob":          dob.isoformat(),
        "blood_type":   random.choice(BLOOD_TYPES),
        "last_visit":   last_visit.isoformat(),
    }

print(f"Generating {TARGET_BASE:,} base patient records …")
records = [generate_patient() for _ in range(TARGET_BASE)]

n_dupes = 2_000
dupe_sources = random.choices(records, k=n_dupes)
records.extend(dupe_sources)
print(f"  ✓ Injected {n_dupes:,} duplicate rows  ({n_dupes/(len(records)):.1%})")

random.shuffle(records)

nhs_blank_indices = random.sample(range(len(records)), k=int(0.05 * len(records)))
for i in nhs_blank_indices:
    records[i] = dict(records[i])  
    records[i]["nhs_number"] = ""
print(f"  ✓ Blanked {len(nhs_blank_indices):,} NHS numbers         (5.0%)")

date_fields     = ["dob", "last_visit"]
n_corrupt_dates = int(0.03 * len(records))
corrupt_indices = random.sample(range(len(records)), k=n_corrupt_dates)

for i in corrupt_indices:
    records[i] = dict(records[i])
    field       = random.choice(date_fields)
    try:
        original = date.fromisoformat(records[i][field])
    except ValueError:
        original = date(1990, 6, 15)   
    corruptor        = random.choice(CORRUPT_DATE_FORMATS)
    records[i][field] = corruptor(original)

print(f"  ✓ Corrupted  {n_corrupt_dates:,} date values            (~3.0%)")


output_path = "legacy_pas_data.csv"
fieldnames  = ["patient_name", "nhs_number", "dob", "blood_type", "last_visit"]

with open(output_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(records)

print(f"\n  Saved {len(records):,} rows → {output_path}")
print("\nData quality summary")
print("─" * 40)
blank_nhs   = sum(1 for r in records if not r["nhs_number"])
print(f"  Blank NHS numbers : {blank_nhs:>6,}  ({blank_nhs/len(records):.1%})")
print(f"  Duplicate rows    : {n_dupes:>6,}  ({n_dupes/len(records):.1%})")
print(f"  Corrupted dates   : {n_corrupt_dates:>6,}  ({n_corrupt_dates/len(records):.1%})")
print(f"  Total rows        : {len(records):>6,}")

