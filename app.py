
from flask import Flask, render_template, request, redirect, url_for
import json
import os
from datetime import date, timedelta
import calendar


app = Flask(__name__)


# =========================================================
# BASE DIRECTORY
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)


# =========================================================
# FILE NAMES
# =========================================================

CUSTOMERS_FILE = os.path.join(
    BASE_DIR,
    "customers.json"
)

DAILY_ENTRIES_FILE = os.path.join(
    BASE_DIR,
    "daily_entries.json"
)

MONTHLY_BILLS_FILE = os.path.join(
    BASE_DIR,
    "monthly_bills.json"
)

CLEARED_BILLS_FILE = os.path.join(
    BASE_DIR,
    "cleared_bills.json"
)


# =========================================================
# CUSTOMER FUNCTIONS
# =========================================================

def load_customers():

    if not os.path.exists(CUSTOMERS_FILE):
        return []

    try:

        with open(
            CUSTOMERS_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

            if isinstance(data, list):
                return data

            return []

    except (
        json.JSONDecodeError,
        OSError
    ):

        return []


def save_customers(customers):

    with open(
        CUSTOMERS_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            customers,
            file,
            indent=4,
            ensure_ascii=False
        )


# =========================================================
# DAILY ENTRY FUNCTIONS
# =========================================================

def load_daily_entries():

    if not os.path.exists(DAILY_ENTRIES_FILE):
        return []

    try:

        with open(
            DAILY_ENTRIES_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

            if isinstance(data, list):
                return data

            return []

    except (
        json.JSONDecodeError,
        OSError
    ):

        return []


def save_daily_entries(entries):

    with open(
        DAILY_ENTRIES_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            entries,
            file,
            indent=4,
            ensure_ascii=False
        )


# =========================================================
# MONTHLY BILL FUNCTIONS
# =========================================================

def load_monthly_bills():

    if not os.path.exists(MONTHLY_BILLS_FILE):
        return []

    try:

        with open(
            MONTHLY_BILLS_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

            if isinstance(data, list):
                return data

            return []

    except (
        json.JSONDecodeError,
        OSError
    ):

        return []


def save_monthly_bills(bills):

    with open(
        MONTHLY_BILLS_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            bills,
            file,
            indent=4,
            ensure_ascii=False
        )


# =========================================================
# CLEARED BILL FUNCTIONS
# =========================================================

def load_cleared_bills():

    if not os.path.exists(CLEARED_BILLS_FILE):
        return []

    try:

        with open(
            CLEARED_BILLS_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

            if isinstance(data, list):
                return data

            return []

    except (
        json.JSONDecodeError,
        OSError
    ):

        return []


def save_cleared_bills(cleared_bills):

    with open(
        CLEARED_BILLS_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            cleared_bills,
            file,
            indent=4,
            ensure_ascii=False
        )


def is_bill_cleared(
    customer_id,
    month_string
):

    cleared_bills = load_cleared_bills()

    for item in cleared_bills:

        try:

            if (
                int(item["customer_id"])
                ==
                int(customer_id)
                and
                item["month"]
                ==
                month_string
            ):

                return True

        except (
            ValueError,
            TypeError,
            KeyError
        ):

            continue

    return False


# =========================================================
# GET ENTRIES FOR A CUSTOMER AND MONTH
# =========================================================

def get_month_entries(
    customer_id,
    year,
    month
):

    entries = load_daily_entries()

    result = []

    for entry in entries:

        try:

            entry_customer_id = int(
                entry["customer_id"]
            )

            if entry_customer_id != int(customer_id):
                continue

            entry_date = date.fromisoformat(
                entry["date"]
            )

            if (
                entry_date.year == year
                and entry_date.month == month
            ):

                result.append(entry)

        except (
            ValueError,
            TypeError,
            KeyError
        ):

            continue

    return result


# =========================================================
# CALCULATE MONTHLY BILL
# =========================================================

def calculate_monthly_bill(
    customer,
    year,
    month
):

    # -----------------------------------------------------
    # CUSTOMER START DATE
    # -----------------------------------------------------

    try:

        customer_start_date = date.fromisoformat(
            customer["start_date"]
        )

    except (
        ValueError,
        TypeError,
        KeyError
    ):

        return None


    # -----------------------------------------------------
    # MONTH START AND END
    # -----------------------------------------------------

    month_start = date(
        year,
        month,
        1
    )

    last_day = calendar.monthrange(
        year,
        month
    )[1]

    month_end = date(
        year,
        month,
        last_day
    )


    # -----------------------------------------------------
    # TODAY
    # -----------------------------------------------------

    today = date.today()


    # -----------------------------------------------------
    # DO NOT CALCULATE FUTURE MONTHS
    # -----------------------------------------------------

    if month_start > today:

        return None


    # -----------------------------------------------------
    # CALCULATION END
    # -----------------------------------------------------

    if (
        year == today.year
        and month == today.month
    ):

        calculation_end = today

    else:

        calculation_end = month_end


    # -----------------------------------------------------
    # CUSTOMER STARTED AFTER THIS PERIOD
    # -----------------------------------------------------

    if customer_start_date > calculation_end:

        return None


    # -----------------------------------------------------
    # BILLING START
    # -----------------------------------------------------

    billing_start = max(
        customer_start_date,
        month_start
    )


    # -----------------------------------------------------
    # DEFAULT QUANTITY
    # -----------------------------------------------------

    try:

        default_qty = float(
            customer.get(
                "default_qty",
                0
            )
        )

    except (
        ValueError,
        TypeError
    ):

        default_qty = 0.0


    # -----------------------------------------------------
    # RATE
    # -----------------------------------------------------

    try:

        rate = float(
            customer.get(
                "rate",
                0
            )
        )

    except (
        ValueError,
        TypeError
    ):

        rate = 0.0


    # -----------------------------------------------------
    # GET DAILY ENTRIES
    # -----------------------------------------------------

    entries = get_month_entries(
        customer["id"],
        year,
        month
    )


    # -----------------------------------------------------
    # DATE -> ENTRY MAP
    # -----------------------------------------------------

    entry_map = {}

    for entry in entries:

        try:

            entry_date = date.fromisoformat(
                entry["date"]
            )

            entry_map[entry_date] = entry

        except (
            ValueError,
            TypeError,
            KeyError
        ):

            continue


    # -----------------------------------------------------
    # BILLING VARIABLES
    # -----------------------------------------------------

    total_liters = 0.0

    total_days_taking_milk = 0

    no_milk_days = 0

    extra_liters = 0.0

    no_milk_details = []


    # -----------------------------------------------------
    # PROCESS EACH DAY
    # -----------------------------------------------------

    current_day = billing_start


    while current_day <= calculation_end:

        actual_qty = default_qty

        reason = ""


        # -------------------------------------------------
        # DAILY OVERRIDE
        # -------------------------------------------------

        if current_day in entry_map:

            entry = entry_map[current_day]

            try:

                actual_qty = float(
                    entry.get(
                        "qty",
                        default_qty
                    )
                )

            except (
                ValueError,
                TypeError
            ):

                actual_qty = default_qty


            reason = entry.get(
                "reason",
                ""
            )


        # -------------------------------------------------
        # PREVENT NEGATIVE QUANTITY
        # -------------------------------------------------

        if actual_qty < 0:

            actual_qty = 0.0


        # -------------------------------------------------
        # NO MILK
        # -------------------------------------------------

        if actual_qty == 0:

            no_milk_days += 1

            no_milk_details.append({

                "date":
                    current_day.isoformat(),

                "reason":
                    reason if reason else "No milk"

            })


        # -------------------------------------------------
        # MILK TAKEN
        # -------------------------------------------------

        else:

            total_days_taking_milk += 1

            total_liters += actual_qty


            # Extra quantity only

            if actual_qty > default_qty:

                extra_liters += (
                    actual_qty - default_qty
                )


        current_day += timedelta(
            days=1
        )


    # =====================================================
    # TOTAL AMOUNT
    # =====================================================

    total_amount = (
        total_liters * rate
    )


    # =====================================================
    # RETURN REPORT
    # =====================================================

    return {

        "customer": customer,

        "customer_id": customer["id"],

        "customer_name": customer["name"],

        "details": customer.get(
            "details",
            ""
        ),

        "month":
            f"{year:04d}-{month:02d}",

        "billing_start":
            billing_start.isoformat(),

        "calculation_end":
            calculation_end.isoformat(),

        "default_qty":
            round(default_qty, 2),

        "rate":
            round(rate, 2),

        "total_days_taking_milk":
            total_days_taking_milk,

        "no_milk_days":
            no_milk_days,

        "no_milk_details":
            no_milk_details,

        "extra_liters":
            round(extra_liters, 2),

        "total_liters":
            round(total_liters, 2),

        "total_amount":
            round(total_amount, 2),

        "payment_status":
            "Pending"
    }


# =========================================================
# CREATE PREVIOUS MONTH SNAPSHOTS
# =========================================================

def create_previous_month_snapshots():

    customers = load_customers()

    bills = load_monthly_bills()

    today = date.today()


    # -----------------------------------------------------
    # FIND PREVIOUS MONTH
    # -----------------------------------------------------

    if today.month == 1:

        previous_year = today.year - 1

        previous_month = 12

    else:

        previous_year = today.year

        previous_month = today.month - 1


    previous_month_string = (
        f"{previous_year:04d}-"
        f"{previous_month:02d}"
    )


    changed = False


    # -----------------------------------------------------
    # CREATE BILL FOR EACH CUSTOMER
    # -----------------------------------------------------

    for customer in customers:

        # -------------------------------------------------
        # IMPORTANT:
        # DO NOT RECREATE A BILL THAT WAS ALREADY CLEARED
        # -------------------------------------------------

        if is_bill_cleared(
            customer["id"],
            previous_month_string
        ):

            continue


        existing_bill = None


        for bill in bills:

            try:

                if (
                    int(
                        bill["customer_id"]
                    )
                    ==
                    int(
                        customer["id"]
                    )
                    and
                    bill["month"]
                    ==
                    previous_month_string
                ):

                    existing_bill = bill

                    break

            except (
                ValueError,
                TypeError,
                KeyError
            ):

                continue


        # -------------------------------------------------
        # BILL ALREADY EXISTS
        # -------------------------------------------------

        if existing_bill is not None:

            continue


        # -------------------------------------------------
        # CALCULATE BILL
        # -------------------------------------------------

        bill = calculate_monthly_bill(
            customer,
            previous_year,
            previous_month
        )


        if bill is None:

            continue


        bills.append(
            bill
        )

        changed = True


    # -----------------------------------------------------
    # SAVE
    # -----------------------------------------------------

    if changed:

        save_monthly_bills(
            bills
        )


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    create_previous_month_snapshots()

    return render_template(
        "index.html"
    )


# =========================================================
# ADD CUSTOMER
# =========================================================

@app.route(
    "/add_customer",
    methods=["GET", "POST"]
)
def add_customer():

    customers = load_customers()


    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        details = request.form.get(
            "details",
            ""
        ).strip()

        default_qty_text = request.form.get(
            "default_qty",
            ""
        ).strip()

        rate_text = request.form.get(
            "rate",
            ""
        ).strip()

        start_date = request.form.get(
            "start_date",
            ""
        ).strip()


        if not name:

            return (
                "Customer name is required.",
                400
            )


        # -------------------------------------------------
        # DUPLICATE NAME
        # -------------------------------------------------

        for customer in customers:

            existing_name = customer.get(
                "name",
                ""
            ).strip()


            if (
                existing_name.lower()
                ==
                name.lower()
            ):

                return (
                    f"Customer '{name}' already exists. "
                    "Please use a different name.",
                    400
                )


        # -------------------------------------------------
        # QUANTITY
        # -------------------------------------------------

        try:

            default_qty = float(
                default_qty_text
            )

            if default_qty < 0:

                raise ValueError

        except (
            ValueError,
            TypeError
        ):

            return (
                "Invalid quantity.",
                400
            )


        # -------------------------------------------------
        # RATE
        # -------------------------------------------------

        try:

            customer_rate = float(
                rate_text
            )

            if customer_rate < 0:

                raise ValueError

        except (
            ValueError,
            TypeError
        ):

            return (
                "Invalid rate.",
                400
            )


        # -------------------------------------------------
        # START DATE
        # -------------------------------------------------

        if not start_date:

            return (
                "Start date is required.",
                400
            )


        try:

            date.fromisoformat(
                start_date
            )

        except (
            ValueError,
            TypeError
        ):

            return (
                "Invalid start date.",
                400
            )


        # -------------------------------------------------
        # CREATE ID
        # -------------------------------------------------

        if customers:

            valid_ids = []

            for customer in customers:

                try:

                    valid_ids.append(
                        int(customer["id"])
                    )

                except (
                    ValueError,
                    TypeError,
                    KeyError
                ):

                    continue


            if valid_ids:

                new_id = max(
                    valid_ids
                ) + 1

            else:

                new_id = 1

        else:

            new_id = 1


        # -------------------------------------------------
        # CREATE CUSTOMER
        # -------------------------------------------------

        new_customer = {

            "id":
                new_id,

            "name":
                name,

            "details":
                details,

            "default_qty":
                default_qty,

            "rate":
                customer_rate,

            "start_date":
                start_date

        }


        customers.append(
            new_customer
        )


        save_customers(
            customers
        )


        return redirect(
            url_for(
                "add_customer"
            )
        )


    return render_template(
        "add_customer.html",
        customers=customers
    )


# =========================================================
# VIEW CUSTOMERS
# =========================================================

@app.route("/customers")
def customers():

    customer_list = load_customers()

    return render_template(
        "customers.html",
        customers=customer_list
    )


# =========================================================
# DELETE CUSTOMER
# =========================================================

@app.route(
    "/delete_customer/<int:customer_id>",
    methods=["POST"]
)
def delete_customer(customer_id):

    customers = load_customers()

    customer_exists = False

    remaining_customers = []


    for customer in customers:

        try:

            if (
                int(customer["id"])
                ==
                customer_id
            ):

                customer_exists = True

                continue

        except (
            ValueError,
            TypeError,
            KeyError
        ):

            pass


        remaining_customers.append(
            customer
        )


    if not customer_exists:

        return (
            "Customer not found.",
            404
        )


    save_customers(
        remaining_customers
    )


    # -----------------------------------------------------
    # DELETE ALL DAILY ENTRIES FOR CUSTOMER
    # -----------------------------------------------------

    daily_entries = load_daily_entries()

    remaining_entries = []


    for entry in daily_entries:

        try:

            if (
                int(entry["customer_id"])
                ==
                customer_id
            ):

                continue

        except (
            ValueError,
            TypeError,
            KeyError
        ):

            pass


        remaining_entries.append(
            entry
        )


    save_daily_entries(
        remaining_entries
    )


    # -----------------------------------------------------
    # DELETE ALL MONTHLY BILLS FOR CUSTOMER
    # -----------------------------------------------------

    monthly_bills = load_monthly_bills()

    remaining_bills = []


    for bill in monthly_bills:

        try:

            if (
                int(bill["customer_id"])
                ==
                customer_id
            ):

                continue

        except (
            ValueError,
            TypeError,
            KeyError
        ):

            pass


        remaining_bills.append(
            bill
        )


    save_monthly_bills(
        remaining_bills
    )


    # -----------------------------------------------------
    # DELETE CLEARED BILL RECORDS FOR CUSTOMER
    # -----------------------------------------------------

    cleared_bills = load_cleared_bills()

    remaining_cleared_bills = []


    for item in cleared_bills:

        try:

            if (
                int(item["customer_id"])
                ==
                customer_id
            ):

                continue

        except (
            ValueError,
            TypeError,
            KeyError
        ):

            pass


        remaining_cleared_bills.append(
            item
        )


    save_cleared_bills(
        remaining_cleared_bills
    )


    return redirect(
        url_for(
            "customers"
        )
    )


# =========================================================
# DAILY ENTRY
# =========================================================

@app.route(
    "/daily_entry",
    methods=["GET", "POST"]
)
def daily_entry():

    customers = load_customers()


    # =====================================================
    # POST
    # =====================================================

    if request.method == "POST":

        customer_id_text = request.form.get(
            "customer_id",
            ""
        ).strip()

        entry_date = request.form.get(
            "date",
            ""
        ).strip()

        qty_text = request.form.get(
            "qty",
            ""
        ).strip()

        reason = request.form.get(
            "reason",
            ""
        ).strip()


        try:

            customer_id = int(
                customer_id_text
            )

        except (
            ValueError,
            TypeError
        ):

            return (
                "Invalid customer.",
                400
            )


        # -------------------------------------------------
        # FIND CUSTOMER
        # -------------------------------------------------

        customer = None


        for item in customers:

            try:

                if (
                    int(item["id"])
                    ==
                    customer_id
                ):

                    customer = item

                    break

            except (
                ValueError,
                TypeError,
                KeyError
            ):

                continue


        if customer is None:

            return (
                "Customer not found.",
                404
            )


        # -------------------------------------------------
        # DATE
        # -------------------------------------------------

        if not entry_date:

            return (
                "Invalid date.",
                400
            )


        try:

            selected_date = date.fromisoformat(
                entry_date
            )

        except (
            ValueError,
            TypeError
        ):

            return (
                "Invalid date.",
                400
            )


        # -------------------------------------------------
        # QUANTITY
        # -------------------------------------------------

        try:

            qty = float(
                qty_text
            )

            if qty < 0:

                raise ValueError

        except (
            ValueError,
            TypeError
        ):

            return (
                "Invalid quantity.",
                400
            )


        # -------------------------------------------------
        # NO MILK REASON
        # -------------------------------------------------

        if (
            qty == 0
            and
            not reason
        ):

            return (
                "Please enter a reason for no milk.",
                400
            )


        # -------------------------------------------------
        # CUSTOMER START DATE
        # -------------------------------------------------

        try:

            customer_start_date = date.fromisoformat(
                customer["start_date"]
            )


            if (
                selected_date
                <
                customer_start_date
            ):

                return (
                    "This date is before the customer's "
                    "start date.",
                    400
                )

        except (
            ValueError,
            TypeError,
            KeyError
        ):

            return (
                "Invalid customer start date.",
                400
            )


        # -------------------------------------------------
        # LOAD ENTRIES
        # -------------------------------------------------

        entries = load_daily_entries()

        updated = False


        # -------------------------------------------------
        # UPDATE EXISTING ENTRY
        # -------------------------------------------------

        for entry in entries:

            try:

                if (
                    int(entry["customer_id"])
                    ==
                    customer_id
                    and
                    entry["date"]
                    ==
                    entry_date
                ):

                    entry["qty"] = qty

                    entry["reason"] = reason

                    updated = True

                    break

            except (
                ValueError,
                TypeError,
                KeyError
            ):

                continue


        # -------------------------------------------------
        # ADD NEW ENTRY
        # -------------------------------------------------

        if not updated:

            entries.append({

                "customer_id":
                    customer_id,

                "date":
                    entry_date,

                "qty":
                    qty,

                "reason":
                    reason

            })


        # -------------------------------------------------
        # SAVE
        # -------------------------------------------------

        save_daily_entries(
            entries
        )


        return redirect(
            url_for(
                "daily_entry",
                customer_id=customer_id,
                date=entry_date
            )
        )


    # =====================================================
    # GET
    # =====================================================

    selected_customer_id = request.args.get(
        "customer_id",
        ""
    )


    selected_date = request.args.get(
        "date",
        date.today().isoformat()
    )


    selected_customer = None


    if selected_customer_id:

        try:

            selected_customer_id_int = int(
                selected_customer_id
            )


            for customer in customers:

                try:

                    if (
                        int(customer["id"])
                        ==
                        selected_customer_id_int
                    ):

                        selected_customer = customer

                        break

                except (
                    ValueError,
                    TypeError,
                    KeyError
                ):

                    continue

        except (
            ValueError,
            TypeError
        ):

            selected_customer = None


    # -----------------------------------------------------
    # FIND EXISTING ENTRY
    # -----------------------------------------------------

    existing_entry = None


    if selected_customer:

        entries = load_daily_entries()


        for entry in entries:

            try:

                if (
                    int(entry["customer_id"])
                    ==
                    int(
                        selected_customer["id"]
                    )
                    and
                    entry["date"]
                    ==
                    selected_date
                ):

                    existing_entry = entry

                    break

            except (
                ValueError,
                TypeError,
                KeyError
            ):

                continue


    return render_template(

        "daily_entry.html",

        customers=customers,

        selected_customer_id=
            selected_customer_id,

        selected_date=
            selected_date,

        selected_customer=
            selected_customer,

        existing_entry=
            existing_entry

    )


# =========================================================
# MONTHLY REPORT
# =========================================================

@app.route(
    "/monthly_report"
)
def monthly_report():

    customers = load_customers()


    selected_customer_id = request.args.get(
        "customer_id",
        ""
    )


    selected_month = request.args.get(
        "month",
        date.today().strftime("%Y-%m")
    )


    report = None


    if (
        selected_customer_id
        and
        selected_month
    ):

        try:

            customer_id = int(
                selected_customer_id
            )


            year, month = map(
                int,
                selected_month.split("-")
            )


            if month < 1 or month > 12:

                raise ValueError


        except (
            ValueError,
            TypeError
        ):

            return (
                "Invalid customer or month.",
                400
            )


        selected_customer = None


        for customer in customers:

            try:

                if (
                    int(customer["id"])
                    ==
                    customer_id
                ):

                    selected_customer = customer

                    break

            except (
                ValueError,
                TypeError,
                KeyError
            ):

                continue


        if selected_customer:

            report = calculate_monthly_bill(

                selected_customer,

                year,

                month

            )


    return render_template(

        "monthly_report.html",

        customers=customers,

        report=report,

        selected_customer_id=
            selected_customer_id,

        selected_month=
            selected_month

    )


# =========================================================
# PREVIOUS MONTH HELPER
# =========================================================

def get_previous_month():

    today = date.today()


    if today.month == 1:

        previous_year = today.year - 1

        previous_month = 12

    else:

        previous_year = today.year

        previous_month = today.month - 1


    previous_month_string = (
        f"{previous_year:04d}-"
        f"{previous_month:02d}"
    )


    return (
        previous_year,
        previous_month,
        previous_month_string
    )


# =========================================================
# PREVIOUS MONTH BILLS
# =========================================================

@app.route(
    "/previous_month_bills"
)
def previous_month_bills():

    # -----------------------------------------------------
    # CREATE PREVIOUS MONTH SNAPSHOTS
    # -----------------------------------------------------

    create_previous_month_snapshots()


    bills = load_monthly_bills()


    (
        previous_year,
        previous_month,
        previous_month_string
    ) = get_previous_month()


    # -----------------------------------------------------
    # ONLY EXISTING/PENDING BILLS
    # -----------------------------------------------------

    previous_bills = [

        bill

        for bill in bills

        if bill.get("month")
        ==
        previous_month_string

    ]


    return render_template(

        "previous_month_bills.html",

        bills=previous_bills,

        selected_month=
            previous_month_string

    )


# =========================================================
# VIEW ONE PREVIOUS MONTH BILL
# =========================================================

@app.route(
    "/previous_month_bill/<int:customer_id>"
)
def previous_month_bill(customer_id):

    create_previous_month_snapshots()


    bills = load_monthly_bills()


    (
        previous_year,
        previous_month,
        previous_month_string
    ) = get_previous_month()


    selected_bill = None


    # -----------------------------------------------------
    # FIND ONLY THIS CUSTOMER'S PREVIOUS MONTH BILL
    # -----------------------------------------------------

    for bill in bills:

        try:

            if (
                int(
                    bill["customer_id"]
                )
                ==
                customer_id
                and
                bill.get("month")
                ==
                previous_month_string
            ):

                selected_bill = bill

                break

        except (
            ValueError,
            TypeError,
            KeyError
        ):

            continue


    # -----------------------------------------------------
    # BILL NOT FOUND
    # -----------------------------------------------------

    if selected_bill is None:

        return redirect(
            url_for(
                "previous_month_bills"
            )
        )


    return render_template(

        "previous_bill_detail.html",

        bill=selected_bill,

        selected_month=
            previous_month_string

    )


# =========================================================
# PAID AND CLEAR PREVIOUS MONTH BILL
# =========================================================

@app.route(
    "/clear_previous_month_bill/<int:customer_id>",
    methods=["POST"]
)
def clear_previous_month_bill(customer_id):

    (
        previous_year,
        previous_month,
        previous_month_string
    ) = get_previous_month()


    # =====================================================
    # DELETE ONLY THIS CUSTOMER'S PREVIOUS MONTH
    # DAILY ENTRIES
    # =====================================================

    daily_entries = load_daily_entries()

    remaining_entries = []


    for entry in daily_entries:

        try:

            entry_customer_id = int(
                entry["customer_id"]
            )

            entry_date = date.fromisoformat(
                entry["date"]
            )


            if (
                entry_customer_id
                ==
                customer_id
                and
                entry_date.year
                ==
                previous_year
                and
                entry_date.month
                ==
                previous_month
            ):

                continue

        except (
            ValueError,
            TypeError,
            KeyError
        ):

            pass


        remaining_entries.append(
            entry
        )


    save_daily_entries(
        remaining_entries
    )


    # =====================================================
    # DELETE ONLY THIS CUSTOMER'S
    # PREVIOUS MONTH BILL
    # =====================================================

    bills = load_monthly_bills()

    remaining_bills = []


    for bill in bills:

        try:

            bill_customer_id = int(
                bill["customer_id"]
            )


            if (
                bill_customer_id
                ==
                customer_id
                and
                bill.get("month")
                ==
                previous_month_string
            ):

                continue

        except (
            ValueError,
            TypeError,
            KeyError
        ):

            pass


        remaining_bills.append(
            bill
        )


    save_monthly_bills(
        remaining_bills
    )


    # =====================================================
    # REMEMBER THAT THIS BILL WAS CLEARED
    # =====================================================

    cleared_bills = load_cleared_bills()

    already_cleared = False


    for item in cleared_bills:

        try:

            if (
                int(item["customer_id"])
                ==
                customer_id
                and
                item["month"]
                ==
                previous_month_string
            ):

                already_cleared = True

                break

        except (
            ValueError,
            TypeError,
            KeyError
        ):

            continue


    if not already_cleared:

        cleared_bills.append({

            "customer_id":
                customer_id,

            "month":
                previous_month_string

        })

        save_cleared_bills(
            cleared_bills
        )


    # =====================================================
    # RETURN TO PREVIOUS MONTH BILLS
    # =====================================================

    return redirect(
        url_for(
            "previous_month_bills"
        )
    )


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )