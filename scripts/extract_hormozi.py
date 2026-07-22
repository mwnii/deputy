"""Extract text from Hormozi PDFs - PyMuPDF (fast, low memory)."""
import os, sys, json, time
from pathlib import Path

import fitz  # PyMuPDF

HORMOZI_DIR = Path(r"C:\Users\PC\Downloads\Alex Hormozi")
OUTPUT_DIR = Path(r"C:\Users\PC\Downloads\income-system\knowledge\hormozi")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
PROGRESS_FILE = OUTPUT_DIR / "_progress.json"

PDF_MAP = [
    ("$100M Offers\\100M Offers (Alex Hormozi).pdf", "offers", "offer_architect"),
    ("$100M Offers\\100M Offers The Lost Chapter (Alex Hormozi)_compressed.pdf", "offers", "offer_architect"),
    ("$100M Leads\\100M Leads How to Get Strangers.pdf", "leads", "lead_generation"),
    ("$100M Leads\\$100M Leads - 2 Bonus Chapters -- Alex Hormozi.pdf", "leads", "lead_generation"),
    ("$100M_Money_Models_How_To_Make_Money_-_Alex_Hormozi.pdf", "money_models", "money_model"),
    ("$100M Lost Chapters by Alex Hormozi.pdf", "money_models", "money_model"),
    ("$100M Journal.pdf", "planning", "scaling_ops"),
    ("Gym_Launch_Secrets_-_Alex_Hormozi.pdf", "launch_playbook", "launch_playbook"),
    ("ACQ Advertising Handbook.pdf", "advertising", "advertising"),
    ("ACQ Closer Handbook How to Win.pdf", "sales", "sales_closing"),
    ("Affiliate Blackbook.pdf", "affiliate", "affiliate"),
    ("Leila Hormozis 5 Scaling Framework SOPs.pdf", "scaling", "scaling_ops"),
    ("$100m Playbooks\\$100M Branding Playbook.pdf", "branding", "retention_proof"),
    ("$100m Playbooks\\$100M Closing Playbook - Closing (+ Page 54, scan).pdf", "sales", "sales_closing"),
    ("$100m Playbooks\\$100M Fast Cash Playbook.pdf", "fast_cash", "fast_cash"),
    ("$100m Playbooks\\$100M Goated Ads Playbook.pdf", "advertising", "advertising"),
    ("$100m Playbooks\\$100M Hooks Playbook.pdf", "leads", "lead_generation"),
    ("$100m Playbooks\\$100M Lead Nurture Playbook (+ Page 30).pdf", "leads", "lead_generation"),
    ("$100m Playbooks\\$100M Lifetime Value Playbook.pdf", "retention", "retention_proof"),
    ("$100m Playbooks\\$100M Marketing Machine.pdf", "marketing", "scaling_ops"),
    ("$100m Playbooks\\$100M Price Raise Playbook.pdf", "pricing", "offer_architect"),
    ("$100m Playbooks\\$100M Pricing Playbook.pdf", "pricing", "offer_architect"),
    ("$100m Playbooks\\$100M Proof Checklist Playbook.pdf", "proof", "retention_proof"),
    ("$100m Playbooks\\$100M Retention Playbook.pdf", "retention", "retention_proof"),
    ("$100m Scaling Roadmap\\Your_ACQ_100MScalingRoadmap-Stage0_.pdf", "scaling", "scaling_ops"),
    ("$100m Scaling Roadmap\\Your_ACQ_100MScalingRoadmap-Stage01_.pdf", "scaling", "scaling_ops"),
    ("$100m Scaling Roadmap\\Your_ACQ_100MScalingRoadmap-Stage02_.pdf", "scaling", "scaling_ops"),
    ("$100m Scaling Roadmap\\Your_ACQ_100MScalingRoadmap-Stage03_.pdf", "scaling", "scaling_ops"),
    ("$100m Scaling Roadmap\\Your_ACQ_100MScalingRoadmap-Stage04_.pdf", "scaling", "scaling_ops"),
    ("$100m Scaling Roadmap\\Your_ACQ_100MScalingRoadmap-Stage05_.pdf", "scaling", "scaling_ops"),
    ("$100m Scaling Roadmap\\Your_ACQ_100MScalingRoadmap-Stage06_.pdf", "scaling", "scaling_ops"),
    ("$100m Scaling Roadmap\\Your_ACQ_100MScalingRoadmap-Stage07_.pdf", "scaling", "scaling_ops"),
    ("$100m Scaling Roadmap\\Your_ACQ_100MScalingRoadmap-Stage08_.pdf", "scaling", "scaling_ops"),
    ("$100m Scaling Roadmap\\Your_ACQ_100MScalingRoadmap-Stage09_.pdf", "scaling", "scaling_ops"),
    ("$100M Money Models Book Launch\\(All Assets) $100M Money Models\\Landing Pages\\1 - Registration.pdf", "book_launch", "launch_playbook"),
    ("$100M Money Models Book Launch\\(All Assets) $100M Money Models\\Landing Pages\\1.1 - Registration (Opt-In).pdf", "book_launch", "launch_playbook"),
    ("$100M Money Models Book Launch\\(All Assets) $100M Money Models\\Landing Pages\\2 - VIP Upgrade.pdf", "book_launch", "launch_playbook"),
    ("$100M Money Models Book Launch\\(All Assets) $100M Money Models\\Landing Pages\\2.1 - VIP Upgrade (Add to Cart).pdf", "book_launch", "launch_playbook"),
    ("$100M Money Models Book Launch\\(All Assets) $100M Money Models\\Landing Pages\\3 - VIP Thank You.pdf", "book_launch", "launch_playbook"),
    ("$100M Money Models Book Launch\\(All Assets) $100M Money Models\\Landing Pages\\4 - No TY VIP.pdf", "book_launch", "launch_playbook"),
    ("$100M Money Models Book Launch\\(All Assets) $100M Money Models\\Landing Pages\\6 - 100M-Money-Models-Launch-Recap.pdf", "book_launch", "launch_playbook"),
]


