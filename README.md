# Interactive Three-Statement Financial Forecasting Model

This project is an interactive Python-based financial modeling tool that builds a fully linked three-statement forecast using real public company data. The purpose of the model is to replicate how financial analysts construct forward-looking Income Statements, Balance Sheets, and Cash Flow Statements in professional settings such as investment banking, corporate finance, and FP&A.

The model begins by prompting the user to input the ticker symbol of a publicly traded U.S. company. Using this ticker, the program retrieves the most recent annual financial statement data directly from the U.S. Securities and Exchange Commission’s XBRL company facts database. This ensures that the base-year financials reflect actual reported results rather than assumed or manually entered values, closely mirroring how real-world financial models are anchored to audited historical data.

After establishing the base year, the user is prompted to enter forecasting assumptions, including revenue growth, operating cost structure, working capital intensity, capital expenditures, and financing policy. These assumptions are treated as judgment-based inputs and are kept separate from factual data. Default values are provided to allow for rapid analysis, while still enabling sensitivity testing by adjusting assumptions without changing the code itself.

Using the base-year financials and the user’s assumptions, the model generates forecasted Income Statements, Balance Sheets, and Cash Flow Statements over a specified time horizon. The three statements are fully linked. Net income flows into equity through retained earnings, capital expenditures affect both cash and long-term assets, working capital changes impact operating cash flow, and financing decisions influence leverage and liquidity. The Balance Sheet is balanced using cash as a plug, reflecting common modeling practice.

The outputs allow users to evaluate how changes in growth, margins, capital intensity, and leverage affect profitability and cash generation over time. The model is designed to emphasize financial logic and decision-making rather than accounting complexity. While certain elements such as detailed debt amortization schedules and deferred tax accounting are simplified, the structure reflects the core mechanics used in professional financial forecasting.

This project demonstrates the ability to translate public financial disclosures into structured forecasts, build linked financial statements programmatically, and analyze the financial impact of assumptions under uncertainty. The skills reflected in this model are directly applicable to roles in investment banking, corporate finance, valuation, FP&A, and strategic finance.

To run the project, Python 3 is required along with the pandas and requests libraries. After installing dependencies, the program can be executed from the terminal. The user enters a ticker symbol and forecasting assumptions, and the model prints the forecasted financial statements to the terminal with an option to export the results to Excel.

Author: Andrew Ignatescu


# interactive-three-statement-model
