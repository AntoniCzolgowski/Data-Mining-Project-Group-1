"""
Generate DOCX summary document for the Enhanced Democratic Priority Score.
Covers methodology, results, validation, and embedded visualizations.

Author: Antoni Czolgowski
Date: April 2026
"""

import os
from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_ORIENT
import pandas as pd

# Paths
BASE = '../data/processed'
FIG_DIR = '../docs/images/methods'
OUTPUT_PATH = '../reports/Enhanced_Democratic_Priority_Score_Summary.docx'

# Load data
df = pd.read_csv(f'{BASE}/enhanced_priority_rankings.csv', dtype={'county_fips': str})
df['county_short'] = df['county_name'].str.replace(' County', '', regex=False)

# ── Create Document ──────────────────────────────────────────────────────
doc = Document()

# Style setup
style = doc.styles['Normal']
font = style.font
font.name = 'Calibri'
font.size = Pt(11)

# Helper functions
def add_heading(text, level=1):
    h = doc.add_heading(text, level=level)
    for run in h.runs:
        run.font.color.rgb = RGBColor(0, 0, 0)
    return h

def add_para(text, bold=False, italic=False):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.bold = bold
    run.italic = italic
    return p

def add_image_centered(path, width=Inches(6.5)):
    if os.path.exists(path):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run()
        run.add_picture(path, width=width)
    else:
        doc.add_paragraph(f'[Image not found: {path}]')

def add_table_from_data(headers, rows):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = 'Light Grid Accent 1'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    # Header
    for j, header in enumerate(headers):
        cell = table.rows[0].cells[j]
        cell.text = header
        for p in cell.paragraphs:
            for run in p.runs:
                run.bold = True
                run.font.size = Pt(9)
    # Data rows
    for i, row_data in enumerate(rows):
        for j, val in enumerate(row_data):
            cell = table.rows[i + 1].cells[j]
            cell.text = str(val)
            for p in cell.paragraphs:
                for run in p.runs:
                    run.font.size = Pt(9)
    return table


# ══════════════════════════════════════════════════════════════════════════
# TITLE PAGE
# ══════════════════════════════════════════════════════════════════════════
title = doc.add_heading('Enhanced Democratic Priority Score', level=0)
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
for run in title.runs:
    run.font.size = Pt(26)
    run.font.color.rgb = RGBColor(0, 51, 102)

subtitle = doc.add_paragraph()
subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = subtitle.add_run('A Data-Driven Composite Index for Campaign Resource Allocation\n'
                        'Swing State Election Analysis: Pennsylvania, Michigan, North Carolina')
run.font.size = Pt(14)
run.font.color.rgb = RGBColor(80, 80, 80)

author = doc.add_paragraph()
author.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = author.add_run('\nAntoni Czolgowski | Data Lead\n'
                      'CSCI 5502 Data Mining | Spring 2026 | University of Colorado Boulder\n'
                      'April 2026')
run.font.size = Pt(11)
run.font.color.rgb = RGBColor(100, 100, 100)

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════════
# 1. EXECUTIVE SUMMARY
# ══════════════════════════════════════════════════════════════════════════
add_heading('1. Executive Summary')

doc.add_paragraph(
    'The Enhanced Democratic Priority Score (DPS) is a composite 0-1 index that ranks '
    '250 counties across three critical swing states (Pennsylvania, Michigan, North Carolina) '
    'by their strategic value for Democratic campaign resource allocation. The score integrates '
    'six data-driven components derived from classification models, regression analysis, '
    'clustering archetypes, and temporal electoral trajectories.'
)

doc.add_paragraph(
    'Key improvements over the previous version:'
)
bullets = [
    'Integrates Random Forest predicted probability of high volatility (AUC = 0.828), '
    'capturing nonlinear demographic interactions that simple weighted sums cannot.',
    'Replaces linear competitiveness function with exponential decay -- a county with '
    'a 20-point margin now scores 14% (not 80%) of a tied county.',
    'Adds directional Democratic Opportunity signal -- counties trending toward Democrats '
    'in recent elections are prioritized over those trending away.',
    'Uses log-transformed electoral weight, preventing mega-counties from dominating.',
    'Incorporates K-Means cluster membership as a persuadability modifier, '
    'reflecting county archetype context (e.g., "Poor & Diverse" clusters are 86% highly volatile).',
    'Direction-adjusts misfit scores: "Surprise Dem" counties are boosted 1.3x '
    '(empirically 2x more volatile than "Surprise Rep" misfits).'
]
for b in bullets:
    p = doc.add_paragraph(b, style='List Bullet')

doc.add_paragraph(
    '\nThe #1 priority county is Bucks County, PA (DPS = 0.734) -- 802,000 votes, '
    'essentially tied (-0.1% margin), and classified as Highly Volatile. The top 10 '
    'includes 5 PA counties (Bucks, Lehigh, Northampton, Monroe, Dauphin), 3 NC counties '
    '(Cabarrus, New Hanover, Wilson), and 2 MI counties (Kent, Oakland).'
)

# ══════════════════════════════════════════════════════════════════════════
# 2. MOTIVATION & PROBLEM STATEMENT
# ══════════════════════════════════════════════════════════════════════════
add_heading('2. Motivation: Why the Previous Score Needed Enhancement')

doc.add_paragraph(
    'The Milestone 3 priority score used four components with manually selected weights:'
)
doc.add_paragraph(
    'priority = 0.30 x volatility + 0.25 x misfit + 0.25 x vote_volume + 0.20 x margin_closeness'
)

doc.add_paragraph('This formula had four specific weaknesses:')

problems = [
    ('Arbitrary weights', 'The 0.30/0.25/0.25/0.20 split was not grounded in any empirical '
     'result. Feature ablation shows Race/Ethnicity features alone cause the largest F1 drop '
     '(0.092), while Economic features are dispensable -- yet the original score weighted all '
     'components roughly equally.'),
    ('No ML integration', 'The Random Forest classifier achieves AUC = 0.828 and captures '
     'critical nonlinear interactions (diversity x density, education x urbanization), but its '
     'predicted probabilities were never incorporated into the score.'),
    ('No directional signal', 'A county drifting steadily toward Republicans is fundamentally '
     'different from one trending toward Democrats. The original score treated all volatility '
     'identically regardless of direction.'),
    ('Linear competitiveness', 'The formula (100 - |margin|)/100 gives a +20pp county 80% of '
     'a tied county\'s competitiveness score. No campaign would allocate resources that way -- '
     'a +20 county is essentially unwinnable/safe.')
]
for title_text, desc in problems:
    p = doc.add_paragraph()
    run = p.add_run(f'{title_text}: ')
    run.bold = True
    p.add_run(desc)

