# 0002 - Keep transfers as a separate table

Status: accepted
Date: 2026-10-10

## Context
A transfer moves money between two of the user's own accounts. It changes
two balances at once and is neither income nor expense. Modeling it as a
transaction would count it in income and expense totals, so moving money
from an e-wallet to cash would look like earning and spending it.

## Decision
Transfers live in their own `transfers` table with `from_account_id` and
`to_account_id`, and a check constraint that the two accounts differ.
`transactions` only ever holds income and expense.

## Consequences
- Income and expense totals and budgets ignore transfers automatically
- Account balance is the initial balance plus income and incoming transfers,
  minus expense and outgoing transfers
- A combined history of transactions and transfers needs a query that
  merges the two tables
- Rejected alternative: a two-row ledger (one debit, one credit per
  transfer). It gives a single balance query but adds complexity that v1
  does not need
