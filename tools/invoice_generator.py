from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    from weasyprint import HTML
except ImportError:
    HTML = None


INVOICE_HTML = """<!DOCTYPE html>
<html>
<head>
<style>
  body {{ font-family: Arial, sans-serif; margin: 40px; color: #333; }}
  .header {{ display: flex; justify-content: space-between; border-bottom: 2px solid #0066cc; padding-bottom: 20px; }}
  .header h1 {{ color: #0066cc; margin: 0; }}
  .meta {{ margin: 20px 0; }}
  .meta p {{ margin: 5px 0; }}
  table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
  th {{ background: #0066cc; color: white; padding: 12px; text-align: left; }}
  td {{ padding: 12px; border-bottom: 1px solid #ddd; }}
  .total {{ font-size: 1.2em; font-weight: bold; text-align: right; margin-top: 20px; }}
  .footer {{ margin-top: 40px; font-size: 0.9em; color: #666; border-top: 1px solid #ddd; padding-top: 10px; }}
</style>
</head>
<body>
  <div class="header">
    <div>
      <h1>INVOICE</h1>
      <p><strong>{invoice_number}</strong></p>
    </div>
    <div style="text-align: right;">
      <p><strong>Date:</strong> {date}</p>
      <p><strong>Due:</strong> {due_date}</p>
    </div>
  </div>
  <div class="meta">
    <p><strong>From:</strong> {sender_name}</p>
    <p><strong>To:</strong> {client_name}</p>
  </div>
  <table>
    <thead>
      <tr><th>Description</th><th>Qty</th><th>Rate</th><th>Amount</th></tr>
    </thead>
    <tbody>
      {items_html}
    </tbody>
  </table>
  <div class="total">
    <p>Total: {currency} {total}</p>
  </div>
  <div class="footer">
    <p>Payment via PayPal: {paypal_email}</p>
    <p>{notes}</p>
  </div>
</body>
</html>"""


def generate_invoice(
    client_name: str,
    items: list[dict[str, Any]],
    invoice_number: str = "",
    sender_name: str = "AI Freelancer",
    paypal_email: str = "",
    currency: str = "USD",
    notes: str = "Thank you for your business!",
    output_dir: str | None = None,
) -> str:
    """Generate a PDF invoice."""
    now = datetime.now()
    if not invoice_number:
        invoice_number = f"INV-{now.strftime('%Y%m%d')}-{now.strftime('%H%M%S')}"

    items_html = ""
    total = 0.0
    for item in items:
        qty = item.get("quantity", 1)
        rate = item.get("rate", 0)
        amount = qty * rate
        total += amount
        items_html += f"<tr><td>{item.get('description', '')}</td><td>{qty}</td><td>{currency} {rate:.2f}</td><td>{currency} {amount:.2f}</td></tr>"

    html = INVOICE_HTML.format(
        invoice_number=invoice_number,
        date=now.strftime("%Y-%m-%d"),
        due_date=now.strftime("%Y-%m-%d"),
        sender_name=sender_name,
        client_name=client_name,
        items_html=items_html,
        total=f"{total:.2f}",
        currency=currency,
        paypal_email=paypal_email,
        notes=notes,
    )

    out_dir = Path(output_dir) if output_dir else Path(__file__).parent.parent / "vault" / "01-INBOX"
    out_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = out_dir / f"{invoice_number}.pdf"

    if HTML:
        HTML(string=html).write_pdf(str(pdf_path))
    else:
        # Fallback: save as HTML if weasyprint not installed
        html_path = out_dir / f"{invoice_number}.html"
        html_path.write_text(html, encoding="utf-8")
        return str(html_path)

    return str(pdf_path)
