import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _(mo):

    import duckdb

    database = mo.notebook_dir() / "database.duckdb"

    def ask(sql):
        with duckdb.connect(database, read_only=True) as _con:
            return _con.sql(sql).pl()


    return ask, database, duckdb


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 1. The Tables

    This section creates the six tables for the Babson Investment Club database. Each table includes the necessary primary keys, foreign keys, and constraints to organize the data and enforce the business rules.
    """)
    return


@app.cell
def _():
    # create members table 
    members_sql = """
    CREATE TABLE members (
        member_id INTEGER PRIMARY KEY,
        first_name VARCHAR NOT NULL,
        last_name VARCHAR NOT NULL,
        school_email VARCHAR NOT NULL UNIQUE,
        class_year INTEGER NOT NULL,
        join_date DATE NOT NULL
    );
    """
    return (members_sql,)


@app.cell
def _():
    #create portfolios table which brings member as FK
    portfolios_sql = """
    CREATE TABLE portfolios (
        portfolio_id INTEGER PRIMARY KEY,
        member_id INTEGER NOT NULL,
        portfolio_name VARCHAR NOT NULL,
        created_date DATE NOT NULL,
        strategy VARCHAR,
        FOREIGN KEY (member_id) REFERENCES members(member_id)
    );
    """
    return (portfolios_sql,)


@app.cell
def _():
    #create assets table with check constraint for asset type
    assets_sql = """
    CREATE TABLE assets (
        asset_id INTEGER PRIMARY KEY,
        asset_name VARCHAR NOT NULL,
        asset_type VARCHAR NOT NULL
            CHECK (asset_type IN ('stock', 'ETF', 'crypto')),
        sector VARCHAR,
        CHECK (asset_type = 'crypto' OR sector IS NOT NULL),
        CHECK (asset_type != 'crypto' OR sector IS NULL)
    );
    """
    return (assets_sql,)


@app.cell
def _():
    #create ticker history table references asset id as FK
    ticker_history_sql = """
    CREATE TABLE ticker_history (
        ticker_history_id INTEGER PRIMARY KEY,
        asset_id INTEGER NOT NULL,
        ticker VARCHAR NOT NULL,
        start_date DATE NOT NULL,
        end_date DATE,
        FOREIGN KEY (asset_id) REFERENCES assets(asset_id),
        CHECK (end_date IS NULL OR end_date >= start_date),
        UNIQUE (asset_id, start_date)
    );
    """
    return (ticker_history_sql,)


@app.cell
def _():
    #trades table is much more complicated with several checks and foreign keys embedded
    trades_sql = """
    CREATE TABLE trades (
        trade_id INTEGER PRIMARY KEY,
        portfolio_id INTEGER NOT NULL,
        asset_id INTEGER NOT NULL,
        trade_date DATE NOT NULL,
        trade_type VARCHAR NOT NULL
            CHECK (trade_type IN ('buy', 'sell')),
        quantity DECIMAL(18, 6) NOT NULL
            CHECK (quantity > 0),
        price_per_unit DECIMAL(18, 6) NOT NULL
            CHECK (price_per_unit > 0),
        fee DECIMAL(18, 2) NOT NULL DEFAULT 0
            CHECK (fee >= 0),
        FOREIGN KEY (portfolio_id) REFERENCES portfolios(portfolio_id),
        FOREIGN KEY (asset_id) REFERENCES assets(asset_id),
        UNIQUE (portfolio_id, asset_id, trade_date)
    );
    """
    return (trades_sql,)


@app.cell
def _():
    #create closing prices table
    #contains a composite primary key 
    closing_prices_sql = """
    CREATE TABLE closing_prices (
        asset_id INTEGER NOT NULL,
        price_date DATE NOT NULL,
        closing_price DECIMAL(18, 6) NOT NULL
            CHECK (closing_price > 0),
        PRIMARY KEY (asset_id, price_date),
        FOREIGN KEY (asset_id) REFERENCES assets(asset_id)
    );
    """
    return (closing_prices_sql,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. The Data

    The data was generated using make_data.py. covering dates from November 1, 2025, through October 31, 2026, with October 31, 2026, as the "as_of" date.

    The script purposefully includes two violations of each rule required for testing:

    - Missing closing prices: Trades 408 and 409 occur on days without a matching closing price.
    - Overselling: Trades 410 and 411 sell more units than their portfolios own.

    Members 13, 14, and 15 have no portfolios, and assets 11 and 15 have never been traded. Asset 7 changes its ticker from QWRT to QMI on March 15, 2026.
    """)
    return


