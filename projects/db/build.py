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


if __name__ == "__main__":
    app.run()
