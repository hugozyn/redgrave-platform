"""AFC Redgrave · publish the paid sales of ONE business day into REDGRAVE.LAB.DAILY_SALES.

Used by the Airflow lab to show why a retried task must be idempotent.

  python publish_daily_sales.py --date 2026-08-03 --mode insert   # naive: a retry adds the day twice
  python publish_daily_sales.py --date 2026-08-03 --mode merge    # idempotent: a retry changes nothing

--crash-on-try 1 --try-number N   simulates a crash AFTER the write on attempt 1
(Airflow passes --try-number {{ ti.try_number }}).

Environment variables: SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER, SNOWFLAKE_PRIVATE_KEY_FILE.
"""
import argparse
import os
from pathlib import Path

import snowflake.connector
from cryptography.hazmat.primitives import serialization

TARGET = "REDGRAVE.LAB.DAILY_SALES"

DAY_SQL = """
SELECT TO_DATE(%(day)s), COUNT(*), COALESCE(SUM(order_total_gbp), 0)
FROM REDGRAVE.BRONZE.ORDERS_INCR
WHERE status = 'paid'
  AND TO_DATE(CONVERT_TIMEZONE('Europe/London', order_ts)) = TO_DATE(%(day)s)
"""

INSERT_SQL = f"INSERT INTO {TARGET} SELECT %(d)s, %(n)s, %(rev)s, CURRENT_TIMESTAMP(), 'insert', %(try)s"

MERGE_SQL = f"""
MERGE INTO {TARGET} t
USING (SELECT TO_DATE(%(d)s) AS sales_date, %(n)s AS paid_orders, %(rev)s AS paid_revenue_gbp, %(try)s AS attempt) s
ON t.sales_date = s.sales_date
WHEN MATCHED THEN UPDATE SET paid_orders = s.paid_orders,
                             paid_revenue_gbp = s.paid_revenue_gbp,
                             published_at = CURRENT_TIMESTAMP(),
                             attempt = s.attempt   -- write_mode is kept: it records how the row was first written
WHEN NOT MATCHED THEN INSERT VALUES (s.sales_date, s.paid_orders, s.paid_revenue_gbp, CURRENT_TIMESTAMP(), 'merge', s.attempt)
"""


def connect():
    key = serialization.load_pem_private_key(
        Path(os.environ.get("SNOWFLAKE_PRIVATE_KEY_FILE", "rsa_key.p8")).read_bytes(), password=None)
    return snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        private_key=key.private_bytes(serialization.Encoding.DER, serialization.PrivateFormat.PKCS8,
                                      serialization.NoEncryption()),
        role="SYSADMIN", warehouse="REDGRAVE_WH", database="REDGRAVE")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", required=True, help="business day to publish, YYYY-MM-DD (London time)")
    ap.add_argument("--mode", choices=["insert", "merge"], default="insert")
    ap.add_argument("--try-number", type=int, default=1)
    ap.add_argument("--crash-on-try", type=int, default=0, help="simulate a crash after the write on this attempt")
    args = ap.parse_args()

    con = connect()
    cur = con.cursor()
    try:
        cur.execute("CREATE SCHEMA IF NOT EXISTS REDGRAVE.LAB")
        cur.execute(f"""CREATE TABLE IF NOT EXISTS {TARGET} (
            sales_date DATE, paid_orders NUMBER, paid_revenue_gbp NUMBER(12,2), published_at TIMESTAMP_TZ,
            write_mode VARCHAR, attempt NUMBER)""")
        cur.execute(DAY_SQL, {"day": args.date})
        day, n, rev = cur.fetchone()
        cur.execute(INSERT_SQL if args.mode == "insert" else MERGE_SQL, {"d": str(day), "n": n, "rev": rev, "try": args.try_number})
        print(f"[{args.mode}] {day}: {n} paid orders, {rev} GBP written to {TARGET} (attempt {args.try_number})")

        if args.try_number == args.crash_on_try:
            raise SystemExit("Simulated crash AFTER the write (network lost before the task reported success).")

        cur.execute(f"SELECT COUNT(*) FROM {TARGET} WHERE sales_date = %s", (str(day),))
        print(f"{TARGET} now has {cur.fetchone()[0]} row(s) for {day} (expected: 1).")
    finally:
        cur.close()
        con.close()


if __name__ == "__main__":
    main()
