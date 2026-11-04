import re
from datetime import datetime

# =========================================================
# ADMIN ACCOUNT
# =========================================================
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# =========================================================
# REGISTERED STUDENTS
# Add more students by copying one student dictionary.
# School ID format: 02-2627-000000
# =========================================================
STUDENTS = [
    {
        "school_id": "02-2627-002561",
        "password": "novo123xd",
        "name": "James Novo",
        "section": "BSIT1-02",
        "gender": "Male",
        "birthdate": "2008-11-23",
    },
    {
        "school_id": "02-2627-002562",
        "password": "macalawi123xd",
        "name": "Jahmel Macalawi",
        "section": "BSIT1-02",
        "gender": "Male",
        "birthdate": "2005-03-14",
    },
]

# =========================================================
# SETTINGS
# =========================================================
VISITOR_FILE = "visitors.txt"
SEP = "|"
ID_PATTERN = re.compile(r"^\d{2}-\d{4}-\d{6}$")
LINE = "=" * 38
MAX_ATTEMPTS = 3
STILL_INSIDE = "Still Inside"
NO_TIME_OUT = "No Time-Out"


# =========================================================
# CHECK THE STUDENT LIST
# =========================================================
def check_student_list():
    """Return valid students and warn about invalid entries."""
    valid = []
    seen_ids = set()

    for number, student in enumerate(STUDENTS, start=1):
        problems = []

        sid = str(student.get("school_id", "")).strip()
        password = str(student.get("password", ""))
        name = str(student.get("name", "")).strip()
        section = str(student.get("section", "")).strip()
        gender = str(student.get("gender", "")).strip()
        birthdate = str(student.get("birthdate", "")).strip()

        if not ID_PATTERN.fullmatch(sid):
            problems.append("school_id must look like 02-2627-000000")
        elif sid in seen_ids:
            problems.append("school_id is a duplicate")

        if not password.strip() or " " in password:
            problems.append("password cannot be empty or have spaces")

        if not name or not all(char.isalpha() or char == " " for char in name):
            problems.append("name must contain letters and spaces only")

        if not section:
            problems.append("section cannot be empty")

        if gender not in ("Male", "Female"):
            problems.append('gender must be "Male" or "Female"')

        try:
            datetime.strptime(birthdate, "%Y-%m-%d")
        except ValueError:
            problems.append("birthdate must be YYYY-MM-DD")

        if SEP in sid + name + section:
            problems.append(f"fields cannot contain the '{SEP}' character")

        if problems:
            print(f"WARNING: Student #{number} ({sid or 'no ID'}) skipped:")
            for problem in problems:
                print("   -", problem)
        else:
            seen_ids.add(sid)
            valid.append({
                "school_id": sid,
                "password": password,
                "name": name,
                "section": section,
                "gender": gender,
                "birthdate": birthdate,
            })

    return valid


REGISTERED = check_student_list()


def find_student(school_id):
    for student in REGISTERED:
        if student["school_id"] == school_id:
            return student
    return None


# =========================================================
# VISITOR FILE HELPERS
# =========================================================
def load_visitors():
    visitors = []

    try:
        with open(VISITOR_FILE, "r", encoding="utf-8") as file:
            for line in file:
                parts = line.rstrip("\n").split(SEP)
                if len(parts) != 6:
                    continue

                visitors.append({
                    "school_id": parts[0],
                    "name": parts[1],
                    "section": parts[2],
                    "date": parts[3],
                    "time_in": parts[4],
                    "time_out": parts[5],
                })
    except FileNotFoundError:
        pass

    return visitors


def to_line(visitor):
    fields = [
        visitor["school_id"],
        visitor["name"],
        visitor["section"],
        visitor["date"],
        visitor["time_in"],
        visitor["time_out"],
    ]
    return SEP.join(fields) + "\n"


def save_visitors(visitors):
    with open(VISITOR_FILE, "w", encoding="utf-8") as file:
        for visitor in visitors:
            file.write(to_line(visitor))


def append_visitor(visitor):
    with open(VISITOR_FILE, "a", encoding="utf-8") as file:
        file.write(to_line(visitor))


def today():
    return datetime.now().strftime("%Y-%m-%d")


def close_old_visits():
    """Close unfinished visits from previous days."""
    visitors = load_visitors()
    changed = False

    for visitor in visitors:
        if visitor["time_out"] == STILL_INSIDE and visitor["date"] != today():
            visitor["time_out"] = NO_TIME_OUT
            changed = True

    if changed:
        save_visitors(visitors)


def is_inside(school_id):
    return any(
        visitor["school_id"] == school_id
        and visitor["time_out"] == STILL_INSIDE
        for visitor in load_visitors()
    )


def show_date(date_text):
    """Convert YYYY-MM-DD to a readable date."""
    try:
        date_value = datetime.strptime(date_text, "%Y-%m-%d")
        return f"{date_value.strftime('%B')} {date_value.day}, {date_value.year}"
    except ValueError:
        return date_text


def show_time(time_text):
    """Convert 24-hour time to a readable 12-hour time."""
    try:
        time_value = datetime.strptime(time_text, "%H:%M:%S")
        return time_value.strftime("%I:%M %p").lstrip("0").lower()
    except ValueError:
        return time_text


def show_name(full_name):
    """Display 'James Novo' as 'Novo, James'."""
    parts = full_name.split()
    if len(parts) < 2:
        return full_name
    return f"{parts[-1]}, {' '.join(parts[:-1])}"


# =========================================================
# INPUT HELPERS
# =========================================================
def pause():
    input("\nPress Enter to continue...")


def header(title):
    print("\n" + LINE)
    print(f"   {title}")
    print(LINE)


def get_text(label):
    """Get required text that is not empty."""
    while True:
        value = input(f"{label}: ").strip()

        if not value:
            print(f"  {label} cannot be empty or spaces only.")
        elif SEP in value:
            print(f"  {label} cannot contain the '{SEP}' character.")
        else:
            return value


def get_school_id():
    """Get a School ID in the required format."""
    while True:
        school_id = input("School ID: ").strip()

        if not school_id:
            print("  School ID cannot be empty or spaces only.")
        elif not ID_PATTERN.fullmatch(school_id):
            print("  Invalid format. Use 02-2627-000000.")
        else:
            return school_id


def get_password():
    while True:
        password = input("Password: ")

        if not password.strip():
            print("  Password cannot be empty or spaces only.")
        else:
            return password


# =========================================================
# ADMIN SIDE
# =========================================================
def print_record(visitor):
    print("-" * 38)
    print(f"School ID : {visitor['school_id']}")
    print(f"Name      : {visitor['name']}")
    print(f"Section   : {visitor['section']}")
    print(f"Date      : {show_date(visitor['date'])}")
    print(f"Time In   : {show_time(visitor['time_in'])}")
    print(f"Time Out  : {show_time(visitor['time_out'])}")


def view_visitors():
    header("VISITORS CURRENTLY INSIDE")
    inside = [
        visitor for visitor in load_visitors()
        if visitor["time_out"] == STILL_INSIDE
    ]

    if not inside:
        print("No visitors inside right now.")
        return

    for visitor in inside:
        print_record(visitor)

    print("-" * 38)
    print(f"Total inside: {len(inside)}")


def view_all_visitors():
    header("ALL VISITOR RECORDS")
    visitors = load_visitors()

    if not visitors:
        print("No visitor records found.")
        return

    for visitor in visitors:
        print_record(visitor)

    print("-" * 38)
    print(f"Total records: {len(visitors)}")


def search_visitor():
    header("SEARCH VISITOR")
    keyword = get_text("Enter School ID or Name").lower()

    matches = [
        visitor for visitor in load_visitors()
        if keyword in visitor["school_id"].lower()
        or keyword in visitor["name"].lower()
    ]

    if not matches:
        print("No matching visitor found.")
        return

    for visitor in matches:
        print_record(visitor)

    print("-" * 38)
    print(f"Matches found: {len(matches)}")


def print_day(date_text, records):
    """Print one day's visitor records in a simple table."""
    headings = ["Name", "Student ID", "Section", "Time In", "Time Out"]
    records = sorted(records, key=lambda item: item["time_in"])

    rows = [
        [
            show_name(visitor["name"]),
            visitor["school_id"],
            visitor["section"],
            show_time(visitor["time_in"]),
            show_time(visitor["time_out"]),
        ]
        for visitor in records
    ]

    blank_count = max(3, len(rows) + 1) - len(rows)
    rows += [["", "", "", "", ""] for _ in range(blank_count)]

    widths = [
        max(len(heading), *(len(row[index]) for row in rows))
        for index, heading in enumerate(headings)
    ]

    def make_line(cells):
        return "| " + " | ".join(
            cell.ljust(width)
            for cell, width in zip(cells, widths)
        ) + " |"

    print(f"\nDATE: {show_date(date_text).upper()}")
    print(make_line(headings))

    for row in rows:
        print(make_line(row))


def ask_date(text):
    """Accept MM-DD-YYYY or MM-DD-YY and return YYYY-MM-DD."""
    for date_format in ("%m-%d-%Y", "%m-%d-%y"):
        try:
            return datetime.strptime(text, date_format).strftime("%Y-%m-%d")
        except ValueError:
            pass
    return None