def sanitize(name):
    return "".join(c if c.isalnum() or c in "-_" else "_" for c in name).strip("_").lower()[:80]


def load_progress():
    if PROGRESS_FILE.exists():
        return set(json.loads(PROGRESS_FILE.read_text()))
    return set()


def save_progress(done):
    PROGRESS_FILE.write_text(json.dumps(list(done)))


def extract_one(pdf_path):
    doc = fitz.open(str(pdf_path))
    pages = []
    for i, page in enumerate(doc):
        try:
            t = page.get_text()
            if t.strip():
                pages.append(f"--- Page {i+1} ---\n{t}")
        except:
            pass
    doc.close()
    return "\n\n".join(pages)


def main():
    done = load_progress()
    agent_files = {}
    errors = []

    for rel, domain, agent in PDF_MAP:
        if rel in done:
            # load existing
            agent_dir = OUTPUT_DIR / agent
            if agent_dir.exists():
                for f in agent_dir.glob("*.md"):
                    if agent not in agent_files:
                        agent_files[agent] = []
                    agent_files[agent].append(str(f))
            continue

        full = HORMOZI_DIR / rel
        if not full.exists():
            errors.append(f"NOT FOUND: {rel}")
            done.add(rel)
            continue

        print(f"Extracting: {rel} [{agent}]")
        try:
            text = extract_one(full)
        except Exception as e:
            errors.append(f"ERROR: {rel} -> {e}")
            done.add(rel)
            continue

        agent_dir = OUTPUT_DIR / agent
        agent_dir.mkdir(exist_ok=True)
        out = agent_dir / f"{sanitize(full.stem)}.md"
        content = f"# {full.stem}\n\n**Domain:** {domain}\n**Agent:** {agent}\n**Source:** {rel}\n\n---\n\n{text}\n"
        out.write_text(content, encoding="utf-8")

        if agent not in agent_files:
            agent_files[agent] = []
        agent_files[agent].append(str(out))
        done.add(rel)
        save_progress(done)
        print(f"  OK: {out.name} ({len(text)} chars)")

    # Build index
    lines = ["# Hormozi Knowledge Base Index\n"]
    for agent in sorted(agent_files):
        lines.append(f"\n## {agent}\n")
        for f in sorted(agent_files[agent]):
            lines.append(f"- {f}")
    if errors:
        lines.append("\n\n## Errors\n")
        for e in errors:
            lines.append(f"- {e}")

    (OUTPUT_DIR / "INDEX.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"\nDone: {len(done)}/{len(PDF_MAP)} extracted, {len(errors)} errors")


if __name__ == "__main__":
    main()
