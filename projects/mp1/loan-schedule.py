# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
# ]
# ///
"""Mini Project 1.
"""

import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium", sql_output="polars")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Mini Project 1

    Your choice of option, what each one asks for, the due date and how it is graded are on the Mini Project 1 page of the course site, linked from the calendar. This notebook is the shape to build it in. Keep the headings, and replace each line in italics with your own.

    Save it in your course repository as `projects/mp1/<your-tool>.py`, named for what it does, such as `loan-schedule.py`, and open it with `uv run marimo edit`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. The Question
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    What is the repayment schedule for a loan I am considering? This schedule of payments would be useful for borrowers before choosing a loan. This framworks allows borrowers to input mortgage interest rates and visualize monthly payments, total interest, and remaining balance for different loan options, allowing them to decide which option best aligns with their budget and long-term goals.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. My Plan Before AI

    *Before you ask your agent anything, write how you would solve it: the steps, in order, in plain words, in five lines or more. Then answer these two questions:*

    - *What does your loop carry from one step to the next, the way a running total carries its sum?*
    - *Which check will you use in section 6, and which two numbers should agree?*

    *Commit this notebook with the message `mp1: plan before AI`.*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    First, I would calculate the monthly interest for each loan by multiplying the loan balance by the interest rate divided by 12, for monthly interest. Next, I would calculate the monthly payments that directly offset the loan balance using the loan payment formula. Third, I would start with the  balance and go through each month one at a time with a loop. Next, in each month I would deduct the respective interest payment from the total payment to find total principal paid and reduce the loan balance by that principal payment. I would further save those amounts in the schedule: month's payment, interest, principal payment, and outstanding loan balance. I would also check that the last payment brings down the balance to zero, and adjust for any differences if they are necessary. Finally, I would compare both loans based on the interest paid and monthly payments.


    In this case, the loop would carry the outstanding balance from one month to the next. It would update the balance after each payment, reducing the balance. Principal paid could also be carried from one month to the next, as a running total of how much of the principal loan has been paidoff so far.

    In section 6, I would check that the sum of all principal payments equal the original loan amount. These two should agree as they would show that the loan has been paid off by the borrower.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. Inputs

    Every number the project starts from goes in the cell below, and nowhere else, so that changing one input changes every result after it.

    Copy in the default inputs for your option from the Mini Project 1 page. If you chose D, your own option, type your data in here, or ask your agent to generate it with `faker`. The required part reads no file.
    """)
    return


@app.cell
def _():
    # Your inputs.
    loan_amount = 400000
    annual_rates = {30: 0.0703, 15: 0.0642}
    return (annual_rates,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. The Work

    Add as many cells as you need. Try each step yourself before you ask your agent, and commit as you go.
    """)
    return


@app.cell
def _(annual_rates):
    #build a dictionary for each type of loan
    loan_15 = {
        "term_years": 15,
        "annual_rate": annual_rates[15],
        "monthly_rate": annual_rates[15] / 12,
        "n_months": 15 * 12,
    }

    loan_30 = {
        "term_years": 30,
        "annual_rate": annual_rates[30],
        "monthly_rate": annual_rates[30] / 12,
        "n_months": 30 * 12,
    }
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. The Answer

    *A table of your results in the cell below, printed with `print` and f-strings, then one sentence here that answers the question in section 1, with the number in it.*
    """)
    return


@app.cell
def _():
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. How I Know These Numbers Are Right

    *At least one check that reaches a result a second, independent way. Name what you compared and what came out.*
    """)
    return


@app.cell
def _():
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 7. Working With the Agent

    *Pick one piece of AI output you did not accept as-is. What did it give you, what did you change, and how did you know? Point to the commit or the cell.*

    *If the agent got it right the first time: what did you do to verify that?*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 8. Going Further

    *Take at least one step past the main task, in any direction, and use your agent as much as you like. It does not have to work. State what you tried, what you found, and where it is in this notebook.*
    """)
    return


if __name__ == "__main__":
    app.run()
