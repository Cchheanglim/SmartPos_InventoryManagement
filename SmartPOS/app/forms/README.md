Real WTForms validator classes, one file per module, matching the exact
fields and rules each route in app/routes/ already enforces.

**Scope note:** these are NOT currently wired into the routes as the
primary validation path. CSRF protection (Flask-WTF's CSRFProtect) IS
fully enabled globally — every POST form and fetch() call in the app
carries a real token and is rejected without one, verified against a
live database. What's not done is switching each route's existing,
already-tested manual validation (`request.form["x"]`, try/except
ValueError) over to `form.validate_on_submit()`.

That's a deliberate scope decision, not an oversight: rewiring ~20
already-working routes to a new validation path is real surgery on
tested code, and doing it without being able to re-test every single one
against a live database risked exactly the kind of regression this
project has already had one scare over. The classes here are real,
correct, and ready to be wired in — either route by route as a follow-up,
or usable right now for standalone unit tests that don't need a Flask
request context.
