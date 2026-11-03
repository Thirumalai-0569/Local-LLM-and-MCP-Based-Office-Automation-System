import pandas as pd
import plotly.express as px
import streamlit as st

def render_dashboard(uploaded_file):
    try:
        uploaded_file.seek(0)
        workbook = pd.ExcelFile(uploaded_file)
        sheet = st.selectbox("Select worksheet", workbook.sheet_names)
        uploaded_file.seek(0)
        df = pd.read_excel(uploaded_file, sheet_name=sheet)
        if df.empty:
            st.warning("This worksheet has no data.")
            return
        st.write(f"{len(df)} rows × {len(df.columns)} columns")
        st.dataframe(df.head(100), use_container_width=True)
        numeric_cols = df.select_dtypes(include="number").columns.tolist()
        all_cols = df.columns.tolist()
        chart_type = st.selectbox("Chart type", ["Bar", "Line", "Scatter", "Pie", "Histogram", "Box"])
        if chart_type == "Histogram":
            x = st.selectbox("Numeric column", numeric_cols or all_cols)
            fig = px.histogram(df, x=x, title=f"Distribution of {x}")
        elif chart_type == "Box":
            y = st.selectbox("Numeric column", numeric_cols or all_cols)
            fig = px.box(df, y=y, title=f"Box plot of {y}")
        else:
            x = st.selectbox("X-axis", all_cols)
            if chart_type == "Pie":
                y = st.selectbox("Values", numeric_cols or all_cols)
                fig = px.pie(df, names=x, values=y, title=f"{y} by {x}")
            else:
                y_options = [c for c in numeric_cols if c != x]
                if not y_options:
                    st.info("A chart with X and Y needs at least one numeric column.")
                    return
                y = st.selectbox("Y-axis (numeric)", y_options)
                if chart_type == "Bar":
                    agg = st.selectbox("Aggregation", ["Sum", "Mean", "Count"])
                    if agg == "Sum":
                        plot_df = df.groupby(x, dropna=False)[y].sum().reset_index()
                    elif agg == "Mean":
                        plot_df = df.groupby(x, dropna=False)[y].mean().reset_index()
                    else:
                        plot_df = df.groupby(x, dropna=False)[y].count().reset_index(name=y)
                    fig = px.bar(plot_df, x=x, y=y, title=f"{agg} of {y} by {x}")
                elif chart_type == "Line":
                    fig = px.line(df, x=x, y=y, title=f"{y} by {x}")
                else:
                    fig = px.scatter(df, x=x, y=y, title=f"{y} vs {x}")
        st.plotly_chart(fig, use_container_width=True)
        st.download_button("Download data as CSV", df.to_csv(index=False),
                           "dashboard_data.csv", "text/csv")
    except Exception as e:
        st.error(f"Dashboard error: {type(e).__name__}: {e}")
