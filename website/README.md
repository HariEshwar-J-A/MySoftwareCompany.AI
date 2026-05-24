# MySoftwareCompany.AI — Marketing Site

Next.js App Router marketing site for [MySoftwareCompany.AI](https://mysoftwarecompany.ai).

## Pages

| Route | Description |
|---|---|
| `/` | Home — hero, how it works, featured org packs |
| `/services` | Services tiers (Spike, MVP, Custom) |
| `/marketplace` | Premium org pack catalog (parity with `msc marketplace orgs`) |
| `/pricing` | CLI + marketplace + services pricing summary |
| `/contact` | Lead capture form |
| `/marketplace/success` | Post-purchase MSC1 token + `msc marketplace login` instructions |

## API routes

| Route | Description |
|---|---|
| `POST /api/checkout` | Create Stripe Checkout session for a pack |
| `GET /api/checkout/session` | Retrieve license token after successful payment |
| `POST /api/stripe/webhook` | Stripe webhook — issues MSC1 tokens (integrates with `packages/msc/entitlements/stripe_webhook.py`) |
| `POST /api/lead` | Contact form stub (forwards to `LEAD_WEBHOOK_URL` when set) |

## Environment variables

Use the **repo-root** [`.env.example`](../.env.example) → copy to `../.env` (never commit secrets). `next.config.ts` loads `../.env` when you run commands from `website/`.

Legacy reference (same variables, now in root `.env.example`):

| Variable | Required | Description |
|---|---|---|
| `STRIPE_SECRET_KEY` | For checkout | Stripe secret key (test or live) |
| `STRIPE_WEBHOOK_SECRET` | For webhook | Signing secret from Stripe CLI or dashboard |
| `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` | For checkout | Publishable key (client-side Stripe.js if added later) |
| `NEXT_PUBLIC_SITE_URL` | Recommended | Public site URL for redirect URLs |
| `NEXT_PUBLIC_DEMO_VIDEO_URL` | Optional | YouTube/Vimeo URL for home page demo iframe |
| `NEXT_PUBLIC_GITHUB_REPO` | Optional | GitHub repo URL for Get started / footer links |
| `MSC_LICENSE_PRIVATE_KEY` or `MSC_LICENSE_PRIVATE_KEY_PATH` | For license issuance | Ed25519 publisher private key (same as `scripts/.marketplace_dev_key.pem` in dev) |
| `LEAD_WEBHOOK_URL` | Optional | CRM webhook for contact form |
| `STRIPE_PRICE_FINTECH_STUDIO` | Optional | Pre-created Stripe Price ID (else dynamic `price_data` is used) |

## Development

```bash
cd website
npm install
cp .env.example .env.local   # add Stripe test keys
npm run dev
```

Regenerate marketplace manifest from `orgs/premium/`:

```bash
npm run gen:manifest
```

## Build

```bash
npm run build
npm start
```

## Stripe webhook (local)

```bash
stripe listen --forward-to localhost:3000/api/stripe/webhook
```

## License

BUSL-1.1 — Copyright (c) 2026 MySoftwareCompany.AI
