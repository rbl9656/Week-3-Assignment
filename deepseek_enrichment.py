import pandas as pd
import requests
import time
from typing import Dict, List, Optional
import json

class DeepSeekEnricher:
    """Uses DeepSeek AI to analyze QB performance and predict NFL success factors"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.rate_limit_delay = 1.0  # Adjust based on API limits
        
    def analyze_player(self, player_data: pd.Series) -> Dict[str, any]:
        """Analyze a single player using DeepSeek AI"""
        
        # Prepare player stats for analysis
        player_stats = self._format_player_stats(player_data)
        
        # Create the analysis prompt
        prompt = self._create_analysis_prompt(player_stats)
        
        try:
            # Make API call
            response = self._make_api_call(prompt)
            
            if response:
                analysis = self._parse_response(response)
                return {
                    'player_name': player_data.get('player_name', ''),
                    'success_probability': analysis.get('success_probability', 0),
                    'key_strengths': analysis.get('key_strengths', []),
                    'key_weaknesses': analysis.get('key_weaknesses', []),
                    'college_to_nfl_transition': analysis.get('college_to_nfl_transition', ''),
                    'statistical_indicators': analysis.get('statistical_indicators', []),
                    'overall_assessment': analysis.get('overall_assessment', ''),
                    'comparisons': analysis.get('comparisons', ''),
                    'development_areas': analysis.get('development_areas', [])
                }
            else:
                return self._create_fallback_analysis(player_data)
                
        except Exception as e:
            print(f"Error analyzing {player_data.get('player_name', 'Unknown')}: {e}")
            return self._create_fallback_analysis(player_data)
    
    def _format_player_stats(self, player_data: pd.Series) -> Dict:
        """Format player statistics for AI analysis"""
        return {
            'college_stats': {
                'team': player_data.get('college_team', 'N/A'),
                'conference': player_data.get('college_conference', 'N/A'),
                'years_played': f"{player_data.get('college_start_year', 'N/A')}-{player_data.get('college_end_year', 'N/A')}",
                'pass_attempts': int(player_data.get('college_pass_attempts', 0)),
                'completions': int(player_data.get('college_pass_completions', 0)),
                'completion_percentage': round(player_data.get('college_completion_pct', 0), 1),
                'pass_yards': int(player_data.get('college_pass_yards', 0)),
                'touchdowns': int(player_data.get('college_pass_tds', 0)),
                'interceptions': int(player_data.get('college_interceptions', 0)),
                'td_int_ratio': round(player_data.get('college_td_int_ratio', 0), 2),
                'yards_per_attempt': round(player_data.get('college_yards_per_attempt', 0), 1)
            },
            'nfl_stats': {
                'games_played': int(player_data.get('nfl_games', 0)),
                'pass_attempts': int(player_data.get('nfl_pass_attempts', 0)),
                'completions': int(player_data.get('nfl_pass_completions', 0)),
                'completion_percentage': round(player_data.get('nfl_completion_percentage', 0), 1),
                'pass_yards': int(player_data.get('nfl_pass_yards', 0)),
                'touchdowns': int(player_data.get('nfl_pass_tds', 0)),
                'interceptions': int(player_data.get('nfl_interceptions', 0)),
                'td_int_ratio': round(player_data.get('nfl_td_int_ratio', 0), 2),
                'yards_per_attempt': round(player_data.get('nfl_yards_per_attempt', 0), 1),
                'qb_rating': round(player_data.get('nfl_qb_rating', 0), 1)
            }
        }
    
    def _create_analysis_prompt(self, player_stats: Dict) -> str:
        """Create a comprehensive analysis prompt for DeepSeek AI"""
        return f"""
        Analyze this quarterback's transition from college to NFL and determine the key factors that led to their NFL success or failure.
        
        Player Statistics:
        
        COLLEGE CAREER:
        - Team: {player_stats['college_stats']['team']}
        - Conference: {player_stats['college_stats']['conference']}
        - Years: {player_stats['college_stats']['years_played']}
        - Pass Attempts: {player_stats['college_stats']['pass_attempts']:,}
        - Completions: {player_stats['college_stats']['completions']:,}
        - Completion %: {player_stats['college_stats']['completion_percentage']}%
        - Pass Yards: {player_stats['college_stats']['pass_yards']:,}
        - Touchdowns: {player_stats['college_stats']['touchdowns']}
        - Interceptions: {player_stats['college_stats']['interceptions']}
        - TD/INT Ratio: {player_stats['college_stats']['td_int_ratio']}
        - Yards/Attempt: {player_stats['college_stats']['yards_per_attempt']}
        
        NFL CAREER:
        - Games: {player_stats['nfl_stats']['games_played']}
        - Pass Attempts: {player_stats['nfl_stats']['pass_attempts']:,}
        - Completions: {player_stats['nfl_stats']['completions']:,}
        - Completion %: {player_stats['nfl_stats']['completion_percentage']}%
        - Pass Yards: {player_stats['nfl_stats']['pass_yards']:,}
        - Touchdowns: {player_stats['nfl_stats']['touchdowns']}
        - Interceptions: {player_stats['nfl_stats']['interceptions']}
        - TD/INT Ratio: {player_stats['nfl_stats']['td_int_ratio']}
        - Yards/Attempt: {player_stats['nfl_stats']['yards_per_attempt']}
        - QB Rating: {player_stats['nfl_stats']['qb_rating']}
        
        Please provide a detailed analysis in JSON format with the following structure:
        {{
            "success_probability": <integer 0-100 representing likelihood of NFL success based on college stats>,
            "key_strengths": [<list of 2-4 key strengths based on statistics>],
            "key_weaknesses": [<list of 1-3 key weaknesses based on statistics>],
            "college_to_nfl_transition": "<brief analysis of how well stats translated to NFL>",
            "statistical_indicators": [<list of 2-3 specific statistical factors that predicted success/failure>],
            "overall_assessment": "<2-3 sentence summary of the player's career trajectory>",
            "comparisons": "<comparison to typical successful/unsuccessful NFL QBs based on similar stats>",
            "development_areas": [<list of 2-3 areas where improvement was needed for NFL success>]
        }}
        
        Focus on statistical analysis and avoid speculation about non-statistical factors. Be objective and data-driven.
        """
    
    def _make_api_call(self, prompt: str) -> Optional[Dict]:
        """Make API call to DeepSeek"""
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert NFL quarterback analyst specializing in statistical analysis of college-to-NFL transitions. Provide detailed, data-driven insights based solely on the provided statistics."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            "temperature": 0.3,
            "max_tokens": 1000
        }
        
        try:
            time.sleep(self.rate_limit_delay)
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            return None
    
    def _parse_response(self, response: Dict) -> Dict:
        """Parse DeepSeek API response and extract analysis"""
        try:
            content = response['choices'][0]['message']['content']
            
            # Try to extract JSON from the response
            if '```json' in content:
                json_start = content.find('```json') + 7
                json_end = content.find('```', json_start)
                json_str = content[json_start:json_end].strip()
            elif '{' in content and '}' in content:
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                json_str = content[json_start:json_end]
            else:
                json_str = content
            
            analysis = json.loads(json_str)
            return analysis
            
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            print(f"Error parsing API response: {e}")
            # Return a basic structure if parsing fails
            return {
                'success_probability': 50,
                'key_strengths': ['Statistical analysis unavailable'],
                'key_weaknesses': ['Analysis parsing failed'],
                'college_to_nfl_transition': 'Unable to analyze transition',
                'statistical_indicators': ['Data processing error'],
                'overall_assessment': 'Analysis could not be completed',
                'comparisons': 'Comparison data unavailable',
                'development_areas': ['Analysis incomplete']
            }
    
    def _create_fallback_analysis(self, player_data: pd.Series) -> Dict:
        """Create basic rule-based analysis if API fails"""
        
        # Simple rule-based analysis based on key metrics
        college_completion_pct = player_data.get('college_completion_pct', 0)
        college_td_int_ratio = player_data.get('college_td_int_ratio', 0)
        college_ypa = player_data.get('college_yards_per_attempt', 0)
        
        nfl_games = player_data.get('nfl_games', 0)
        nfl_qb_rating = player_data.get('nfl_qb_rating', 0)
        
        # Calculate basic success probability
        success_score = 0
        if college_completion_pct >= 60: success_score += 20
        if college_td_int_ratio >= 2.0: success_score += 25
        if college_ypa >= 7.5: success_score += 20
        if nfl_games >= 16: success_score += 20  # Played at least one full season
        if nfl_qb_rating >= 85: success_score += 15
        
        return {
            'player_name': player_data.get('player_name', ''),
            'success_probability': min(success_score, 100),
            'key_strengths': self._identify_strengths(player_data),
            'key_weaknesses': self._identify_weaknesses(player_data),
            'college_to_nfl_transition': self._assess_transition(player_data),
            'statistical_indicators': ['Completion percentage', 'TD/INT ratio', 'Yards per attempt'],
            'overall_assessment': 'Analysis generated using fallback rule-based system',
            'comparisons': 'Statistical comparison unavailable',
            'development_areas': ['Accuracy', 'Decision-making', 'Arm strength']
        }
    
    def _identify_strengths(self, player_data: pd.Series) -> List[str]:
        """Identify strengths based on statistical thresholds"""
        strengths = []
        
        if player_data.get('college_completion_pct', 0) >= 65:
            strengths.append('High completion percentage')
        if player_data.get('college_td_int_ratio', 0) >= 2.5:
            strengths.append('Excellent TD/INT ratio')
        if player_data.get('college_yards_per_attempt', 0) >= 8.0:
            strengths.append('Strong yards per attempt')
        if player_data.get('nfl_qb_rating', 0) >= 90:
            strengths.append('High NFL passer rating')
        
        return strengths if strengths else ['Statistical analysis incomplete']
    
    def _identify_weaknesses(self, player_data: pd.Series) -> List[str]:
        """Identify weaknesses based on statistical thresholds"""
        weaknesses = []
        
        if player_data.get('college_completion_pct', 0) < 55:
            weaknesses.append('Low completion percentage')
        if player_data.get('college_td_int_ratio', 0) < 1.5:
            weaknesses.append('Poor TD/INT ratio')
        if player_data.get('college_yards_per_attempt', 0) < 7.0:
            weaknesses.append('Low yards per attempt')
        if player_data.get('nfl_qb_rating', 0) < 80 and player_data.get('nfl_qb_rating', 0) > 0:
            weaknesses.append('Struggled in NFL transition')
        
        return weaknesses if weaknesses else ['No major statistical weaknesses identified']
    
    def _assess_transition(self, player_data: pd.Series) -> str:
        """Assess college to NFL transition"""
        nfl_games = player_data.get('nfl_games', 0)
        nfl_rating = player_data.get('nfl_qb_rating', 0)
        
        if nfl_games == 0:
            return "Did not establish NFL career"
        elif nfl_games < 16:
            return "Limited NFL playing time"
        elif nfl_rating >= 85:
            return "Successful transition to NFL"
        elif nfl_rating >= 75:
            return "Moderate NFL success"
        else:
            return "Struggled in NFL transition"
    
    def enrich_dataset(self, df: pd.DataFrame) -> pd.DataFrame:
        """Enrich entire dataset with AI analysis"""
        print(f"Starting DeepSeek analysis for {len(df)} players...")
        
        enriched_data = []
        
        for idx, player in df.iterrows():
            print(f"Analyzing player {idx + 1}/{len(df)}: {player.get('player_name', 'Unknown')}")
            
            # Get AI analysis
            analysis = self.analyze_player(player)
            
            # Combine original data with analysis
            enriched_player = player.to_dict()
            enriched_player.update(analysis)
            
            enriched_data.append(enriched_player)
            
            # Progress indicator
            if (idx + 1) % 10 == 0:
                print(f"Progress: {idx + 1}/{len(df)} players analyzed")
        
        enriched_df = pd.DataFrame(enriched_data)
        print(f"DeepSeek analysis complete for all {len(enriched_df)} players!")
        
        return enriched_df