Historical migration scripts from before the two draft files
(`schema.sql` + these) were consolidated into one `schema.sql`.
`schema.sql` already includes every change these make — verified
column-for-column — so for a fresh database you only need `schema.sql`.
Kept here for reference/history only; do not run against a database
that was already created from the current `schema.sql`.
