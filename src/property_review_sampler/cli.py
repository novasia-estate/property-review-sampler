import argparse, csv, json
from pathlib import Path
from .sampler import select

def main():
    p=argparse.ArgumentParser(description="Choose whole property groups for editorial QA; never splits language variants.")
    p.add_argument("input",type=Path);p.add_argument("--budget",type=int,required=True);p.add_argument("--out",type=Path,required=True)
    p.add_argument("--seed",default="20261106");p.add_argument("--group",default="property_id");p.add_argument("--strata",default="market,language")
    p.add_argument("--exclude-reviewed",type=Path,help="JSON object mapping already-reviewed property IDs to reasons")
    a=p.parse_args()
    try:
        rows=json.loads(a.input.read_text(encoding="utf-8"))
        if not isinstance(rows,list): raise ValueError("input must be a JSON array")
        exclusions=None
        if a.exclude_reviewed is not None:
            if a.exclude_reviewed.stat().st_size > 100000: raise ValueError("exclusion file exceeds 100KB")
            exclusions=json.loads(a.exclude_reviewed.read_text(encoding="utf-8"))
        result=select(rows,a.budget,exclude_groups=exclusions,group=a.group,strata=tuple(a.strata.split(",")),seed=a.seed)
        a.out.mkdir(parents=True,exist_ok=True)
        (a.out/"audit.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        fields=sorted(set().union(*(r.keys() for r in result["selected_rows"]))) if result["selected_rows"] else ["row_id"]
        with (a.out/"selected.csv").open("w",encoding="utf-8",newline="") as f:
            w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
            for row in result["selected_rows"]:
                # Protect spreadsheets from formula injection. JSON retains originals.
                w.writerow({k:("'"+v if isinstance(v,str) and v.lstrip().startswith(("=","+","-","@")) else v) for k,v in row.items()})
        print(f"Selected {len(result['selected_rows'])} rows in {len(result['selected_groups'])} groups; uncovered strata: {len(result['uncovered_strata'])}")
    except (OSError,ValueError,TypeError) as e:p.error(str(e))
if __name__=="__main__":main()