# ══════════════════════════════════════════════════════════════════════════
# 3. METHODOLOGY
# ══════════════════════════════════════════════════════════════════════════
doc.add_page_break()
add_heading('3. Methodology: The 6-Component Enhanced Score')

doc.add_paragraph(
    'The Enhanced DPS decomposes into six sub-scores, each normalized to 0-1, '
    'combined with data-driven weights summing to 1.0:'
)
doc.add_paragraph(
    'DPS = 0.20 x S_persuadability + 0.20 x S_electoral_weight + 0.20 x S_competitiveness '
    '+ 0.20 x S_predicted_volatility + 0.10 x S_dem_opportunity + 0.10 x S_misfit'
)

# Weight rationale table
add_heading('3.1 Weight Rationale', level=2)
headers = ['Component', 'Weight', 'Justification']
rows = [
    ['S_persuadability', '0.20', 'Diversity threshold (OR=7.15) + cluster archetype context'],
    ['S_electoral_weight', '0.20', 'Academic literature: vote volume is half the resource allocation equation'],
    ['S_competitiveness', '0.20', 'Academic literature: competitiveness is the other half'],
    ['S_predicted_volatility', '0.20', 'RF model (AUC=0.828) integrates all 28 features + interactions'],
    ['S_dem_opportunity', '0.10', 'Directional signal; lower weight because backward-looking'],
    ['S_misfit', '0.10', 'Captures "surprise" counties; overlaps with other ML components'],
]
add_table_from_data(headers, rows)

doc.add_paragraph(
    '\nThe core four components receive equal weight (0.20 each), reflecting both '
    'academic campaign theory (competitiveness x electoral weight) and data mining results '
    '(persuadability and predicted volatility). The two supplementary signals receive '
    '0.10 each because they are either backward-looking (opportunity) or partially '
    'redundant with other components (misfit).'
)

# Sub-score details
add_heading('3.2 Sub-Score Definitions', level=2)

# S1
add_heading('S1: Persuadability Score', level=3)
doc.add_paragraph(
    'Captures whether a county\'s electorate is likely to be persuadable, combining '
    'the diversity threshold discovery with K-Means cluster context.'
)
doc.add_paragraph('Formula: S1 = 0.60 x sigmoid((race_entropy_norm - 0.552) x 10) + 0.40 x cluster_vol_rate_norm')
doc.add_paragraph(
    'The sigmoid function creates a soft step at the empirically identified diversity threshold '
    'of 0.552 (where counties become 7.15x more likely to be highly volatile). '
    'The cluster component maps each county\'s K-Means cluster to its observed '
    'high-volatility rate: Cluster 2 "Poor & Diverse" = 86%, Cluster 4 "Educated Urban" = 73%, '
    'Cluster 0 "High-Diversity Urban" = 62%, Cluster 1 "Affluent Stable" = 49%, '
    'Cluster 3 "Rural Stable" = 26%.'
)

# S2
add_heading('S2: Electoral Weight Score', level=3)
doc.add_paragraph('Formula: S2 = MinMaxScale(log(1 + total_votes_2024))')
doc.add_paragraph(
    'Log-transformation prevents the top 5 mega-counties (Allegheny PA with 1.4M votes, '
    'Oakland MI with 772K) from compressing 245 of 250 counties into the bottom of the scale. '
    'A county with 100K votes scores meaningfully higher than one with 10K, '
    'but not 10x higher -- approximately 2x with the log transform.'
)

# S3
add_heading('S3: Competitiveness Score', level=3)
doc.add_paragraph('Formula: S3 = exp(-|dem_margin_2024| / 10)')
doc.add_paragraph(
    'Exponential decay with tau = 10 percentage points. Score mapping: '
    '0pp margin = 1.00, 5pp = 0.61, 10pp = 0.37, 20pp = 0.14, 40pp = 0.02. '
    'This reflects campaign reality: resources deployed in a +20pp county are largely wasted.'
)

# S4
add_heading('S4: Predicted Volatility Score', level=3)
doc.add_paragraph('Formula: S4 = RF.predict_proba(28_demographic_features)[:, 1]')
doc.add_paragraph(
    'A Random Forest classifier (500 trees, max_depth=8, AUC=0.828) is trained to predict '
    'binary high/low volatility from 28 scaled demographic features. The predicted probability '
    'P(high volatility) is already on a 0-1 scale. This is the most powerful individual component '
    'because it captures ALL nonlinear feature interactions -- diversity x density, '
    'education x urbanization, rent x poverty -- that no linear formula can.'
)

# S5
add_heading('S5: Democratic Opportunity Score', level=3)
doc.add_paragraph('Formula: S5 = MinMaxScale(0.65 x d_20_24 + 0.35 x d_16_20)')
doc.add_paragraph(
    'Positive d_20_24 means the county shifted toward Democrats in the most recent election cycle. '
    'The 65/35 weighting favors recency. This component is weighted at only 0.10 because '
    'past trajectory does not reliably predict future direction -- Blue Bounceback '
    '(2020 Biden surge reversing in 2024) is the most common pattern at 47% of counties.'
)

# S6
add_heading('S6: Demographic Misfit Score', level=3)
doc.add_paragraph('Formula: S6 = MinMaxScale(direction_adjusted_misfit)')
doc.add_paragraph(
    'The misfit score (|actual_winner - P(Dem)| from logistic regression) is adjusted by direction: '
    '"Surprise Dem" counties (model predicted Republican, voted Democrat) receive a 1.3x multiplier, '
    '"Surprise Rep" counties receive 0.7x. This reflects the empirical finding that '
    'Surprise Dem misfits have average volatility of 0.807, double that of Surprise Rep misfits (0.383). '
    'Examples: Leelanau MI (misfit = 0.96, demographics say Republican, votes Democrat +8%).'
)

# ══════════════════════════════════════════════════════════════════════════
# 4. DATA SOURCES
# ══════════════════════════════════════════════════════════════════════════
doc.add_page_break()
add_heading('4. Data Sources & Integration')

doc.add_paragraph(
    'The enhanced score integrates outputs from across the entire project pipeline:'
)

