import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from config import COLORS

def unified_time_series(df, time_unit='day', metric='minutes'):
    """
    Unified time series with multiple aggregation levels
    time_unit: 'day', 'month', 'year'
    metric: 'minutes' or 'streams'
    """
    music_df = df[df['is_music'] & df['actually_listened']].copy()
    
    if time_unit == 'day':
        grouped = music_df.groupby('date').agg(
            value=('minutes_played', 'sum') if metric == 'minutes' else ('ts', 'count'),
            artists=('master_metadata_album_artist_name', 'nunique'),
            tracks=('master_metadata_track_name', 'nunique')
        ).reset_index()
        grouped['date'] = pd.to_datetime(grouped['date'])
        
    elif time_unit == 'month':
        grouped = music_df.groupby(['year', 'month']).agg(
            value=('minutes_played', 'sum') if metric == 'minutes' else ('ts', 'count'),
            artists=('master_metadata_album_artist_name', 'nunique'),
            tracks=('master_metadata_track_name', 'nunique')
        ).reset_index()
        grouped['date'] = pd.to_datetime(grouped[['year', 'month']].assign(day=1))
        
    elif time_unit == 'year':
        grouped = music_df.groupby('year').agg(
            value=('minutes_played', 'sum') if metric == 'minutes' else ('ts', 'count'),
            artists=('master_metadata_album_artist_name', 'nunique'),
            tracks=('master_metadata_track_name', 'nunique')
        ).reset_index()
        grouped['date'] = pd.to_datetime(grouped['year'].astype(str) + '-01-01')
    
    if metric == 'minutes':
        grouped['value'] = grouped['value'] / 60  # Convert to hours
        value_label = 'Hours'
    else:
        value_label = 'Streams'
    
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Main metric area chart
    fig.add_trace(
        go.Scatter(
            x=grouped['date'],
            y=grouped['value'],
            fill='tozeroy',
            mode='lines+markers' if time_unit == 'year' else 'lines',
            line=dict(color='#1DB954', width=1.5),
            marker=dict(size=6, color='#1DB954') if time_unit == 'year' else None,
            fillcolor='rgba(29, 185, 84, 0.08)',
            name=value_label,
            hovertemplate='%{x|%b %d, %Y}<br>%{y:.1f} ' + value_label.lower() + '<extra></extra>'
        ),
        secondary_y=False
    )
    
    # Artist diversity line
    fig.add_trace(
        go.Scatter(
            x=grouped['date'],
            y=grouped['artists'],
            mode='lines',
            line=dict(color='#C8A951', width=1.5, dash='dot'),
            name='Unique Artists',
            hovertemplate='%{x|%b %d, %Y}<br>%{y} artists<extra></extra>'
        ),
        secondary_y=True
    )
    
    fig.update_layout(
        height=450,
        margin=dict(l=10, r=10, t=50, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter', color='#999999', size=11),
        hovermode='x unified',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
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
            title=value_label if time_unit != 'day' else None
        ),
        yaxis2=dict(
            gridcolor='rgba(255,255,255,0.03)',
            tickfont=dict(size=10),
            title='Artists' if time_unit != 'day' else None
        ),
        title=dict(
            text=f'LISTENING ACTIVITY — {time_unit.upper()}LY VIEW',
            font=dict(size=13, color='#999999', family='Inter'),
            x=0, xanchor='left',
            y=0.95
        )
    )
    
    return fig

def playlist_analysis(playlist_df, df):
    """Analyze playlist composition and overlap with listening"""
    
    if playlist_df.empty:
        fig = go.Figure()
        fig.update_layout(
            height=400,
            title=dict(
                text='PLAYLIST ANALYSIS — NO DATA AVAILABLE',
                font=dict(size=13, color='#999999', family='Inter')
            )
        )
        return fig
    
    # Top playlists by track count
    top_playlists = playlist_df.nlargest(10, 'track_count')
    
    fig = go.Figure(go.Bar(
        y=top_playlists['name'][::-1],
        x=top_playlists['track_count'][::-1],
        orientation='h',
        marker=dict(
            color=top_playlists['track_count'][::-1],
            colorscale=[[0, '#1DB954'], [0.5, '#1ED760'], [1, '#C8A951']],
            showscale=False
        ),
        text=top_playlists['track_count'][::-1].apply(lambda x: f'{x} tracks'),
        textposition='outside',
        textfont=dict(color='#CCCCCC', size=11, family='Inter'),
        width=0.7,
        hovertemplate='%{y}<br>%{x} tracks<extra></extra>'
    ))
    
    fig.update_layout(
        height=420,
        margin=dict(l=10, r=30, t=50, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter', color='#999999', size=11),
        xaxis=dict(gridcolor='rgba(255,255,255,0.03)'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.03)'),
        title=dict(
            text='LARGEST PLAYLISTS BY TRACK COUNT',
            font=dict(size=13, color='#999999', family='Inter'),
            x=0, xanchor='left',
            y=0.95
        )
    )
    
    return fig

def artist_time_distribution(df, artist_time_category):
    """Show when you listen to different artists"""
    
    time_counts = artist_time_category['time_category'].value_counts()
    time_order = ['Morning', 'Afternoon', 'Evening', 'Night']
    time_counts = time_counts.reindex(time_order).fillna(0)
    
    fig = go.Figure(data=[
        go.Bar(
            x=time_counts.index,
            y=time_counts.values,
            marker=dict(
                color=['#C8A951', '#1DB954', '#888888', '#666666'],
                opacity=0.8
            ),
            text=time_counts.values,
            textposition='outside',
            textfont=dict(color='#CCCCCC', size=12),
            width=0.5,
            hovertemplate='%{x}<br>%{y} artists peak here<extra></extra>'
        )
    ])
    
    fig.update_layout(
        height=380,
        margin=dict(l=10, r=10, t=50, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter', color='#999999', size=11),
        xaxis=dict(gridcolor='rgba(255,255,255,0.03)'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.03)', title='Artists'),
        title=dict(
            text='ARTIST PEAK LISTENING TIMES',
            font=dict(size=13, color='#999999', family='Inter'),
            x=0, xanchor='left',
            y=0.95
        )
    )
    
    return fig

def listening_diversity_radar(monthly_diversity):
    """Create a radar chart showing listening diversity"""
    
    latest = monthly_diversity.nlargest(6, 'date')
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=latest['unique_artists'].values,
        theta=latest['date'].dt.strftime('%B %Y').values,
        fill='toself',
        marker=dict(color='#1DB954'),
        line=dict(color='#1ED760', width=2),
        fillcolor='rgba(29, 185, 84, 0.15)',
        name='Unique Artists',
        hovertemplate='%{theta}<br>%{r} artists<extra></extra>'
    ))
    
    fig.update_layout(
        height=420,
        margin=dict(l=30, r=30, t=50, b=30),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter', color='#999999', size=11),
        polar=dict(
            radialaxis=dict(
                visible=True,
                gridcolor='rgba(255,255,255,0.05)',
                tickfont=dict(size=9, color='#666666')
            ),
            angularaxis=dict(
                gridcolor='rgba(255,255,255,0.05)',
                tickfont=dict(size=10, color='#999999')
            ),
            bgcolor='rgba(0,0,0,0)'
        ),
        title=dict(
            text='MONTHLY LISTENING DIVERSITY',
            font=dict(size=13, color='#999999', family='Inter'),
            x=0, xanchor='left',
            y=0.95
        )
    )
    
    return fig

