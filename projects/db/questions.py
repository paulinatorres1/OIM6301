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

    return as_of, ask


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ##The Business Questions
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. How much did each portfolio trade in the last 30 days?

    The report includes every portfolio, even those with no trades. The 30-day window includes the as-of date.
    """)
    return


@app.cell
def _(as_of, ask):
    q1_activity = ask(f"""
    SELECT
        p.portfolio_id,    -- Show the portfolio's unique ID.
        p.portfolio_name,  -- Show its name so the report is easy to read.

        -- Count only matched trades. A portfolio with no trades gets 0.
        COUNT(t.trade_id) AS trade_count,

        -- For buys only, multiply quantity by price and add the fee.
        -- SUM adds those costs together. COALESCE shows 0 if there were no buys.
        COALESCE(SUM(CASE WHEN t.trade_type = 'buy'
            THEN t.quantity * t.price_per_unit + t.fee END), 0) AS spent_on_buys,

        -- For sells only, multiply quantity by price and subtract the fee.
        -- COALESCE shows 0 if there were no sells.
        COALESCE(SUM(CASE WHEN t.trade_type = 'sell'
            THEN t.quantity * t.price_per_unit - t.fee END), 0) AS received_from_sells

    FROM portfolios AS p  -- Start with the full list of portfolios.

    -- LEFT JOIN keeps portfolios even if they have no matching trades.
    LEFT JOIN trades AS t
        ON p.portfolio_id = t.portfolio_id  -- Match each trade to its portfolio.
        -- Match only trades on the as-of date or in the 29 days before it.
        -- Keep this in ON so portfolios with no recent trades still show up.
        AND t.trade_date BETWEEN DATE '{as_of}' - INTERVAL 29 DAY AND DATE '{as_of}'

    -- Combine the matching trades into one result row per portfolio.
    GROUP BY p.portfolio_id, p.portfolio_name

    -- Show the portfolios in ID order.
    ORDER BY p.portfolio_id
    """)

    q1_activity
    return (q1_activity,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    From October 2 through October 31, 2026, portfolios 2, 7, and 14 each made one buy and spent $34,031.38, $303.66, and $899.10, respectively, including fees, while portfolio 3 made one sell and received $3,973.79, meanwhile, the other 10 portfolios made no trades.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. How many portfolios does each member own, and how much have they bought across them?
    """)
    return


@app.cell
def _(as_of, ask):
    q2_member_purchases = ask(f"""
    SELECT
        m.member_id,   -- Identify each member, even if two members share a name.
        m.first_name,
        m.last_name,

        -- A portfolio can appear once for each matching buy, so count each ID once.
        -- COUNT skips NULL, so a member with no portfolio gets 0.
        COUNT(DISTINCT p.portfolio_id) AS portfolio_count,

        -- Add up the value of all buys. Show 0 when no buys match.
        COALESCE(SUM(t.quantity * t.price_per_unit), 0) AS total_purchase_value

    FROM members AS m  -- Start with the full member list.

    -- Keep each member even if they don't own a portfolio as of the report date.
    LEFT JOIN portfolios AS p
        ON m.member_id = p.member_id
        AND p.created_date <= DATE '{as_of}'

    -- Match only buys through the report date, while keeping portfolios with no buys.
    LEFT JOIN trades AS t
        ON p.portfolio_id = t.portfolio_id
        AND t.trade_type = 'buy'
        AND t.trade_date <= DATE '{as_of}'

    -- Combine the matched rows into one result row per member.
    GROUP BY m.member_id, m.first_name, m.last_name

    -- Display members in ID order.
    ORDER BY m.member_id
    """)

    q2_member_purchases
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    As of October 31, 2026, 10 members owned one portfolio , 2 owned two each, and 3 owned none and had $0 in purchases, while Mia Hernandez had the highest total purchase value at $1,159,550.24 across her two portfolios.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. What investments does each portfolio hold as of the report date?
    """)
    return


@app.cell
def _(as_of, ask):
    q3_holdings = ask(f"""
    WITH balances AS (
        SELECT
            p.portfolio_id,    -- Identify the portfolio.
            p.portfolio_name,  -- Show its name in the report.
            a.asset_id,        -- Identify the asset even if its ticker changed.
            a.asset_name,      -- Show the investment's name.

            -- Add units for buys and subtract units for sells.
            SUM(CASE
                WHEN t.trade_type = 'buy' THEN t.quantity
                WHEN t.trade_type = 'sell' THEN -t.quantity
            END) AS units_held

        FROM trades AS t  -- Start with one row per trade.
        JOIN portfolios AS p ON t.portfolio_id = p.portfolio_id
        JOIN assets AS a ON t.asset_id = a.asset_id

        -- Include all recorded trades through the shared report date.
        WHERE t.trade_date <= DATE '{as_of}'

        -- Combine trades into one balance per portfolio and asset.
        GROUP BY p.portfolio_id, p.portfolio_name, a.asset_id, a.asset_name
    )

    -- Read the balances calculated above.
    SELECT portfolio_id, portfolio_name, asset_id, asset_name, units_held
    FROM balances
    WHERE units_held > 0  -- Show only investments the portfolio still holds.
    ORDER BY portfolio_id, asset_id  -- Keep each portfolio's holdings together.
    """)

    q3_holdings
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    As of October 31, 2026, the 14 portfolios held 88 positive positions across 13 different assets, including Olivia’s Crypto Sandbox, which held 23 shares of Apple and 2.808246 Bitcoin, with positions calculated as bought - sold.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. How did each trade price compare with that day’s closing price over the last 90 days?
    """)
    return


