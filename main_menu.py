import streamlit as st
from src.utils import apply_base_style, load_data, init_session_states


st.container(height=20)
st.image('hv_logo.png')

st.set_page_config(
    page_title='HomeVision Quality Control Dashboard',
    layout='wide',
    initial_sidebar_state='expanded',
)
apply_base_style()

# st.title('HomeVision Quality Control Dashboard')
st.caption('Explore Quality Control Metrics and Insights')

apps = {
    'Main': [st.Page('apps/main_dashboard/main_dashboard.py', title='Main Dashboard', icon='🏠')],
    # 'Time Series': [st.Page('apps/time_series/time_series.py', title='Time Series Analysis', icon='📈')],
}

pg = st.navigation(apps)
pg.run()
