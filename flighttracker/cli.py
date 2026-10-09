import argparse
import time

from .db import DB
from .notify import NOTIFIERS
from .providers import get_provider
from .tracker import check_watch, describe


def run_checks(db, provider, notifiers, min_history):
    for w in db.watches():
        try:
            price, low = check_watch(db, provider, w, notifiers, min_history)
        except Exception as exc:
            print(f"[{w['id']}] {describe(w)}: error: {exc}")
            continue
        flag = "  <-- ALL-TIME LOW" if low else ""
        shown = "no offers" if price is None else f"{w['currency']} {price:.2f}"
        print(f"[{w['id']}] {describe(w)}: {shown}{flag}")


def main(argv=None):
    p = argparse.ArgumentParser(prog="flighttracker", description="Alert on all-time-low flight prices.")
    p.add_argument("--db", default="flights.db")
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("add", help="watch a route")
    a.add_argument("origin"); a.add_argument("destination")
    a.add_argument("depart_date", help="YYYY-MM-DD")
    a.add_argument("--return-date"); a.add_argument("--currency", default="USD")

    sub.add_parser("list", help="show watches with lowest price seen")
    r = sub.add_parser("remove", help="stop watching"); r.add_argument("id", type=int)
    h = sub.add_parser("history", help="price history"); h.add_argument("id", type=int)

    for name in ("check", "watch"):
        c = sub.add_parser(name, help="check prices once" if name == "check" else "check repeatedly")
        c.add_argument("--provider", choices=["mock", "amadeus"], default="amadeus")
        c.add_argument("--notify", nargs="+", choices=list(NOTIFIERS), default=["console"])
        c.add_argument("--min-history", type=int, default=3,
                       help="prior checks required before alerting (default 3)")
        if name == "watch":
            c.add_argument("--interval", type=int, default=3600, help="seconds between checks")

    args = p.parse_args(argv)
    db = DB(args.db)

    if args.cmd == "add":
        wid = db.add_watch(args.origin, args.destination, args.depart_date, args.return_date, args.currency)
        print(f"Watching (id {wid})" if wid else "Already watching that trip")
    elif args.cmd == "list":
        for w in db.watches():
            low = db.lowest_price(w["id"])
            print(f"[{w['id']}] {describe(w)}  lowest: {'-' if low is None else f'{low:.2f}'}"
                  f"  checks: {db.price_count(w['id'])}")
    elif args.cmd == "remove":
        print("Removed" if db.remove_watch(args.id) else "No such watch")
    elif args.cmd == "history":
        for row in db.history(args.id):
            print(f"{row['checked_at']}  {row['price']:.2f}")
    else:
        provider = get_provider(args.provider)
        notifiers = [NOTIFIERS[n] for n in args.notify]
        run_checks(db, provider, notifiers, args.min_history)
        while args.cmd == "watch":
            time.sleep(args.interval)
            run_checks(db, provider, notifiers, args.min_history)


if __name__ == "__main__":
    main()