@app.cell
def _(
    assets_sql,
    closing_prices_sql,
    database,
    duckdb,
    members_sql,
    mo,
    portfolios_sql,
    ticker_history_sql,
    trades_sql,
):
    # Rebuild the database from scratch
    if database.exists():
        database.unlink()

    with duckdb.connect(database) as _con:

        # Create the six tables using the SQL already defined
        for sql in [
            members_sql,
            assets_sql,
            portfolios_sql,
            ticker_history_sql,
            closing_prices_sql,
            trades_sql
        ]:
            _con.execute(sql)

        # Load the six CSV files
        data_dir = mo.notebook_dir() / "data"

        for table in [
            "members",
            "assets",
            "portfolios",
            "ticker_history",
            "closing_prices",
            "trades"
        ]:
            csv_path = data_dir / f"{table}.csv"

            _con.execute(
                f"INSERT INTO {table} SELECT * FROM read_csv_auto(?)",
                [str(csv_path)]
            )
        
        # Create a view for weekly trading activity
        _con.execute("""
            CREATE VIEW weekly_trading_activity AS
            SELECT
                portfolio_id,
                COUNT(*) AS number_of_trades,
                SUM(quantity * price_per_unit) AS total_traded_value
            FROM trades
            WHERE trade_date > (
                SELECT MAX(trade_date) FROM trades
            ) - INTERVAL 7 DAY
            GROUP BY portfolio_id
        """)

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. A Look at the Data

    I will examine the historical closing prices of one investment asset to see whether the generated price movements look realistic.
    import polars as pl
    """)
    return


@app.cell
def _(mo):
    import polars as pl

    # Read the closing prices CSV file
    prices_df = pl.read_csv(
        mo.notebook_dir() / "data" / "closing_prices.csv",
        try_parse_dates=True
    )

    # Show closing prices for asset 1
    asset_prices = prices_df.filter(
        pl.col("asset_id") == 1
    ).sort("price_date")

    asset_prices.head(10)
    return (asset_prices,)


@app.cell
def _(asset_prices):
    import matplotlib.pyplot as plt

    # Plot the closing prices for asset 1
    fig, ax = plt.subplots(figsize=(10, 4))

    ax.plot(
        asset_prices["price_date"].to_list(),
        asset_prices["closing_price"].to_list()
    )

    ax.set_title("Asset 1 — Closing Prices Over 12 Months")
    ax.set_xlabel("Date")
    ax.set_ylabel("Closing Price ($)")
    ax.grid(True, alpha=0.3)

    plt.xticks(rotation=45)
    fig.tight_layout()

    fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The closing prices for Asset 1 look  realistic because they fluctuate throughout the year, with periods of growth and decline. The price rises during the first half of 2026 and then falls toward October, resembling the chnage in price or volatility of a real stock. Since the pattern looks realistic, I did not make changes to the price-generation logic in make_data.py.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. Row Counts

    This section checks how many records were loaded into each of the six database tables.
    """)
    return


@app.cell
def _(ask):
    # Count the number of rows in each database table
    ask("""
    SELECT 'members' AS table_name, COUNT(*) AS row_count FROM members
    UNION ALL
    SELECT 'portfolios', COUNT(*) FROM portfolios
    UNION ALL
    SELECT 'assets', COUNT(*) FROM assets
    UNION ALL
    SELECT 'ticker_history', COUNT(*) FROM ticker_history
    UNION ALL
    SELECT 'trades', COUNT(*) FROM trades
    UNION ALL
    SELECT 'closing_prices', COUNT(*) FROM closing_prices
    ORDER BY table_name
    """)

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. A Row It Refuses

    This section tests whether the database enforces its constraints by attempting to insert a trade with a negative quantity. Since the TRADES table requires quantity to be greater than zero, the database should reject the insertion.
    """)
    return


@app.cell
def _(database, duckdb):

    # Test a trade that violates the quantity rule
    try:
        with duckdb.connect(database) as _con:
            _con.execute("""
                INSERT INTO trades (
                    trade_id, portfolio_id, asset_id,
                    trade_date, trade_type, quantity,
                    price_per_unit, fee
                )
                VALUES (
                    9999, 1, 1,
                    '2026-10-15', 'buy', -5,
                    150.00, 0
                )
            """)
    except Exception as error:
        print("The database rejected the row:")
        print(error)

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. Answers You Already Knew

    This section uses three SQL queries to verify information that was intentionally included in the generated data. I know the expected answers before running the queries because they were defined in make_data.py.

    1. **How many members are in the club?** Expected answer: 15 members.
    2. **Which members have no portfolios?** Expected answer: member IDs 13, 14, and 15.
    3. **Which assets have never been traded?** Expected answer: asset IDs 11 and 15.
    """)
    return


@app.cell
def _(ask):

    # Question 1: How many members are in the club?
    # Expected answer: 15

    ask("""
    SELECT COUNT(*) AS total_members
    FROM members
    """)

    return


@app.cell
def _(ask):

    # Question 2: Which members have no portfolios?
    # Expected answer: member IDs 13, 14, and 15

    ask("""
    SELECT m.member_id, m.first_name, m.last_name
    FROM members AS m
    LEFT JOIN portfolios AS p
        ON m.member_id = p.member_id
    WHERE p.portfolio_id IS NULL
    ORDER BY m.member_id
    """)

    return


@app.cell
def _(ask):

    # Question 3: Which assets have never been traded?
    # Expected answer: asset IDs 11 and 15

    ask("""
    SELECT a.asset_id, a.asset_name
    FROM assets AS a
    LEFT JOIN trades AS t
        ON a.asset_id = t.asset_id
    WHERE t.trade_id IS NULL
    ORDER BY a.asset_id
    """)

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 7. A View

    The weekly_trading_activity view summarizes the number of trades and total traded value for each portfolio during the last seven days. This allows the investment club to review recent trading activity without rewriting the same SQL query every week. The view will also be used in Part B.
    """)
    return


@app.cell
def _(ask):
    # Test the weekly trading activity view
    ask("""
    SELECT *
    FROM weekly_trading_activity
    ORDER BY number_of_trades DESC
    """)

    return


if __name__ == "__main__":
    app.run()
