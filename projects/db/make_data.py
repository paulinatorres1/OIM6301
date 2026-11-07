"""
Generates one CSV file per table for the Babson Investment Club database.

Tables: members, portfolios, assets, ticker_history, trades, closing_prices.
Run with: uv run python projects/db/make_data.py
"""

import csv
import os
import random
from datetime import date, timedelta

SEED = 42
random.seed(SEED)

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, "data")
os.makedirs(DATA_DIR, exist_ok=True)

START_DATE = date(2025, 11, 1)
END_DATE = date(2026, 10, 31)
AS_OF = date(2026, 10, 31)

# members we deliberately leave without a portfolio
NO_PORTFOLIO_MEMBER_IDS = {13, 14, 15}

# assets we deliberately never trade
UNTRADED_ASSET_IDS = {11, 15}

# the one asset that changes ticker partway through the year
TICKER_CHANGE_ASSET_ID = 7
TICKER_CHANGE_DATE = date(2026, 3, 15)


def format_decimal(value, places):
    # turns a float into a fixed-decimal string so the CSV matches a SQL DECIMAL column
    return "{:.{p}f}".format(value, p=places)


def is_trading_day(asset_type, a_date):
    # stocks and ETFs only trade on weekdays; crypto trades every day
    if asset_type == "crypto":
        return True
    return a_date.weekday() < 5  # Monday=0 ... Sunday=6


def write_csv(filename, fieldnames, rows):
    path = os.path.join(DATA_DIR, filename)
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    print(f"wrote {len(rows)} rows to {path}")


# ---------------------------------------------------------------------------
# 1. MEMBERS
# ---------------------------------------------------------------------------

first_names = [
    "Olivia", "Liam", "Emma", "Noah", "Ava", "Ethan", "Sophia", "Mason",
    "Isabella", "Lucas", "Mia", "Logan", "Amelia", "Benjamin", "Charlotte",
]
last_names = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
    "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
    "Wilson", "Anderson",
]
class_years = [2026, 2027, 2028, 2029]

NUM_MEMBERS = 15
members = []
member_join_dates = {}
for member_id in range(1, NUM_MEMBERS + 1):
    first = first_names[member_id - 1]
    last = last_names[member_id - 1]
    class_year = random.choice(class_years)
    join_date = date(2023, 9, 1) + timedelta(days=random.randint(0, 770))
    email = f"{first.lower()}.{last.lower()}{member_id}@babson.edu"
    members.append({
        "member_id": member_id,
        "first_name": first,
        "last_name": last,
        "school_email": email,
        "class_year": class_year,
        "join_date": join_date.isoformat(),
    })
    member_join_dates[member_id] = join_date

# ---------------------------------------------------------------------------
# 2. ASSETS
# ---------------------------------------------------------------------------

# (asset_id, asset_name, asset_type, sector, starting_ticker, base_price)
asset_definitions = [
    (1, "Apple Inc.", "stock", "Technology", "AAPL", 180.00),
    (2, "Microsoft Corporation", "stock", "Technology", "MSFT", 330.00),
    (3, "Amazon.com Inc.", "stock", "Consumer Discretionary", "AMZN", 145.00),
    (4, "Tesla Inc.", "stock", "Consumer Discretionary", "TSLA", 240.00),
    (5, "NVIDIA Corporation", "stock", "Technology", "NVDA", 450.00),
    (6, "JPMorgan Chase & Co.", "stock", "Financials", "JPM", 150.00),
    (7, "Qwerty Media Inc.", "stock", "Communication Services", "QWRT", 35.00),
    (8, "SPDR S&P 500 ETF Trust", "ETF", "Index Fund", "SPY", 450.00),
    (9, "Invesco QQQ Trust", "ETF", "Index Fund", "QQQ", 370.00),
    (10, "Vanguard Total Stock Market ETF", "ETF", "Index Fund", "VTI", 230.00),
    (11, "iShares Russell 2000 ETF", "ETF", "Index Fund", "IWM", 195.00),
    (12, "Bitcoin", "crypto", None, "BTC", 65000.00),
    (13, "Ethereum", "crypto", None, "ETH", 3200.00),
    (14, "Solana", "crypto", None, "SOL", 140.00),
    (15, "Cardano", "crypto", None, "ADA", 0.45),
]

