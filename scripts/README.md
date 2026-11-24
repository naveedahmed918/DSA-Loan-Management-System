# DSA Loan Portal – data and test scripts

Run each script from the bench's `sites` folder, so it can find the site:

```bash
cd ~/frappe/frappe-bench-v15/sites
../env/bin/python ../apps/dsa_loan/scripts/<script>.py <site>
```

Every script runs as one transaction: if anything fails, nothing is saved. All of them are safe to run again.

## Build a site's data, in this order

| # | Script | What it does |
|---|---|---|
| 1 | `import_atharva_master_data.py` | Imports the master data from `data/atharva_fixtures/` (branch `atharva/home-loan-master-data`): 3 lender types, 6 lenders, 5 DSA branches, 30 products, 38 schemes and 70 document rules. Branches are moved to the site's company. |
| 2 | `fix_atharva_rules.py` | Turns off document rules that only repeat a standard checklist row. Gives property and legal papers to the property owner only. Copies self-employed rules across Self Employed, Business Owner and Professional. |
| 3 | `fix_master_data.py` | Fills product tenure from schemes and adds the Plot + Construction products. Adds one commission slab per lender, valid branch PIN codes, and SBI's published document rules. |
| 4 | `load_bank_rates.py` | Loads each bank's published rates, fees and limits, with the source link and date. Sets commission % on the slabs; these are **samples** to replace with the agreed payouts. |
| 5 | `setup_gst.py [--reraise]` | Creates Output CGST, SGST and IGST accounts and the GST 18% templates (in-state is the default). `--reraise` re-issues lender invoices that were raised without tax. |
| 6 | `seed_scenarios.py` | Demo data: every DocType gets 5–20 records, and every application, document, disbursement, payout, clawback, settlement, franchise and lead status is covered. People and addresses are fictional. |
| 7 | `create_demo_users.py` | Creates one user per DSA role, limited to a branch or franchise. Test passwords are written to `<bench>/demo_users.txt`, which is not committed. |

Scripts 4 and later rely on the results of the earlier ones.

## Check

- `e2e_flow_test.py` walks the whole flow (86 checks) inside a transaction and rolls everything back, so the site is left as it was.

## Notes

- Lender invoices are emailed only to the members of each lender's **Invoice Email Group**. A group that exists but is empty means "send to nobody". The lender's Official Email is used only when no group is set.
- Bank rates change with the repo rate. To refresh them, edit the figures in `load_bank_rates.py` and run it again.
