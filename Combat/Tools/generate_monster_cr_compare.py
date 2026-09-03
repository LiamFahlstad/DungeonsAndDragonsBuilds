"""Regenerate Combat/Tools/monster_cr_compare.html.

Runs monster_cr_compare.py's implied-CR model (see that file for the full
explanation) over every *official* monster instead of a few named on a
command line, and writes a self-contained, sortable/filterable HTML table
with one row per monster: assigned CR, implied CR, delta (implied minus
assigned), and per-tier score.

Homebrew monsters are intentionally excluded -- this report only covers
the *official* monsters.py population the CR-tier distributions are fit
from (the same population monster_score.py/monster_cr_compare.py always
fit against, never score, when a homebrew monster is looked up).

Run from the repo root:
    python -m Combat.Tools.generate_monster_cr_compare
Writes Combat/Tools/monster_cr_compare.html
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from Combat.Tools.generate_monster_cr_distributions import cr_key, extract_all  # noqa: E402
from Combat.Tools.monster_cr_compare import build_continuous_stats, implied_cr  # noqa: E402
from Combat.Tools.monster_score import SCORED_ATTR_COUNT, build_stats, score_monster  # noqa: E402

OUTPUT_HTML = Path(__file__).resolve().parent / "monster_cr_compare.html"
PLACEHOLDER = "__MONSTER_CR_COMPARE_DATA_JSON__"


def build_rows(data):
    stats = build_stats(data["monsters"])
    attr_tiers = build_continuous_stats(data["monsters"])
    cr_order_nums = sorted({cr_key(cr) for cr in data["cr_order"]})

    rows = []
    for m in data["monsters"]:  # official only -- homebrew excluded by design
        assigned = cr_key(m["cr"])
        cr_val, clamped = implied_cr(m, attr_tiers, cr_order_nums)
        scores, k, _breakdown = score_monster(m, stats)
        rows.append({
            "name": m["name"],
            "cr": m["cr"],
            "crNum": assigned,
            "implied": cr_val,
            "clamped": clamped,
            "delta": (cr_val - assigned) if cr_val is not None else None,
            "score": scores["score"],
            "k": k,
        })
    return rows


HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Monster CR Comparison</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Public+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  :root {
    color-scheme: light;
    --surface:      #f8f9fb;
    --page:         #eef0f4;
    --card-border:  rgba(20,24,31,0.10);
    --ink:          #14181f;
    --ink-secondary:#545b66;
    --ink-muted:    #898f9c;
    --grid:         #e2e5ea;
    --focus-ring:   #2a78d6;
    --pos:          #2a78d6;
    --neg:          #e34948;
    --meter-track:  #dbe9fb;
  }
  @media (prefers-color-scheme: dark) {
    :root:not([data-theme="light"]) {
      color-scheme: dark;
      --surface:      #14171c;
      --page:         #0d0e11;
      --card-border:  rgba(242,244,247,0.10);
      --ink:          #f2f4f7;
      --ink-secondary:#b9bfc9;
      --ink-muted:    #7d838f;
      --grid:         #262b33;
      --focus-ring:   #6da7ec;
      --pos:          #3987e5;
      --neg:          #e66767;
      --meter-track:  #1f2c40;
    }
  }
  :root[data-theme="dark"] {
    color-scheme: dark;
    --surface:      #14171c;
    --page:         #0d0e11;
    --card-border:  rgba(242,244,247,0.10);
    --ink:          #f2f4f7;
    --ink-secondary:#b9bfc9;
    --ink-muted:    #7d838f;
    --grid:         #262b33;
    --focus-ring:   #6da7ec;
    --pos:          #3987e5;
    --neg:          #e66767;
    --meter-track:  #1f2c40;
  }

  * { box-sizing: border-box; }
  html, body { margin: 0; padding: 0; }
  body {
    background: var(--page);
    color: var(--ink);
    font-family: "Public Sans", system-ui, -apple-system, "Segoe UI", sans-serif;
    -webkit-font-smoothing: antialiased;
  }
  .wrap {
    max-width: 980px;
    margin: 0 auto;
    padding: 40px 24px 64px;
    display: flex;
    flex-direction: column;
    gap: 18px;
  }
  header h1 { font-size: 22px; margin: 0 0 6px; }
  header p { font-size: 13.5px; color: var(--ink-secondary); margin: 0; max-width: 68ch; line-height: 1.5; }
  header code { font-family: "JetBrains Mono", ui-monospace, monospace; font-size: 0.92em; }

  .controls {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    align-items: center;
  }
  .controls input[type="search"],
  .controls select {
    font-family: inherit;
    font-size: 13.5px;
    color: var(--ink);
    background: var(--surface);
    border: 1px solid var(--card-border);
    border-radius: 8px;
    padding: 8px 12px;
  }
  .controls input[type="search"] { min-width: 220px; flex: 1 1 220px; }
  .controls input[type="search"]:focus-visible,
  .controls select:focus-visible,
  table.cmp-table thead th:focus-visible {
    outline: 2px solid var(--focus-ring);
    outline-offset: 1px;
  }
  .count { font-size: 12px; color: var(--ink-muted); margin-left: auto; }

  .table-scroll {
    max-height: 78vh;
    overflow: auto;
    border: 1px solid var(--card-border);
    border-radius: 10px;
    background: var(--surface);
  }
  table.cmp-table {
    border-collapse: collapse;
    width: 100%;
    min-width: 620px;
    font-size: 13px;
  }
  table.cmp-table thead th {
    position: sticky;
    top: 0;
    background: var(--surface);
    color: var(--ink-muted);
    font-weight: 500;
    text-transform: uppercase;
    font-size: 10.5px;
    letter-spacing: 0.05em;
    text-align: left;
    padding: 9px 12px;
    border-bottom: 1px solid var(--card-border);
    cursor: pointer;
    user-select: none;
    white-space: nowrap;
  }
  table.cmp-table thead th.sorted { color: var(--ink); }
  table.cmp-table thead th .arrow { font-size: 9px; margin-left: 3px; opacity: 0.7; }
  table.cmp-table td {
    padding: 7px 12px;
    border-bottom: 1px solid var(--grid);
    vertical-align: middle;
  }
  table.cmp-table td.num {
    font-family: "JetBrains Mono", ui-monospace, monospace;
    font-variant-numeric: tabular-nums;
    text-align: right;
    white-space: nowrap;
  }
  table.cmp-table tbody tr:hover { background: var(--grid); }
  table.cmp-table .name-cell { font-weight: 600; }
  table.cmp-table .k-note { color: var(--ink-muted); font-weight: 400; font-size: 11px; }
  table.cmp-table .pos { color: var(--pos); }
  table.cmp-table .neg { color: var(--neg); }
  table.cmp-table .na { color: var(--ink-muted); }

  footer { font-size: 11.5px; color: var(--ink-muted); }
</style>
</head>
<body>
<div class="wrap">
  <header>
    <h1>Monster CR Comparison</h1>
    <p>
      Every official monster's <strong>implied CR</strong> -- the continuous CR at which its raw
      stats would be exactly average -- against its assigned CR, per
      <code>monster_cr_compare.py</code>'s model (fit from official <code>monsters.py</code> stat
      blocks only; homebrew is excluded here). <strong>Delta</strong> is implied minus assigned:
      positive means a monster is statistically stronger than its label suggests, negative means
      weaker. <strong>Score</strong> is the monster's percentile within its own assigned CR tier
      only (0.50 = average for that CR) -- unlike implied CR, it can't be compared across tiers.
      Click a column to sort.
    </p>
  </header>

  <div class="controls">
    <input type="search" id="search" placeholder="Filter by name...">
    <select id="cr-filter" aria-label="Filter by CR"></select>
    <span class="count" id="count"></span>
  </div>

  <div class="table-scroll">
    <table class="cmp-table" id="cmp-table">
      <thead>
        <tr>
          <th data-key="name" data-type="str">Name</th>
          <th data-key="crNum" data-type="num">CR</th>
          <th data-key="implied" data-type="num">Implied CR</th>
          <th data-key="delta" data-type="num">Delta</th>
          <th data-key="score" data-type="num">Score</th>
          <th data-key="k" data-type="num">Attrs</th>
        </tr>
      </thead>
      <tbody></tbody>
    </table>
  </div>

  <footer>Regenerate with <code>python -m Combat.Tools.generate_monster_cr_compare</code>.</footer>
</div>

<script id="monster-cmp-data" type="application/json">__MONSTER_CR_COMPARE_DATA_JSON__</script>
<script>
(function () {
  var PAYLOAD = JSON.parse(document.getElementById('monster-cmp-data').textContent);
  var ROWS = PAYLOAD.rows;
  var N_ATTRS = PAYLOAD.n_attrs;
  var CR_LABELS = PAYLOAD.cr_labels;

  var sortState = { key: 'crNum', dir: 'asc' };
  var filter = { query: '', cr: 'all' };

  function crLabel(cr) { return 'CR ' + cr; }

  function fmtImplied(r) {
    if (r.implied === null) return { text: 'n/a', cls: 'na' };
    var prefix = r.clamped === 'low' ? '≤' : (r.clamped === 'high' ? '≥' : '');
    return { text: prefix + r.implied.toFixed(2), cls: '' };
  }
  function fmtDelta(r) {
    if (r.delta === null) return { text: 'n/a', cls: 'na' };
    var cls = r.delta > 0.05 ? 'pos' : (r.delta < -0.05 ? 'neg' : '');
    var sign = r.delta > 0 ? '+' : '';
    return { text: sign + r.delta.toFixed(2), cls: cls };
  }

  function populateCrFilter() {
    var sel = document.getElementById('cr-filter');
    var opt = document.createElement('option');
    opt.value = 'all'; opt.textContent = 'All CRs';
    sel.appendChild(opt);
    CR_LABELS.forEach(function (cr) {
      var o = document.createElement('option');
      o.value = cr; o.textContent = crLabel(cr);
      sel.appendChild(o);
    });
    sel.addEventListener('change', function () { filter.cr = sel.value; render(); });
  }

  function applyFilter() {
    var q = filter.query.trim().toLowerCase();
    return ROWS.filter(function (r) {
      if (filter.cr !== 'all' && r.cr !== filter.cr) return false;
      if (q && r.name.toLowerCase().indexOf(q) === -1) return false;
      return true;
    });
  }

  function applySort(rows) {
    var key = sortState.key, dir = sortState.dir === 'asc' ? 1 : -1;
    return rows.slice().sort(function (a, b) {
      var av = a[key], bv = b[key];
      var aNull = av === null || av === undefined;
      var bNull = bv === null || bv === undefined;
      if (aNull && bNull) return 0;
      if (aNull) return 1;   // nulls always sort last, regardless of direction
      if (bNull) return -1;
      if (typeof av === 'string') return av.localeCompare(bv) * dir;
      return (av - bv) * dir;
    });
  }

  function updateHeaders() {
    Array.prototype.forEach.call(document.querySelectorAll('#cmp-table thead th'), function (th) {
      var key = th.getAttribute('data-key');
      th.classList.toggle('sorted', key === sortState.key);
      var arrow = th.querySelector('.arrow');
      if (arrow) arrow.remove();
      if (key === sortState.key) {
        var span = document.createElement('span');
        span.className = 'arrow';
        span.textContent = sortState.dir === 'asc' ? '▲' : '▼';
        th.appendChild(span);
      }
    });
  }

  function render() {
    var rows = applySort(applyFilter());
    var tbody = document.querySelector('#cmp-table tbody');
    tbody.innerHTML = '';
    var frag = document.createDocumentFragment();
    rows.forEach(function (r) {
      var tr = document.createElement('tr');

      var tdName = document.createElement('td');
      tdName.className = 'name-cell';
      tdName.textContent = r.name;
      tr.appendChild(tdName);

      var tdCr = document.createElement('td');
      tdCr.className = 'num';
      tdCr.textContent = 'CR ' + r.cr;
      tr.appendChild(tdCr);

      var implied = fmtImplied(r);
      var tdImplied = document.createElement('td');
      tdImplied.className = 'num ' + implied.cls;
      tdImplied.textContent = implied.text;
      tr.appendChild(tdImplied);

      var delta = fmtDelta(r);
      var tdDelta = document.createElement('td');
      tdDelta.className = 'num ' + delta.cls;
      tdDelta.textContent = delta.text;
      tr.appendChild(tdDelta);

      var tdScore = document.createElement('td');
      tdScore.className = 'num';
      tdScore.textContent = r.score.toFixed(2);
      tr.appendChild(tdScore);

      var tdK = document.createElement('td');
      tdK.className = 'num';
      var kSpan = document.createElement('span');
      kSpan.className = r.k < N_ATTRS ? 'k-note' : '';
      kSpan.textContent = r.k + '/' + N_ATTRS;
      tdK.appendChild(kSpan);
      tr.appendChild(tdK);

      frag.appendChild(tr);
    });
    tbody.appendChild(frag);
    document.getElementById('count').textContent = rows.length + ' of ' + ROWS.length + ' monsters';
    updateHeaders();
  }

  document.getElementById('search').addEventListener('input', function (e) {
    filter.query = e.target.value;
    render();
  });

  Array.prototype.forEach.call(document.querySelectorAll('#cmp-table thead th'), function (th) {
    th.setAttribute('tabindex', '0');
    th.addEventListener('click', function () {
      var key = th.getAttribute('data-key');
      if (sortState.key === key) {
        sortState.dir = sortState.dir === 'asc' ? 'desc' : 'asc';
      } else {
        sortState.key = key;
        sortState.dir = th.getAttribute('data-type') === 'str' ? 'asc' : 'desc';
      }
      render();
    });
    th.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); th.click(); }
    });
  });

  populateCrFilter();
  render();
})();
</script>
</body>
</html>
"""


def main() -> None:
    data, errors = extract_all()

    print(
        f"Extracted {len(data['monsters'])} official monsters "
        f"({len(data['cr_order'])} CR tiers)",
        file=sys.stderr,
    )
    if errors:
        print(f"{len(errors)} errors:", file=sys.stderr)
        for e in errors:
            print("  " + e, file=sys.stderr)

    rows = build_rows(data)
    payload = {
        "rows": rows,
        "n_attrs": SCORED_ATTR_COUNT,
        "cr_labels": data["cr_order"],
    }

    # Escape "</" so a monster name/data value can never prematurely close
    # the surrounding <script> tag.
    payload_json = json.dumps(payload, separators=(",", ":")).replace("</", "<\\/")
    output = HTML_TEMPLATE.replace(PLACEHOLDER, payload_json)
    OUTPUT_HTML.write_text(output, encoding="utf-8")
    print(f"Wrote {OUTPUT_HTML} ({len(output):,} bytes)", file=sys.stderr)


if __name__ == "__main__":
    main()
