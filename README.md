# Leontief Economic Model

This is our Linear Algebra project at JG University. The model tracks how much each sector needs to produce when sectors buy inputs from one another and customers place their own demands.

The first demo compares the original sample with an edited scenario. Select Energy and enter 20 in Demand change (units). The app adds 20 units to the base demand of 30, giving a new final demand of 50. Then change the Energy input used by Manufacturing and look at the coefficient in the Energy equation. Adding a sector shows the extra matrix row, column and equation.

## Run locally

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m streamlit run streamlit_app.py
```

The five-sector data is made up for the demo. Rows show who supplies an input. Columns show who uses that input for production.

## Follow the calculation

After a scenario change, compare the two input matrices and the selected balance equation. Under **Total production**, the table and chart compare output by sector. Open **Show the row operations and verify the answer** to step through reduction of [I − A | d] and compare the result with the matrix inverse and Ax + d.

Run the math tests with:

```powershell
.venv\Scripts\python -m unittest discover -s tests
```

The solver, inverse and productivity check use Python arithmetic. The tests use NumPy as a reference.

For Streamlit Community Cloud, use the `main` branch and `streamlit_app.py` as the entry point.

## Save a scenario

The app reads the original sectors, demand and input rates from SQLite. Open **Save or load scenarios** in the sidebar, enter a name and click **Save scenario**. Then select it under **Saved scenario** and click **Load scenario** to see the same inputs and results again. Use **Back to editor** to try a new change.

The schema and sample inserts are in `db/`. Python creates `db/leontief.sqlite3` automatically. Scenario names and inputs are visible to anyone using the same app deployment. Streamlit Community Cloud can reset its local storage, so cloud saves may disappear. The sample is recreated from SQL when the app starts.
