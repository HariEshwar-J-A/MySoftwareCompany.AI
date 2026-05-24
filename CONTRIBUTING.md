# Contributing

Thank you for your interest in MySoftwareCompany.AI. This document covers the core product only (`packages/msc/`, `orgs/`, `scripts/`, `benchmarks/`, `website/`). Vendored trees under `vendor/` follow their upstream contribution guides.

## License

Contributions to the core are accepted under the same terms as the project: [BUSL-1.1](LICENSE) with the Additional Use Grant described in the license file. **Production use** of the Licensed Work still requires a commercial agreement — see [COMMERCIAL.md](COMMERCIAL.md).

## Development setup

```bash
git clone https://github.com/mysoftwarecompany/MySoftwareCompany.AI.git
cd MySoftwareCompany.AI
make vendor-sync install-dev
```

Copy `config.example.yaml` to `~/.msc/config.yaml`. Put LLM API keys in `~/.metagpt/config2.yaml` only — never commit secrets.

## Checks before opening a PR

```bash
make ci                    # ruff, license headers, pytest
cd website && npm ci && npm run lint && npm run build
```

CI runs the same steps on push to `main` and on pull requests (see [.github/workflows/ci.yml](.github/workflows/ci.yml)).

## Code style

- Python: `ruff` (line length 100), BUSL header on new files (`python scripts/license_header.py --fix`).
- TypeScript (website): `npm run lint` in `website/`.

## Pull requests

1. Branch from `main` with a focused change.
2. Add or update tests when behavior changes.
3. Update [CHANGELOG.md](CHANGELOG.md) under **Unreleased** for user-visible changes (maintainers fold into release sections at tag time).
4. Describe how you tested (`pytest`, manual CLI steps, website build).

## Security

Do not open public issues for sensitive vulnerabilities. Email **security@mysoftwarecompany.ai** (or the address in [COMMERCIAL.md](COMMERCIAL.md) if that alias is not yet live).

## Questions

Use GitHub Discussions on the project repository for design questions; use Issues for bugs with reproduction steps.