@app.cell
def _(as_of, ask):
    q4_price_comparison = ask(f"""
    SELECT
        t.trade_id,                          -- Identify each trade.
        t.trade_date,                        -- Show when it happened.
        a.asset_name,                        -- Show which asset was traded.
        t.price_per_unit AS trade_price,      -- Show the actual price per unit.
        c.closing_price,                     -- Show the close on that same date.

        -- Divide the price difference by the closing price and convert to percent.
        -- If the close is missing, the percentage stays NULL rather than showing 0.
        ROUND(
            100 * (t.price_per_unit - c.closing_price) / c.closing_price,
            2
        ) AS pct_vs_close

    FROM trades AS t  -- Start with one row per trade.

    -- Look up the name using the asset's permanent ID.
    JOIN assets AS a ON t.asset_id = a.asset_id

    -- Match the price by both asset and date. LEFT JOIN keeps unmatched trades.
    LEFT JOIN closing_prices AS c
        ON t.asset_id = c.asset_id
        AND t.trade_date = c.price_date

    -- Include the as-of date and the 89 days before it, for 90 days total.
    WHERE t.trade_date BETWEEN DATE '{as_of}' - INTERVAL 89 DAY AND DATE '{as_of}'

    -- Show the newest trades first, with trade ID breaking ties.
    ORDER BY t.trade_date DESC, t.trade_id
    """)

    q4_price_comparison
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The report covers 72 trades from August 3 through October 31, 2026, and shows how far each trade price was above or below its closing price, expressed as a percentage of the close, with the latest trade, NVIDIA trade 61 on October 19, matching its $414.97 close.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. Which assets does the club follow that no portfolio has ever traded?
    """)
    return


@app.cell
def _(as_of, ask):
    q5_untraded_assets = ask(f"""
    SELECT
        a.asset_id,    -- Identify each asset by its permanent ID.
        a.asset_name   -- Show the name so we can recognize it.
    FROM assets AS a   -- Start with every asset the club follows.

    -- Keep the asset only if the search below finds no matching trade.
    WHERE NOT EXISTS (
        SELECT 1      -- We only need to know whether a matching row exists.
        FROM trades AS t
        WHERE t.asset_id = a.asset_id          -- Look for trades of this asset.
          AND t.trade_date <= DATE '{as_of}'   -- Include trades through the report date.
    )

    -- Display the results in asset ID order.
    ORDER BY a.asset_id
    """)

    q5_untraded_assets
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    As of October 31, 2026, the club followed 2 assets that no portfolio had ever traded: iShares Russell 2000 ETF (asset 11) and Cardano (asset 15).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. How much did the club trade in the asset that changed its ticker during the year?
    """)
    return


