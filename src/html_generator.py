import markdown
import os
import sys
from datetime import datetime as dt

def render_mail(mail_path: str, date: str, idx: int):
    with open('src/template.mjml', 'r') as f:
        template = f.read()

    with open(mail_path, 'r') as f:
        text = f.read()

    rendered = template.replace('%%%BODY%%%', markdown.markdown(text))
    rendered = rendered.replace('%%%DATE%%%', date)
    rendered = rendered.replace('%%%IDX%%%', str(idx))
    return rendered


if __name__ == '__main__':
    # Get list of mail files sorted by date
    mails = os.listdir('archive')
    mails = sorted(
        mails,
        key=lambda x: dt.strptime(x, '%B_%Y.md'),
        reverse=True
    )

    if len(sys.argv) > 1:
        # Get the mail from the command line
        mail_path = sys.argv[1]
    else:
        # Get the last mail in the
        # archive folder. Mails are
        # stored in the format
        # "monthname_year.md"
        mail_path = f'archive/{mails[0]}'

    # Retrieve the date from the filename
    date = dt.strptime(mail_path.split('/')[-1].split('.')[0], '%B_%Y')
    date = dt.strftime(date, '%B %Y')

    # Get index of the mail
    idx = mails.index(mail_path.split('/')[-1])

    print(render_mail(mail_path, date, idx))
