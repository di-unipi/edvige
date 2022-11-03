import os
from datetime import datetime as dt

template = """
<html>
  <head>
    <meta charset="utf-8">
    <title>🦉 Edvige</title>
  </head>
  <body>
    <h1>🦉 Edvige</h1>
    <ol>
      {{mail_list}}
    </ol>
  </body>
</html>
"""


if __name__ == '__main__':
    # Get list of mail files sorted by date
    mails = os.listdir('www/newsletter')

    # Remove index.html if present
    mails = [mail for mail in mails if mail != "index.html"]
    mails = sorted(
        mails,
        key=lambda x: dt.strptime(x, '%B_%Y.html'),
        reverse=False
    )

    # Construct list elements
    elements = []
    for mail in mails:
        # Retrieve the date from the filename
        date = dt.strptime(mail, '%B_%Y.html')
        date = dt.strftime(date, '%B %Y')
        li = '<li><a href="{}">{}</a></li>'.format(mail, date)
        elements.append(li)

    # Construct the list
    mail_list = '\n'.join(elements)
    template = template.replace('{{mail_list}}', mail_list)

    # Write the file
    print(template)
