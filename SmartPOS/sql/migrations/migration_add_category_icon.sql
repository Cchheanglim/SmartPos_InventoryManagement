-- Adds an editable icon to categories, replacing the hardcoded
-- name -> icon Python dict that used to live in app/__init__.py. That
-- dict only covered 6 fixed category names and silently broke the
-- moment a category was renamed or a new one was added — both of which
-- are now real, working features (see CategoryService). Safe to run —
-- purely additive, existing rows just get NULL (falls back to a
-- generic icon in the UI) until backfilled below.

USE smartpos;

ALTER TABLE categories ADD COLUMN icon VARCHAR(40) NULL AFTER description;

-- Backfill the 6 categories that shipped with schema.sql's seed data,
-- so existing installs keep the same icons they already had.
UPDATE categories SET icon = 'fa-cookie-bite' WHERE name = 'Snacks';
UPDATE categories SET icon = 'fa-bottle-water' WHERE name = 'Beverages';
UPDATE categories SET icon = 'fa-cheese' WHERE name = 'Dairy';
UPDATE categories SET icon = 'fa-broom' WHERE name = 'Household';
UPDATE categories SET icon = 'fa-pump-soap' WHERE name = 'Personal Care';
UPDATE categories SET icon = 'fa-jar' WHERE name = 'Pantry';
