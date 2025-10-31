import re
import pandas as pd

filename = r"W:\Repos-Github\whatsapp-archive-manager\docs\_chat.txt"
with open(filename, "r", encoding="utf-8") as f:
    lines = f.readlines()

pattern = re.compile(
    r'^\[(?P<date>\d{4}-\d{2}-\d{2}), (?P<time>\d{1,2}:\d{2}:\d{2}\s*[AP]M)\] (?P<sender>[^:]+): (?P<message>.+)$'
)

data = {"date": [], "time": [], "sender": [], "message": []}

current = {"date": None, "time": None, "sender": None, "message": ""}

def clean_line(line):
    # Remove hidden LTR/RTL and U+202a chars
    return (line
        .replace('\u200e','')
        .replace('\u200f','')
        .replace('\u202a','')
        .strip()
    )

for line in lines:
    line = clean_line(line)
    m = pattern.match(line)
    if m:
        # Save previous message if exists
        if current["date"]:
            data["date"].append(current["date"])
            data["time"].append(current["time"])
            data["sender"].append(current["sender"])
            data["message"].append(current["message"].strip())
        # Start new
        current = {
            "date": m.group("date"),
            "time": m.group("time"),
            "sender": m.group("sender"),
            "message": m.group("message"),
        }
    elif line != "":
        # Likely continuation or attachment—append to previous message
        current["message"] += "\n" + line
# Save last message
if current["date"]:
    data["date"].append(current["date"])
    data["time"].append(current["time"])
    data["sender"].append(current["sender"])
    data["message"].append(current["message"].strip())

df = pd.DataFrame(data)
print(df.head(20))