@app.cell
def _(as_of, ask):
    q6_ticker_value = ask(f"""
    WITH changed_assets AS (
        -- Find assets that had more than one ticker by the report date.
        SELECT asset_id
        FROM ticker_history
        WHERE start_date <= DATE '{as_of}'
        GROUP BY asset_id
        HAVING COUNT(DISTINCT ticker) > 1
    ),
    value_by_ticker AS (
        SELECT
            a.asset_id,    -- The ID stays the same when the ticker changes.
            a.asset_name,
            h.ticker,
            -- Add the value of buys and sells without including fees.
            COALESCE(SUM(t.quantity * t.price_per_unit), 0) AS value_under_ticker
        FROM changed_assets AS ca
        JOIN assets AS a ON ca.asset_id = a.asset_id
        JOIN ticker_history AS h ON a.asset_id = h.asset_id

        -- Match each trade to the ticker that was active on its trade date.
        -- LEFT JOIN keeps the ticker in the report even if it had no trades.
        LEFT JOIN trades AS t
            ON t.asset_id = h.asset_id
            AND t.trade_date >= h.start_date
            AND (h.end_date IS NULL OR t.trade_date <= h.end_date)
            -- For this report, the year runs from Nov 1, 2025 through Oct 31, 2026.
            AND t.trade_date > DATE '{as_of}' - INTERVAL 1 YEAR
            AND t.trade_date <= DATE '{as_of}'
        WHERE h.start_date <= DATE '{as_of}'
        GROUP BY a.asset_id, a.asset_name, h.ticker
    )
    SELECT
        asset_id,
        asset_name,
        ticker,
        ROUND(value_under_ticker, 2) AS value_under_ticker,
        -- Add both ticker subtotals for the same asset before rounding.
        ROUND(SUM(value_under_ticker) OVER (PARTITION BY asset_id), 2)
            AS total_across_tickers
    FROM value_by_ticker
    ORDER BY asset_id, ticker
    """)

    q6_ticker_value
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Over the 12 months ending October 31, 2026, the club traded $88,485.48 in Qwerty Media Inc. stock, with $43,581.65 traded under its old ticker, QWRT, and $44,903.83 under its new ticker, QMI.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 7. Which trades are missing a closing price for the day they happened?
    """)
    return


@app.cell
def _(as_of, ask):
    q7_missing_closes = ask(f"""
    SELECT
        t.trade_id,    -- Identify the trade that broke the rule.
        t.trade_date,  -- Show the date that should have a closing price.
        a.asset_name   -- Show which investment was traded.

    FROM trades AS t  -- Start with every recorded trade.

    -- Look up the asset's name using its ID.
    JOIN assets AS a ON t.asset_id = a.asset_id

    -- Look for a closing price for the same asset on the same date.
    -- LEFT JOIN keeps the trade even if no closing price matches.
    LEFT JOIN closing_prices AS c
        ON t.asset_id = c.asset_id
        AND t.trade_date = c.price_date

    -- Check all trades through the report date.
    WHERE t.trade_date <= DATE '{as_of}'

    -- A missing price date means the join found no matching price row.
        AND c.price_date IS NULL

    -- List the exceptions in trade ID order.
    ORDER BY t.trade_id
    """)

    q7_missing_closes
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Exactly two trades broke the closing-price rule: trade 408 for Apple and trade 409 for Microsoft both took place on November 1, 2025, when neither asset had a recorded closing price.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 8. Which sales exceeded the number of units the portfolio held at the time?
    """)
    return


@app.cell
def _(as_of, ask):
    q8_oversells = ask(f"""
    WITH trade_balances AS (
        SELECT
            t.trade_id,
            t.trade_date,
            t.portfolio_id,
            t.asset_id,
            t.trade_type,
            t.quantity,

            -- Add earlier buys and subtract earlier sells.
            -- COALESCE gives a starting balance of 0 if there are no earlier trades.
            COALESCE(
                SUM(CASE
                    WHEN t.trade_type = 'buy' THEN t.quantity
                    ELSE -t.quantity
                END) OVER (
                    -- Track each asset separately within each portfolio.
                    PARTITION BY t.portfolio_id, t.asset_id
                    -- Put trades in date order, with trade ID breaking ties.
                    ORDER BY t.trade_date, t.trade_id
                    -- Stop one row before the current trade so it isn't counted yet.
                    ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
                ),
                0
            ) AS units_before_trade

        -- Keep buys and sells here because both affect the balance.
        FROM trades AS t
        WHERE t.trade_date <= DATE '{as_of}'
    )
    SELECT
        b.trade_id,
        b.trade_date,
        p.portfolio_name,
        a.asset_name,
        b.units_before_trade AS units_available,
        b.quantity AS units_sold,
        b.quantity - b.units_before_trade AS units_oversold
    FROM trade_balances AS b

    -- Look up the names so the exception report is easy to read.
    JOIN portfolios AS p ON b.portfolio_id = p.portfolio_id
    JOIN assets AS a ON b.asset_id = a.asset_id

    -- Filter to sells only after calculating balances from all trades.
    WHERE b.trade_type = 'sell'
      AND b.quantity > b.units_before_trade
    ORDER BY b.trade_id
    """)

    q8_oversells
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Olivia’s Crypto Sandbox oversold in exactly two trades: trade 410 sold 161 NVIDIA shares when it held 89, an oversell of 72 shares, and trade 411 sold 485 units of Invesco QQQ Trust when it held 392, an oversell of 93 units.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 9. Which types of investments generated the most trading fees?
    """)
    return


@app.cell
def _(as_of, ask):
    q9_fees_by_type = ask(f"""
    SELECT
        a.asset_type,  -- Show whether the investment is a stock, ETF, or crypto.

        -- Count only trades where a fee was charged.
        COUNT(*) FILTER (WHERE t.fee > 0) AS trades_with_fees,

        -- Add up the fees themselves, without including the value of the trades.
        SUM(t.fee) AS total_fees

    FROM trades AS t  -- Start with the recorded trades.

    -- Use the asset ID to look up each trade's investment type.
    JOIN assets AS a ON t.asset_id = a.asset_id

    -- Include all recorded trades through the shared report date.
    WHERE t.trade_date <= DATE '{as_of}'

    -- Produce one row per investment type and put the highest fee total first.
    GROUP BY a.asset_type
    ORDER BY total_fees DESC, a.asset_type
    """)

    q9_fees_by_type
    return (q9_fees_by_type,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Through October 31, 2026, the club paid the most in fees on stock trades (1,437.79 across 140 trades that incurred fees), followed by ETFs (852.91 across 79 trades) and crypto (765.34 across 76 trades).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 10. What share of the club’s trading value came from each portfolio in the latest active week?

    The latest active week means the seven days ending on the most recent recorded trade date, not the seven days ending on the report date. Trading value includes buys and sells before fees.
    """)
    return


