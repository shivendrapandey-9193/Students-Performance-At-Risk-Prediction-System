from pathlib import Path

path = Path("src/dashboard/app.py")
content = path.read_text(encoding="utf-8")

# Update configuration and evaluation values.
updates = {
    "MODEL_THRESHOLD = 0.4583": "MODEL_THRESHOLD = 0.24567134268537077",
    '"88.14%"': '"74.32%"',
    '"13.70%"': '"9.08%"',
    '"39.73%"': '"63.52%"',
    '"20.37%"': '"15.89%"',
    "                88.14,": "                74.32,",
    "                13.70,": "                9.08,",
    "                39.73,": "                63.52,",
    "                20.37,": "                15.89,",
    "                [35568, 3926],": "                [29523, 9971],",
    "                [945, 623]": "                [572, 996]",
    "Test records: 41,062 | Threshold: 0.4583":
        "Test records: 41,062 | Threshold: 0.24567",
    "Decision threshold:</b> 0.4583":
        "Decision threshold:</b> 0.24567",
}

for old, new in updates.items():
    count = content.count(old)
    if count != 1:
        raise RuntimeError(
            f"Expected one occurrence of {old!r}, found {count}. "
            "File was not saved."
        )
    content = content.replace(old, new, 1)

# Update the Overview warning by locating its st.warning block.
start = content.find('    st.warning(\n', content.find('### Important model limitation'))
if start == -1:
    raise RuntimeError("Overview warning block not found.")

end = content.find("\n    )", start)
if end == -1:
    raise RuntimeError("End of Overview warning block not found.")

warning = '''    st.warning(
        "At the recall-focused threshold, test precision is 9.08% and recall "
        "is 63.52%. The model generated 9,971 false positives and 572 false "
        "negatives. Predictions must support educator review, never automatic "
        "academic decisions."
    )'''

content = content[:start] + warning + content[end + 6:]

# Update the Model Insights limitations section.
old = "- Test precision is 13.70%, so false-positive alerts are substantial."
new = "- At this threshold, test precision is 9.08% and recall is 63.52%."
if content.count(old) != 1:
    raise RuntimeError("Model Insights precision limitation not found.")
content = content.replace(old, new, 1)

old = "- Test recall is 39.73%, so many low-score records are missed."
new = (
    "- The model flagged 10,967 of 41,062 test records.\n"
    "    - There were 9,971 false positives and 572 false negatives."
)
if content.count(old) != 1:
    raise RuntimeError("Model Insights recall limitation not found.")
content = content.replace(old, new, 1)

path.write_text(content, encoding="utf-8")
print("Dashboard updated successfully.")
print("Threshold: 0.24567134268537077")
print("Test accuracy: 74.32%")
print("Test precision: 9.08%")
print("Test recall: 63.52%")
print("Test F1: 15.89%")