assets = []
asset_lookup = {}
for asset_id, asset_name, asset_type, sector, ticker, base_price in asset_definitions:
    row = {
        "asset_id": asset_id,
        "asset_name": asset_name,
        "asset_type": asset_type,
        "sector": sector if sector is not None else "",
    }
    assets.append(row)
    asset_lookup[asset_id] = {
        "asset_type": asset_type,
        "ticker": ticker,
        "base_price": base_price,
    }

# ---------------------------------------------------------------------------
# 3. TICKER_HISTORY
# ---------------------------------------------------------------------------

ticker_history = []
ticker_history_id = 1
for asset_id, _name, _atype, _sector, ticker, _price in asset_definitions:
    if asset_id == TICKER_CHANGE_ASSET_ID:
        # old ticker, in use until the day before the change
        ticker_history.append({
            "ticker_history_id": ticker_history_id,
            "asset_id": asset_id,
            "ticker": ticker,
            "start_date": date(2020, 1, 1).isoformat(),
            "end_date": (TICKER_CHANGE_DATE - timedelta(days=1)).isoformat(),
        })
        ticker_history_id += 1
        # new ticker, open-ended (end_date is NULL / blank)
        ticker_history.append({
            "ticker_history_id": ticker_history_id,
            "asset_id": asset_id,
            "ticker": "QMI",
            "start_date": TICKER_CHANGE_DATE.isoformat(),
            "end_date": "",
        })
        ticker_history_id += 1
    else:
        ticker_history.append({
            "ticker_history_id": ticker_history_id,
            "asset_id": asset_id,
            "ticker": ticker,
            "start_date": date(2020, 1, 1).isoformat(),
            "end_date": "",
        })
        ticker_history_id += 1

# ---------------------------------------------------------------------------
# 4. CLOSING_PRICES (every weekday for stock/ETF, every day for crypto)
# ---------------------------------------------------------------------------

closing_prices = []
closing_price_lookup = {}  # (asset_id, date) -> price, used later by trades
for asset_id, _name, asset_type, _sector, _ticker, base_price in asset_definitions:
    price = base_price
    current_date = START_DATE
    while current_date <= END_DATE:
        if is_trading_day(asset_type, current_date):
            if asset_type == "crypto":
                pct_change = random.uniform(-0.06, 0.06)
            else:
                pct_change = random.uniform(-0.02, 0.02)
            price = price * (1 + pct_change)
            if price < 0.05:
                price = 0.05
            decimals = 6 if price < 10 else 2
            price_str = format_decimal(price, decimals)
            closing_prices.append({
                "asset_id": asset_id,
                "price_date": current_date.isoformat(),
                "closing_price": price_str,
            })
            closing_price_lookup[(asset_id, current_date)] = float(price_str)
        current_date += timedelta(days=1)

# ---------------------------------------------------------------------------
# 5. PORTFOLIOS
# ---------------------------------------------------------------------------

strategies = ["Growth", "Value", "Income", "Index", "Balanced", None]
name_suffixes = [
    "Growth Fund", "Tech Portfolio", "Dividend Portfolio", "Index Tracker",
    "Crypto Sandbox", "Value Picks", "Core Holdings",
]

portfolios = []
portfolio_id = 1
for member_id in range(1, NUM_MEMBERS + 1):
    if member_id in NO_PORTFOLIO_MEMBER_IDS:
        continue
    num_portfolios = random.choice([1, 1, 2])
    for _ in range(num_portfolios):
        join_date = member_join_dates[member_id]
        earliest = join_date if join_date > START_DATE else START_DATE
        span_days = (END_DATE - earliest).days
        created_date = earliest + timedelta(days=random.randint(0, max(span_days, 0)))
        first = members[member_id - 1]["first_name"]
        suffix = random.choice(name_suffixes)
        strategy = random.choice(strategies)
        portfolios.append({
            "portfolio_id": portfolio_id,
            "member_id": member_id,
            "portfolio_name": f"{first}'s {suffix}",
            "created_date": created_date.isoformat(),
            "strategy": strategy if strategy is not None else "",
        })
        portfolio_id += 1

# ---------------------------------------------------------------------------
# 6. TRADES
# ---------------------------------------------------------------------------

TRADED_ASSET_IDS = []
for asset_id, _n, _t, _s, _tk, _p in asset_definitions:
    if asset_id not in UNTRADED_ASSET_IDS:
        TRADED_ASSET_IDS.append(asset_id)

