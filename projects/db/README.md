
# Database Project — Babson Investment Club

## 1. The Scenario

Scenario B: Babson Investment Club

The Babson Investment Club manages paper investment portfolios for students. The club currently tracks members, portfolios, assets, trades, and closing prices using spreadsheets. The goal is to create a database that organizes this information and allows the club to track investments, calculate portfolio holdings, and analyze trading activity.

## 2. The ERD 
Every table, its columns, its primary key and its foreign keys, and every relationship with both of its ends marked, as a mermaid erDiagram. Put it between a line `mermaid and a line , as below, and VS Code's preview and GitHub both show it as a diagram. Chapter A of the SQL handbook, §5, shows how to read one.

```mermaid
erDiagram
    MEMBERS ||--o{ PORTFOLIOS : owns
    PORTFOLIOS ||--o{ TRADES : makes
    ASSETS ||--o{ TRADES : traded_in
    ASSETS ||--o{ CLOSING_PRICES : has
    ASSETS ||--o{ TICKER_HISTORY : uses

    MEMBERS {
        int member_id PK
        string first_name
        string last_name
        string school_email UK
        int class_year
        date join_date
    }

    PORTFOLIOS {
        int portfolio_id PK
        int member_id FK
        string portfolio_name
        date created_date
        string strategy
    }

    ASSETS {
        int asset_id PK
        string asset_name
        string asset_type
        string sector
    }

    TICKER_HISTORY {
        int ticker_history_id PK
        int asset_id FK
        string ticker
        date start_date
        date end_date
    }

    TRADES {
        int trade_id PK
        int portfolio_id FK
        int asset_id FK
        date trade_date
        string trade_type
        decimal quantity
        decimal price_per_unit
        decimal fee
    }

    CLOSING_PRICES {
        int asset_id PK,FK
        date price_date PK
        decimal closing_price
    }
```


## 3. What One Row Means
One sentence for each table, in the way Northwind's would read: "One row of orders is one order placed by one customer."

- MEMBERS: Each row represents one student who belongs to the Babson Investment Club, including their name, email, class year, and join date.

- PORTFOLIOS: Each row represents one investment portfolio owned by a club member. Note that a member can own multiple portfolios.

- ASSETS: Each row represents one investment asset that the club follows, such as a stock, ETF, or cryptocurrency.

- TICKER_HISTORY: Each row represents one ticker symbol assigned to an asset during a specific period. This allows the database to track ticker changes without creating a new asset since both tickers reference one same asset_id.

- TRADES: Each row represents one buy or sell transaction made by a portfolio for a particular asset on a specific date.

- CLOSING_PRICES: Each row represents the closing price of one asset on one specific date, allowing the club to maintain historical pricing information.


## 4. Design Choices