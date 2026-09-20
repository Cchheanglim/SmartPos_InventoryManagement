-- ============================================================
-- Migration: adds "Forgot password" support.
--
-- Safe to run even if these columns already exist -- uses
-- IF NOT EXISTS, so it only adds what's missing.
--
-- Run this in phpMyAdmin (SQL tab, on the smartpos database).
-- ============================================================

USE smartpos;

ALTER TABLE users
    ADD COLUMN IF NOT EXISTS reset_token_hash VARCHAR(255) NULL AFTER password_hash,
    ADD COLUMN IF NOT EXISTS reset_token_expires_at DATETIME NULL AFTER reset_token_hash,
    ADD COLUMN IF NOT EXISTS phone VARCHAR(20) NULL UNIQUE AFTER email;
