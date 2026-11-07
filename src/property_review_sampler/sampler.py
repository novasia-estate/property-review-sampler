import hashlib
import json
from collections import Counter, defaultdict
from .scope import review_exclusions

def select(rows, budget, *, group="property_id", strata=("market", "language"), seed="20261106", must_review="must_review", exclude_groups=None):
    """Select whole property groups; budget is a hard row limit.

    Mandatory groups are included first. Then greedily cover as-yet uncovered
    joint strata, balancing selected group counts; SHA-256 breaks ties stably.
    This is purposive QA sampling, not probability sampling or a prevalence estimate.
    """
    if isinstance(budget, bool) or not isinstance(budget, int) or budget < 0:
        raise ValueError("budget must be a nonnegative integer")
    rows = list(rows)
    if len(rows) > 100000:
        raise ValueError("maximum 100000 rows")
    strata = tuple(strata)
    if not strata or len(set(strata)) != len(strata):
        raise ValueError("strata must be distinct fields")
    groups = defaultdict(list)
    seen = set()
    for r in rows:
        if not isinstance(r, dict): raise ValueError("each row must be an object")
        rid = r.get("row_id")
        if not isinstance(rid, str) or not rid.strip() or rid in seen:
            raise ValueError("unique nonempty string row_id required")
        seen.add(rid)
        gid = r.get(group)
        if not isinstance(gid, str) or not gid.strip(): raise ValueError("nonempty string group required")
        for field in strata:
            if not isinstance(r.get(field), str) or not r[field].strip(): raise ValueError("missing stratum: " + field)
        if must_review in r and not isinstance(r[must_review], bool): raise ValueError("must_review must be boolean")
        groups[gid].append(r)
    exclusions = review_exclusions(exclude_groups, groups)
    for gid in exclusions:
        if any(row.get(must_review, False) for row in groups[gid]):
            raise ValueError("cannot exclude a mandatory group: " + gid)
    excluded = [{"group": gid, "reason": exclusions[gid], "row_ids": sorted(row["row_id"] for row in groups[gid])} for gid in sorted(exclusions)]
    groups = {gid: members for gid, members in groups.items() if gid not in exclusions}
    cells = {g: set(tuple(r[f] for f in strata) for r in rs) for g, rs in groups.items()}
    rank = lambda g: (hashlib.sha256((str(seed)+"\0"+g).encode()).hexdigest(), g)
    chosen = []
    mandatory = sorted((g for g, rs in groups.items() if any(r.get(must_review, False) for r in rs)), key=rank)
    cost = sum(len(groups[g]) for g in mandatory)
    if cost > budget: raise ValueError(f"mandatory groups require {cost} rows, budget is {budget}")
    covered = Counter()
    reasons = {}
    def add(g, reason):
        chosen.append(g); reasons[g] = reason; covered.update(cells[g])
    for g in mandatory: add(g, "mandatory group")
    remaining = set(groups) - set(chosen)
    while remaining:
        fitting = [g for g in remaining if cost + len(groups[g]) <= budget]
        if not fitting: break
        g = min(fitting, key=lambda g: (-sum(c not in covered for c in cells[g]), sum(covered[c] for c in cells[g]), len(groups[g]), rank(g)))
        add(g, "coverage / balance / deterministic tie-break")
        cost += len(groups[g]); remaining.remove(g)
    all_cells = set().union(*cells.values()) if cells else set()
    selected = [dict(r) for g in chosen for r in sorted(groups[g], key=lambda r:r["row_id"])]
    report = {"schema_version":1, "seed":str(seed), "budget_rows":budget, "selected_rows":selected,
            "selected_groups":[{"group":g,"rows":len(groups[g]),"reason":reasons[g]} for g in chosen],
            "coverage":[{"stratum":dict(zip(strata,c)),"population_groups":sum(c in cs for cs in cells.values()),"selected_groups":covered[c]} for c in sorted(all_cells)],
            "uncovered_strata":[dict(zip(strata,c)) for c in sorted(all_cells-set(covered))],
            "unused_budget_rows":budget-cost,
            "population_sha256":hashlib.sha256(json.dumps(sorted(rows,key=lambda r:r["row_id"]),sort_keys=True,ensure_ascii=False,separators=(",",":")).encode()).hexdigest(),
            "limitation":"Purposive editorial QA sample; inclusion probabilities and unbiased prevalence estimates are not supplied."}

    if exclude_groups is not None:
        report.update(schema_version=2, excluded_groups=excluded,
                      population_rows=len(rows), eligible_rows=sum(len(members) for members in groups.values()))
    return report
