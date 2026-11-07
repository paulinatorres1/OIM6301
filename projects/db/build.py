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


    return


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
    return


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

    return


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

    return


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

    return


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

    return


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

    return


if __name__ == "__main__":
    app.run()
