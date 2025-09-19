College QB NFL Analysis

A project that uses AI to analyize and predict which college quarterbacks will succeed in the NFL

What This Project Does:
Ever wonder why some college QBs become NFL superstars while others flop? This project analyzes 20+ years of quarterback data to find patterns that predict NFL success, then uses AI to explain what those patterns actually mean.
The Goal: Build a system that could help NFL teams make smarter draft decisions (and maybe prevent another Johnny Manziel situation)
Data Sources

College Football Data API: 2001-2023 college QB stats (completions, yards, TDs, etc.)
NFL Statistics CSV: Professional career data for the same players
Coverage: 150+ quarterbacks with complete college to NFL career tracking

Note: Using publicly available data and APIs:
The AI Enhancement (DeepSeek)

Why Add AI?
Raw stats only tell part of the story. Russell Wilson had solid but not spectacular college numbers yet became a Pro Bowl QB. Meanwhile, Johnny Manziel dominated college but struggled in the NFL.
The AI figures out WHY some players succeed when others don't.

hat DeepSeek Adds:

Success Probability: 0-100% chance of NFL success based on college stats
Pattern Recognition: Which college metrics actually matter for the pros
Risk Assessment: Red flags that indicate potential busts
Smart Comparisons: "This player's profile looks like [successful/unsuccessful QB]"

Before/After: The AI Difference
Example: Russell Wilson (Wisconsin/NC State, 2007-2011)
Just Stats:

COLLEGE CAREER:
  Team: Wisconsin
  Conference: Big Ten
  Years: 2008-2011
  Pass Attempts: 1,396
  Completions: 849
  Completion %: 61.3%
  Pass Yards: 10,963
  Touchdowns: 104
  Interceptions: 29
  TD/INT Ratio: 7.75
  Yards/Attempt: 8.0
Solid but not Heisman-level numbers

NFL CAREER:
  Games: 203
  Pass Attempts: 6,112
  Completions: 3,965
  Completion %: 64.9%
  Pass Yards: 46,723
  Yards/Attempt: 7.6
  Touchdowns: 360
  Interceptions: 114
  TD/INT Ratio: 3.2
  QB Rating: 100.0
Elite NFL Career

With AI Analysis:
Success Probability: 85%
  Key Strengths:
    • Exceptional touchdown-to-interception ratio (7.75 in college, 3.16 in NFL)
    • High completion percentage (61.3% college to 64.9% NFL improvement)
    • Consistent yardage production (8.0 Y/A college, 7.6 Y/A NFL)
  Key Weaknesses:
    • Slight decline in yards per attempt from college to NFL
    • Increased interception rate relative to college performance
    • Moderate reduction in TD/INT ratio at professional level
  
  College to NFL Transition: Strong statistical translation with improved completion percentage and maintained high-level production over extended NFL career (203 games), though with expected efficiency adjustments to higher competition level
  
  Overall Assessment: This quarterback successfully transitioned from college to NFL with statistically significant improvements in completion percentage while maintaining strong production metrics. The 100.0 career QB rating and 46,723 passing yards indicate sustained elite performance over a lengthy NFL career.

Example: Johnny Manziel (Texas A&M, 2012-2013)
Just Stats:

COLLEGE CAREER:
  Heisman Winner
  Team: Texas A&M
  Conference: SEC
  Years: 2012-2013
  Pass Attempts: 791
  Completions: 543
  Completion %: 68.7%
  Pass Yards: 7,151
  Touchdowns: 57
  Interceptions: 21
  TD/INT Ratio: 2.77
  Yards/Attempt: 9.0

NFL CAREER:
  Games: 14
  Pass Attempts: 258
  Completions: 147
  Completion %: 57.0%
  Pass Yards: 1,675
  Yards/Attempt: 6.5
  Touchdowns: 7
  Interceptions: 7
  TD/INT Ratio: 1.0
  QB Rating: 60.7

With AI ANALYSIS:
  Success Probability: 25%
  Key Strengths:
    • Excellent college completion percentage (68.7%)
    • Strong yards per attempt (9.0) in college
    • Positive TD/INT ratio (2.77) in SEC competition
  Key Weaknesses:
    • Severe drop in completion percentage (-11.7% from college to NFL)
    • Poor NFL yards per attempt (6.5) well below league average
    • Concerning TD/INT ratio regression to 1.0 in NFL
  
  College to NFL Transition: Poor statistical translation with significant regression across all major passing metrics, particularly in completion percentage and efficiency metrics
  
  Overall Assessment: This quarterback demonstrated strong college production in the SEC but failed to translate those skills to the NFL level. The statistical regression across all efficiency metrics suggests fundamental limitations in processing NFL defenses and executing at the professional level.

The Bottom Line: AI identified Wilson as undervalued and Manziel as overvalued based purely on statistical patterns and can identify what lead to success/failure at the professional level!

Installation & Setup:
What You Need:

Python 3.8+

Free API key:
College Football Data API


Quick Setup:
bash
1. Clone and install
git clone <repo-url>
cd college-qb-nfl-analysis
pip install -r requirements.txt

# 2. Add your API keys to .env file
CFBD_API_KEY='your_key_here' >> .env
DEEPSEEK_API_KEY='your_key_here' >> .env

# 3. Run it!
python main.py

How to Use:

Basic Usage:

Run python main.py
Wait for data extraction (takes ~5 minutes for full dataset)
Search for quarterbacka in the time frame by name
Choose whether to run AI analysis

Example Session:
🔍 Enter quarterback name: Josh Allen
🤖 Run AI analysis? (y/n): y

🤖 Analyzing Cam Newton with DeepSeek AI...
💾 Enriched data saved to data/enriched/Cam_Newton_20241218_143045.csv
✅ AI analysis complete!

============================================================
PLAYER PROFILE: Josh Allen
============================================================

COLLEGE CAREER:
  Team: Wyoming
  Conference: Mountain West
  Years: 2016-2017
  Pass Attempts: 592
  Completions: 333
  Completion %: 56.2%
  Pass Yards: 4,654
  Touchdowns: 39
  Interceptions: 19
  TD/INT Ratio: 2.08
  Yards/Attempt: 7.7

NFL CAREER:
  Games: 111
  Pass Attempts: 3,724
  Completions: 2,374
  Completion %: 63.7%
  Pass Yards: 27,009
  Yards/Attempt: 7.3
  Touchdowns: 196
  Interceptions: 96
  TD/INT Ratio: 2.0
  QB Rating: 90.5

🤖 AI ANALYSIS:
  Success Probability: 65%
  Key Strengths:
    • Improved completion percentage (+7.5% from college to NFL)
    • Strong touchdown production (196 TDs in 111 games)
    • Durable and consistent performance (111 games played)
  Key Weaknesses:
    • Below-average yards per attempt (7.3 NFL, below league average)
    • Moderate interception rate (2.6% of attempts)
    • Limited college efficiency (56.2% completion, 7.7 Y/A)
  
  College to NFL Transition: The quarterback demonstrated significant improvement in completion percentage (+7.5%) while maintaining similar TD/INT ratios (2.08 college vs 2.04 NFL), indicating better accuracy and decision-making at the professional level despite facing tougher defenses.
  
  Overall Assessment: This quarterback achieved moderate NFL success with improved accuracy and sustained touchdown production. The statistical profile suggests a capable starter who adapted well to the professional level despite coming from a non-power conference, though efficiency metrics remained average.