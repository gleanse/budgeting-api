# 0003 - Enforce money rules with database constraints

Status: accepted
Date: 2026-10-10

## Context
The old models declared rules like `gt=0` on amounts, but SQLModel table
classes do not validate on their own, so the database accepted zero and
negative amounts. Money columns had no precision, and category type was a
free string.

## Decision
- Money columns are `Numeric(14, 2)`
- CHECK constraints for amount > 0, limit_amount > 0, month between 1 and
  12, and from_account_id <> to_account_id
- `transaction_type` and `account_type` are real enums
- Delete rules are explicit. Accounts referenced by transactions or
  transfers cannot be deleted (restrict), deleting a category clears it on
  its transactions (set null), and everything cascades from the user
- A category's type matching its transaction's type is validated in the
  service layer, not in the database

## Consequences
- Bad data is rejected even if application code has a bug
- Constraints must be declared in the models, and the generated Alembic
  migration must be checked by hand, because autogenerate may not emit
  CHECK constraints and any that are missing have to be added manually
- The service layer owns the category and transaction type check
