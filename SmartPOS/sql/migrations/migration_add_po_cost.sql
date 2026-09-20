-- ============================================================
-- Migration: adds cost tracking to Purchase Orders, so ordering
-- stock actually shows up as money spent.
--
-- Run this in phpMyAdmin (SQL tab, on the smartpos database).
-- ============================================================

USE smartpos;

ALTER TABLE purchase_orders
    ADD COLUMN IF NOT EXISTS unit_cost DECIMAL(10,2) NULL AFTER quantity_ordered;