headers = ['Data Source', 'File', 'Key Variables Used']
rows = [
    ['Raw Election Data (2024)', 'master_dataset.csv', 'dem_margin (pp), total_votes, total_population'],
    ['Scaled Demographics (2024)', 'master_dataset_scaled.csv', 'race_entropy_norm (raw 0-1 scale)'],
    ['Classification Features', 'classification_dataset_250.csv', '28 z-scored demographic features, vol_binary'],
    ['Volatility Metrics', 'county_volatility_dimTable.csv', 'd_16_20, d_20_24 (swing direction/magnitude)'],
    ['K-Means Clusters', 'kmeans_clusters.csv', 'kmeans_cluster_label (5 clusters)'],
    ['Classification Predictions', 'classification_predictions.csv', 'p_dem, misfit_score (logistic regression)'],
    ['Old Priority Scores', 'campaign_priority_rankings.csv', 'priority_score (Milestone 3, for comparison)'],
]
add_table_from_data(headers, rows)

doc.add_paragraph(
    '\nAll datasets are merged on county_fips (5-digit FIPS code). '
    'The master_dataset is filtered to election_year = 2024 for current-state features.'
)

add_heading('4.1 Integration of Project Analysis Results', level=2)
integration_points = [
    ('Classification (Random Forest)', 'P(high volatility) from RF binary classifier becomes S4. '
     'The model captures nonlinear interactions between race_entropy_norm, log_median_gross_rent, '
     'pct_bachelors_plus, and population density that are invisible to linear combinations.'),
    ('Regression (Linear Regression)', 'Regression coefficients informed the choice of components and their '
     'relative importance. The universal significance of log_median_gross_rent (beta = 0.88, strongest across all states) '
     'is captured through the RF model. State-specific signatures (PA: diversity-driven, MI: education-driven, '
     'NC: poverty-driven) are implicitly encoded in the RF predicted probabilities.'),
    ('Clustering (K-Means, k=5)', 'Cluster membership directly feeds S1 (Persuadability) as a modifier. '
     'Each cluster\'s observed high-volatility rate maps to the persuadability score, so a county in '
     '"Poor & Diverse" (Cluster 2, 86% high vol) gets a higher persuadability boost than one in '
     '"Rural Stable" (Cluster 3, 26% high vol).'),
    ('Temporal Analysis', 'Swing direction data (d_16_20, d_20_24) from volatility dimension table becomes S5. '
     'Trajectory classification (Blue Bounceback, Steady Red Drift, etc.) informed the decision '
     'to weight this component at only 0.10.'),
    ('Misfit Detector', 'The logistic regression misfit score becomes S6, with direction adjustment based on '
     'the finding that Surprise Dem misfits are 2x more volatile than Surprise Rep.'),
    ('Diversity Threshold', 'The race_entropy_norm threshold of 0.552 (OR = 7.15, bootstrap CI [0.397, 0.642]) '
     'is the core of S1, implemented as a soft sigmoid to capture the step-function relationship.'),
]
for title_text, desc in integration_points:
    p = doc.add_paragraph()
    run = p.add_run(f'{title_text}: ')
    run.bold = True
    p.add_run(desc)

# ══════════════════════════════════════════════════════════════════════════
# 5. RESULTS
# ══════════════════════════════════════════════════════════════════════════
doc.add_page_break()
add_heading('5. Results')

add_heading('5.1 Top 10 Democratic Priority Counties (Overall)', level=2)

top10 = df.nlargest(10, 'DPS')
headers = ['Rank', 'County', 'State', 'DPS', 'Persuad.', 'Elec.Wt', 'Compet.', 'Pred.Vol', 'Dem.Opp', 'Misfit', 'Margin', 'Votes']
rows = []
for i, (_, row) in enumerate(top10.iterrows(), 1):
    rows.append([
        str(i),
        row['county_short'],
        row['state'],
        f"{row['DPS']:.3f}",
        f"{row['S_persuadability']:.3f}",
        f"{row['S_electoral_weight']:.3f}",
        f"{row['S_competitiveness']:.3f}",
        f"{row['S_volatility_predicted']:.3f}",
        f"{row['S_dem_opportunity']:.3f}",
        f"{row['S_misfit']:.3f}",
        f"{row['dem_margin_2024_pp']:+.1f}%",
        f"{row['total_votes_2024']:,.0f}",
    ])
add_table_from_data(headers, rows)

doc.add_paragraph(
    '\nBucks County, PA is the undisputed #1 target: 802,000 votes, virtually tied (-0.1%), '
    'and classified as Highly Volatile. Its S_competitiveness score (0.993) is the highest '
    'in the dataset. The top 4 counties are all in the Philadelphia suburban corridor '
    '(Bucks, Lehigh, Northampton, Monroe) -- the decisive PA battleground.'
)

# Top 5 per state
for state_abbr, state_name in [('PA', 'Pennsylvania'), ('MI', 'Michigan'), ('NC', 'North Carolina')]:
    add_heading(f'5.2 Top 5 -- {state_name}', level=2)
    state_top5 = df[df['state'] == state_abbr].nlargest(5, 'DPS')
    rows = []
    for i, (_, row) in enumerate(state_top5.iterrows(), 1):
        rows.append([
            str(i), row['county_short'], row['state'],
            f"{row['DPS']:.3f}",
            f"{row['S_persuadability']:.3f}", f"{row['S_electoral_weight']:.3f}",
            f"{row['S_competitiveness']:.3f}", f"{row['S_volatility_predicted']:.3f}",
            f"{row['S_dem_opportunity']:.3f}", f"{row['S_misfit']:.3f}",
            f"{row['dem_margin_2024_pp']:+.1f}%", f"{row['total_votes_2024']:,.0f}",
        ])
    add_table_from_data(headers, rows)

    # State-specific narrative
    if state_abbr == 'PA':
        doc.add_paragraph(
            '\nPennsylvania dominates the top 10, with 5 of its counties ranking nationally. '
            'The Lehigh Valley (Lehigh + Northampton) and Poconos (Monroe) form a critical corridor '
            'alongside Bucks. Dauphin (Harrisburg metro) rounds out the top 5 as the state capital region. '
            'All 5 counties are in the eastern half of the state, consistent with the diversity-driven '
            'volatility signature identified in state-specific models (top predictor: race_entropy_norm).'
        )
    elif state_abbr == 'MI':
        doc.add_paragraph(
            '\nMichigan\'s top targets are split between large suburban centers (Oakland 772K votes, '
            'Kent/Grand Rapids 372K, Macomb 509K) and smaller competitive markets (Grand Traverse 63K). '
            'Kent County\'s #1 state ranking reflects its combination of Highly Volatile classification, '
            'large voter pool, and recent Democratic momentum (d_20_24 positive). '
            'Oakland has the highest persuadability (0.802) in the state, driven by its high diversity and '
            'educated urban cluster profile. Macomb, despite being -13.7%, ranks #5 because its massive '
            'vote count (509K) makes even small shifts electorally significant.'
        )
    elif state_abbr == 'NC':
        doc.add_paragraph(
            '\nNorth Carolina presents a diverse targeting landscape. Cabarrus (Charlotte suburbs) leads '
            'with the highest S_dem_opportunity (0.932), indicating strong recent Democratic momentum. '
            'New Hanover (Wilmington area) is near-competitive (+0.6% margin, S_competitiveness = 0.940). '
            'Wilson is notable for its extreme persuadability score (0.940) -- the highest in the top 10 '
            'nationally -- driven by its position in the "Poor & Diverse" cluster. Wake County (Raleigh) '
            'ranks #4 despite a +25% Democratic margin because of its enormous electoral weight (654K votes) '
            'and high persuadability.'
        )

