import markdown
import os
import sys
from datetime import datetime as dt

def render_mail(mail_path: str):
    with open('src/template.mjml', 'r') as f:
        template = f.read()

    with open(mail_path, 'r') as f:
        text = f.read()

    return template.replace('%%%BODY%%%', markdown.markdown(text))


if __name__ == '__main__':
    if len(sys.argv) > 1:
        mail_path = sys.argv[1]
    else:
        # Get the last mail in the
        # archive folder. Mails are
        # stored in the format
        # "monthname_year.md"
        mails = os.listdir('archive')
        mails = sorted(
            mails,
            key=lambda x: dt.strptime(x, '%B_%Y.md'),
            reverse=True
        )
        mail_path = f'archive/{mails[0]}'

    print(render_mail(mail_path))
