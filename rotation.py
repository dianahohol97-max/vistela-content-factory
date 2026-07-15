"""Rotation backlog for phone-reveal reels.

The backlog is the pool of every scene x product pair plus a JSON log of what
went out when. Each run it picks the pairs that have waited longest, while
respecting quarantines, and rotates the hook on repeats — so the feed stays
even and never shows the same pair (or the same scene) back-to-back.

Log shape (rotation_log.json):
  {"pairs": {"scene|product": {"last": "2026-07-14", "count": 2, "last_hook": 3}},
   "scenes": {"scene": "2026-07-14"}}
"""
import json
import os
import datetime as dt

LOG_FILE = "rotation_log.json"
QUARANTINE_PAIR_DAYS = 21     # a pair can't repeat within this window
QUARANTINE_SCENE_DAYS = 3     # a scene can't reappear within this window


def _load(root):
    p = os.path.join(root, LOG_FILE)
    if os.path.exists(p):
        try:
            return json.load(open(p))
        except Exception:
            pass
    return {"pairs": {}, "scenes": {}}


def _save(root, log):
    json.dump(log, open(os.path.join(root, LOG_FILE), "w"), indent=2, ensure_ascii=False)


def _days_since(iso, today):
    if not iso:
        return 10 ** 6
    return (today - dt.date.fromisoformat(iso)).days


def next_pairs(root, scenes, products, n, today=None):
    """Pick n (scene, product, hook_index) tuples and update the log. The caller
    maps hook_index to a product-type-specific hook list. `scenes` and
    `products` are file paths; identity is the basename."""
    today = today or dt.date.today()
    log = _load(root)
    pairs, scenes_log = log["pairs"], log["scenes"]
    sname = {s: os.path.basename(s) for s in scenes}
    pname = {p: os.path.basename(p) for p in products}
    all_pairs = [(s, p) for p in products for s in scenes]
    chosen = []

    for _ in range(n):
        picked_scenes = {sname[c[0]] for c in chosen}
        picked_products = {pname[c[1]] for c in chosen}

        def key(sp):
            return f"{sname[sp[0]]}|{pname[sp[1]]}"

        def usable(sp, strict=True):
            if sname[sp[0]] in picked_scenes:                 # not same scene twice in a batch
                return False
            if strict and pname[sp[1]] in picked_products:    # prefer a different product too
                return False
            rec = pairs.get(key(sp), {})
            pair_ok = _days_since(rec.get("last"), today) >= QUARANTINE_PAIR_DAYS
            scene_ok = _days_since(scenes_log.get(sname[sp[0]]), today) >= QUARANTINE_SCENE_DAYS
            return pair_ok and scene_ok

        pool = [sp for sp in all_pairs if usable(sp, strict=True)]
        if not pool:
            pool = [sp for sp in all_pairs if usable(sp, strict=False)]
        if not pool:
            pool = [sp for sp in all_pairs if sname[sp[0]] not in picked_scenes] or all_pairs

        def score(sp):
            rec = pairs.get(key(sp), {})
            return (rec.get("count", 0), rec.get("last") or "0000-00-00")   # never-used first, then oldest

        sp = sorted(pool, key=score)[0]
        rec = pairs.get(key(sp), {"count": 0, "last": None, "last_hook": -1})
        hook_i = (rec.get("last_hook", -1) + 1) % 1000        # rotate; caller does % len(hooks)
        chosen.append((sp[0], sp[1], hook_i))
        pairs[key(sp)] = {"last": today.isoformat(), "count": rec.get("count", 0) + 1, "last_hook": hook_i}
        scenes_log[sname[sp[0]]] = today.isoformat()

    _save(root, log)
    return chosen


def next_single(root, clips, hooks, prefix, today=None):
    """Pick the single clip that has waited longest (oldest-first) and rotate its
    hook. Used for un-paired reel types like Personalize-With-Me. Logs under
    'single:<prefix>'."""
    today = today or dt.date.today()
    log = _load(root)
    store = log.setdefault(f"single:{prefix}", {})
    cname = {c: os.path.basename(c) for c in clips}

    def score(c):
        rec = store.get(cname[c], {})
        return (rec.get("count", 0), rec.get("last") or "0000-00-00")

    clip = sorted(clips, key=score)[0]
    rec = store.get(cname[clip], {"count": 0, "last": None, "last_hook": -1})
    hook_i = (rec.get("last_hook", -1) + 1) % len(hooks)
    store[cname[clip]] = {"last": today.isoformat(), "count": rec.get("count", 0) + 1, "last_hook": hook_i}
    _save(root, log)
    return clip, hooks[hook_i]
