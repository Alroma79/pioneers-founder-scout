import pandas as pd, os
os.makedirs("data", exist_ok=True)
rows = [
    {"name":"Alice","profile_type":"technical","summary":"CTO","contacts":"https://linkedin.com","source_links":"https://linkedin.com","match_justification":"Strong tech","tier":"A","score":90},
    {"name":"Bob","profile_type":"business","summary":"Founder","contacts":"https://linkedin.com","source_links":"https://linkedin.com","match_justification":"Serial founder","tier":"B","score":65}
]
pd.DataFrame(rows).to_csv("data/candidates.csv", index=False)
print("Seeded data/candidates.csv")
