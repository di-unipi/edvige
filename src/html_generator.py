import sys
import markdown

with open('src/template.mjml', 'r') as f:
    template = f.read()

with open(sys.argv[1], 'r') as f:
    text = f.read()

mail = template.replace('%%%BODY%%%', markdown.markdown(text))
print(mail)