trades = []
trade_id = 1
holdings_by_pair = {}    # (portfolio_id, asset_id) -> current quantity held
dates_used_by_pair = {}  # (portfolio_id, asset_id) -> set of trade dates already used
last_date_by_pair = {}   # (portfolio_id, asset_id) -> most recent trade date

for portfolio in portfolios:
    portfolio_id_value = portfolio["portfolio_id"]
    num_assets_for_portfolio = random.randint(5, 8)
    chosen_assets = random.sample(TRADED_ASSET_IDS, num_assets_for_portfolio)

    for asset_id in chosen_assets:
        pair_key = (portfolio_id_value, asset_id)
        holdings_by_pair[pair_key] = 0.0
        dates_used_by_pair[pair_key] = set()

        asset_type = asset_lookup[asset_id]["asset_type"]
        num_trades_for_pair = random.randint(3, 6)

        latest_start = END_DATE - timedelta(days=60)
        span_days = (latest_start - START_DATE).days
        current_date = START_DATE + timedelta(days=random.randint(0, max(span_days, 0)))

        for _ in range(num_trades_for_pair):
            # move to the next day this asset actually has a closing price
            while current_date <= END_DATE and not is_trading_day(asset_type, current_date):
                current_date += timedelta(days=1)
            # move past any date already used for this portfolio/asset pair
            while current_date <= END_DATE and current_date in dates_used_by_pair[pair_key]:
                current_date += timedelta(days=1)
                while current_date <= END_DATE and not is_trading_day(asset_type, current_date):
                    current_date += timedelta(days=1)
            if current_date > END_DATE:
                break

            price = closing_price_lookup[(asset_id, current_date)]
            holding = holdings_by_pair[pair_key]

            if holding <= 0:
                trade_type = "buy"
            else:
                trade_type = random.choice(["buy", "buy", "sell"])

            if trade_type == "buy":
                if asset_type == "crypto":
                    quantity = round(random.uniform(0.01, 5.0), 6)
                else:
                    quantity = float(random.randint(1, 150))
                holding += quantity
            else:
                if asset_type == "crypto":
                    quantity = round(random.uniform(0.01, holding), 6)
                else:
                    quantity = float(random.randint(1, max(int(holding), 1)))
                holding -= quantity

            fee = 0.0 if random.random() < 0.3 else round(random.uniform(1, 20), 2)

            trades.append({
                "trade_id": trade_id,
                "portfolio_id": portfolio_id_value,
                "asset_id": asset_id,
                "trade_date": current_date.isoformat(),
                "trade_type": trade_type,
                "quantity": format_decimal(quantity, 6),
                "price_per_unit": format_decimal(price, 6),
                "fee": format_decimal(fee, 2),
            })

            holdings_by_pair[pair_key] = holding
            dates_used_by_pair[pair_key].add(current_date)
            last_date_by_pair[pair_key] = current_date
            trade_id += 1

            current_date += timedelta(days=random.randint(3, 20))

print(f"generated {len(trades)} normal trades before intentional rule violations")

# ---------------------------------------------------------------------------
# intentional rule violation #1: trade on a day its asset has no closing price
# (pick a Saturday for a stock/ETF, since those only price on weekdays)
# ---------------------------------------------------------------------------

violation_1_trade_ids = []
stock_etf_asset_ids = []
for asset_id, _n, asset_type, _s, _tk, _p in asset_definitions:
    if asset_type in ("stock", "ETF") and asset_id in TRADED_ASSET_IDS:
        stock_etf_asset_ids.append(asset_id)

violation_1_targets = [
    (portfolios[0]["portfolio_id"], stock_etf_asset_ids[0]),
    (portfolios[1]["portfolio_id"], stock_etf_asset_ids[1]),
]

