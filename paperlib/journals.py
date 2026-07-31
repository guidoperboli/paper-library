from __future__ import annotations

MAP = {
    "transportation research part a: policy and practice": "TRA",
    "transportation research part b: methodological": "TRB",
    "transportation research part c: emerging technologies": "TRC",
    "transportation research part d: transport and environment": "TRD",
    "transportation research part e: logistics and transportation review": "TRE",
    "european journal of operational research": "EJOR",
    "computers & operations research": "COR",
    "expert systems with applications": "ESWA",
    "annals of operations research": "ANOR",
    "operations research": "OR",
    "management science": "MS",
    "transportation science": "TS",
    "omega": "Omega",
    "ieee transactions on intelligent transportation systems": "IEEE T-ITS",
}

def abbreviate(name: str) -> str:
    clean = " ".join((name or "").split())
    return MAP.get(clean.casefold(), clean or "Unknown Journal")
