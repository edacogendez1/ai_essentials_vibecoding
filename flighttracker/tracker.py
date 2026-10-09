def describe(watch):
    trip = f"{watch['origin']} -> {watch['destination']} on {watch['depart_date']}"
    if watch["return_date"]:
        trip += f" (return {watch['return_date']})"
    return trip


def check_watch(db, provider, watch, notifiers, min_history=3):
    """Record the current price; notify if it is a new all-time low.

    Alerts only after `min_history` prior observations, so the first few
    checks (which are trivially "lowest ever") don't spam you.
    Returns (price, is_new_low).
    """
    price = provider.get_cheapest(watch)
    if price is None:
        return None, False
    prev_low = db.lowest_price(watch["id"])
    prev_count = db.price_count(watch["id"])
    db.record_price(watch["id"], price)

    is_low = prev_low is not None and price < prev_low and prev_count >= min_history
    if is_low:
        title = f"Flight price at all-time low: {watch['currency']} {price:.2f}"
        msg = f"{describe(watch)}\nNow {price:.2f} (previous low {prev_low:.2f}, {prev_count} checks)."
        for notify in notifiers:
            try:
                notify(title, msg)
            except Exception as exc:  # one broken channel shouldn't block the others
                print(f"notifier failed: {exc}")
    return price, is_low