for portfolio_id_value, asset_id in violation_1_targets:
    pair_key = (portfolio_id_value, asset_id)
    if pair_key not in dates_used_by_pair:
        dates_used_by_pair[pair_key] = set()

    # find a Saturday in the range that is not already used for this pair
    bad_date = START_DATE
    while bad_date.weekday() != 5 or bad_date in dates_used_by_pair[pair_key]:
        bad_date += timedelta(days=1)

    # use the next weekday's closing price as a stand-in price, since
    # there is deliberately no closing price on this Saturday
    lookup_date = bad_date
    while (asset_id, lookup_date) not in closing_price_lookup:
        lookup_date += timedelta(days=1)
    price = closing_price_lookup[(asset_id, lookup_date)]

    quantity = float(random.randint(1, 50))
    fee = round(random.uniform(1, 15), 2)

    trades.append({
        "trade_id": trade_id,
        "portfolio_id": portfolio_id_value,
        "asset_id": asset_id,
        "trade_date": bad_date.isoformat(),
        "trade_type": "buy",
        "quantity": format_decimal(quantity, 6),
        "price_per_unit": format_decimal(price, 6),
        "fee": format_decimal(fee, 2),
    })
    dates_used_by_pair[pair_key].add(bad_date)
    violation_1_trade_ids.append(trade_id)
    trade_id += 1

# ---------------------------------------------------------------------------
# intentional rule violation #2: sell more units than the portfolio owns
# ---------------------------------------------------------------------------

violation_2_trade_ids = []
candidate_pairs = []
for pair_key, holding in holdings_by_pair.items():
    if holding > 5:
        candidate_pairs.append(pair_key)

violation_2_targets = [candidate_pairs[0], candidate_pairs[1]]

for pair_key in violation_2_targets:
    portfolio_id_value, asset_id = pair_key
    asset_type = asset_lookup[asset_id]["asset_type"]
    holding = holdings_by_pair[pair_key]

    bad_date = last_date_by_pair[pair_key] + timedelta(days=1)
    while True:
        while not is_trading_day(asset_type, bad_date):
            bad_date += timedelta(days=1)
        if bad_date not in dates_used_by_pair[pair_key] and (asset_id, bad_date) in closing_price_lookup:
            break
        bad_date += timedelta(days=1)

    price = closing_price_lookup[(asset_id, bad_date)]
    # sell noticeably more than the portfolio actually holds
    oversell_quantity = holding + random.uniform(20, 100)
    if asset_type != "crypto":
        oversell_quantity = float(int(oversell_quantity) + 1)
    fee = round(random.uniform(1, 15), 2)

    trades.append({
        "trade_id": trade_id,
        "portfolio_id": portfolio_id_value,
        "asset_id": asset_id,
        "trade_date": bad_date.isoformat(),
        "trade_type": "sell",
        "quantity": format_decimal(oversell_quantity, 6),
        "price_per_unit": format_decimal(price, 6),
        "fee": format_decimal(fee, 2),
    })
    dates_used_by_pair[pair_key].add(bad_date)
    violation_2_trade_ids.append(trade_id)
    trade_id += 1

# ---------------------------------------------------------------------------
# write all six CSV files
# ---------------------------------------------------------------------------

write_csv("members.csv",
          ["member_id", "first_name", "last_name", "school_email", "class_year", "join_date"],
          members)
write_csv("assets.csv",
          ["asset_id", "asset_name", "asset_type", "sector"],
          assets)
write_csv("ticker_history.csv",
          ["ticker_history_id", "asset_id", "ticker", "start_date", "end_date"],
          ticker_history)
write_csv("portfolios.csv",
          ["portfolio_id", "member_id", "portfolio_name", "created_date", "strategy"],
          portfolios)
write_csv("trades.csv",
          ["trade_id", "portfolio_id", "asset_id", "trade_date", "trade_type",
           "quantity", "price_per_unit", "fee"],
          trades)
write_csv("closing_prices.csv",
          ["asset_id", "price_date", "closing_price"],
          closing_prices)

# ---------------------------------------------------------------------------
# report the intentional rule violations
# ---------------------------------------------------------------------------

print(f"\nas_of date: {AS_OF.isoformat()}")
print(f"members without a portfolio: {sorted(NO_PORTFOLIO_MEMBER_IDS)}")
print(f"assets never traded: {sorted(UNTRADED_ASSET_IDS)}")
print(f"asset with a ticker change: asset_id {TICKER_CHANGE_ASSET_ID} (QWRT -> QMI on {TICKER_CHANGE_DATE.isoformat()})")

print("\nRule broken on purpose #1 (trade on a day with no closing price):")
for tid in violation_1_trade_ids:
    print(f"  trades.csv row with trade_id = {tid}")

print("\nRule broken on purpose #2 (sold more units than the portfolio owned):")
for tid in violation_2_trade_ids:
    print(f"  trades.csv row with trade_id = {tid}")
