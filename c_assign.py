import re

input_file = "place_list.txt"
output_file = "cleaned_file.txt"

with open(input_file, "r", encoding="utf-8") as f:
    content = f.read()

# Remove all non-alphanumeric characters except space and newlines
cleaned = re.sub(r"[^a-zA-Z0-9\s\n]", "", content)

# Save the cleaned content
with open(output_file, "w", encoding="utf-8") as f:
    f.write(cleaned)

print("✅ Special characters removed and saved to:", output_file)