@app.cell
def _(as_of, ask):
    q10_weekly_share = ask(f"""
    WITH view_week AS (
        -- Find the date the saved view uses as the end of its seven-day window.
        SELECT MAX(trade_date) AS week_end
        FROM trades
    )
    SELECT
        p.portfolio_name,                     -- Show the name of each active portfolio.
        d.week_end - 6 AS week_start,         -- Include the end date and six days before it.
        d.week_end,                           -- Show the last day of the view's window.
        ROUND(w.total_traded_value, 2) AS traded_value,

        -- Divide each portfolio's value by the club-wide value for that week.
        -- SUM(...) OVER () adds all portfolios without collapsing them into one row.
        ROUND(
            100.0 * w.total_traded_value
            / SUM(w.total_traded_value) OVER (),
            2
        ) AS pct_of_weekly_value

    FROM weekly_trading_activity AS w         -- Read the view created in build.py.
    JOIN portfolios AS p
        ON w.portfolio_id = p.portfolio_id    -- Match each portfolio ID to its name.
    CROSS JOIN view_week AS d                 -- Attach the same week-ending date to each row.

    -- Only use the view if its window does not extend past the shared report date.
    WHERE d.week_end <= DATE '{as_of}'

    -- Put the portfolio with the largest share first.
    ORDER BY pct_of_weekly_value DESC, p.portfolio_id
    """)

    q10_weekly_share
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    During the club’s latest active week, October 13–19, 2026, Liam’s Dividend Portfolio accounted for 97.48% of trading value (34,027.54 before fees), while Logan’s Tech Portfolio accounted for the remaining 2.52% (879.25 before fees).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Section 1. How I Know These Numbers Are Right

    I checked Question 1 by comparing the sum of the portfolio trade counts with a direct count of trades in the same 30-day window.

    I checked Question 9 by adding the fees across investment types and comparing that total with the fees in the trades table, without joining to assets.
    """)
    return


@app.cell
def _(as_of, ask, mo, q1_activity, q9_fees_by_type):
    # Add the trade counts from the actual Question 1 result.
    q1_count_from_report = q1_activity["trade_count"].sum()

    # Count trade rows directly, without joining to portfolios or grouping.
    q1_count_direct = ask(f"""
        SELECT COUNT(*) AS trade_count
        FROM trades
        -- Include the report date and the 29 days before it.
        WHERE trade_date BETWEEN DATE '{as_of}' - INTERVAL 29 DAY AND DATE '{as_of}'
    """).item()  # Take the single number out of the result table.

    # Add the fee totals from the actual Question 9 result.
    q9_fees_from_report = q9_fees_by_type["total_fees"].sum()

    # Add up fees directly, without joining to assets or grouping by type.
    q9_fees_direct = ask(f"""
        SELECT SUM(fee) AS total_fees
        FROM trades
        WHERE trade_date <= DATE '{as_of}'
    """).item()  # Take the single number out of the result table.

    # Stop with a message showing both numbers if either check disagrees.
    assert q1_count_from_report == q1_count_direct, (
        f"Q1 trade count differs: report = {q1_count_from_report}, direct = {q1_count_direct}"
    )
    assert q9_fees_from_report == q9_fees_direct, (
        f"Q9 fee total differs: report = {q9_fees_from_report}, direct = {q9_fees_direct}"
    )

    # Display both comparisons in the notebook.
    mo.md(f"""
    | Answer checked | From the report | Directly from trades |
    | --- | ---: | ---: |
    | Q1 trade count | {q1_count_from_report} | {q1_count_direct} |
    | Q9 total fees (USD) | {q9_fees_from_report:,.2f} | {q9_fees_direct:,.2f} |
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Section 2. Working With the Agent

    The original data generator picked a crypto sale quantity between 0.01 units and the amount the portfolio held. I didn’t keep that code as-is because my Question 8 query found three oversells instead of the two I had added on purpose. In trade 142, Ava’s Index Tracker held only 0.000598 Solana but sold 0.008004 because Python’s random.uniform() still picks a number when the bounds are reversed.

    I changed make_data.py to round the available balance to six decimal places and use the smaller of 0.01 and that balance as the lower bound for a sale. Then I regenerated the CSVs, rebuilt the database, and reran the same Question 8 query without changing it. It returned only the two intentional oversells, trades 410 and 411. The fix is in commit: db: fix unintended crypto oversell.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Section 3. Reading It Back

    **Question 3 — What does each portfolio hold as of October 31, 2026?**

    I predict that joining trades, portfolios, and assets will give me 411 rows before grouping. I’m starting with the 411 trades counted in Part A, and I expect all of them to be on or before October 31, 2026, so the date filter shouldn’t remove any rows. Each trade belongs to exactly one portfolio and one asset. Since each portfolio ID and asset ID appears only once in its own table, I expect each trade to match one row in each table without being duplicated or dropped.

    At this stage, one row still represents one trade. The final answer will have fewer rows because I’ll combine the buys and sells for each portfolio and asset, then keep only the holdings with a positive balance.
    """)
    return


@app.cell
def _(as_of, ask):
    # Use the same joins and date filter as Question 3, but count the rows
    # before combining buys and sells or filtering to positive holdings.
    q3_join_count = ask(f"""
    SELECT COUNT(*) AS rows_before_grouping
    FROM trades AS t
    -- Match each trade to its portfolio.
    JOIN portfolios AS p ON t.portfolio_id = p.portfolio_id
    -- Match each trade to its asset.
    JOIN assets AS a ON t.asset_id = a.asset_id
    -- Use the same report date as the holdings query.
    WHERE t.trade_date <= DATE '{as_of}'
    """)

    # Display the count in Marimo.
    q3_join_count
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    My prediction matched. The joins returned 411 rows before grouping because every trade was on or before the report date and matched exactly one portfolio and one asset. No trades were dropped or duplicated.

    In the final holdings table, one row shows how many units of one investment a portfolio held on October 31, 2026. I calculated that balance by adding the units bought and subtracting the units sold, then kept balances above zero.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. Going Further
    """)
    return