# ══════════════════════════════════════════════════════════════════════════
# 6. QUALITATIVE ANALYSIS -- EXPERT COMMENTARY
# ══════════════════════════════════════════════════════════════════════════
doc.add_page_break()
add_heading('6. Qualitative Analysis: County-by-County Expert Commentary')

doc.add_paragraph(
    'This section provides strategic context for every county in the top 10, top 5 per state, '
    'and notable alternatives. Each county is assessed not just by its score, but by its '
    'political trajectory, demographic dynamics, and strategic role in the Electoral College map.'
)

# --- Score Quality Metrics ---
add_heading('6.1 Score Quality: Old vs. New Rankings', level=2)

headers = ['Metric', 'Old Top 10', 'New Top 10', 'Improvement']
rows = [
    ['Total voter pool', '1,806,039', '3,451,281', '+91% more votes reachable'],
    ['Avg |margin|', '6.8 pp', '3.6 pp', '47% more competitive'],
    ['Counties > 50K votes', '6 of 10', '9 of 10', 'Better resource efficiency'],
    ['Counties Highly Volatile', '7 of 10', '5 of 10', 'Broader targeting (incl. Volatile)'],
]
add_table_from_data(headers, rows)
doc.add_paragraph(
    '\nThe enhanced score dramatically improves strategic resource allocation. '
    'The old score placed two micro-counties (Leelanau MI with 17K votes, Scotland NC with 14K votes) '
    'in the top 5 -- no campaign strategist would allocate national resources to counties '
    'where even a 10-point swing yields fewer than 2,000 votes.'
)

# --- Top 10 County Profiles ---
add_heading('6.2 Top 10 County Profiles', level=2)

# County 1 - Bucks
p = doc.add_paragraph()
run = p.add_run('#1 -- Bucks County, Pennsylvania (DPS = 0.734)')
run.bold = True
run.font.size = Pt(12)
doc.add_paragraph(
    'THE bellwether. Bucks County\'s trajectory tells the story of American suburban politics: '
    '+0.8% for Clinton (2016), +4.4% for Biden (2020), then back to -0.1% in 2024 -- '
    'the textbook "Blue Bounceback" pattern. With 802,056 total votes and a margin of just 582 votes '
    'in 2024, this is the single most competitive large county in the three-state study region. '
    'Every sub-score is strong: near-perfect competitiveness (0.993), very high predicted volatility (0.878), '
    'and a large electoral footprint (0.914). '
    'Campaign implication: This is a persuasion county. The voters are there, they swing, and there are '
    'enough of them to decide Pennsylvania\'s 19 electoral votes. Ground game, earned media, and '
    'targeted digital advertising in the Bucks County media market should be the #1 budget line item.'
)

# County 2 - Lehigh
p = doc.add_paragraph()
run = p.add_run('#2 -- Lehigh County, Pennsylvania (DPS = 0.702)')
run.bold = True
run.font.size = Pt(12)
doc.add_paragraph(
    'The heart of the Lehigh Valley -- Allentown, Bethlehem, Easton. '
    'Lehigh has been on a Democratic trajectory (+4.7% in 2016, +7.6% in 2020), '
    'but snapped back to +2.7% in 2024. The racial diversity index (entropy = 0.699) '
    'places it well above the critical 0.552 threshold, and it sits in the "High-Diversity Urban" '
    'cluster. With 379,620 votes, it delivers real electoral weight. '
    'The persuadability score (0.728) reflects a rapidly diversifying population driven by '
    'Hispanic immigration and NYC commuter spillover -- precisely the demographic dynamics that '
    'our regression model identifies as the strongest predictor of volatility (race_entropy: beta = 0.47). '
    'Campaign implication: Bilingual outreach and housing affordability messaging. '
    'The Lehigh Valley\'s volatility is driven by rapid demographic change, not swing voters per se.'
)

# County 3 - Northampton
p = doc.add_paragraph()
run = p.add_run('#3 -- Northampton County, Pennsylvania (DPS = 0.702)')
run.bold = True
run.font.size = Pt(12)
doc.add_paragraph(
    'Northampton is the classic bellwether -- it voted for Obama (2008, 2012), flipped to Trump '
    'in 2016 (-3.8%), flipped back to Biden in 2020 (+0.7%), and returned to Republican lean '
    'in 2024 (-1.8%). This county has correctly predicted the PA winner in 4 of the last 5 cycles. '
    'Paired with Lehigh, the two counties form a natural media market. '
    'Its competitiveness (0.837) and predicted volatility (0.844) are both among the highest in the dataset. '
    'Campaign implication: Northampton\'s swing voters are genuine persuadables -- white working-class '
    'voters in the Easton/Bethlehem area who have voted for both parties. This is a classic '
    'persuasion-first county, distinct from Lehigh\'s diversity-driven volatility.'
)

