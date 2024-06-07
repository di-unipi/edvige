# Edvige 🦉

Edvige is the codename
for the communication team
of the [Department of Computer Science](https://di.unipi.it)
at the University of Pisa.
In this repository,
you will find the code
to serve our public calendar,
which we currently screencast
near the coffee machines. ☕

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

Then, we keep track of the Department events
via a Google Calendar.
The following command automatically downloads
the calendar as an ICS file and generates
a static website in `www` to visualize
upcoming events.

```bash
npm run calendar
```
