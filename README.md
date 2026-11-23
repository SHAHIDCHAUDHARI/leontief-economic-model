# Leontief Economic Model

This is our Linear Algebra project at JG University. The model tracks how much each sector needs to produce when sectors buy inputs from one another and customers place their own demands.

The first demo compares the original sample with an edited scenario. Try increasing Energy demand by 20% and check how its equation changes from a final demand of 30 to 36. Then change the Energy input used by Manufacturing and look at the coefficient in the Energy equation. Adding a sector shows the extra matrix row, column and equation.

## Run locally

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m streamlit run streamlit_app.py
```

The five-sector data is made up for the demo. Rows show who supplies an input. Columns show who uses that input for production.

## Project progress

- Scenario editor and before/after equation view.
- Next milestones are the team-written solver and productivity check, SQLite storage, output chart and ranking, tests, report, and Streamlit Community Cloud deployment.
