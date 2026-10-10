# 0001 - Merge income and expense into transactions

Status: accepted
Date: 2026-10-10

## Context
Income and expense were separate tables with identical columns. Changing a
transaction's type meant deleting and recreating the row, and every balance,
budget, or report query had to read both tables.

## Decision
Replace `incomes` and `expenses` with one `transactions` table and a `type`
column (income or expense). Existing rows are copied over by a migration.

## Consequences
- One set of models, repositories, services, and routes instead of two
- Changing a transaction's type is a normal update
- Account balance becomes one query over one table
- The income and expense endpoints are replaced, which is safe because
  nothing outside this repo consumes the API yet