def view_visitor_per_day():
    header("VISITOR PER DAY SUMMARY")
    visitors = load_visitors()

    print("Enter a date (MM-DD-YYYY, example 10-20-2026)")
    choice = input("or press Enter to see all days: ").strip()

    days = {}
    for visitor in visitors:
        days.setdefault(visitor["date"], []).append(visitor)

    if choice:
        wanted_date = ask_date(choice)

        if wanted_date is None:
            print("\nInvalid date. Use MM-DD-YYYY (example: 10-20-2026).")
            return

        print_day(wanted_date, days.get(wanted_date, []))
        return

    if not days:
        print("\nNo visitor records found.")
        return

    for date_text in sorted(days):
        print_day(date_text, days[date_text])


def admin_login():
    """Return True when the admin logs in successfully."""
    header("ADMIN LOGIN")

    for attempt in range(1, MAX_ATTEMPTS + 1):
        username = get_text("Username")
        password = get_password()

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            print("\nAdmin login successful!")
            return True

        attempts_left = MAX_ATTEMPTS - attempt
        if attempts_left > 0:
            print(
                f"\nIncorrect username or password. "
                f"{attempts_left} attempt(s) left."
            )

    print("\nToo many failed attempts. Returning to main menu.")
    return False


def admin_menu():
    while True:
        print("\n======================")
        print("ADMIN MENU")
        print("======================")
        print("1. View Visitors (Currently Inside)")
        print("2. View All Visitor Records")
        print("3. Search Visitor")
        print("4. View Visitor Per Day Summary")
        print("5. Log Out")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            close_old_visits()
            view_visitors()
            pause()
        elif choice == "2":
            close_old_visits()
            view_all_visitors()
            pause()
        elif choice == "3":
            close_old_visits()
            search_visitor()
            pause()
        elif choice == "4":
            close_old_visits()
            view_visitor_per_day()
            pause()
        elif choice == "5":
            print("\nAdmin logged out.")
            break
        else:
            print("\nInvalid choice. Please choose from 1 to 5.")
            pause()


def show_day_table(date_text):
    """Show all visitors recorded on the given date."""
    records = [
        visitor for visitor in load_visitors()
        if visitor["date"] == date_text
    ]
    print_day(date_text, records)


# =========================================================
# STUDENT SIDE
# =========================================================
def student_login():
    """Log in with School ID and password; return student or None."""
    header("STUDENT LOGIN")

    school_id = get_school_id()
    password = get_password()
    student = find_student(school_id)

    if student is None:
        print("\nSchool ID is not registered. Please see the librarian.")
        return None

    if student["password"] != password:
        print("\nIncorrect School ID or Password. Login failed.")
        return None

    print(f"\nLogin successful! Welcome, {student['name']}.")
    return student


def time_in(student):
    header("TIME IN")
    close_old_visits()
    school_id = student["school_id"]

    if is_inside(school_id):
        print("You are already inside the library. Please Time Out first.")
        return

    now = datetime.now()
    visitor = {
        "school_id": school_id,
        "name": student["name"],
        "section": student["section"],
        "date": now.strftime("%Y-%m-%d"),
        "time_in": now.strftime("%H:%M:%S"),
        "time_out": STILL_INSIDE,
    }

    append_visitor(visitor)
    print("Time In successful!")
    show_day_table(visitor["date"])


def time_out(student):
    header("TIME OUT")
    close_old_visits()
    school_id = student["school_id"]
    visitors = load_visitors()

    for visitor in visitors:
        if (
            visitor["school_id"] == school_id
            and visitor["time_out"] == STILL_INSIDE
        ):
            visitor["time_out"] = datetime.now().strftime("%H:%M:%S")
            save_visitors(visitors)
            print("Time Out successful!")
            show_day_table(visitor["date"])
            return

    print("No active visit found. Please Time In first.")


def student_menu(student):
    while True:
        print("\n======================")
        print(f"STUDENT MENU - {student['name']}")
        print("======================")
        print("1. Time In")
        print("2. Time Out")
        print("3. Log Out")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            time_in(student)
            pause()
        elif choice == "2":
            time_out(student)
            pause()
        elif choice == "3":
            print("\nStudent logged out.")
            break
        else:
            print("\nInvalid choice. Please choose from 1 to 3.")
            pause()


# =========================================================
# MAIN MENU
# =========================================================
def main():
    close_old_visits()

    while True:
        print("\n======================")
        print("Digital Library Visitor Logbook")
        print("======================")
        print("1. Admin Login")
        print("2. Student Login")
        print("3. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            success = admin_login()
            if success:
                admin_menu()
            else:
                pause()
        elif choice == "2":
            student = student_login()
            if student:
                student_menu(student)
            else:
                pause()
        elif choice == "3":
            print("\nThank you! Goodbye!")
            break
        else:
            print("\nInvalid choice. Please choose from 1 to 3.")
            pause()


if __name__ == "__main__":
    main()
