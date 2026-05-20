# Interactive Three-Statement Financial Forecasting Model

This project is a Python tool that builds linked Income Statement, Balance Sheet, and Cash Flow forecasts for any publicly traded U.S. company. It mirrors how analysts build forward-looking financial models in investment banking, corporate finance, and FP&A.

The user enters a ticker symbol, and the program pulls the company's most recent annual financials directly from the SEC's XBRL company facts database. Anchoring the base year to actual reported results keeps the historical side of the model grounded in audited data rather than manual entry.

From there, the user enters forecasting assumptions: revenue growth, operating costs, working capital intensity, capex, and financing policy. Defaults are provided for each, so the model can be run quickly or used to test sensitivities by varying inputs without changing the code.

The three statements are fully linked. Net income flows into equity through retained earnings, capex affects both cash and long-term assets, working capital changes pass through operating cash flow, and financing decisions drive leverage and liquidity. Cash plugs the balance sheet, following standard modeling practice. Detailed debt amortization and deferred tax accounting are simplified, but the core mechanics reflect how professional models are structured.

To run the project, Python 3 is required along with the pandas and requests libraries. After installing dependencies, the program runs from the terminal, prompting the user for a ticker and assumptions, then printing the forecasted statements with an option to export to Excel.
