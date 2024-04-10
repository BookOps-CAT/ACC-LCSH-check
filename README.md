# ACC-LCSH-Check
## About
This repo contains a set of scripts to check [id.loc.gov](id.loc.gov) for changes made to LCSH. These scripts check for changes made in LCSH for a specific list of subject headings identified by the BPL Alternative Classification Committee. The script runs monthly on a schedule using GitHub Actions (see `.github\workflows\monthly-run.yaml` for workflow).

### Workflow
The `monthly_lcsh_check.py` script runs every month on the 10th at 4AM EST. The script will read each term in `data/acc_in.csv` and check [id.loc.gov](id.loc.gov) for changes made in the last month. This monthly check is logged in `lcsh.log`. 

### Output
Each monthly run will result in the workflow opening a pull request in this repo. If no changes have been made in the previous month to any of the LCSH in `acc_in.csv`, the PR will only include changes made to `lcsh.log` logging the results of the monthly run. 

#### Changes
If any of the terms in `acc_in.csv` have been changed or deprecated in the previous month, these changes will be listed in the log file and new files will be written to the `data/` directory of this repo. 

Any terms that have not been changed or deprecated in the last month will be written to `acc_out.csv`. The older list of terms, `acc_in.csv`, will be renamed to `acc_in_{yyyymmdd}.csv` and `acc_out.csv`, the current list of terms, will be renamed `acc_in.csv` to be used in future monthly checks.

If any terms have been changed or deprecated the workflow will open an issue. The PR that the workflow opens will include changes made to `lcsh.log` and any files in the `data/` directory.