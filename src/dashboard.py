import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
from data_processor import SpotifyDataProcessor
from config import COLORS, CUSTOM_CSS
import warnings
warnings.filterwarnings('ignore')
from visualizations import (
    unified_time_series, 
    playlist_analysis, 
    artist_time_distribution,
    listening_diversity_radar,
    listening_consistency_calendar
)

st.set_page_config(
    page_title="Spotify Analytics",
    page_icon="●",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

@st.cache_data
def load_data():
    processor = SpotifyDataProcessor()
    df, metrics, account_data = processor.process_all()
    return df, metrics, account_data

def create_metric_card(label, value, subtitle=None, prefix="", suffix=""):
    """Premium metric card"""
    formatted_value = f"{prefix}{value:,.0f}{suffix}" if isinstance(value, (int, float)) else f"{prefix}{value}{suffix}"
    st.metric(label=label, value=formatted_value)
    if subtitle:
        st.caption(subtitle)

def listening_heatmap(df):
    """Premium listening heatmap"""
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    music_df = df[df['is_music'] & df['actually_listened']]
    heatmap_data = music_df.groupby(['day_of_week', 'hour'])['minutes_played'].sum().reset_index()
    pivot = heatmap_data.pivot(index='day_of_week', columns='hour', values='minutes_played')
    pivot = pivot.reindex(day_order)
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=[f'{h:02d}:00' for h in pivot.columns],
        y=pivot.index,
        colorscale=[[0, '#0A0A0A'], [0.3, '#0D2818'], [0.6, '#1DB954'], [0.8, '#1ED760'], [1, '#C8A951']],
        hoverongaps=False,
        hovertemplate='%{y} %{x}<br>%{z:.0f} minutes<extra></extra>',
        showscale=False
    ))
    
    fig.update_layout(
        height=420,
        margin=dict(l=10, r=10, t=50, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter', color='#999999', size=11),
        xaxis=dict(
            tickmode='linear', dtick=3,
            gridcolor='rgba(255,255,255,0.03)',
            tickfont=dict(size=10)
        ),
        yaxis=dict(
            gridcolor='rgba(255,255,255,0.03)',
            tickfont=dict(size=11)
        ),
        title=dict(
            text='LISTENING PATTERNS',
            font=dict(size=13, color='#999999', family='Inter'),
            x=0, xanchor='left',
            y=0.95
        )
    )
    
    return fig

def monthly_trend(df):
    """Premium monthly trend with gradient"""
    music_df = df[df['is_music'] & df['actually_listened']]
    monthly = music_df.groupby(['year', 'month'])['minutes_played'].sum().reset_index()
    monthly['date'] = pd.to_datetime(monthly[['year', 'month']].assign(day=1))
    monthly['hours'] = monthly['minutes_played'] / 60
    monthly['rolling'] = monthly['hours'].rolling(window=3, center=True).mean()
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=monthly['date'],
        y=monthly['hours'],
        fill='tozeroy',
        mode='lines',
        line=dict(width=0),
        fillcolor='rgba(29, 185, 84, 0.08)',
        showlegend=False,
        hoverinfo='skip'
    ))
    
    fig.add_trace(go.Scatter(
        x=monthly['date'],
        y=monthly['hours'],
        mode='lines',
        line=dict(color='#1DB954', width=1.5),
        name='Monthly',
        hovertemplate='%{x|%B %Y}<br>%{y:.0f} hours<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=monthly['date'],
        y=monthly['rolling'],
        mode='lines',
        line=dict(color='#C8A951', width=2.5),
        name='3-Month Average',
        hovertemplate='%{x|%B %Y}<br>%{y:.0f} hours (avg)<extra></extra>'
    ))
    
    fig.update_layout(
        height=400,
        margin=dict(l=10, r=10, t=50, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter', color='#999999', size=11),
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=10)
        ),
        xaxis=dict(
            gridcolor='rgba(255,255,255,0.03)',
            tickfont=dict(size=10)
        ),
        yaxis=dict(
            gridcolor='rgba(255,255,255,0.03)',
            tickfont=dict(size=10),
            title='Hours'
        ),
        title=dict(
            text='LISTENING TREND',
            font=dict(size=13, color='#999999', family='Inter'),
            x=0, xanchor='left',
            y=0.95
        )
    )
    
    return fig