def listening_consistency_calendar(df, year=None):
    """Create a GitHub-style calendar heatmap for a year"""
    
    if year is None:
        year = pd.Timestamp.now().year
    
    music_df = df[df['is_music'] & df['actually_listened']].copy()
    music_df['date'] = pd.to_datetime(music_df['date'])
    
    year_data = music_df[music_df['date'].dt.year == year]
    
    if year_data.empty:
        fig = go.Figure()
        fig.update_layout(
            height=200,
            title=dict(
                text=f'LISTENING CALENDAR — {year} (No Data)',
                font=dict(size=13, color='#999999', family='Inter'),
                x=0, xanchor='left'
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        return fig
    
    daily = year_data.groupby('date')['minutes_played'].sum().reset_index()
    daily['hours'] = daily['minutes_played'] / 60
    
    # Create complete date range up to today for current year
    if year == pd.Timestamp.now().year:
        end_date = pd.Timestamp.now().date()
    else:
        end_date = pd.Timestamp(f'{year}-12-31').date()
    
    start_date = pd.Timestamp(f'{year}-01-01').date()
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    full_year = pd.DataFrame({'date': date_range})
    full_year['date'] = pd.to_datetime(full_year['date'])
    full_year = full_year.merge(daily[['date', 'hours']], on='date', how='left').fillna(0)
    
    # Add week and day info
    full_year['day_of_week'] = full_year['date'].dt.dayofweek  # 0=Monday
    full_year['week_num'] = (full_year['date'] - full_year['date'].min()).dt.days // 7
    
    # Create pivot table
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    pivot_data = full_year.pivot_table(
        values='hours', 
        index='day_of_week', 
        columns='week_num', 
        aggfunc='sum',
        fill_value=0
    )
    
    # Reindex to ensure all days are present
    pivot_data = pivot_data.reindex(range(7), fill_value=0)
    pivot_data.index = days
    
    # Create hover text matrix matching pivot shape
    hover_matrix = []
    for day_idx in range(7):
        day_hovers = []
        for week_num in pivot_data.columns:
            matching_rows = full_year[
                (full_year['day_of_week'] == day_idx) & 
                (full_year['week_num'] == week_num)
            ]
            if not matching_rows.empty:
                date_str = matching_rows.iloc[0]['date'].strftime('%B %d, %Y')
                hours = matching_rows.iloc[0]['hours']
                day_hovers.append(f"{date_str}<br>{hours:.1f} hours")
            else:
                day_hovers.append("No data")
        hover_matrix.append(day_hovers)
    
    # Create week labels
    week_labels = []
    first_date = full_year['date'].min()
    for week_num in pivot_data.columns:
        week_start = first_date + pd.Timedelta(weeks=week_num)
        week_labels.append(week_start.strftime('%b %d'))
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot_data.values,
        x=week_labels,
        y=days,
        colorscale=[
            [0, '#0F0F0F'], 
            [0.15, '#0A1F12'], 
            [0.3, '#0D2818'], 
            [0.5, '#1A7A3A'], 
            [0.7, '#1DB954'], 
            [0.85, '#1ED760'], 
            [1, '#C8A951']
        ],
        hoverongaps=False,
        text=hover_matrix,
        hoverinfo='text',
        showscale=False,
        xgap=3,
        ygap=3
    ))
    
    fig.update_layout(
        height=220,
        margin=dict(l=10, r=20, t=50, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter', color='#999999', size=9),
        xaxis=dict(
            showgrid=False,
            tickfont=dict(size=8, color='#666666'),
            tickangle=-45,
            tickmode='auto',
            nticks=15
        ),
        yaxis=dict(
            showgrid=False,
            tickfont=dict(size=9, color='#999999')
        ),
        title=dict(
            text=f'LISTENING CALENDAR — {year}',
            font=dict(size=13, color='#999999', family='Inter'),
            x=0, xanchor='left',
            y=0.95
        )
    )
    
    return fig