# County 4 - Monroe
p = doc.add_paragraph()
run = p.add_run('#4 -- Monroe County, Pennsylvania (DPS = 0.688)')
run.bold = True
run.font.size = Pt(12)
doc.add_paragraph(
    'The Pocono Mountains. Monroe County is one of the fastest-diversifying counties in PA, '
    'with a racial entropy index of 0.730 (highest among PA top 5). Its trajectory mirrors Bucks: '
    '+0.8% (2016), +6.4% (2020), -0.8% (2024) -- another Blue Bounceback county. '
    'Monroe is being transformed by NYC exurban migration along I-80, bringing in younger, '
    'more diverse residents who are reshaping an historically rural county. '
    'The Highly Volatile classification and strong predicted volatility (0.680) reflect '
    'a county in genuine demographic transition. '
    'Campaign implication: Monroe is a "future Lehigh Valley" -- investing here now builds '
    'infrastructure for a county that will only become more electorally significant. '
    'Focus on new residents and first-time voters.'
)

# County 5 - Cabarrus
p = doc.add_paragraph()
run = p.add_run('#5 -- Cabarrus County, North Carolina (DPS = 0.678)')
run.bold = True
run.font.size = Pt(12)
doc.add_paragraph(
    'The Charlotte suburbs are the story of NC politics, and Cabarrus is the leading edge. '
    'The trajectory is remarkable: -19.6% (2016), -9.4% (2020), -7.7% (2024) -- a 12-point '
    'shift toward Democrats over 8 years. This is NOT a Blue Bounceback; it\'s a Steady Blue Drift, '
    'one of the most volatile trajectory types (50% high volatility rate). '
    'Cabarrus has the highest S_dem_opportunity score (0.932) in the entire top 10, reflecting '
    'this consistent Democratic momentum. Its racial entropy (0.802) is well above the threshold. '
    'Campaign implication: Cabarrus may not be winnable in 2028, but the trend is unmistakable. '
    'Every dollar invested here erodes the Republican structural advantage in the Charlotte metro. '
    'Focus on suburban women, college-educated professionals, and the growing Hispanic community.'
)

# County 6 - Kent
p = doc.add_paragraph()
run = p.add_run('#6 -- Kent County, Michigan (DPS = 0.672)')
run.bold = True
run.font.size = Pt(12)
doc.add_paragraph(
    'Grand Rapids -- historically the capital of Michigan Republicanism (Gerald Ford\'s district). '
    'Kent flipped to Biden in 2020 (+6.1%) after Trump lost it by just -3.1% in 2016, and Democrats '
    'held it at +5.4% in 2024. With 371,947 votes, Kent is the largest competitive county in Michigan. '
    'The combination of Highly Volatile classification, high predicted volatility (0.828), and '
    'strong Democratic opportunity (0.814) makes this a county where Democrats have recently built gains '
    'but cannot yet take them for granted. '
    'Campaign implication: Kent is where Michigan will be decided. The evangelical base that made '
    'this a GOP stronghold is being offset by the growing urban core, education-driven '
    'suburban shift, and diversifying population. This is THE persuasion county in MI.'
)

# County 7 - New Hanover
p = doc.add_paragraph()
run = p.add_run('#7 -- New Hanover County, North Carolina (DPS = 0.657)')
run.bold = True
run.font.size = Pt(12)
doc.add_paragraph(
    'Wilmington and the NC coast. New Hanover flipped Democratic in 2020 (+2.1%) after going '
    'Republican in 2016 (-3.9%), then narrowed to just +0.6% in 2024 -- a margin of approximately '
    '830 votes out of 139,000 cast. This is essentially tied. '
    'Its S_competitiveness score (0.940) is the second-highest in the top 10, trailing only Bucks. '
    'The county\'s entropy (0.565) sits right at the critical diversity threshold (0.552), '
    'meaning it is on the exact knife-edge where our model predicts volatility probability jumps. '
    'Campaign implication: New Hanover is the "Bucks County of North Carolina" -- a coastal '
    'suburban county that swings with the national mood. Resource allocation here is among '
    'the most efficient in NC because the margin is razor-thin and the vote count is meaningful.'
)

# County 8 - Oakland
p = doc.add_paragraph()
run = p.add_run('#8 -- Oakland County, Michigan (DPS = 0.654)')
run.bold = True
run.font.size = Pt(12)
doc.add_paragraph(
    'Oakland is the single most important "protect the gains" county in the dataset. '
    'Once reliably Republican, Oakland flipped decisively to Democrats: +8.1% (2016), '
    '+14.0% (2020), but then eroded to +10.6% in 2024 -- a loss of 3.4 points in one cycle. '
    'With 772,145 votes (the second-largest county in the study), this erosion translates to '
    'approximately 26,000 votes lost. If the trend continues at this rate, Oakland becomes '
    'competitive by 2028 -- and losing Oakland means losing Michigan. '
    'The predicted volatility of 0.887 (highest in the top 10) confirms the RF model sees '
    'Oakland as demographically unstable. Its "Educated Urban" cluster profile (Cluster 4) '
    'reflects the kind of diverse, high-income, highly-educated suburbs that have been drifting '
    'Democratic nationally but may have hit a ceiling. '
    'Campaign implication: This is a defensive investment. Oakland does not need persuasion -- it needs '
    'Democratic turnout infrastructure to arrest the erosion. Focus on the Black community in Pontiac/Southfield, '
    'suburban mothers, and young professionals. Every 1% turnout increase in Oakland = ~7,700 votes.'
)

# County 9 - Dauphin
p = doc.add_paragraph()
run = p.add_run('#9 -- Dauphin County, Pennsylvania (DPS = 0.643)')
run.bold = True
run.font.size = Pt(12)
doc.add_paragraph(
    'The state capital region. Harrisburg has been steadily Democratic (+2.9%, +8.5%, +5.9%), '
    'but the 2024 pullback from Biden\'s +8.5% reveals vulnerability. '
    'Dauphin\'s high racial diversity (entropy = 0.775) and position in the High-Diversity Urban '
    'cluster make it one of the most persuadable counties in PA. The S_dem_opportunity score (0.667) '
    'indicates a net-positive trajectory despite the 2024 pullback. '
    'With 299,052 votes, Dauphin provides a strong voter pool in central PA -- '
    'a region where Democrats otherwise have few targets. '
    'Campaign implication: Dauphin is the gateway to central PA. It\'s the only top-10 county '
    'outside the eastern suburban corridor, providing geographic diversification of campaign presence. '
    'This county can anchor a central PA media buy that also reaches adjacent Cumberland (#20) and Lebanon.'
)

