import pandas as pd
import streamlit as st

from leontief import inverse, matvec, productivity_bounds, solve, system_matrix, validate_inputs

SAMPLE_SECTORS = ["Agriculture", "Manufacturing", "Energy", "Transport", "Services"]
SAMPLE_DEMAND = [66.0, 48.0, 30.0, 25.0, 40.0]
SAMPLE_INPUTS = [
    [0.20, 0.10, 0.05, 0.02, 0.03],
    [0.10, 0.20, 0.10, 0.08, 0.04],
    [0.10, 0.15, 0.20, 0.12, 0.09],
    [0.06, 0.08, 0.05, 0.15, 0.04],
    [0.05, 0.10, 0.06, 0.08, 0.20],
]


def equation(inputs, demand, row):
    terms = [
        rf"{coefficient:g} x_{{{column + 1}}}"
        for column, coefficient in enumerate(inputs[row])
        if coefficient != 0
    ]
    right_side = " + ".join([*terms, f"{demand[row]:g}"])
    return rf"x_{{{row + 1}}} = {right_side}"


st.set_page_config(page_title="Leontief Economic Model", layout="wide")
st.title("Leontief Economic Model")
st.write("Change one demand or input rate and trace it through the production equations.")

scenario = st.sidebar.radio("What do you want to change?", [
    "Final demand", "Input rate", "Add sectors",
])
sectors = SAMPLE_SECTORS.copy()
inputs = [row.copy() for row in SAMPLE_INPUTS]
demand = SAMPLE_DEMAND.copy()

if scenario == "Final demand":
    sector = st.sidebar.selectbox("Sector", sectors, index=2)
    row = sectors.index(sector)
    percent = st.sidebar.number_input("Demand change (%)", min_value=-100.0, value=20.0, step=5.0)
    demand[row] *= 1 + percent / 100
    explanation = (
        f"{sector}'s final demand changes from {SAMPLE_DEMAND[row]:g} to {demand[row]:g}. "
        "The input matrix A and the system matrix I − A stay the same."
    )
elif scenario == "Input rate":
    supplier = st.sidebar.selectbox("Input supplied by", sectors, index=2)
    producer = st.sidebar.selectbox("Used to produce one unit of", sectors, index=1)
    row, column = sectors.index(supplier), sectors.index(producer)
    before = SAMPLE_INPUTS[row][column]
    rate = st.sidebar.number_input(
        "Input per unit", min_value=0.0, value=before, step=0.01, format="%.4f",
        key=f"rate-{row}-{column}",
    )
    inputs[row][column] = rate
    explanation = (
        f"A[{supplier}, {producer}] goes from {before:g} to {rate:g}. "
        f"The coefficient of x{column + 1} changes in the {supplier} equation."
    )
else:
    count = st.sidebar.slider("Total sectors", min_value=6, max_value=10)
    for number in range(len(sectors) + 1, count + 1):
        label = st.sidebar.text_input(f"Name of sector {number}", f"Sector {number}")
        sectors.append(label.strip() or f"Sector {number}")
        demand.append(st.sidebar.number_input(
            f"Final demand for sector {number}", min_value=0.0, value=10.0,
        ))
        for values in inputs:
            values.append(0.0)
        inputs.append([0.0] * number)
    row = len(SAMPLE_SECTORS)
    inputs[0][row] = st.sidebar.number_input(
        f"Agriculture input per unit of {sectors[row]}", min_value=0.0, value=0.10, step=0.01,
    )
    inputs[row][0] = st.sidebar.number_input(
        f"{sectors[row]} input per unit of Agriculture", min_value=0.0, value=0.05, step=0.01,
    )
    explanation = (
        f"A grows from 5 × 5 to {count} × {count}. Each new sector adds a row, a column, "
        "a demand value and an equation. The first new sector can trade inputs with Agriculture."
    )

