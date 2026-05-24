# Publishing `mscai` to PyPI

The distribution name on PyPI is **`mscai`**. Console entry points: `msc` and `mscai` → `msc.cli:app`.

## Prerequisites

- PyPI account with access to the `mscai` project (or a new project registration).
- API token stored locally (never commit): `~/.pypirc` or `TWINE_USERNAME=__token__` / `TWINE_PASSWORD`.

## Build locally

From the repository root:

```bash
python -m pip install --upgrade pip build twine
python -m build
```

Artifacts land in `dist/` (`mscai-0.1.0-py3-none-any.whl` and `mscai-0.1.0.tar.gz`).

Verify the wheel installs in a clean venv:

```bash
python -m venv /tmp/mscai-test
source /tmp/mscai-test/bin/activate
pip install dist/mscai-0.1.0-py3-none-any.whl
msc --version
```

**Note:** A full `msc run` still requires cloning the repo for `vendor/`, `orgs/`, and MetaGPT editable install — the PyPI wheel ships the `msc` Python package only.

## Upload (maintainers)

Test PyPI first (recommended):

```bash
twine upload --repository testpypi dist/*
pip install -i https://test.pypi.org/simple/ mscai==0.1.0
```

Production:

```bash
twine upload dist/*
```

## Git release tag

After the release commit is on `main`:

```bash
git tag -a v0.1.0 -m "Release v0.1.0"
git push origin main
git push origin v0.1.0
```

Create a GitHub Release from tag `v0.1.0` with notes from [CHANGELOG.md](../CHANGELOG.md).

## CI

[.github/workflows/release.yml](../.github/workflows/release.yml) builds sdist/wheel on tag push `v*`. Publishing to PyPI is manual unless `PYPI_API_TOKEN` is configured as a repository secret.