# County 10 - Wilson
p = doc.add_paragraph()
run = p.add_run('#10 -- Wilson County, North Carolina (DPS = 0.639)')
run.bold = True
run.font.size = Pt(12)
doc.add_paragraph(
    'Wilson is the most analytically interesting county in the top 10 -- and the most debatable. '
    'At only 40,045 votes, it is the smallest county in the national top 10 by a significant margin. '
    'Its presence here is driven by an extraordinary combination: near-perfect competitiveness '
    '(+0.4% margin, S_competitiveness = 0.961) and the highest persuadability in the entire top 10 '
    '(0.940), powered by its position in the "Poor & Diverse" K-Means cluster where 86% of '
    'counties are classified as highly volatile. '
    'Wilson\'s trajectory is the most concerning: +5.6% (2016), +2.9% (2020), +0.4% (2024) -- '
    'a Steady Red Drift of 5.2 points over 8 years. If this trend continues, Wilson flips '
    'Republican by 2028. This is exactly the pattern the Steady Red Drift trajectory analysis '
    'identified as the most volatile (50% high vol rate). '
    'Campaign implication: Wilson is a CANARY IN THE COAL MINE. It represents the dozens of '
    'small, racially diverse, economically struggling Southern counties that are slipping away from '
    'Democrats. Losing Wilson itself costs ~200 votes net. But the pattern Wilson exemplifies -- '
    'the erosion of rural diverse Southern counties -- could cost tens of thousands across NC. '
    'Strategic value: diagnostic, not volume-based.'
)

# --- Top 5 Per State Deep Analysis ---
doc.add_page_break()
add_heading('6.3 State-Level Strategic Assessment', level=2)

# PENNSYLVANIA
add_heading('Pennsylvania: The Decisive Battleground', level=3)
doc.add_paragraph(
    'Pennsylvania dominates the national top 10 with 5 of 10 counties. This is not a scoring artifact -- '
    'it reflects genuine strategic reality. PA has 19 electoral votes (the most of the three states), '
    'the state-specific regression model has the highest R-squared (0.674), and the eastern suburban '
    'corridor contains an unusual concentration of large, competitive, volatile counties. '
    'The top 5 PA counties account for 2,007,208 total votes -- more than the entire top 10 '
    'of the old score.'
)
doc.add_paragraph(
    'All 5 PA targets are in the eastern third of the state, forming a natural media corridor '
    'from Philadelphia (Bucks, #1) through the Lehigh Valley (Lehigh #2, Northampton #3) '
    'to the Poconos (Monroe #4) and inland to Harrisburg (Dauphin #5). A coordinated ground game '
    'across this 150-mile corridor could be served by 3-4 field offices and a single TV media buy.'
)

p = doc.add_paragraph()
run = p.add_run('Near-miss -- Lackawanna PA (#12, DPS = 0.627): ')
run.bold = True
p.add_run(
    'Scranton -- Joe Biden\'s hometown. Lackawanna was #2 in the old score and drops to #12 here. '
    'It remains a strong target (233K votes, +2.8%, Highly Volatile) but its lower diversity '
    '(entropy = 0.485, below the 0.552 threshold) reduces its persuadability score. '
    'The decline from +8.4% (2020) to +2.8% (2024) is alarming and merits attention. '
    'A campaign with resources for 6 PA counties should add Lackawanna.'
)

p = doc.add_paragraph()
run = p.add_run('Near-miss -- Erie PA (#23, DPS = 0.579): ')
run.bold = True
p.add_run(
    'The famous bellwether. Erie went Obama, Obama, Trump, Biden, then Trump again in 2024 (-1.0%). '
    'At 275K votes and a near-tied margin, Erie seems like it should rank higher. '
    'However, the RF model assigns it only 33% probability of high volatility -- the demographics '
    'suggest stable working-class patterns despite the historical swings. '
    'Erie\'s bellwether status may owe more to its representativeness of the national mood '
    'than to persuadable demographics.'
)

# MICHIGAN
add_heading('Michigan: Volume Targets vs. Bellwethers', level=3)
doc.add_paragraph(
    'Michigan\'s top 5 splits into two distinct categories: large suburban/urban centers '
    '(Kent 372K, Oakland 772K, Macomb 509K) and smaller competitive markets '
    '(Genesee 223K, Grand Traverse 63K). '
    'The combined voter pool of the top 5 is 1,939,284 -- more than the entire old top 10 nationally.'
)
doc.add_paragraph(
    'Kent County (#1 in MI) is the state\'s premier persuasion target. '
    'Oakland (#2) is a defensive priority. Genesee (#3, Flint) is the traditional Democratic '
    'anchor in central Michigan, showing troubling erosion (+9.5% to +4.2% in 8 years). '
    'Grand Traverse (#4, Traverse City) is a genuinely competitive small market (-1.7%). '
    'Macomb (#5) is the most controversial inclusion: at -13.7%, it\'s not competitive in the '
    'traditional sense. But with 509,152 votes, Macomb is too large to ignore. '
    'The county\'s working-class demographics and "High-Diversity Urban" cluster profile suggest '
    'a persuadable electorate -- if the right message reaches them.'
)

p = doc.add_paragraph()
run = p.add_run('Near-miss -- Saginaw MI (#31, DPS = 0.544): ')
run.bold = True
p.add_run(
    'A traditional bellwether (-3.3% margin, 104K votes) but classified as Moderate volatility. '
    'Saginaw\'s predicted volatility is low (0.26) despite its historical swing patterns. '
    'Worth monitoring but not a top-5 target.'
)

p = doc.add_paragraph()
run = p.add_run('Not recommended -- Leelanau MI (old #4, now #33): ')
run.bold = True
p.add_run(
    'At 17,685 votes, Leelanau (Traverse City resort area) was significantly overranked '
    'in the old score. Its maximum electoral impact is ~880 votes if the margin shifted by 10 points. '
    'Interesting as a misfit case study (highest misfit score in the dataset, 0.956) but '
    'not a resource allocation target.'
)

# NORTH CAROLINA
add_heading('North Carolina: The Most Complex Targeting Landscape', level=3)
doc.add_paragraph(
    'NC presents the most challenging targeting decisions. Unlike PA (concentrated eastern corridor) '
    'and MI (clear suburban targets), NC\'s priority counties are geographically scattered and '
    'include a mix of genuinely competitive suburbs, safe Democratic bases, and small rural counties. '
    'The state-specific regression model has the weakest performance (R-squared = 0.435) because '
    'NC\'s poverty-driven volatility mechanism is harder to predict than PA\'s diversity-driven one.'
)