@app.cell
def _(q9_fees_by_type):
    import matplotlib.pyplot as plt

    # Get the investment types and fee totals from the Question 9 result.
    fee_labels = q9_fees_by_type["asset_type"].to_list()
    fee_amounts = [float(amount) for amount in q9_fees_by_type["total_fees"]]

    # Create a figure and draw one bar per investment type.
    fee_fig, fee_ax = plt.subplots(figsize=(7, 4))
    fee_bars = fee_ax.bar(fee_labels, fee_amounts, color="#287C71")

    # Give the chart a title and label both axes.
    fee_ax.set_title("Trading Fees by Investment Type")
    fee_ax.set_xlabel("Investment type")
    fee_ax.set_ylabel("Total trading fees (USD)")

    # Print the dollar amount above each bar and leave room for the labels.
    fee_ax.bar_label(fee_bars, labels=[f"${amount:,.2f}" for amount in fee_amounts], padding=4)
    fee_ax.set_ylim(0, max(fee_amounts) * 1.15)

    fee_fig.tight_layout()
    fee_fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    I turned my Question 9 results into the bar chart above so the club could compare fees across investment types at a glance. The chart shows that stocks had the highest total fees ($ 1,437.79), followed by ETFs ($ 852.91) and crypto ($ 765.34).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. Time Spent

    I spent approximately 5-6 hours on this project.
    """)
    return


if __name__ == "__main__":
    app.run()
