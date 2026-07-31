from __future__ import annotations

import argparse
from pathlib import Path

from .config import Settings
from .downloader import PaperLibrary
from .exporters import export_bibtex, export_csv, export_ris
from .semantic import semantic_search
from .utils.doi import normalize_doi


def read_dois(path: str) -> list[str]:
    values=[]
    for line in Path(path).read_text(encoding="utf-8-sig").splitlines():
        line=line.strip()
        if line and not line.startswith("#"):
            try: values.append(normalize_doi(line))
            except ValueError: pass
    return list(dict.fromkeys(values))

def main(argv=None):
    parser=argparse.ArgumentParser(prog="paper", description="Scientific paper library manager")
    parser.add_argument("--env", help="Path to .env file")
    sub=parser.add_subparsers(dest="command", required=True)
    d=sub.add_parser("download"); g=d.add_mutually_exclusive_group(required=True); g.add_argument("--doi"); g.add_argument("--file")
    d.add_argument("--overwrite", action="store_true"); d.add_argument("--workers", type=int)
    s=sub.add_parser("search"); s.add_argument("query", nargs="?", default=""); s.add_argument("--author", default=""); s.add_argument("--journal", default=""); s.add_argument("--year", type=int); s.add_argument("--limit", type=int, default=100)
    ss=sub.add_parser("semantic-search"); ss.add_argument("query"); ss.add_argument("--limit", type=int, default=10)
    sub.add_parser("stats")
    e=sub.add_parser("export"); e.add_argument("--format", choices=["csv","bibtex","ris"], default="csv"); e.add_argument("--output")
    args=parser.parse_args(argv)
    lib=PaperLibrary(Settings.load(args.env))
    if args.command=="download":
        dois=[args.doi] if args.doi else read_dois(args.file)
        results=lib.process_many(dois, args.overwrite, args.workers)
        for p in results: print(f"{p.status:14} {p.doi} {p.pdf_path or p.error}")
    elif args.command=="search":
        for r in lib.db.search(args.query,args.author,args.journal,args.year,args.limit):
            print(f"{r.get('year') or '-'} | {r.get('journal_abbr') or r.get('journal') or '-'} | {r.get('title') or '-'} | {r.get('doi')}")
    elif args.command=="semantic-search":
        for r in semantic_search(lib.db.all(), args.query, args.limit):
            print(f"{r['score']:.3f} | {r.get('year') or '-'} | {r.get('title')} | {r.get('doi')}")
    elif args.command=="stats":
        for k,v in lib.db.stats().items(): print(f"{k}: {v}")
    elif args.command=="export":
        rows=lib.db.all(); ext={"csv":"csv","bibtex":"bib","ris":"ris"}[args.format]
        out=Path(args.output or f"papers/export.{ext}")
        out.parent.mkdir(parents=True,exist_ok=True)
        {"csv":export_csv,"bibtex":export_bibtex,"ris":export_ris}[args.format](rows,out)
        print(out)

if __name__=="__main__": main()