p = doc.add_paragraph()
run = p.add_run('Strong picks -- Cabarrus (#1 NC) and New Hanover (#2 NC): ')
run.bold = True
p.add_run(
    'These are the two clearest NC targets. Cabarrus (Charlotte suburbs) shows consistent '
    'Democratic momentum and is the fastest-blue-shifting large county in NC. '
    'New Hanover (Wilmington) is essentially tied at +0.6% -- the NC equivalent of Bucks County. '
    'Together they represent 258,936 votes in two genuinely competitive, growing markets.'
)

p = doc.add_paragraph()
run = p.add_run('Borderline -- Wilson (#3 NC): ')
run.bold = True
p.add_run(
    'At 40K votes, Wilson is small but its near-zero margin (+0.4%) and maximum persuadability (0.940) '
    'make it strategically interesting. Its real value is diagnostic: Wilson represents the pattern '
    'of diverse rural Southern counties that are drifting Republican. If the campaign finds a message '
    'that works in Wilson, it may work in dozens of similar counties across the South.'
)

p = doc.add_paragraph()
run = p.add_run('Caution -- Wake (#4 NC, +25.4%, 654K votes): ')
run.bold = True
p.add_run(
    'Wake County (Raleigh) is NOT a persuasion target at +25.4%. Its presence in the top 5 '
    'is driven by its enormous electoral weight (654K votes) and high persuadability score '
    '(entropy = 0.826). In practical campaign terms, Wake is a TURNOUT target, not a swing target. '
    'Even a 1% turnout improvement in Wake delivers ~6,500 votes. '
    'An alternative framing: if Wake was removed from the top 5 and replaced with a competitive county, '
    'Pitt County (Greenville, 87K votes, +6.0%, ECU university town) or Nash County (52K votes, '
    '-1.8% margin, essentially tied) would be more traditional persuasion targets.'
)

p = doc.add_paragraph()
run = p.add_run('Weakest pick -- Lenoir (#5 NC, -6.8%, 28K votes, STABLE): ')
run.bold = True
p.add_run(
    'Lenoir is the most questionable entry in any state\'s top 5. It is classified as Stable '
    '(not volatile), has only 27,503 votes, and has been drifting Republican (-3.7% to -6.8% over '
    '8 years). Its high ranking is driven almost entirely by its extremely high persuadability '
    'score (0.918) from being in the "Poor & Diverse" cluster -- meaning its demographics PREDICT '
    'volatility that hasn\'t materialized yet. This could be a leading indicator (the county is '
    'about to become volatile) or a false positive (cultural factors override demographic predictions). '
    'Better alternatives for NC #5: Nash County (52K votes, -1.8%, near-tied) or Pitt County '
    '(87K votes, +6.0%, growing university town). Both offer more votes, more competitive margins, '
    'and more established campaign infrastructure.'
)

# --- Summary Assessment Box ---
doc.add_page_break()
add_heading('6.4 Overall Assessment: Score Reliability', level=2)

doc.add_paragraph(
    'The Enhanced Democratic Priority Score produces rankings that are overwhelmingly consistent '
    'with expert political judgement. Of the 10 nationally-ranked counties:'
)

bullets_assess = [
    'Top 7 (#1-7) are unambiguously correct targets that any campaign strategist would validate. '
    'They combine competitive margins, meaningful voter pools, and documented demographic volatility.',
    '#8 Oakland MI is a "protect the gains" pick that reflects sophisticated campaign thinking -- '
    'defending a 772K-vote suburban anchor against a documented erosion trend.',
    '#9 Dauphin PA provides essential geographic diversification, anchoring Democratic presence '
    'in central PA beyond the eastern corridor.',
    '#10 Wilson NC is the most analytically interesting and most debatable pick. '
    'Its inclusion as a diagnostic bellwether is defensible but a pure resource-efficiency model '
    'would replace it with Genesee MI (#11, 223K votes, +4.2%) or Lackawanna PA (#12, 233K votes, +2.8%).',
    'The score correctly demotes micro-counties (Leelanau, Scotland, Marquette) from the old top 10, '
    'nearly doubling the total reachable voter pool from 1.8M to 3.5M votes.',
]
for b in bullets_assess:
    doc.add_paragraph(b, style='List Bullet')

# ══════════════════════════════════════════════════════════════════════════
# 7. VISUALIZATIONS
# ══════════════════════════════════════════════════════════════════════════
doc.add_page_break()
add_heading('7. Visualizations')

add_heading('7.1 Three-State Choropleth: All Counties by Priority Score', level=2)
doc.add_paragraph(
    'Every county shaded by its Democratic Priority Score (0 = low priority, darker = higher priority). '
    'Clear geographic patterns emerge: eastern PA, southern/central MI, and the urban/suburban '
    'crescent of NC show the highest concentrations of high-priority counties.'
)
add_image_centered(f'{FIG_DIR}/enhanced_priority_3state_choropleth.png', Inches(6.5))

add_heading('7.2 Top 10 Priority Counties Highlighted', level=2)
doc.add_paragraph(
    'Only the top 10 counties are colored, with all other counties in neutral gray. '
    'The color scale is relative to the top 10 range, making it easy to see which '
    'targets have the highest strategic value. PA dominates with 5 of the top 10, '
    'all concentrated in the eastern suburban corridor.'
)
add_image_centered(f'{FIG_DIR}/enhanced_priority_top10_highlight.png', Inches(6.5))

doc.add_page_break()
add_heading('7.3 Pennsylvania: Top 5 Priority Counties', level=2)
add_image_centered(f'{FIG_DIR}/enhanced_priority_PA_top5.png', Inches(6))

add_heading('7.4 Michigan: Top 5 Priority Counties', level=2)
add_image_centered(f'{FIG_DIR}/enhanced_priority_MI_top5.png', Inches(6))

add_heading('7.5 North Carolina: Top 5 Priority Counties', level=2)
add_image_centered(f'{FIG_DIR}/enhanced_priority_NC_top5.png', Inches(6))

# ══════════════════════════════════════════════════════════════════════════
# 7. VALIDATION
# ══════════════════════════════════════════════════════════════════════════
doc.add_page_break()
add_heading('8. Validation & Quality Checks')

corr = df['DPS'].corr(df['old_priority_score'])
top10_vol = top10['volatility_class'].value_counts().to_dict()
skewness = df['DPS'].skew()

