import pandas as pd
import requests
import time
import os
from typing import Dict, List, Optional
import json
from datetime import datetime
from deepseek_enrichment import DeepSeekEnricher

# Add this for using .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("python-dotenv not installed. Using environment variables directly.")

class QBStatsETL:
    """ETL Pipeline for College Football QB to NFL performance comparison"""
    
    def __init__(self, api_key: str, csv_file_path: str):
        self.api_key = api_key
        self.csv_file_path = csv_file_path
        self.base_url = "https://api.collegefootballdata.com"
        self.headers = {"Authorization": f"Bearer {api_key}"}
        self.rate_limit_delay = 1.0  # seconds between API calls
        
        # Initialize dataframes
        self.college_stats = pd.DataFrame()
        self.nfl_stats = pd.DataFrame()
        self.combined_data = pd.DataFrame()
        
    def rate_limited_request(self, url: str, params: Dict = None) -> Optional[requests.Response]:
        """Make rate-limited API request with basic error handling"""
        try:
            time.sleep(self.rate_limit_delay)  # Rate limiting
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            return None
    
    def extract_college_data(self, years: List[int] = None) -> pd.DataFrame:
        """Extract college QB stats from the API"""
        if years is None:
            years = list(range(2001, 2024))  # Full range 2001-2023
        
        all_stats = []
        
        print("Extracting college quarterback data...")
        for year in years:
            print(f"Processing year {year}...")
            
            # Get player stats for QBs
            stats_url = f"{self.base_url}/stats/player/season"
            params = {
                'year': year,
                'category': 'passing',
                'seasonType': 'regular'
            }
            
            response = self.rate_limited_request(stats_url, params)
            if response:
                try:
                    year_stats = response.json()
                    
                    # Convert list of individual stats to DataFrame for easier manipulation
                    stats_df = pd.DataFrame(year_stats)
                    
                    # Filter to only QBs
                    qb_stats = stats_df[stats_df['position'] == 'QB'].copy()
                    
                    if len(qb_stats) == 0:
                        print(f"   No QB stats found for {year}")
                        continue
                    
                    # Pivot the data so each player has one row with all their stats
                    # Group by player and pivot statType to columns
                    player_stats = qb_stats.pivot_table(
                        index=['playerId', 'player', 'team', 'conference'], 
                        columns='statType', 
                        values='stat', 
                        aggfunc='first'  # In case of duplicates, take first
                    ).reset_index()
                    
                    # Convert to our format
                    for _, player in player_stats.iterrows():
                        all_stats.append({
                            'player_name': player['player'],
                            'team': player['team'],
                            'conference': player['conference'],
                            'year': year,
                            'position': 'QB',
                            'pass_attempts': int(player.get('ATT', 0) or 0),
                            'pass_completions': int(player.get('COMPLETIONS', 0) or 0),
                            'pass_yards': int(player.get('YDS', 0) or 0),
                            'pass_tds': int(player.get('TD', 0) or 0),
                            'interceptions': int(player.get('INT', 0) or 0),
                            'qb_rating': float(player.get('QBR', 0) or 0),
                            'yards_per_attempt': float(player.get('YPA', 0) or 0),
                            'games': int(player.get('GAMES', 0) or 0)
                        })
                    
                    print(f"   Successfully processed {len(player_stats)} QBs")
                    
                except json.JSONDecodeError as e:
                    print(f"   JSON decode error for {year}: {e}")
                except Exception as e:
                    print(f"   Error processing year {year}: {e}")
            else:
                print(f"   Failed to get data for year {year}")
        
        self.college_stats = pd.DataFrame(all_stats)
        print(f"College data extraction complete: {len(self.college_stats)} records")
        return self.college_stats
    
    def extract_nfl_data(self) -> pd.DataFrame:
        """Extract NFL stats from CSV file"""
        try:
            print("Loading NFL data from CSV...")
            
            # Try to read CSV with different encodings
            encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
            
            for encoding in encodings:
                try:
                    self.nfl_stats = pd.read_csv(self.csv_file_path, encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
                except Exception as e:
                    print(f"Error with {encoding}: {e}")
                    continue
            else:
                print("Failed to load CSV with any encoding")
                return pd.DataFrame()
            
            # Standardize column names (comprehensive mapping)
            column_mapping = {
                # Name variations
                'Name': 'player_name',
                'Player': 'player_name',
                'Player_Name': 'player_name',
                'PLAYER': 'player_name',
                # Team variations
                'Tm': 'nfl_team',
                'Team': 'nfl_team',
                'NFL_Team': 'nfl_team',
                # Year variations
                'Year': 'nfl_year',
                'Season': 'nfl_year',
                'YEAR': 'nfl_year',
                # Games variations
                'G': 'nfl_games',
                'Games': 'nfl_games',
                'GP': 'nfl_games',
                # Passing stats
                'Att': 'nfl_pass_attempts',
                'ATT': 'nfl_pass_attempts',
                'Pass_Att': 'nfl_pass_attempts',
                'Cmp': 'nfl_pass_completions',
                'CMP': 'nfl_pass_completions',
                'Completions': 'nfl_pass_completions',
                'Yds': 'nfl_pass_yards',
                'YDS': 'nfl_pass_yards',
                'Pass_Yds': 'nfl_pass_yards',
                'Passing_Yards': 'nfl_pass_yards',
                'TD': 'nfl_pass_tds',
                'Pass_TD': 'nfl_pass_tds',
                'Int': 'nfl_interceptions',
                'INT': 'nfl_interceptions',
                'Interceptions': 'nfl_interceptions',
                'Rate': 'nfl_qb_rating',
                'QBR': 'nfl_qb_rating',
                'Passer_Rating': 'nfl_qb_rating'
            }
            
            # Rename columns that exist
            existing_cols = {k: v for k, v in column_mapping.items() if k in self.nfl_stats.columns}
            if existing_cols:
                self.nfl_stats.rename(columns=existing_cols, inplace=True)
            
            print(f"Loaded {len(self.nfl_stats)} NFL records")
            return self.nfl_stats
            
        except FileNotFoundError:
            print(f"Error: CSV file '{self.csv_file_path}' not found")
            return pd.DataFrame()
        except Exception as e:
            print(f"Error loading NFL data: {e}")
            return pd.DataFrame()
    
    def clean_college_data(self) -> pd.DataFrame:
        """Clean and standardize college data"""
        if self.college_stats.empty:
            return self.college_stats
        
        print("Cleaning college data...")
        
        # Remove duplicates
        self.college_stats.drop_duplicates(subset=['player_name', 'team', 'year'], inplace=True)
        
        # Clean player names
        self.college_stats['player_name'] = self.college_stats['player_name'].str.strip()
        self.college_stats['player_name'] = self.college_stats['player_name'].str.title()
        
        # Convert numeric columns
        numeric_cols = ['games', 'pass_attempts', 'pass_completions', 'pass_yards', 
                       'pass_tds', 'interceptions', 'qb_rating', 'yards_per_attempt']
        
        for col in numeric_cols:
            self.college_stats[col] = pd.to_numeric(self.college_stats[col], errors='coerce').fillna(0)
        
        # Calculate additional metrics
        self.college_stats['completion_percentage'] = (
            self.college_stats['pass_completions'] / self.college_stats['pass_attempts'] * 100
        ).fillna(0)
        
        self.college_stats['td_int_ratio'] = (
            self.college_stats['pass_tds'] / self.college_stats['interceptions'].replace(0, 1)
        )
        
        # Filter out players with minimal activity
        self.college_stats = self.college_stats[self.college_stats['pass_attempts'] >= 50]
        
        print(f"College data cleaned: {len(self.college_stats)} records remaining")
        return self.college_stats
    
    def clean_nfl_data(self) -> pd.DataFrame:
        """Clean and standardize NFL data"""
        if self.nfl_stats.empty:
            return self.nfl_stats
        
        print("Cleaning NFL data...")
        
        # Clean player names
        if 'player_name' in self.nfl_stats.columns:
            self.nfl_stats['player_name'] = self.nfl_stats['player_name'].str.strip()
            self.nfl_stats['player_name'] = self.nfl_stats['player_name'].str.title()
        
        # Convert numeric columns
        numeric_cols = [col for col in self.nfl_stats.columns if col.startswith('nfl_') and 
                       col not in ['nfl_team', 'player_name']]
        
        for col in numeric_cols:
            self.nfl_stats[col] = pd.to_numeric(self.nfl_stats[col], errors='coerce').fillna(0)
        
        # Calculate additional NFL metrics
        if 'nfl_pass_attempts' in self.nfl_stats.columns and 'nfl_pass_completions' in self.nfl_stats.columns:
            self.nfl_stats['nfl_completion_percentage'] = (
                self.nfl_stats['nfl_pass_completions'] / self.nfl_stats['nfl_pass_attempts'] * 100
            ).fillna(0)
        
        if 'nfl_pass_tds' in self.nfl_stats.columns and 'nfl_interceptions' in self.nfl_stats.columns:
            self.nfl_stats['nfl_td_int_ratio'] = (
                self.nfl_stats['nfl_pass_tds'] / self.nfl_stats['nfl_interceptions'].replace(0, 1)
            ).fillna(0)
        
        if 'nfl_pass_yards' in self.nfl_stats.columns and 'nfl_pass_attempts' in self.nfl_stats.columns:
            self.nfl_stats['nfl_yards_per_attempt'] = (
                self.nfl_stats['nfl_pass_yards'] / self.nfl_stats['nfl_pass_attempts']
            ).fillna(0)
        
        # Filter years 2001-2023
        if 'nfl_year' in self.nfl_stats.columns:
            self.nfl_stats = self.nfl_stats[
                (self.nfl_stats['nfl_year'] >= 2001) & (self.nfl_stats['nfl_year'] <= 2023)
            ]
        
        print(f"NFL data cleaned: {len(self.nfl_stats)} records")
        return self.nfl_stats
    
    def merge_data(self) -> pd.DataFrame:
        """Merge college and NFL data"""
        if self.college_stats.empty or self.nfl_stats.empty:
            print("Warning: One or both datasets are empty")
            return pd.DataFrame()
        
        print("Merging college and NFL data...")
        
        # Group college stats by player (career totals)
        college_career = self.college_stats.groupby('player_name').agg({
            'team': 'last',  # Most recent team
            'conference': 'last',
            'year': ['min', 'max'],  # College career span
            'pass_attempts': 'sum',
            'pass_completions': 'sum',
            'pass_yards': 'sum',
            'pass_tds': 'sum',
            'interceptions': 'sum',
            'completion_percentage': 'mean',
            'td_int_ratio': 'mean',
            'yards_per_attempt': 'mean'
        }).reset_index()
        
        # Flatten column names (removed games column)
        college_career.columns = ['player_name', 'college_team', 'college_conference', 
                                'college_start_year', 'college_end_year',
                                'college_pass_attempts', 'college_pass_completions',
                                'college_pass_yards', 'college_pass_tds', 'college_interceptions',
                                'college_completion_pct', 'college_td_int_ratio', 'college_yards_per_attempt']
        
        # Group NFL stats by player (career totals/averages)
        if 'player_name' in self.nfl_stats.columns:
            # Define aggregation rules for NFL stats
            agg_funcs = {}
            for col in self.nfl_stats.columns:
                if col in ['player_name', 'nfl_team']:
                    continue
                elif any(word in col.lower() for word in ['games', 'attempts', 'yards', 'tds', 'completions', 'interceptions']):
                    agg_funcs[col] = 'sum'
                elif col in ['nfl_completion_percentage', 'nfl_td_int_ratio', 'nfl_qb_rating', 'nfl_yards_per_attempt']:
                    agg_funcs[col] = 'mean'
                else:
                    agg_funcs[col] = 'mean'
            
            nfl_career = self.nfl_stats.groupby('player_name').agg(agg_funcs).reset_index()
            
            # Recalculate completion percentage and TD/INT ratio based on career totals for accuracy
            if 'nfl_pass_attempts' in nfl_career.columns and 'nfl_pass_completions' in nfl_career.columns:
                nfl_career['nfl_completion_percentage'] = (
                    nfl_career['nfl_pass_completions'] / nfl_career['nfl_pass_attempts'] * 100
                ).fillna(0)
            
            if 'nfl_pass_tds' in nfl_career.columns and 'nfl_interceptions' in nfl_career.columns:
                nfl_career['nfl_td_int_ratio'] = (
                    nfl_career['nfl_pass_tds'] / nfl_career['nfl_interceptions'].replace(0, 1)
                ).fillna(0)
            
            if 'nfl_pass_yards' in nfl_career.columns and 'nfl_pass_attempts' in nfl_career.columns:
                nfl_career['nfl_yards_per_attempt'] = (
                    nfl_career['nfl_pass_yards'] / nfl_career['nfl_pass_attempts']
                ).fillna(0)
            
            # Merge the datasets
            self.combined_data = pd.merge(college_career, nfl_career, on='player_name', how='inner')
            
            print(f"Successfully merged data for {len(self.combined_data)} players")
        else:
            print("Error: 'player_name' column not found in NFL data")
            self.combined_data = college_career
        
        return self.combined_data
    
    def save_raw_data(self) -> str:
        """Save raw data to data/raw/ directory"""
        os.makedirs('data/raw', exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        raw_filename = f"data/raw/qb_raw_data_{timestamp}.csv"
        self.combined_data.to_csv(raw_filename, index=False)
        print(f"Raw data saved to {raw_filename}")
        return raw_filename
    
    def save_enriched_player(self, enriched_player: pd.Series) -> str:
        """Save individual enriched player data to data/enriched/"""
        os.makedirs('data/enriched', exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        player_name_clean = enriched_player['player_name'].replace(' ', '_').replace('.', '').replace("'", "")
        filename = f"data/enriched/{player_name_clean}_{timestamp}.csv"
        
        # Convert Series to DataFrame for saving
        player_df = pd.DataFrame([enriched_player])
        player_df.to_csv(filename, index=False)
        
        print(f"💾 Enriched data saved to {filename}")
        return filename
    
    def run_etl_setup(self, years: List[int] = None) -> str:
        """Run the ETL process and prepare for on-demand AI analysis"""
        print("🚀 Starting ETL process...\n")
        
        # Extract and process raw data
        self.extract_college_data(years)
        self.extract_nfl_data()
        self.clean_college_data()
        self.clean_nfl_data()
        self.merge_data()
        
        print(f"\n✅ ETL process complete! Dataset contains {len(self.combined_data)} players")
        
        if self.combined_data.empty:
            print("❌ No data available for analysis.")
            return None
        
        # Save raw data
        raw_filename = self.save_raw_data()
        return raw_filename
    
    def search_player(self, player_name: str) -> Optional[pd.Series]:
        """Search for a specific player's stats"""
        if self.combined_data.empty:
            print("No data available. Please run the ETL process first.")
            return None
        
        # Case-insensitive search
        matches = self.combined_data[
            self.combined_data['player_name'].str.contains(player_name, case=False, na=False)
        ]
        
        if matches.empty:
            print(f"No player found matching '{player_name}'")
            return None
        elif len(matches) > 1:
            print(f"Multiple players found matching '{player_name}':")
            for idx, row in matches.iterrows():
                print(f"  - {row['player_name']} ({row.get('college_team', 'N/A')})")
            return matches
        else:
            return matches.iloc[0]
    
    def analyze_specific_player(self, player_name: str, deepseek_api_key: str = None) -> Optional[pd.Series]:
        """Analyze a specific player using AI on-demand"""
        
        if not deepseek_api_key:
            print("❌ DeepSeek API key required for AI analysis")
            return None
        
        # Find the player first
        result = self.search_player(player_name)
        
        if result is None:
            return None
        
        if isinstance(result, pd.DataFrame):  # Multiple matches
            print("Please be more specific with the player name.")
            return None
        
        # Single player found - analyze with AI
        print(f"\n🤖 Analyzing {result['player_name']} with DeepSeek AI...")
        
        try:
            enricher = DeepSeekEnricher(deepseek_api_key)
            analysis = enricher.analyze_player(result)
            
            # Combine original data with AI analysis
            enriched_player = result.copy()
            for key, value in analysis.items():
                if key != 'player_name':  # Don't overwrite existing name
                    enriched_player[key] = value
            
            # Save enriched player data immediately
            self.save_enriched_player(enriched_player)
            
            print("✅ AI analysis complete!")
            return enriched_player
            
        except Exception as e:
            print(f"❌ AI analysis failed: {e}")
            return result  # Return original data without AI analysis
    
    def display_player_stats(self, player_data: pd.Series, show_ai_analysis: bool = False):
        """Display formatted player statistics with optional AI analysis"""
        if player_data is None:
            return
        
        print(f"\n{'='*60}")
        print(f"PLAYER PROFILE: {player_data['player_name']}")
        print(f"{'='*60}")
        
        print(f"\nCOLLEGE CAREER:")
        print(f"  Team: {player_data.get('college_team', 'N/A')}")
        print(f"  Conference: {player_data.get('college_conference', 'N/A')}")
        print(f"  Years: {player_data.get('college_start_year', 'N/A')}-{player_data.get('college_end_year', 'N/A')}")
        print(f"  Pass Attempts: {player_data.get('college_pass_attempts', 0):,.0f}")
        print(f"  Completions: {player_data.get('college_pass_completions', 0):,.0f}")
        print(f"  Completion %: {player_data.get('college_completion_pct', 0):.1f}%")
        print(f"  Pass Yards: {player_data.get('college_pass_yards', 0):,.0f}")
        print(f"  Touchdowns: {player_data.get('college_pass_tds', 0):.0f}")
        print(f"  Interceptions: {player_data.get('college_interceptions', 0):.0f}")
        print(f"  TD/INT Ratio: {player_data.get('college_td_int_ratio', 0):.2f}")
        print(f"  Yards/Attempt: {player_data.get('college_yards_per_attempt', 0):.1f}")
        
        # NFL stats if available
        nfl_cols = [col for col in player_data.index if col.startswith('nfl_')]
        if nfl_cols:
            print(f"\nNFL CAREER:")
            
            # Display NFL stats in a specific order for better readability
            nfl_display_order = [
                ('nfl_games', 'Games'),
                ('nfl_pass_attempts', 'Pass Attempts'),
                ('nfl_pass_completions', 'Completions'),
                ('nfl_completion_percentage', 'Completion %'),
                ('nfl_pass_yards', 'Pass Yards'),
                ('nfl_yards_per_attempt', 'Yards/Attempt'),
                ('nfl_pass_tds', 'Touchdowns'),
                ('nfl_interceptions', 'Interceptions'), 
                ('nfl_td_int_ratio', 'TD/INT Ratio'),
                ('nfl_qb_rating', 'QB Rating')
            ]
            
            # Fields to exclude from display (year is meaningless when aggregated)
            excluded_fields = ['nfl_year']
            
            for col, display_name in nfl_display_order:
                if col in player_data.index and pd.notna(player_data[col]) and player_data[col] != 0:
                    if col in ['nfl_completion_percentage']:
                        print(f"  {display_name}: {player_data[col]:.1f}%")
                    elif col in ['nfl_td_int_ratio', 'nfl_qb_rating', 'nfl_yards_per_attempt']:
                        print(f"  {display_name}: {player_data[col]:.1f}")
                    elif col in ['nfl_games', 'nfl_pass_attempts', 'nfl_pass_completions', 'nfl_pass_yards', 'nfl_pass_tds', 'nfl_interceptions']:
                        print(f"  {display_name}: {player_data[col]:,.0f}")
            
            # Display any remaining NFL stats that weren't in the ordered list
            displayed_cols = [col for col, _ in nfl_display_order]
            for col in nfl_cols:
                if col not in displayed_cols and col not in excluded_fields and pd.notna(player_data[col]) and player_data[col] != 0:
                    display_name = col.replace('nfl_', '').replace('_', ' ').title()
                    if 'percentage' in col.lower():
                        print(f"  {display_name}: {player_data[col]:.1f}%")
                    elif 'ratio' in col.lower() or 'rating' in col.lower():
                        print(f"  {display_name}: {player_data[col]:.2f}")
                    else:
                        print(f"  {display_name}: {player_data[col]:,.1f}")
        
        # AI Analysis section
        if show_ai_analysis and 'success_probability' in player_data.index:
            print(f"\n🤖 AI ANALYSIS:")
            print(f"  Success Probability: {player_data.get('success_probability', 0)}%")
            
            strengths = player_data.get('key_strengths', [])
            if isinstance(strengths, list) and strengths:
                print(f"  Key Strengths:")
                for strength in strengths:
                    print(f"    • {strength}")
            
            weaknesses = player_data.get('key_weaknesses', [])
            if isinstance(weaknesses, list) and weaknesses:
                print(f"  Key Weaknesses:")
                for weakness in weaknesses:
                    print(f"    • {weakness}")
            
            transition = player_data.get('college_to_nfl_transition', '')
            if transition:
                print(f"  College to NFL Transition: {transition}")
            
            assessment = player_data.get('overall_assessment', '')
            if assessment:
                print(f"  Overall Assessment: {assessment}")
        
        elif show_ai_analysis:
            print(f"\n⚠️  AI analysis not available for this player")


def main():
    """Main function to run the ETL pipeline with on-demand AI analysis"""
    
    # Configuration
    API_KEY = os.getenv('CFBD_API_KEY')
    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
    CSV_FILE = 'passing_cleaned.csv'  # Your NFL stats CSV file
    
    print("🏈 College Football QB to NFL Performance ETL with On-Demand AI Analysis")
    print("=" * 75)
    
    if not API_KEY:
        print("❌ College Football API key not found!")
        print("Please set your CFBD_API_KEY environment variable:")
        print("  Method 1: Create .env file with: CFBD_API_KEY=your_key_here")
        print("  Method 2: Set environment variable: export CFBD_API_KEY=your_key_here")
        return
    
    # Initialize ETL pipeline
    etl = QBStatsETL(API_KEY, CSV_FILE)
    
    # Run basic ETL process
    try:
        raw_file = etl.run_etl_setup()
        
        if not raw_file:
            print("❌ ETL process failed")
            return
        
        print(f"\n📁 Raw Data File Created: {raw_file}")
        
        # Show AI availability status
        if DEEPSEEK_API_KEY:
            print("🤖 DeepSeek AI analysis available for individual players")
        else:
            print("⚠️  DeepSeek API key not found. AI analysis will be unavailable.")
            print("To enable AI analysis, set DEEPSEEK_API_KEY environment variable")
        
        # Interactive player search
        print(f"\n🔍 Interactive Player Search")
        print("=" * 30)
        print("Search for players to view their stats and optionally get AI analysis")
        
        while True:
            player_name = input("\nEnter quarterback name to search (or 'quit' to exit): ").strip()
            
            if player_name.lower() == 'quit':
                break
            
            if not player_name:
                continue
            
            # First, try basic search to see if player exists
            basic_result = etl.search_player(player_name)
            
            if basic_result is None:
                continue  # Player not found message already shown
            
            if isinstance(basic_result, pd.DataFrame):
                print("Please be more specific with the player name.")
                continue
            
            # Player found - ask if they want AI analysis
            ai_analysis = False
            if DEEPSEEK_API_KEY:
                ai_choice = input(f"\n🤖 Run AI analysis for {basic_result['player_name']}? (y/n, default=n): ").strip().lower()
                ai_analysis = ai_choice == 'y'
            
            if ai_analysis:
                # Get AI-enhanced data
                result = etl.analyze_specific_player(player_name, DEEPSEEK_API_KEY)
                show_ai = True
            else:
                # Use basic data
                result = basic_result
                show_ai = False
            
            if result is not None:
                etl.display_player_stats(result, show_ai_analysis=show_ai)
    
    except KeyboardInterrupt:
        print("\nETL process interrupted by user")
    except Exception as e:
        print(f"❌ Error running ETL process: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()