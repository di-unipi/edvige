# Edvige 🦉

Edvige is the codename
for the communication team
of the [Department of Computer Science](https://di.unipi.it)
at the University of Pisa.
In this repository,
you will find the code
to format our monthly newsletter
and to serve our website,
which we currently screencast
near the coffee machines. ☕

This amount of spaghetti
that we love to call codebase
depends on various tools.
Assuming that you already installed
`npm` for
[NodeJS](https://nodejs.org/en/)
and `pip3` for
[Python](https://www.python.org/),
you can install the required dependencies
as follows.

```bash
npm ci
```

yep, that easy.

## 📰 Newsletter

The newsletter entries
should be written
in Markdown format
and stored in the `archive` folder
with naming `month_year.md`,
as in `september_2022.md`.

Then, you should run:

```bash
npm run newsletter 
```

The script transpiles Markdown documents
into HTML files using [mjml](https://mjml.io/),
so that thay can be easily and cross-platform
shared through email.
The resulting HTML files are in the
`www/newsletter/` folder.

## 📺 Website

We keep track of the Department events
via a Google Calendar.
The following command automatically downloads
the calendar as an ICS file and generates
a static website in `www` to visualize
upcoming events.

```bash
npm run calendar
```
