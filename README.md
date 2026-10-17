# Signature: Mourad.Soltani

# FounderPricingDigest

Minimal CLI micro-tool for solo SaaS founders to snapshot and digest competitor pricing pages.

Extracts price-like amounts, computes a content hash for change detection, and stores local snapshots.

## Features

- Fetch public pricing page
- Extract common price patterns ($29, $99/mo, etc.)
- Content hash for change detection (ignores nav/footer noise)
- Local snapshot store in ~/.founder_pricing_digest
- JSON or human-readable output
- Health tests included

## Install

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py https://example.com/pricing https://another.com/pricing
python main.py --json https://example.com/pricing
```

## Tests

```bash
python -m unittest tests/test_health.py
```

All health tests must pass.

## License

MIT

Built by Mourad.Soltani
