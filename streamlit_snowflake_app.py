import streamlit as st
from snowflake.snowpark.context import get_active_session
import pandas as pd
import altair as alt

# Set page configuration
st.set_page_config(
    page_title="Interactive Sales Dashboard",
    page_icon="❄️",
    layout="wide",
)

# --- Snowflake Connection ---
def get_snowpark_session():
    """Gets the active Snowpark session."""
    try:
        return get_active_session()
    except Exception:
        st.error("Could not get Snowpark session. Are you running this in Snowflake?")
        return None

session = get_snowpark_session()

# --- Data Loading and Caching ---
@st.cache_data(ttl=3600) # Cache data for 1 hour
def load_data(table_name="sales_data"):
    """Loads data from the specified Snowflake table."""
    if not session:
        return None
    try:
        snowpark_df = session.table(table_name)
        return snowpark_df.to_pandas()
    except Exception as e:
        st.error(f"Error loading data from Snowflake: {e}")
        return None

# --- Main Application ---
def main():
    """The main function for the Streamlit application."""

    st.title("❄️ Interactive Sales Dashboard")
    st.markdown("This dashboard provides an interactive way to explore sales data directly from your Snowflake database.")

    # Load the data
    with st.spinner("Loading data from Snowflake..."):
        df = load_data()

    if df is None or df.empty:
        st.warning("No data found or failed to load. Please ensure the 'sales_data' table exists and contains data.")
        st.stop()

    # --- Data Transformation ---
    # Convert 'DATE' column to datetime objects
    df['DATE'] = pd.to_datetime(df['DATE'])
    df['YEAR'] = df['DATE'].dt.year
    df['MONTH'] = df['DATE'].dt.to_period('M').astype(str)
    df['SALES'] = pd.to_numeric(df['SALES'])


    # --- Sidebar Filters ---
    st.sidebar.header("Dashboard Filters")

    # Region Filter
    unique_regions = sorted(df['REGION'].unique())
    selected_regions = st.sidebar.multiselect("Region", unique_regions, default=unique_regions)

    # Year Filter
    unique_years = sorted(df['YEAR'].unique(), reverse=True)
    selected_year = st.sidebar.selectbox("Year", unique_years)

    # --- Filter Dataframe ---
    if selected_regions:
        df_filtered = df[df['REGION'].isin(selected_regions) & (df['YEAR'] == selected_year)]
    else:
        df_filtered = df[df['YEAR'] == selected_year]
        st.sidebar.warning("Please select at least one region.")


    if df_filtered.empty:
        st.warning("No data available for the selected filters.")
        st.stop()

    # --- Key Performance Indicators (KPIs) ---
    total_sales = df_filtered['SALES'].sum()
    total_transactions = df_filtered.shape[0]
    average_sale_value = df_filtered['SALES'].mean()

    st.header(f"Sales Performance for {selected_year}")
    kpi_cols = st.columns(3)
    kpi_cols[0].metric(label="Total Sales", value=f"${total_sales:,.2f}")
    kpi_cols[1].metric(label="Total Transactions", value=f"{total_transactions:,}")
    kpi_cols[2].metric(label="Average Sale Value", value=f"${average_sale_value:,.2f}")

    st.markdown("---")


    # --- Charts ---
    st.header("Visualizations")
    col1, col2 = st.columns(2)

    with col1:
        # Sales Over Time (Monthly)
        st.subheader("Monthly Sales Trend")
        monthly_sales = df_filtered.groupby('MONTH')['SALES'].sum().reset_index()

        time_chart = alt.Chart(monthly_sales).mark_line(
            point=True,
            strokeWidth=3,
            tooltip=True
        ).encode(
            x=alt.X('MONTH', title='Month'),
            y=alt.Y('SALES', title='Total Sales', axis=alt.Axis(format='$,.0f')),
        ).properties(
            height=300
        )
        st.altair_chart(time_chart, use_container_width=True)

    with col2:
        # Sales by Region
        st.subheader("Sales by Region")
        region_sales = df_filtered.groupby('REGION')['SALES'].sum().reset_index()
        
        region_chart = alt.Chart(region_sales).mark_bar(
            cornerRadius=5,
            tooltip=True
        ).encode(
            x=alt.X('SALES', title='Total Sales', axis=alt.Axis(format='$,.0f')),
            y=alt.Y('REGION', title='Region', sort='-x'),
            color=alt.Color('REGION', legend=None)
        ).properties(
            height=300
        )
        st.altair_chart(region_chart, use_container_width=True)

    # --- Detailed Data View ---
    st.header("Detailed Sales Data")
    st.dataframe(df_filtered.sort_values(by="DATE", ascending=False))


if __name__ == "__main__":
    if session:
        main()

