# Premium Dark Theme Configuration - Luxe Edition
COLORS = {
    'background': '#080808',
    'surface': '#0F0F0F',
    'surface_light': '#1A1A1A',
    'surface_hover': '#222222',
    'primary': '#1DB954',
    'primary_dark': '#169C46',
    'primary_light': '#1ED760',
    'accent_gold': '#C8A951',
    'accent_silver': '#A8A8A8',
    'text_primary': '#FAFAFA',
    'text_secondary': '#999999',
    'text_muted': '#666666',
    'border': 'rgba(255,255,255,0.06)',
    'border_hover': 'rgba(255,255,255,0.12)',
    'gradient_dark': 'linear-gradient(135deg, #0A0A0A 0%, #1A1A1A 100%)',
    'gradient_green': 'linear-gradient(135deg, #1DB954 0%, #0D5C2A 100%)',
    'gradient_gold': 'linear-gradient(135deg, #C8A951 0%, #8B7332 100%)',
}

CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, sans-serif;
    }
    
    .stApp {
        background: #080808;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #0A0A0A;
        border-right: 1px solid rgba(255,255,255,0.04);
        padding: 2rem 1.5rem;
    }
    
    section[data-testid="stSidebar"] .stMarkdown {
        color: #999999;
    }
    
    /* Metric Cards - Premium Style */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #111111, #0F0F0F);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 1px;
        padding: 28px 24px;
        position: relative;
        overflow: hidden;
    }
    
    [data-testid="stMetric"]::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, #1DB954, #C8A951);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    [data-testid="stMetric"]:hover::before {
        opacity: 1;
    }
    
    [data-testid="stMetric"]:hover {
        border-color: rgba(255,255,255,0.1);
        background: linear-gradient(135deg, #141414, #111111);
    }
    
    [data-testid="stMetricLabel"] {
        font-family: 'Inter', sans-serif !important;
        font-size: 0.7rem !important;
        font-weight: 500 !important;
        letter-spacing: 2px !important;
        text-transform: uppercase !important;
        color: #666666 !important;
        margin-bottom: 8px !important;
    }
    
    [data-testid="stMetricValue"] {
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        font-size: 2.2rem !important;
        color: #FAFAFA !important;
        letter-spacing: -0.5px !important;
    }
    
    [data-testid="stMetricDelta"] {
        color: #1DB954 !important;
    }
    
    /* Typography */
    h1 {
        font-family: 'Inter', sans-serif !important;
        font-weight: 700 !important;
        font-size: 2.8rem !important;
        letter-spacing: -1px !important;
        color: #FAFAFA !important;
    }
    
    h2 {
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        font-size: 1.5rem !important;
        color: #FAFAFA !important;
        letter-spacing: -0.3px !important;
    }
    
    h3 {
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
        font-size: 1.1rem !important;
        color: #FAFAFA !important;
    }
    
    /* Tabs - Premium Style */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background: transparent;
        border-bottom: 1px solid rgba(255,255,255,0.06);
        padding-bottom: 0;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 0;
        color: #666666;
        padding: 14px 28px;
        font-weight: 500;
        font-size: 0.9rem;
        letter-spacing: 0.5px;
        border: none;
        border-bottom: 2px solid transparent;
        margin-bottom: -1px;
        transition: all 0.2s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: #999999;
        background: rgba(255,255,255,0.02);
    }
    
    .stTabs [aria-selected="true"] {
        color: #FAFAFA !important;
        border-bottom: 2px solid #1DB954 !important;
        background: transparent !important;
    }
    
    /* DataFrames */
    .dataframe {
        background: #0F0F0F;
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 1px;
        font-size: 0.85rem !important;
    }
    
    .dataframe th {
        background: #0A0A0A;
        color: #999999 !important;
        font-weight: 500 !important;
        letter-spacing: 1px !important;
        text-transform: uppercase !important;
        font-size: 0.7rem !important;
        padding: 12px 16px !important;
    }
    
    .dataframe td {
        color: #CCCCCC !important;
        padding: 10px 16px !important;
    }
    
    /* Select Boxes */
    .stSelectbox [data-baseweb="select"] {
        background: #0F0F0F;
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 1px;
        color: #FAFAFA;
    }
    
    /* Info/Warning Messages */
    .stAlert {
        background: #0F0F0F;
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 1px;
        color: #999999;
    }
    
    /* Spinner */
    .stSpinner {
        border-color: #1DB954;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
    }
    
    ::-webkit-scrollbar-track {
        background: #080808;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #333333;
        border-radius: 0;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #1DB954;
    }
</style>
"""