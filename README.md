
# DSA-ERPNext-CrossAsyst

## DSA Loan Portal

Direct Selling Agent Loan Management System

## Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch develop
bench install-app dsa_loan
```

## Contributing

This app uses `pre-commit` for code formatting and linting.

Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/dsa_loan
pre-commit install
```

Pre-commit is configured to use the following tools:

- ruff
- eslint
- prettier
- pyupgrade

## License

MIT
