
with open('test.csv', 'r') as file:
  content = file.read()

items = content.split(',')
quoted = [f"'{i}'" for i in items]

result = "\n".join(quoted)

print(result)

with open('only-spatial-cols.py', 'w') as f:
  f.write(result)