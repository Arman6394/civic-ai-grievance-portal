import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import joblib

data = [
    # Electricity
    ("High voltage fluctuation in street lights, sparks falling", "Electricity", "P1"),
    ("Power outage in block B since yesterday morning", "Electricity", "P2"),
    ("Street light pole broken and hanging near school", "Electricity", "P1"),
    ("Electricity meter is running fast, need inspection", "Electricity", "P4"),
    ("Transformer caught fire after heavy rain", "Electricity", "P1"),
    
    # Water Supply & Sewerage
    ("Main water pipeline burst, clean water flooding the street", "Water Supply", "P1"),
    ("Contaminated dirty brown water coming from taps", "Water Supply", "P2"),
    ("No water supply in sector 4 for the past 24 hours", "Water Supply", "P2"),
    ("Sewage line overflow on the main road, unbearable smell", "Water Supply", "P2"),
    ("Water pressure is very low on second floor", "Water Supply", "P4"),

    # Sanitation & Waste
    ("Garbage dump overflowing outside community park", "Sanitation", "P3"),
    ("Dead animal lying near the bus stop, hygiene issue", "Sanitation", "P2"),
    ("Door-to-door waste collection truck hasn't visited this week", "Sanitation", "P3"),
    ("Open dumping of chemical waste behind factory", "Sanitation", "P1"),
    ("Litter around public market area needs regular sweeping", "Sanitation", "P4"),

    # Roads & Infrastructure
    ("Huge pothole on highway caused two bike accidents today", "Roads & Infrastructure", "P1"),
    ("Manhole cover missing on pedestrian footpath", "Roads & Infrastructure", "P1"),
    ("Road damaged severely after monsoon, need resurfacing", "Roads & Infrastructure", "P3"),
    ("Footpath encroached by illegal vendors", "Roads & Infrastructure", "P3"),
    ("Traffic signal not working at main crossing", "Roads & Infrastructure", "P2"),

    # Public Health
    ("Stagnant water breeding dengue mosquitoes in vacant plot", "Public Health", "P2"),
    ("Stray dog pack biting pedestrians near market", "Public Health", "P2"),
    ("Food poisoning cases reported from uninspected street stalls", "Public Health", "P1"),
    ("Public clinic ran out of basic fever medicines", "Public Health", "P3")
]

# Expand data slightly by duplication for training baseline
df = pd.DataFrame(data * 6, columns=["text", "department", "priority"])

# Build Department Classifier
dept_model = Pipeline([
    ("tfidf", TfidfVectorizer(ngram_range=(1, 2))),
    ("clf", LogisticRegression(class_weight="balanced"))
])
dept_model.fit(df["text"], df["department"])

# Build Priority Classifier
priority_model = Pipeline([
    ("tfidf", TfidfVectorizer(ngram_range=(1, 2))),
    ("clf", LogisticRegression(class_weight="balanced"))
])
priority_model.fit(df["text"], df["priority"])

# Save models
joblib.dump(dept_model, "dept_classifier.joblib")
joblib.dump(priority_model, "priority_classifier.joblib")
print("Models trained and exported successfully!")