def platform_distribution(df):
    """Premium platform donut"""
    music_df = df[df['is_music'] & df['actually_listened']]
    platform_data = music_df['platform_clean'].value_counts()
    
    fig = go.Figure(data=go.Pie(
        labels=platform_data.index,
        values=platform_data.values,
        hole=0.65,
        marker=dict(
            colors=['#1DB954', '#C8A951', '#888888', '#666666', '#444444'],
            line=dict(color='#080808', width=3)
        ),
        textinfo='label+percent',
        textfont=dict(size=11, family='Inter', color='#CCCCCC'),
        textposition='outside',
        hovertemplate='%{label}<br>%{value:,} streams<br>%{percent}<extra></extra>',
        showlegend=False
    ))
    
    fig.update_layout(
        height=420,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter', color='#999999'),
        title=dict(
            text='PLATFORM DISTRIBUTION',
            font=dict(size=13, color='#999999', family='Inter'),
            x=0, xanchor='left',
            y=0.95
        )
    )
    
    return fig

def top_artists_chart(df, limit=15):
    """Premium top artists visualization"""
    music_df = df[df['is_music'] & df['actually_listened']]
    
    top = (music_df.groupby('master_metadata_album_artist_name')
           .agg(hours=('minutes_played', 'sum'), streams=('master_metadata_track_name', 'count'))
           .sort_values('hours', ascending=False)
           .head(limit))
    
    top['hours'] = top['hours'] / 60
    
    fig = go.Figure(go.Bar(
        y=top.index[::-1],
        x=top['hours'][::-1],
        orientation='h',
        marker=dict(
            color=top['hours'][::-1],
            colorscale=[[0, '#1DB954'], [0.5, '#1ED760'], [1, '#C8A951']],
            showscale=False
        ),
        text=top['hours'][::-1].apply(lambda x: f'{x:.0f}h'),
        textposition='outside',
        textfont=dict(color='#CCCCCC', size=11, family='Inter'),
        hovertemplate='%{y}<br>%{x:.0f} hours<br>%{customdata:,} streams<extra></extra>',
        customdata=top['streams'].iloc[::-1].values,
        width=0.7
    ))
    
    fig.update_layout(
        height=500,
        margin=dict(l=10, r=30, t=50, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter', color='#999999', size=11),
        xaxis=dict(gridcolor='rgba(255,255,255,0.03)'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.03)', tickfont=dict(size=11)),
        title=dict(
            text='TOP ARTISTS BY LISTENING TIME',
            font=dict(size=13, color='#999999', family='Inter'),
            x=0, xanchor='left',
            y=0.95
        )
    )
    
    return fig

def top_tracks_chart(df, limit=15):
    """Premium top tracks"""
    music_df = df[df['is_music'] & df['actually_listened']]
    
    top = (music_df.groupby(['master_metadata_track_name', 'master_metadata_album_artist_name'])
           .agg(hours=('minutes_played', 'sum'), streams=('ts', 'count'))
           .sort_values('hours', ascending=False)
           .head(limit))
    
    top['hours'] = top['hours'] / 60
    top['label'] = top.index.get_level_values(0) + ' — ' + top.index.get_level_values(1)
    
    fig = go.Figure(go.Bar(
        y=top['label'][::-1],
        x=top['hours'][::-1],
        orientation='h',
        marker=dict(
            color=top['hours'][::-1],
            colorscale=[[0, '#C8A951'], [0.5, '#1ED760'], [1, '#1DB954']],
            showscale=False
        ),
        text=top['hours'][::-1].apply(lambda x: f'{x:.1f}h'),
        textposition='outside',
        textfont=dict(color='#CCCCCC', size=11, family='Inter'),
        hovertemplate='%{customdata[0]}<br>%{x:.1f} hours<br>%{customdata[1]:,} streams<extra></extra>',
        customdata=top[['label', 'streams']].iloc[::-1].values,
        width=0.7
    ))
    
    fig.update_layout(
        height=500,
        margin=dict(l=10, r=50, t=50, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter', color='#999999', size=10),
        xaxis=dict(gridcolor='rgba(255,255,255,0.03)'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.03)'),
        title=dict(
            text='MOST PLAYED TRACKS',
            font=dict(size=13, color='#999999', family='Inter'),
            x=0, xanchor='left',
            y=0.95
        )
    )
    
    return fig

def skip_analysis(df):
    """Premium skip rate analysis"""
    music_df = df[df['is_music']]
    
    hourly = music_df.groupby('hour').agg(total=('skipped', 'count'), skipped=('skipped', 'sum'))
    hourly['skip_rate'] = (hourly['skipped'] / hourly['total']) * 100
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=hourly.index,
        y=hourly['skip_rate'],
        mode='lines+markers',
        line=dict(color='#C8A951', width=2),
        marker=dict(size=6, color='#C8A951', line=dict(color='#080808', width=1)),
        fill='tozeroy',
        fillcolor='rgba(200, 169, 81, 0.08)',
        hovertemplate='%{x}:00<br>%{y:.1f}% skip rate<extra></extra>'
    ))
    
    fig.update_layout(
        height=400,
        margin=dict(l=10, r=10, t=50, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter', color='#999999', size=11),
        xaxis=dict(tickmode='linear', dtick=3, gridcolor='rgba(255,255,255,0.03)'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.03)', ticksuffix='%'),
        title=dict(
            text='SKIP RATE BY HOUR',
            font=dict(size=13, color='#999999', family='Inter'),
            x=0, xanchor='left',
            y=0.95
        )
    )
    
    return fig

def discovery_analysis(df):
    """Artist discovery over time"""
    music_df = df[df['is_music'] & df['actually_listened']].copy()
    music_df = music_df.sort_values('ts')
    
    # Track first appearance of each artist
    first_seen = music_df.groupby('master_metadata_album_artist_name')['date'].min().reset_index()
    first_seen['year_month'] = pd.to_datetime(first_seen['date']).dt.to_period('M')
    
    new_artists_monthly = first_seen.groupby('year_month').size().reset_index(name='new_artists')
    new_artists_monthly['date'] = new_artists_monthly['year_month'].dt.to_timestamp()
    new_artists_monthly['cumulative'] = new_artists_monthly['new_artists'].cumsum()
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig.add_trace(
        go.Bar(
            x=new_artists_monthly['date'],
            y=new_artists_monthly['new_artists'],
            name='New Artists',
            marker=dict(color='#1DB954', opacity=0.7),
            hovertemplate='%{x|%B %Y}<br>%{y} new artists<extra></extra>'
        ),
        secondary_y=False
    )
    
    fig.add_trace(
        go.Scatter(
            x=new_artists_monthly['date'],
            y=new_artists_monthly['cumulative'],
            name='Total Discovered',
            line=dict(color='#C8A951', width=2.5),
            hovertemplate='%{x|%B %Y}<br>%{y} total artists<extra></extra>'
        ),
        secondary_y=True
    )
    
    fig.update_layout(
        height=400,
        margin=dict(l=10, r=10, t=50, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter', color='#999999', size=11),
        hovermode='x unified',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        xaxis=dict(gridcolor='rgba(255,255,255,0.03)'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.03)', title='New Artists'),
        yaxis2=dict(gridcolor='rgba(255,255,255,0.03)', title='Cumulative'),
        title=dict(
            text='ARTIST DISCOVERY',
            font=dict(size=13, color='#999999', family='Inter'),
            x=0, xanchor='left',
            y=0.95
        )
    )
    
    return fig

def listening_sessions(df):
    """Analyze listening sessions"""
    music_df = df[df['is_music']].copy()
    music_df = music_df.sort_values('ts')
    
    # Identify sessions (breaks > 30 min)
    music_df['gap'] = music_df['ts'].diff().dt.total_seconds() / 60
    music_df['new_session'] = music_df['gap'] > 30
    
    sessions = []
    current_start = None
    current_tracks = []
    current_minutes = 0
    
    for idx, row in music_df.iterrows():
        if row['new_session'] or current_start is None:
            if current_start is not None and current_tracks:
                sessions.append({
                    'start': current_start,
                    'tracks': len(current_tracks),
                    'minutes': current_minutes,
                    'hour': current_start.hour,
                    'day': current_start.day_name()
                })
            current_start = row['ts']
            current_tracks = [row['master_metadata_track_name']]
            current_minutes = row['minutes_played'] if row['actually_listened'] else 0
        else:
            current_tracks.append(row['master_metadata_track_name'])
            if row['actually_listened']:
                current_minutes += row['minutes_played']
    
    sessions_df = pd.DataFrame(sessions)
    
    # Session length distribution
    bins = [0, 10, 30, 60, 120, 240, float('inf')]
    labels = ['<10m', '10-30m', '30-60m', '1-2h', '2-4h', '4h+']
    sessions_df['duration_bucket'] = pd.cut(sessions_df['minutes'], bins=bins, labels=labels)
    
    bucket_counts = sessions_df['duration_bucket'].value_counts().reindex(labels)
    
    fig = go.Figure(go.Bar(
        x=bucket_counts.index,
        y=bucket_counts.values,
        marker=dict(
            color=bucket_counts.values,
            colorscale=[[0, '#1DB954'], [1, '#C8A951']],
            showscale=False
        ),
        text=bucket_counts.values,
        textposition='outside',
        textfont=dict(color='#CCCCCC', size=11),
        width=0.6
    ))
    
    fig.update_layout(
        height=400,
        margin=dict(l=10, r=10, t=50, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter', color='#999999', size=11),
        xaxis=dict(gridcolor='rgba(255,255,255,0.03)'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.03)', title='Sessions'),
        title=dict(
            text='SESSION DURATION DISTRIBUTION',
            font=dict(size=13, color='#999999', family='Inter'),
            x=0, xanchor='left',
            y=0.95
        )
    )
    
    return fig

def top_artists_skip(df, min_streams=30):
    """Artists with highest/lowest skip rates"""
    music_df = df[df['is_music']]
    
    artist_stats = music_df.groupby('master_metadata_album_artist_name').agg(
        total_streams=('skipped', 'count'),
        skips=('skipped', 'sum'),
        avg_time=('minutes_played', 'mean')
    )
    
    artist_stats = artist_stats[artist_stats['total_streams'] >= min_streams]
    artist_stats['skip_rate'] = (artist_stats['skips'] / artist_stats['total_streams']) * 100
    
    # Least skipped (most engaging)
    least_skipped = artist_stats.nsmallest(10, 'skip_rate')[['skip_rate', 'total_streams']]
    
    fig = go.Figure(go.Bar(
        y=least_skipped.index[::-1],
        x=least_skipped['skip_rate'][::-1],
        orientation='h',
        marker=dict(
            color=least_skipped['skip_rate'][::-1],
            colorscale=[[0, '#1DB954'], [1, '#1ED760']],
            showscale=False
        ),
        text=least_skipped['skip_rate'][::-1].apply(lambda x: f'{x:.1f}%'),
        textposition='outside',
        textfont=dict(color='#CCCCCC', size=11),
        width=0.6
    ))
    
    fig.update_layout(
        height=400,
        margin=dict(l=10, r=30, t=50, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter', color='#999999', size=11),
        xaxis=dict(gridcolor='rgba(255,255,255,0.03)', ticksuffix='%'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.03)'),
        title=dict(
            text='MOST ENGAGING ARTISTS (LOWEST SKIP RATE)',
            font=dict(size=13, color='#999999', family='Inter'),
            x=0, xanchor='left',
            y=0.95
        )
    )
    
    return fig

def yearly_comparison(df):
    """Year over year comparison"""
    music_df = df[df['is_music'] & df['actually_listened']]
    yearly = music_df.groupby('year').agg(
        hours=('minutes_played', 'sum'),
        artists=('master_metadata_album_artist_name', 'nunique'),
        tracks=('master_metadata_track_name', 'nunique'),
        streams=('ts', 'count')
    ).reset_index()
    
    yearly['hours'] = yearly['hours'] / 60
    
    current_year = datetime.now().year
    yearly = yearly[yearly['year'] < current_year + 1]
    
    fig = make_subplots(rows=2, cols=2, 
                        subplot_titles=('Total Hours', 'Unique Artists', 'Unique Tracks', 'Total Streams'),
                        vertical_spacing=0.15,
                        horizontal_spacing=0.15)
    
    metrics = [
        ('hours', 'Hours', '#1DB954'),
        ('artists', 'Artists', '#C8A951'),
        ('tracks', 'Tracks', '#888888'),
        ('streams', 'Streams', '#666666')
    ]
    
    for i, (col, title, color) in enumerate(metrics):
        row, col_pos = i // 2 + 1, i % 2 + 1
        fig.add_trace(
            go.Bar(
                x=yearly['year'],
                y=yearly[col],
                marker=dict(color=color, opacity=0.8),
                text=yearly[col].apply(lambda x: f'{x:,.0f}'),
                textposition='outside',
                textfont=dict(size=10, color='#CCCCCC'),
                name=title,
                showlegend=False
            ),
            row=row, col=col_pos
        )
    
    fig.update_layout(
        height=500,
        margin=dict(l=10, r=10, t=50, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter', color='#999999', size=10),
    )
    
    fig.update_xaxes(gridcolor='rgba(255,255,255,0.03)', dtick=1)
    fig.update_yaxes(gridcolor='rgba(255,255,255,0.03)')
    
    return fig

def main():
    processor = SpotifyDataProcessor()
    df, metrics, account_data = processor.process_all()
    
    # Premium Header
    st.markdown("""
    <div style="padding: 40px 0 50px 0;">
        <div style="display: flex; align-items: baseline; gap: 12px; margin-bottom: 8px;">
            <div style="width: 4px; height: 32px; background: linear-gradient(180deg, #1DB954, #C8A951);"></div>
            <h1 style="margin: 0;">Listening Analytics</h1>
        </div>
        <p style="color: #666666; font-size: 0.9rem; letter-spacing: 2px; text-transform: uppercase; margin-left: 16px;">
            Personal Statistics &nbsp;·&nbsp; 2021–2026
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Key Metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        create_metric_card("TOTAL LISTENING", metrics['total_hours'], suffix=" hours")
    with col2:
        create_metric_card("DAILY AVERAGE", metrics['avg_daily_minutes'], suffix=" min")
    with col3:
        create_metric_card("ARTISTS EXPLORED", metrics['unique_artists'])
    with col4:
        create_metric_card("UNIQUE TRACKS", metrics['unique_tracks'])
    with col5:
        create_metric_card("AVG SESSION", metrics['avg_session_length'], suffix=" min")
    
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    
        # Tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Overview", 
        "Time Analysis",
        "Artists & Tracks", 
        "Playlists & Genres",
        "Discovery", 
        "Behavior"
    ])
    
    with tab1:
        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([1.2, 0.8])
        with col1:
            st.plotly_chart(listening_heatmap(df), use_container_width=True, config={'displayModeBar': False})
        with col2:
            st.plotly_chart(platform_distribution(df), use_container_width=True, config={'displayModeBar': False})
        
        st.plotly_chart(monthly_trend(df), use_container_width=True, config={'displayModeBar': False})
        
        # Calendar heatmap for current year
        st.plotly_chart(
            listening_consistency_calendar(df, year=datetime.now().year), 
            use_container_width=True, 
            config={'displayModeBar': False}
        )
    
    with tab2:
        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
        
        # Time unit and metric filters
        col1, col2, col3 = st.columns([1, 1, 3])
        with col1:
            time_unit = st.selectbox(
                'Time Scale',
                ['day', 'month', 'year'],
                format_func=lambda x: x.title()
            )
        with col2:
            metric = st.selectbox(
                'Metric',
                ['minutes', 'streams'],
                format_func=lambda x: 'Hours' if x == 'minutes' else 'Streams'
            )
        
        st.plotly_chart(
            unified_time_series(df, time_unit=time_unit, metric=metric), 
            use_container_width=True, 
            config={'displayModeBar': False}
        )
        
        # Additional time-based stats
        st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
        
        music_df = df[df['is_music'] & df['actually_listened']]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Most active day of week
            day_stats = music_df.groupby('day_of_week')['minutes_played'].sum() / 60
            most_active_day = day_stats.idxmax()
            day_hours = day_stats.max()
            st.markdown(f"""
            <div style="background: #0F0F0F; border: 1px solid rgba(255,255,255,0.06); padding: 24px;">
                <p style="color: #666666; font-size: 0.7rem; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 8px;">Most Active Day</p>
                <p style="color: #FAFAFA; font-size: 1.8rem; font-weight: 600; margin: 0;">{most_active_day}</p>
                <p style="color: #999999; font-size: 0.85rem; margin-top: 8px;">{day_hours:.0f} hours total</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Most active month
            month_stats = music_df.groupby('month')['minutes_played'].sum() / 60
            most_active_month_num = month_stats.idxmax()
            month_names = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 
                          5: 'May', 6: 'June', 7: 'July', 8: 'August',
                          9: 'September', 10: 'October', 11: 'November', 12: 'December'}
            month_hours = month_stats.max()
            st.markdown(f"""
            <div style="background: #0F0F0F; border: 1px solid rgba(255,255,255,0.06); padding: 24px;">
                <p style="color: #666666; font-size: 0.7rem; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 8px;">Most Active Month</p>
                <p style="color: #FAFAFA; font-size: 1.8rem; font-weight: 600; margin: 0;">{month_names[most_active_month_num]}</p>
                <p style="color: #999999; font-size: 0.85rem; margin-top: 8px;">{month_hours:.0f} hours total</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            # Listening streak
            music_df_daily = music_df.groupby('date')['minutes_played'].sum().reset_index()
            music_df_daily['date'] = pd.to_datetime(music_df_daily['date'])
            music_df_daily = music_df_daily.sort_values('date')
            
            # Calculate streaks (days with >10 min listening)
            music_df_daily['streak_day'] = music_df_daily['minutes_played'] > 10
            streaks = (music_df_daily['streak_day'] != music_df_daily['streak_day'].shift()).cumsum()
            streak_lengths = music_df_daily.groupby(streaks)['streak_day'].sum()
            longest_streak = streak_lengths[streak_lengths > 0].max()
            
            st.markdown(f"""
            <div style="background: #0F0F0F; border: 1px solid rgba(255,255,255,0.06); padding: 24px;">
                <p style="color: #666666; font-size: 0.7rem; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 8px;">Longest Streak</p>
                <p style="color: #FAFAFA; font-size: 1.8rem; font-weight: 600; margin: 0;">{longest_streak} days</p>
                <p style="color: #999999; font-size: 0.85rem; margin-top: 8px;">Consecutive listening days</p>
            </div>
            """, unsafe_allow_html=True)
    
    with tab3:
        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(top_artists_chart(df), use_container_width=True, config={'displayModeBar': False})
        with col2:
            st.plotly_chart(top_tracks_chart(df), use_container_width=True, config={'displayModeBar': False})
        
        st.plotly_chart(top_artists_skip(df), use_container_width=True, config={'displayModeBar': False})
    
    with tab4:
        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Playlist analysis
            st.plotly_chart(
                playlist_analysis(processor.playlist_df, df), 
                 use_container_width=True, 
                config={'displayModeBar': False}
)
            
            # Playlist stats
            if not processor.playlist_df.empty:
                total_playlists = len(processor.playlist_df)
                total_tracks_in_playlists = processor.playlist_df['track_count'].sum()
                avg_tracks = processor.playlist_df['track_count'].mean()
                
                st.markdown(f"""
                <div style="background: #0F0F0F; border: 1px solid rgba(255,255,255,0.06); padding: 20px; margin-top: 10px;">
                    <div style="display: flex; justify-content: space-around; text-align: center;">
                        <div>
                            <p style="color: #666666; font-size: 0.65rem; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 4px;">Playlists</p>
                            <p style="color: #FAFAFA; font-size: 1.5rem; font-weight: 600; margin: 0;">{total_playlists}</p>
                        </div>
                        <div>
                            <p style="color: #666666; font-size: 0.65rem; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 4px;">Total Tracks</p>
                            <p style="color: #FAFAFA; font-size: 1.5rem; font-weight: 600; margin: 0;">{total_tracks_in_playlists}</p>
                        </div>
                        <div>
                            <p style="color: #666666; font-size: 0.65rem; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 4px;">Avg. Size</p>
                            <p style="color: #FAFAFA; font-size: 1.5rem; font-weight: 600; margin: 0;">{avg_tracks:.0f}</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            # Genre/Time distribution
            st.plotly_chart(
                artist_time_distribution(df, processor.artist_time_category), 
                use_container_width=True, 
                config={'displayModeBar': False}
            )
            
            # Top genres from Wrapped
            if processor.genre_data:
                st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                st.markdown("""
                <p style="color: #999999; font-size: 13px; margin-bottom: 15px; letter-spacing: 0.5px;">
                    TOP GENRES — SPOTIFY WRAPPED 2025
                </p>
                """, unsafe_allow_html=True)
                
                for i, genre in enumerate(processor.genre_data[:10]):
                    st.markdown(f"""
                    <div style="display: flex; align-items: center; margin-bottom: 8px;">
                        <div style="color: #666666; font-size: 0.7rem; width: 20px;">{i+1:02d}</div>
                        <div style="flex: 1; color: #CCCCCC; font-size: 0.85rem;">{genre}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Genre data available from Spotify Wrapped")
        
        # Diversity radar
        st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
        st.plotly_chart(
            listening_diversity_radar(processor.monthly_diversity), 
            use_container_width=True, 
            config={'displayModeBar': False}
        )
    
    with tab5:
        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
        st.plotly_chart(discovery_analysis(df), use_container_width=True, config={'displayModeBar': False})
        
        # Recently discovered
        music_df = df[df['is_music'] & df['actually_listened']]
        artists_by_first = music_df.groupby('master_metadata_album_artist_name')['date'].min().sort_values(ascending=False)
        recent = artists_by_first.head(5)
        
        st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
        st.markdown("""
        <p style="color: #999999; font-size: 13px; letter-spacing: 0.5px;">
            RECENTLY DISCOVERED ARTISTS
        </p>
        """, unsafe_allow_html=True)
        
        cols = st.columns(5)
        for i, (artist, date) in enumerate(recent.items()):
            with cols[i]:
                st.markdown(f"""
                <div style="background: #0F0F0F; border: 1px solid rgba(255,255,255,0.06); padding: 20px; text-align: center;">
                    <p style="color: #CCCCCC; font-size: 0.9rem; margin-bottom: 8px;">{artist}</p>
                    <p style="color: #666666; font-size: 0.75rem;">{date.strftime('%B %d, %Y')}</p>
                </div>
                """, unsafe_allow_html=True)
    
    with tab6:
        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(skip_analysis(df), use_container_width=True, config={'displayModeBar': False})
        with col2:
            st.plotly_chart(listening_sessions(df), use_container_width=True, config={'displayModeBar': False})
        
        # Additional behavior stats
        st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
        
        music_df_all = df[df['is_music']]
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            shuffle_rate = (music_df_all['shuffle'] == True).mean() * 100
            st.markdown(f"""
            <div style="background: #0F0F0F; border: 1px solid rgba(255,255,255,0.06); padding: 20px; text-align: center;">
                <p style="color: #666666; font-size: 0.65rem; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 8px;">Shuffle Usage</p>
                <p style="color: #FAFAFA; font-size: 1.5rem; font-weight: 600; margin: 0;">{shuffle_rate:.1f}%</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            offline_rate = (music_df_all['offline'] == True).mean() * 100
            st.markdown(f"""
            <div style="background: #0F0F0F; border: 1px solid rgba(255,255,255,0.06); padding: 20px; text-align: center;">
                <p style="color: #666666; font-size: 0.65rem; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 8px;">Offline Listening</p>
                <p style="color: #FAFAFA; font-size: 1.5rem; font-weight: 600; margin: 0;">{offline_rate:.1f}%</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            completion_rate = (music_df_all['ms_played'] > (music_df_all['ms_played'].quantile(0.9))).mean() * 100
            st.markdown(f"""
            <div style="background: #0F0F0F; border: 1px solid rgba(255,255,255,0.06); padding: 20px; text-align: center;">
                <p style="color: #666666; font-size: 0.65rem; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 8px;">High Completion</p>
                <p style="color: #FAFAFA; font-size: 1.5rem; font-weight: 600; margin: 0;">{completion_rate:.1f}%</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            incognito_rate = (music_df_all['incognito_mode'] == True).mean() * 100
            st.markdown(f"""
            <div style="background: #0F0F0F; border: 1px solid rgba(255,255,255,0.06); padding: 20px; text-align: center;">
                <p style="color: #666666; font-size: 0.65rem; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 8px;">Incognito Mode</p>
                <p style="color: #FAFAFA; font-size: 1.5rem; font-weight: 600; margin: 0;">{incognito_rate:.1f}%</p>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()