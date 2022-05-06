import sys
import markdown

template = """
<mjml>
  <mj-head>
      <mj-font name="IBM Plex Sans" href="https://fonts.googleapis.com/css?family=IBM+Plex+Sans" />
  </mj-head>
  <mj-body>
    <mj-section>
      <mj-column>
        <mj-text font-family=\"IBM Plex Sans\" line-height=\"2\">
            %%%BODY%%%
        </mj-text>
      </mj-column>
    </mj-section>
  </mj-body>
</mjml>"""

with open(sys.argv[1], 'r') as f:
    text = f.read()

mail = template.replace('%%%BODY%%%', markdown.markdown(text))
print(mail)
