# Market Dashboard
## Techstack (Development)
* PostgresDB
* Python (Scikit-learn, Pandas, Dash(Django+Plotly))

## Techstack (Depoyment)
* Cloud VM (GCP or AWS)
* PostgresDB
* Python (Scikit-learn, Pandas, Dash(Django+Plotly))

## Components
* Database
* Portfolio Optimizers
* User Dashboard

## Database
Database local (or global in future) to store OHLC data of all stocks (in index or on exchange).
Updates every business day with close price of last day.

### Objectives
1. Setup module: Sets up local DB on initialization with table for each stock
2. Each table contains historical OHLC data for stock
3. A cronjob updates this table every business day (maybe a part of setup module)
4. Fetcher module: has functions for fetching data without putting load on DB

### Inputs
None

### Outputs
Database of OHLC and metadata

### Constraints
1. Storage constraints for DB on local systems
2. API limit exhaust during setup phase

## Portfolio Optimizers
Runs optimizer to create best portfolio using strategies in pyportfolioopt

## User Dashboard
Stores data of stocks owned by user.
Displays metrics like Stop loss and profit exit (dynamic).
