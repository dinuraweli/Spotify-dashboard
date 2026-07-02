import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import numpy as np

class SpotifyDataProcessor:
    def __init__(self):
        self.df = None
        self.account_data = {}
        
    def load_extended_history(self):
        """Load and combine all extended streaming history files"""
        print("📂 Loading extended streaming history...")
        
        all_streams = []
        history_path = Path('data/extended_history')
        
        # Get all audio history files (excluding video)
        audio_files = sorted(history_path.glob('Streaming_History_Audio_*.json'))
        
        for file in audio_files:
            with open(file, 'r') as f:
                data = json.load(f)
                all_streams.extend(data)
        
        self.df = pd.DataFrame(all_streams)
        print(f"✅ Loaded {len(self.df):,} streams")
        
    def clean_data(self):
        """Clean and transform the streaming data"""
        print("🧹 Cleaning data...")
        
        # Convert timestamp
        self.df['ts'] = pd.to_datetime(self.df['ts'])
        
        # Extract time components
        self.df['date'] = self.df['ts'].dt.date
        self.df['hour'] = self.df['ts'].dt.hour
        self.df['day_of_week'] = self.df['ts'].dt.day_name()
        self.df['month'] = self.df['ts'].dt.month
        self.df['year'] = self.df['ts'].dt.year
        self.df['weekday'] = self.df['ts'].dt.weekday  # 0=Monday
        
        # Listening time in minutes
        self.df['minutes_played'] = self.df['ms_played'] / 60000
        
        # Define "actually listened" - Spotify uses 30 seconds minimum
        self.df['actually_listened'] = self.df['ms_played'] >= 30000
        
        # Clean platform names
        self.df['platform_clean'] = self.df['platform'].str.lower()
        self.df['platform_clean'] = self.df['platform_clean'].apply(self._clean_platform)
        
        # Identify podcasts/audiobooks vs music
        self.df['is_music'] = self.df['master_metadata_track_name'].notna()
        
        # Filter out null artists/tracks (usually podcasts/audiobooks)
        music_mask = (
            self.df['master_metadata_album_artist_name'].notna() & 
            self.df['master_metadata_track_name'].notna()
        )
        self.df.loc[music_mask, 'artist_track'] = (
            self.df.loc[music_mask, 'master_metadata_album_artist_name'] + ' - ' + 
            self.df.loc[music_mask, 'master_metadata_track_name']
        )
        
        print(f"✅ Data cleaned")
        print(f"   Date range: {self.df['ts'].min()} to {self.df['ts'].max()}")
        print(f"   Unique artists: {self.df[music_mask]['master_metadata_album_artist_name'].nunique():,}")
        print(f"   Unique tracks: {self.df[music_mask]['master_metadata_track_name'].nunique():,}")
        
    def _clean_platform(self, platform):
        """Standardize platform names"""
        if pd.isna(platform):
            return 'Unknown'
        platform = str(platform).lower()
        if 'ios' in platform or 'iphone' in platform:
            return 'iOS'
        elif 'android' in platform:
            return 'Android'
        elif 'osx' in platform or 'os x' in platform or 'mac' in platform:
            return 'macOS'
        elif 'windows' in platform:
            return 'Windows'
        elif 'web' in platform:
            return 'Web Player'
        elif 'linux' in platform:
            return 'Linux'
        else:
            return 'Other'
    
    def load_account_data(self):
        """Load Spotify account data"""
        print("📂 Loading account data...")
        account_path = Path('data/account_data')
        
        # Load Wrapped 2025 data (very useful)
        with open(account_path / 'Wrapped2025.json', 'r') as f:
            self.account_data['wrapped'] = json.load(f)
        
        # Load library
        with open(account_path / 'YourLibrary.json', 'r') as f:
            self.account_data['library'] = json.load(f)
        
        # Load playlists
        with open(account_path / 'Playlist1.json', 'r') as f:
            self.account_data['playlists'] = json.load(f)
        
        # Load search queries
        with open(account_path / 'SearchQueries.json', 'r') as f:
            self.account_data['searches'] = json.load(f)
            
        print("✅ Account data loaded")
    
    def compute_metrics(self):
        """Compute key listening metrics"""
        print("📊 Computing metrics...")
        
        music_df = self.df[self.df['is_music']]
        actually_listened = music_df[music_df['actually_listened']]
        
        metrics = {
            'total_streams': len(music_df),
            'total_hours': actually_listened['minutes_played'].sum() / 60,
            'unique_artists': actually_listened['master_metadata_album_artist_name'].nunique(),
            'unique_tracks': actually_listened['master_metadata_track_name'].nunique(),
            'avg_daily_minutes': actually_listened.groupby('date')['minutes_played'].sum().mean(),
            'skip_rate': (music_df['skipped'] == True).mean() * 100,
            'active_days': actually_listened['date'].nunique(),
            'avg_session_length': self._compute_avg_session_length(),
        }
        
        self.metrics = metrics
        print(f"✅ Metrics computed: {metrics['total_hours']:.0f} hours total")
        
    def _compute_avg_session_length(self):
        """Estimate average listening session length"""
        music_df = self.df[self.df['is_music']].copy()
        music_df = music_df.sort_values('ts')
        
        # A session break is >30 minutes between tracks
        music_df['time_diff'] = music_df['ts'].diff().dt.total_seconds() / 60
        music_df['new_session'] = music_df['time_diff'] > 30
        
        session_lengths = []
        current_session = 0
        
        for _, row in music_df.iterrows():
            if row['new_session'] or current_session == 0:
                if current_session > 0:
                    session_lengths.append(current_session)
                current_session = row['minutes_played']
            else:
                current_session += row['minutes_played']
        
        if current_session > 0:
            session_lengths.append(current_session)
            
        return np.mean(session_lengths) if session_lengths else 0

    def extract_playlist_data(self):
        """Extract detailed playlist information"""
        print("📋 Extracting playlist data...")
        
        playlists_raw = self.account_data.get('playlists', {})
        playlists_list = playlists_raw.get('playlists', [])
        
        playlist_data = []
        for playlist in playlists_list:
            name = playlist.get('name', 'Unknown')
            modified = playlist.get('lastModifiedDate', '')
            items = playlist.get('items', [])
            
            # Extract tracks from playlist
            tracks = []
            for item in items:
                track = item.get('track', {})
                track_name = track.get('trackName', '')
                if track_name:
                    tracks.append(track_name)
            
            playlist_data.append({
                'name': name,
                'track_count': len(tracks),
                'last_modified': modified,
                'tracks': tracks
            })
        
        self.playlist_df = pd.DataFrame(playlist_data)
        print(f"✅ Extracted {len(self.playlist_df)} playlists")
        
    def extract_genre_data(self):
        """Extract genre information from Wrapped data"""
        print("🎸 Extracting genre data...")
        
        wrapped = self.account_data.get('wrapped', {})
        top_genres_data = wrapped.get('topGenres', {})
        
        # Try different possible structures
        genres = []
        if isinstance(top_genres_data, dict):
            genre_list = top_genres_data.get('topGenreUris', [])
            genre_names = top_genres_data.get('topGenreNames', [])
            
            if genre_names:
                genres = genre_names
            elif genre_list:
                # Extract genre names from URIs
                for uri in genre_list:
                    if 'genre:' in uri:
                        genre_name = uri.split(':')[-1].replace('+', ' ').title()
                        genres.append(genre_name)
        
        self.genre_data = genres
        print(f"✅ Found {len(genres)} top genres")
        
        # If no genres in Wrapped, we'll derive genres from artist analysis
        if not genres:
            print("ℹ️ No genre data in Wrapped, will use proxy analysis")
        
    def analyze_artist_genres(self):
        """Create genre proxies based on artist listening patterns"""
        print("🔍 Analyzing listening patterns for genre insights...")
        
        music_df = self.df[self.df['is_music'] & self.df['actually_listened']]
        
        # Group artists by listening time patterns (morning/afternoon/evening/night)
        artist_time = music_df.groupby(['master_metadata_album_artist_name', 'hour'])['minutes_played'].sum().reset_index()
        
        # Find peak listening hour for each artist
        artist_peak = artist_time.loc[artist_time.groupby('master_metadata_album_artist_name')['minutes_played'].idxmax()]
        
        # Categorize artists by peak listening time
        def categorize_time(hour):
            if 5 <= hour < 12:
                return 'Morning'
            elif 12 <= hour < 17:
                return 'Afternoon'
            elif 17 <= hour < 22:
                return 'Evening'
            else:
                return 'Night'
        
        artist_peak['time_category'] = artist_peak['hour'].apply(categorize_time)
        
        self.artist_time_category = artist_peak
        
        # Analyze listening diversity per month
        monthly_diversity = music_df.groupby(['year', 'month']).agg(
            unique_artists=('master_metadata_album_artist_name', 'nunique'),
            unique_tracks=('master_metadata_track_name', 'nunique'),
            total_hours=('minutes_played', 'sum')
        ).reset_index()
        
        monthly_diversity['hours'] = monthly_diversity['total_hours'] / 60
        monthly_diversity['date'] = pd.to_datetime(
            monthly_diversity[['year', 'month']].assign(day=1)
        )
        
        self.monthly_diversity = monthly_diversity
        print("✅ Genre/time analysis complete")
    def process_all(self):
        """Run the complete processing pipeline"""
        self.load_extended_history()
        self.clean_data()
        self.load_account_data()
        self.compute_metrics()
        self.extract_playlist_data()
        self.extract_genre_data()
        self.analyze_artist_genres()
        return self.df, self.metrics, self.account_data

if __name__ == "__main__":
    processor = SpotifyDataProcessor()
    df, metrics, account_data = processor.process_all()
    
    print("\n" + "="*50)
    print("PROCESSING COMPLETE")
    print("="*50)
    for key, value in metrics.items():
        print(f"{key}: {value}")