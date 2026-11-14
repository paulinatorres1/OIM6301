import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _(mo):
    import duckdb #can query part a database

    from datetime import date

    # Set reference date 
    as_of = date(2026, 10, 31)

    database = mo.notebook_dir() / "database.duckdb"

    # Define a helper that takes a SQL query as text.
    def ask(sql):
        # Open a read-only connection that closes when this block ends.
        with duckdb.connect(database, read_only=True) as _con:
            # Run the query and return its result as a Polars table.
            return _con.sql(sql).pl()

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. Reading It Back

    **Question 3 — What does each portfolio hold as of October 31, 2026?**

    I predict that joining trades, portfolios, and assets will give me 411 rows before grouping. I’m starting with the 411 trades counted in Part A, and I expect all of them to be on or before October 31, 2026, so the date filter shouldn’t remove any rows. Each trade belongs to exactly one portfolio and one asset. Since each portfolio ID and asset ID appears only once in its own table, I expect each trade to match one row in each table without being duplicated or dropped.

    At this stage, one row still represents one trade. The final answer will have fewer rows because I’ll combine the buys and sells for each portfolio and asset, then keep only the holdings with a positive balance.
    """)
    return


if __name__ == "__main__":
    app.run()
