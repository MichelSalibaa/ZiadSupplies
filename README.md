# Ziad's Supplies storefront

Self-contained web storefront for **Ziad's Supplies** built with Python standard library tooling and a lightweight static frontend. It provides:

- Visual catalog grouped by category and subcategory (detergents, packaging, hygiene, cloths, tissues).
- Client-side cart with cash on delivery (COD) checkout form.
- SQLite database for catalog data, orders and order items.
- Optional email confirmations for each order (using your SMTP credentials).

The stack uses Python's built-in HTTP server, `sqlite3`, and `smtplib`, so it runs without third-party dependencies.

## Getting started

1. Ensure Python 3.10+ is available.
2. Configure environment variables (optional but recommended) before running the server:

   ```powershell
   setx ZIAD_DB_PATH "data\ziad_store.sqlite3"
   setx SMTP_HOST "smtp.yourprovider.com"
   setx SMTP_PORT "587"
   setx SMTP_USERNAME "no-reply@ziadsupplies.com"
   setx SMTP_PASSWORD "your-smtp-password"
   setx EMAIL_FROM "Ziad's Supplies <no-reply@ziadsupplies.com>"
   setx BASE_URL "http://localhost:8000"
   ```

   > If SMTP variables are omitted the application still works, but confirmation emails are only logged to the console.

3. Launch the development server:

   ```powershell
   python -m app.server
   ```

4. Open `http://localhost:8000` in your browser.

### Order confirmation emails

Every submitted order is immediately marked as `received` and an email summary is sent to the customer (if SMTP is configured). The message lists the ordered items and confirms that the delivery team will reach out to coordinate dispatch.

> Upgrading from an older build? Delete the existing `data\ziad_store.sqlite3` file to reload the refreshed catalog with category images and item variants.

## Project structure

```
app/
  config.py          # Environment-driven settings
  database.py        # SQLite schema, seed data, query helpers
  email_service.py   # SMTP integration for confirmation emails
  server.py          # HTTP server, API endpoints, static asset delivery
static/
  app.js             # Catalog rendering, cart interactions, checkout flow
  styles.css         # Responsive layout styles
templates/
  index.html         # Storefront landing page
  verify.html        # Legacy order status template (kept for future flows)
data/
  ziad_store.sqlite3 # Created on first run (path configurable)
```

## Next steps

- Add more granular product variants or pricing tiers once finalized.
- Hook the order pipeline into an ERP or fulfillment system.
- Add an authenticated admin dashboard for catalog and orders management.