focus = st.sidebar.selectbox(
    "Equation to inspect", options=range(len(sectors)), index=row,
    format_func=lambda index: f"x{index + 1} · {sectors[index]}",
    key=f"inspect-{scenario}-{row}",
)
left, right = st.columns(2)
for panel, heading, names, values, final_demand in (
    (left, "Before", SAMPLE_SECTORS, SAMPLE_INPUTS, SAMPLE_DEMAND),
    (right, "After", sectors, inputs, demand),
):
    with panel:
        st.subheader(heading)
        st.write("**A** · Rows supply inputs. Columns produce output.")
        st.dataframe(pd.DataFrame(values, index=names, columns=names).round(4))
        st.write("**d** · Final demand")
        st.dataframe(pd.DataFrame({"Demand": final_demand}, index=names))
        if focus < len(names):
            st.write(f"**{names[focus]} balance**")
            st.latex(equation(values, final_demand, focus))
        else:
            st.write("This sector is added in the new scenario.")

st.subheader("What changed?")
st.write(explanation)
with st.expander("Show how the system matrix is built"):
    st.latex(r"x = Ax + d \quad\Longrightarrow\quad (I-A)x=d")
    st.write("I has 1 on the diagonal and 0 everywhere else. Subtract A cell by cell.")
    before_system, after_system = st.columns(2)
    with before_system:
        st.write("**Before · I − A**")
        st.dataframe(pd.DataFrame(
            system_matrix(SAMPLE_INPUTS), index=SAMPLE_SECTORS, columns=SAMPLE_SECTORS,
        ).round(4))
    with after_system:
        st.write("**After · I − A**")
        st.dataframe(pd.DataFrame(system_matrix(inputs), index=sectors, columns=sectors).round(4))


def show_production():
    st.header("Total production")
    try:
        validate_inputs(inputs, demand)
        if len(set(sectors)) != len(sectors):
            raise ValueError("Give each sector a different name.")
        lower, upper = productivity_bounds(inputs)
        st.write(f"**Productivity check:** spectral radius bounds {lower:.6g} to {upper:.6g}.")
        if lower >= 1:
            st.error("This input matrix is not productive. The spectral radius is at least 1.")
            return
        if upper >= 1:
            st.warning("The current bounds cannot confirm productivity. Try reducing the input rates.")
            return

        st.success("Productive: the upper bound is below 1.")
        coefficients = system_matrix(inputs)
        steps = []
        after = solve(coefficients, demand, trace=steps)
        before = solve(system_matrix(SAMPLE_INPUTS), SAMPLE_DEMAND)
        via_inverse = matvec(inverse(coefficients), demand)
    except ValueError as error:
        st.error(str(error))
        return

    before_lookup = dict(zip(SAMPLE_SECTORS, before))
    comparison = pd.DataFrame({
        "Before": [before_lookup.get(name, 0.0) for name in sectors],
        "After": after,
    }, index=pd.Index(sectors, name="Sector"))
    comparison["Change"] = comparison["After"] - comparison["Before"]
    st.dataframe(comparison.round(4))
    st.bar_chart(
        comparison[["Before", "After"]].reset_index().melt(
            id_vars="Sector", var_name="Scenario", value_name="Production",
        ),
        x="Sector", y="Production", color="Scenario", stack=False,
    )

    ranking = comparison["Change"].abs().sort_values(ascending=False, kind="stable").index
    st.write("**Ranked by size of change**")
    st.dataframe(comparison.loc[ranking, ["Change"]].round(4))

    with st.expander("Show the row operations and verify the answer"):
        st.write("Start with [I − A | d]. Each step makes one column of the left side match the identity matrix.")
        step = st.slider("Elimination step", 0, len(steps) - 1)
        operation, snapshot = steps[step]
        st.write(operation)
        columns = [f"x{number + 1}" for number in range(len(sectors))] + ["Right side"]
        st.dataframe(pd.DataFrame(snapshot, columns=columns).round(6))
        internal = matvec(inputs, after)
        check = pd.DataFrame({
            "Internal demand (Ax)": internal,
            "Final demand (d)": demand,
            "Ax + d": [a + b for a, b in zip(internal, demand)],
            "Elimination (x)": after,
            "Inverse (x)": via_inverse,
        }, index=sectors)
        st.dataframe(check.round(6))


show_production()