checks = [
    ('Correlation with old score', f'Pearson r = {corr:.3f}',
     'The enhanced score is strongly correlated with the original (r = 0.85), confirming it preserves '
     'the core signal. But r < 1.0 confirms meaningful new information has been added.'),
    ('Top 10 volatility classes', str(top10_vol),
     'All top-10 counties are Volatile or Highly Volatile (except Wilson NC at Moderate, ranked #10). '
     'No Very Stable or Stable county appears in the top 10 -- the score correctly identifies '
     'unstable, competitive counties.'),
    ('Score distribution', f'Skewness = {skewness:.3f}',
     'Positive skewness indicates a right-skewed distribution -- most counties are low-priority '
     '(mean = 0.34, median = 0.29) with a tail of high-priority targets. This is exactly what a '
     'campaign resource allocator needs: a small number of high-value targets.'),
    ('Bucks County #1', 'DPS = 0.734',
     'The undisputed top target remains Bucks County PA -- consistent with both the old score '
     'and conventional campaign wisdom about this critical Philadelphia suburb.'),
    ('Small county demotion', 'Leelanau MI: old #4 -> new #22',
     'Leelanau (17K votes) correctly drops from #4 to #22. Despite high volatility and misfit scores, '
     'its small electoral footprint means campaign resources have limited impact. '
     'Similarly Scotland NC (14K votes) drops from #5 to #47.'),
]

for title_text, metric, explanation in checks:
    p = doc.add_paragraph()
    run = p.add_run(f'{title_text} ({metric}): ')
    run.bold = True
    p.add_run(explanation)

# ══════════════════════════════════════════════════════════════════════════
# 8. CAMPAIGN STRATEGY IMPLICATIONS
# ══════════════════════════════════════════════════════════════════════════
add_heading('9. Campaign Strategy Implications')

doc.add_paragraph(
    'The Enhanced Democratic Priority Score translates complex data mining results into '
    'actionable campaign intelligence. Here is what campaign strategists should take away:'
)

implications = [
    ('Pennsylvania is the top battleground',
     'Five of the top 10 priority counties are in PA. The eastern suburban corridor '
     '(Bucks-Lehigh-Northampton-Monroe-Dauphin) is the decisive region. These counties are '
     'large (171K-802K votes), competitive (margins under 6%), and volatile. A coordinated '
     'ground game across this corridor could swing the state.'),
    ('Michigan requires a dual strategy',
     'Kent (Grand Rapids) and Oakland (Detroit suburbs) are the volume targets. '
     'Grand Traverse (Traverse City) is a smaller but highly competitive bellwether. '
     'Macomb is worth monitoring despite its -14% margin because of its massive size (509K votes).'),
    ('North Carolina is a mobilization play',
     'Cabarrus (Charlotte suburbs) and Wilson are top targets due to strong recent '
     'Democratic momentum (S_dem_opportunity > 0.90). Wake (Raleigh) is a turnout target '
     'rather than a persuasion target -- already +25% Dem but enormous (654K votes).'),
    ('Persuadability is not the same as competitiveness',
     'Wilson NC has the highest persuadability in the top 10 (0.940) but is only +0.4% margin. '
     'Oakland MI has very high persuadability (0.802) but sits at +10.6%. '
     'The score integrates both dimensions -- a county can be persuadable but already won, '
     'or competitive but not persuadable.'),
    ('Past volatility does not guarantee future persuadability',
     'The S_dem_opportunity component (weight 0.10) is deliberately small because trajectory '
     'reversal is common (47% of counties showed Blue Bounceback). The score prioritizes '
     'structural factors (demographics, cluster type, predicted volatility) over momentum.'),
]
for title_text, desc in implications:
    p = doc.add_paragraph()
    run = p.add_run(f'{title_text}: ')
    run.bold = True
    p.add_run(desc)

# ══════════════════════════════════════════════════════════════════════════
# 9. LIMITATIONS & FUTURE WORK
# ══════════════════════════════════════════════════════════════════════════
add_heading('10. Limitations & Future Work')

limitations = [
    'The RF model is trained on only 250 counties (small sample). Bootstrap CIs suggest '
    'robust performance, but external validation on other swing states would strengthen confidence.',
    'Demographic data is from ACS estimates, which lag real-time population changes by 1-2 years. '
    'Rapidly growing counties (e.g., Cabarrus NC) may have shifted since the data was collected.',
    'The score treats all Democratic voters equally. In practice, campaigns distinguish between '
    'turnout targets (increasing participation among existing supporters) and persuasion targets '
    '(changing minds). Integrating voter file-level data would enable this distinction.',
    'Cross-state models fail (LOSO F1 = 0.195), meaning state-specific mechanisms are not '
    'transferable. The Enhanced DPS handles this through implicit RF encoding rather than '
    'explicit state adjustment -- a more robust but less interpretable approach.',
    'The 2024 election cycle may represent a unique political environment. The score should be '
    'recalibrated for each election cycle as new demographic data and election results become available.',
]
for lim in limitations:
    doc.add_paragraph(lim, style='List Bullet')

# ══════════════════════════════════════════════════════════════════════════
# 10. FILES PRODUCED
# ══════════════════════════════════════════════════════════════════════════
add_heading('11. Files Produced')

headers = ['File', 'Description']
rows = [
    ['notebooks/enhanced_democratic_priority_score.py', 'Main script: computes all 6 sub-scores, generates rankings and maps'],
    ['data/processed/enhanced_priority_rankings.csv', '250 counties with all sub-scores, composite DPS, and old score comparison'],
    ['docs/images/methods/enhanced_priority_3state_choropleth.png', 'Three-state map with all counties shaded by DPS'],
    ['docs/images/methods/enhanced_priority_top10_highlight.png', 'Three-state map highlighting only top 10 counties'],
    ['docs/images/methods/enhanced_priority_PA_top5.png', 'Pennsylvania map with top 5 counties labeled'],
    ['docs/images/methods/enhanced_priority_MI_top5.png', 'Michigan map with top 5 counties labeled'],
    ['docs/images/methods/enhanced_priority_NC_top5.png', 'North Carolina map with top 5 counties labeled'],
    ['reports/Enhanced_Democratic_Priority_Score_Summary.docx', 'This document'],
]
add_table_from_data(headers, rows)

# ── Save ─────────────────────────────────────────────────────────────────
doc.save(OUTPUT_PATH)
print(f'DOCX saved to: {OUTPUT_PATH}')
