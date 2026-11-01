"""DWM lab analyses (EDA, regression, decision tree, naive bayes, k-means, hierarchical, apriori)."""
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import linkage as sp_linkage, dendrogram
from sklearn.cluster import AgglomerativeClustering, KMeans
from sklearn.decomposition import PCA
from sklearn.feature_selection import mutual_info_classif
from sklearn.linear_model import LinearRegression
from sklearn.metrics import (accuracy_score, adjusted_rand_score, classification_report,
                             confusion_matrix, mean_absolute_error, mean_squared_error,
                             r2_score, silhouette_score)
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier, export_text

CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "Student_Social_Media_And_Mental_Health_Impact.csv"
NUM = ["Age", "Avg_Daily_Usage_Hours", "Daily_Unlocks", "Study_Hours",
       "Physical_Activity_Hours", "Sleep_Hours_Per_Night", "Mental_Health_Score"]
CAT = ["Gender", "Academic_Level", "Most_Used_Platform", "Purpose_Of_Use"]
TARGET = "Stress_Level"
ORDER = ["Low", "Medium", "High", "Very High"]

_df = None


def load(path=None):
    global _df
    _df = pd.read_csv(path or CSV_PATH)
    return _df


def df():
    return _df if _df is not None else load()


def clean():
    d = df().drop_duplicates().dropna().copy()
    return d


def features(d):
    """Numeric features (minus mental score handled by caller) + one-hot categoricals."""
    return pd.get_dummies(d[NUM + CAT], columns=CAT, dtype=float)


def hist(s, bins=12):
    c, e = np.histogram(s, bins=bins)
    return {"counts": c.tolist(), "edges": [round(float(x), 2) for x in e]}


# 1 ─ Preprocessing + EDA
def eda():
    raw = df()
    d = clean()
    desc = d[NUM].describe().round(2)
    corr = d[NUM].corr().round(2)
    return {
        "shape_raw": list(raw.shape), "shape_clean": list(d.shape),
        "missing": int(raw.isna().sum().sum()), "duplicates": int(raw.duplicated().sum()),
        "dtypes": {c: str(t) for c, t in raw.dtypes.items()},
        "describe": {"columns": list(desc.columns), "rows": list(desc.index),
                     "values": desc.values.tolist()},
        "corr": {"labels": NUM, "values": corr.values.tolist()},
        "hists": {c: hist(d[c]) for c in NUM},
        "counts": {c: d[c].value_counts().head(10).to_dict() for c in CAT + [TARGET]},
        "by_platform": d.groupby("Most_Used_Platform")[["Avg_Daily_Usage_Hours", "Mental_Health_Score",
                       "Sleep_Hours_Per_Night"]].mean().round(2).sort_values("Mental_Health_Score")
                       .reset_index().to_dict("records"),
        "by_stress": d.groupby(TARGET)[["Avg_Daily_Usage_Hours", "Mental_Health_Score",
                      "Sleep_Hours_Per_Night"]].mean().round(2).reindex(ORDER).reset_index().to_dict("records"),
    }


# 2 ─ Linear regression: predict Mental_Health_Score from the other columns
def regression(target="Mental_Health_Score", x="Avg_Daily_Usage_Hours", test_size=0.2):
    target = "Mental_Health_Score"
    d = clean()
    if x not in NUM or x == target:
        raise ValueError("x must be a numeric column other than the target")
    y = d[target]
    out = {"target": target}
    Xs = d[[x]]
    tr, te, ytr, yte = train_test_split(Xs, y, test_size=test_size, random_state=42)
    m = LinearRegression().fit(tr, ytr)
    p = m.predict(te)
    idx = np.random.RandomState(1).choice(len(d), min(300, len(d)), replace=False)
    lo, hi = float(Xs[x].min()), float(Xs[x].max())
    out["simple"] = {"x": x, "target": target, "coef": float(m.coef_[0]), "intercept": float(m.intercept_),
                     "r2": r2_score(yte, p), "mae": mean_absolute_error(yte, p),
                     "rmse": float(np.sqrt(mean_squared_error(yte, p))),
                     "xmin": lo, "xmax": hi, "xmean": float(Xs[x].mean()),
                     "points": d.iloc[idx][[x, target]].values.tolist(),
                     "line": [[lo, float(m.intercept_ + m.coef_[0] * lo)], [hi, float(m.intercept_ + m.coef_[0] * hi)]]}
    Xm = features(d).drop(columns=[target])
    tr, te, ytr, yte = train_test_split(Xm, y, test_size=test_size, random_state=42)
    m2 = LinearRegression().fit(tr, ytr)
    p2 = m2.predict(te)
    sc = StandardScaler().fit(tr)
    ms = LinearRegression().fit(sc.transform(tr), ytr)
    coefs = sorted(zip(Xm.columns, ms.coef_), key=lambda t: -abs(t[1]))[:12]
    out["multiple"] = {"r2": r2_score(yte, p2), "mae": mean_absolute_error(yte, p2),
                       "rmse": float(np.sqrt(mean_squared_error(yte, p2))), "n_features": int(Xm.shape[1]),
                       "coefs": [[n, float(c)] for n, c in coefs],
                       "actual_vs_pred": [[float(a), float(b)] for a, b in zip(yte.values[:300], p2[:300])]}
    cor = d[NUM].corr()[target].drop(target)
    out["corr"] = [[k, round(float(v), 3)] for k, v in cor.sort_values(key=abs, ascending=False).items()]
    out["inputs"] = [c for c in NUM if c != target]
    return out


def _clf_data():
    d = clean()
    X = features(d)
    y = d[TARGET]
    return X, y, train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)


def _clf_result(model, Xte, yte, pred):
    labels = [l for l in ORDER if l in set(yte)]
    rep = classification_report(yte, pred, labels=labels, output_dict=True, zero_division=0)
    return {"accuracy": accuracy_score(yte, pred), "labels": labels,
            "confusion": confusion_matrix(yte, pred, labels=labels).tolist(),
            "report": {l: {k: round(v, 3) for k, v in rep[l].items()} for l in labels}}


# 3 ─ Decision tree + mutual information
def tree(max_depth=4):
    X, y, (Xtr, Xte, ytr, yte) = _clf_data()
    m = DecisionTreeClassifier(max_depth=max_depth, random_state=42).fit(Xtr, ytr)
    r = _clf_result(m, Xte, yte, m.predict(Xte))
    mi = mutual_info_classif(X, y, random_state=42)
    r["mutual_info"] = sorted([[c, float(v)] for c, v in zip(X.columns, mi)], key=lambda t: -t[1])[:12]
    r["importances"] = sorted([[c, float(v)] for c, v in zip(X.columns, m.feature_importances_) if v > 0],
                              key=lambda t: -t[1])[:12]
    r["rules"] = export_text(m, feature_names=list(X.columns), max_depth=3)
    r["depth"] = int(m.get_depth()); r["leaves"] = int(m.get_n_leaves())
    r["train_accuracy"] = float(m.score(Xtr, ytr))
    return r


# 4 ─ Naive Bayes
def naive_bayes():
    X, y, (Xtr, Xte, ytr, yte) = _clf_data()
    m = GaussianNB().fit(Xtr, ytr)
    r = _clf_result(m, Xte, yte, m.predict(Xte))
    r["priors"] = {str(c): float(p) for c, p in zip(m.classes_, m.class_prior_)}
    return r


def _cluster_X(sample=None):
    d = clean()
    if sample and len(d) > sample:
        d = d.sample(sample, random_state=42)
    X = StandardScaler().fit_transform(features(d))
    return d, X


def _profile(d, labels):
    t = d.assign(cluster=labels)
    g = t.groupby("cluster")[NUM].mean().round(2)
    g.insert(0, "size", t.groupby("cluster").size())
    g["top_stress"] = t.groupby("cluster")[TARGET].agg(lambda s: s.mode().iat[0])
    return g.reset_index().to_dict("records")


def _pca_points(X, labels, n=600):
    xy = PCA(2, random_state=42).fit_transform(X)
    idx = np.random.RandomState(0).choice(len(X), min(n, len(X)), replace=False)
    return [[float(xy[i, 0]), float(xy[i, 1]), int(labels[i])] for i in idx]


_ELBOW_CACHE = None

# 5 ─ K-Means
def kmeans(k=3):
    global _ELBOW_CACHE
    d, X = _cluster_X()
    if _ELBOW_CACHE is None:
        elbow = []
        for kk in range(2, 9):
            km_e = KMeans(kk, n_init=3, random_state=42).fit(X)
            elbow.append({"k": kk, "inertia": float(km_e.inertia_),
                          "silhouette": float(silhouette_score(X, km_e.labels_, sample_size=1000, random_state=42))})
        _ELBOW_CACHE = elbow
    else:
        elbow = _ELBOW_CACHE
    km = KMeans(k, n_init=5, random_state=42).fit(X)
    prof = _profile(d, km.labels_)
    return {"k": k, "elbow": elbow, "inertia": float(km.inertia_),
            "silhouette": float(silhouette_score(X, km.labels_, sample_size=1000, random_state=42)),
            "profile": prof, "profiles": prof, "clusters": prof, "points": _pca_points(X, km.labels_)}


# 6 ─ Hierarchical clustering
def hierarchical(k=3, method="ward", sample=5000):
    if method not in {"ward", "complete", "average", "single"}:
        raise ValueError("bad linkage")
    d, X = _cluster_X(sample=sample if (sample and sample < 5000) else None)
    ag = AgglomerativeClustering(n_clusters=k, linkage=method).fit(X)
    km = KMeans(k, n_init=10, random_state=42).fit(X)
    dn = dendrogram(sp_linkage(X, method=method), truncate_mode="lastp", p=24, no_plot=True)
    prof = _profile(d, ag.labels_)
    return {"k": k, "method": method, "n": len(d), "silhouette": float(silhouette_score(X, ag.labels_)),
            "ari_vs_kmeans": float(adjusted_rand_score(km.labels_, ag.labels_)),
            "profile": prof, "profiles": prof, "clusters": prof, "points": _pca_points(X, ag.labels_),
            "dendro": {"icoord": dn["icoord"], "dcoord": dn["dcoord"]}}


# 7 ─ Apriori association rules
def apriori_rules(min_support=0.1, min_confidence=0.6, top=25):
    from mlxtend.frequent_patterns import apriori, association_rules
    d = clean()
    items = d[CAT + [TARGET]].astype(str).apply(lambda s: s.name + "=" + s)
    for c in ["Avg_Daily_Usage_Hours", "Sleep_Hours_Per_Night", "Mental_Health_Score", "Study_Hours"]:
        items[c] = c + "=" + pd.qcut(d[c], 3, labels=["Low", "Mid", "High"], duplicates="drop").astype(str)
    onehot = pd.get_dummies(items.stack()).groupby(level=0).max().astype(bool)
    fi = apriori(onehot, min_support=min_support, use_colnames=True)
    if fi.empty:
        return {"n_transactions": len(d), "n_itemsets": 0, "n_rules": 0, "rules": [], "itemsets": []}
    rules = association_rules(fi, metric="confidence", min_threshold=min_confidence)
    rules = rules.sort_values("lift", ascending=False).head(top)
    fs = lambda s: " & ".join(sorted(s))
    return {"n_transactions": len(d), "n_itemsets": len(fi), "n_rules": len(rules),
            "itemsets": [{"items": fs(r["itemsets"]), "support": round(float(r["support"]), 3)}
                         for _, r in fi.sort_values("support", ascending=False).head(10).iterrows()],
            "rules": [{"if": fs(r["antecedents"]), "then": fs(r["consequents"]),
                       "antecedents": list(r["antecedents"]), "consequents": list(r["consequents"]),
                       "antecedent_str": fs(r["antecedents"]), "consequent_str": fs(r["consequents"]),
                       "support": round(float(r["support"]), 3), "confidence": round(float(r["confidence"]), 3),
                       "lift": round(float(r["lift"]), 3)} for _, r in rules.iterrows()]}


# 2 ─ OLAP, OLTP and warehouse schemas
def _star():
    d = clean().reset_index(drop=True)
    d.insert(0, "student_id", d.index + 1)
    def dim(cols, key):
        t = d[cols].drop_duplicates().reset_index(drop=True)
        t.insert(0, key, t.index + 1)
        return t
    dims = {"Dim_Student": d[["student_id", "Age", "Gender", "Academic_Level"]],
            "Dim_Platform": dim(["Most_Used_Platform"], "platform_id"),
            "Dim_Purpose": dim(["Purpose_Of_Use"], "purpose_id"),
            "Dim_Country": dim(["Country"], "country_id"),
            "Dim_Stress": dim([TARGET], "stress_id")}
    fact = d.merge(dims["Dim_Platform"]).merge(dims["Dim_Purpose"]).merge(dims["Dim_Country"]).merge(dims["Dim_Stress"])
    return d, dims, fact


def schema():
    d, dims, fact = _star()
    def t(name, df_, pk=None, fks=()):
        return {"name": name, "pk": pk, "fks": list(fks), "columns": list(df_.columns), "rows": len(df_),
                "sample": df_.head(3).values.tolist()}
    f1 = fact[["student_id", "platform_id", "purpose_id", "country_id", "stress_id",
               "Avg_Daily_Usage_Hours", "Daily_Unlocks", "Mental_Health_Score"]]
    f2 = fact[["student_id", "country_id", "Study_Hours", "Physical_Activity_Hours", "Sleep_Hours_Per_Night"]]
    star_dims = [t(n, v, v.columns[0]) for n, v in dims.items()]
    gender = pd.DataFrame({"gender_id": [1, 2], "Gender": sorted(d.Gender.unique())})
    lvl = pd.DataFrame({"level_id": range(1, d.Academic_Level.nunique() + 1), "Academic_Level": sorted(d.Academic_Level.unique())})
    stu = d[["student_id", "Age"]].assign(gender_id=d.Gender.map(dict(zip(gender.Gender, gender.gender_id))),
                                         level_id=d.Academic_Level.map(dict(zip(lvl.Academic_Level, lvl.level_id))))
    snow_dims = [t("Dim_Student", stu, "student_id", ["gender_id", "level_id"]), t("Dim_Gender", gender, "gender_id"),
                 t("Dim_AcademicLevel", lvl, "level_id")] + [x for x in star_dims if x["name"] != "Dim_Student"]
    return {"star": {"fact": [t("Fact_Usage", f1, None, ["student_id", "platform_id", "purpose_id", "country_id", "stress_id"])],
                     "dims": star_dims,
                     "note": "One fact table joined directly to denormalized dimensions. Fewest joins, fastest queries."},
            "snowflake": {"fact": [t("Fact_Usage", f1, None, ["student_id", "platform_id", "purpose_id", "country_id", "stress_id"])],
                          "dims": snow_dims,
                          "note": "Dim_Student is normalized into Dim_Gender and Dim_AcademicLevel. Less redundancy, more joins."},
            "constellation": {"fact": [t("Fact_Usage", f1, None, ["student_id", "platform_id", "purpose_id", "country_id", "stress_id"]),
                                       t("Fact_Lifestyle", f2, None, ["student_id", "country_id"])],
                              "dims": star_dims,
                              "note": "Two fact tables (usage, lifestyle) share Dim_Student and Dim_Country."}}


MEASURES = ["Mental_Health_Score", "Avg_Daily_Usage_Hours", "Sleep_Hours_Per_Night", "Study_Hours"]
DIMS = ["Gender", "Academic_Level", "Most_Used_Platform", "Purpose_Of_Use", "Stress_Level"]


def olap(op="rollup", measure="Mental_Health_Score", sdim="Gender", sval="Female", levels="", purposes="",
         prow="Most_Used_Platform", pcol="Stress_Level"):
    if measure not in MEASURES:
        raise ValueError("bad measure")
    d = clean()
    agg = lambda g: g[measure].agg(["count", "mean"]).round(2).rename(columns={"count": "students", "mean": "avg_" + measure})
    def out(title, note, tab):
        tab = tab.reset_index()
        rows = [[None if isinstance(v, float) and v != v else v for v in r] for r in tab.values.tolist()]
        return {"title": title, "note": note, "columns": list(tab.columns), "rows": rows}
    if op == "drilldown":
        g = d.groupby(["Academic_Level", "Most_Used_Platform", "Purpose_Of_Use"])
        return out("Drill-down: Level → Platform → Purpose", "Moves from summary to detail by adding dimension levels. Top 40 rows by students.",
                   agg(g).sort_values("students", ascending=False).head(40))
    if op == "rollup":
        a = agg(d.groupby(["Academic_Level", "Most_Used_Platform"])).reset_index()
        b = agg(d.groupby("Academic_Level")).reset_index().assign(Most_Used_Platform="(all)")
        c = pd.DataFrame([{"Academic_Level": "(all)", "Most_Used_Platform": "(all)", "students": len(d),
                           "avg_" + measure: round(d[measure].mean(), 2)}])
        return out("Roll-up: Platform → Level → Grand total", "Aggregates upward along the hierarchy, from detail to totals.",
                   pd.concat([a, b, c]).set_index("Academic_Level"))
    if op == "slice":
        if sdim not in DIMS:
            raise ValueError("bad dimension")
        if sval not in set(d[sdim].astype(str)):
            sval = sorted(d[sdim].astype(str).unique())[0]
        s = d[d[sdim].astype(str) == sval]
        other_dims = [x for x in ["Most_Used_Platform", "Academic_Level", "Stress_Level"] if x != sdim][:2]
        return out(f"Slice: {sdim} = {sval}", f"Fixes one dimension ({sdim}) to '{sval}'. Shown grouped by {', '.join(other_dims)}.",
                   agg(s.groupby(other_dims)).sort_values("students", ascending=False))
    if op == "dice":
        L = [x for x in levels.split(",") if x] or ["Undergraduate", "Graduate"]
        P = [x for x in purposes.split(",") if x] or ["Education", "Networking"]
        s = d[d.Academic_Level.isin(L) & d.Purpose_Of_Use.isin(P)]
        return out(f"Dice: Level in {L} AND Purpose in {P}", "Selects values on two or more dimensions at once (sub-cube).",
                   agg(s.groupby(["Academic_Level", "Purpose_Of_Use", "Most_Used_Platform"])).sort_values("students", ascending=False))
    if op == "pivot":
        r = prow if prow in DIMS else "Most_Used_Platform"
        c = pcol if pcol in DIMS and pcol != r else ("Stress_Level" if r != "Stress_Level" else "Academic_Level")
        p = d.pivot_table(index=r, columns=c, values=measure, aggfunc="mean").round(2)
        if c == TARGET:
            p = p.reindex(columns=[col for col in ORDER if col in p.columns])
        return out(f"Pivot: {r} (rows) × {c} (columns), avg {measure}", "Rotates the axes to view the same data from another angle.", p)
    raise ValueError("unknown op")


# Graph builder + metadata for the UI
def meta():
    d = clean()
    vals = {c: (ORDER if c == TARGET else sorted(d[c].unique().tolist())) for c in CAT + [TARGET] + ["Country"]}
    vals["Age"] = sorted([int(a) for a in d["Age"].unique()])
    vals.update({b: BAND for b in ["Usage_Band", "Sleep_Band", "Study_Band"]})
    return {
        "numeric": NUM, "categorical": CAT + [TARGET], "dims": CUBE_DIMS,
        "olap_dims": OLAP_DIMS, "olap_measures": OLAP_MEASURES, "values": vals
    }


def chart(x, y=None, agg="mean", hue=None):
    d = clean()
    allc = NUM + CAT + [TARGET]
    if x not in allc or (hue and hue not in CAT + [TARGET]) or agg not in {"mean", "sum", "median", "count"}:
        raise ValueError("bad chart request")
    if agg != "count" and y not in NUM:
        raise ValueError("y must be numeric")
    s = d[x]
    if x in NUM and s.nunique() > 12:
        b = pd.cut(s, 10)
        d = d.assign(_x=b.map(lambda iv: f"{iv.mid:.1f}"))
        order = [f"{iv.mid:.1f}" for iv in b.cat.categories]
    else:
        d = d.assign(_x=s.astype(str))
        order = [str(v) for v in (ORDER if x == TARGET else sorted(s.unique()))]
    keys = ["_x"] + ([hue] if hue else [])
    g = d.groupby(keys, observed=True)
    r = g.size() if agg == "count" else g[y].agg(agg)
    r = r.round(3)
    labels = [o for o in order if o in set(d["_x"])]
    if hue:
        t = r.unstack(hue).reindex(labels)
        series = [{"name": str(c), "values": [None if pd.isna(v) else float(v) for v in t[c]]} for c in t.columns]
    else:
        series = [{"name": agg if agg == "count" else f"{agg} {y}", "values": [float(r.get(o, 0)) for o in labels]}]
    return {"labels": labels, "series": series}


# 3D OLAP cube: any 3 feature dimensions, "All" = rolled up
BAND = ["Low", "Mid", "High"]
CUBE_DIMS = ["Academic_Level", "Most_Used_Platform", "Purpose_Of_Use", "Stress_Level", "Gender",
             "Usage_Band", "Sleep_Band", "Study_Band", "Country"]
DIM_ORDER = {"Academic_Level": ["High School", "Undergraduate", "Graduate"], "Stress_Level": ORDER,
             "Usage_Band": BAND, "Sleep_Band": BAND, "Study_Band": BAND}


def _frame():
    d = clean().copy()
    for col, src in [("Usage_Band", "Avg_Daily_Usage_Hours"), ("Sleep_Band", "Sleep_Hours_Per_Night"),
                     ("Study_Band", "Study_Hours")]:
        d[col] = pd.qcut(d[src], 3, labels=BAND).astype(str)
    return d


def cube(x="Academic_Level", y="Most_Used_Platform", z="Stress_Level", measure="Mental_Health_Score",
         agg="mean", fdim="none", fval="", dice_dims="", dice_vals=""):
    if measure not in NUM:
        raise ValueError("bad measure")
    dims = [x, y, z]
    used = [a for a in dims if a != "All"]
    if any(a not in CUBE_DIMS for a in used) or len(set(used)) != len(used):
        raise ValueError("pick different dimensions for each axis")
    d = _frame()
    if fdim not in ("none", ""):
        if fdim in d.columns:
            if fval:
                d = d[d[fdim].astype(str) == str(fval)].copy()
            if d.empty:
                raise ValueError("no rows for that slice")
    if dice_dims and dice_vals:
        dims_list = [c.strip() for c in dice_dims.split(",") if c.strip()]
        vals_groups = [g.split(",") for g in dice_vals.split("|")]
        for dim, vals in zip(dims_list, vals_groups):
            if dim in d.columns:
                valid_vals = [v.strip() for v in vals if v.strip()]
                if valid_vals:
                    d = d[d[dim].astype(str).isin(valid_vals)].copy()
    if d.empty:
        raise ValueError("no rows match current filters")
    axes, keys = [], []
    for i, a in enumerate(dims):
        col = f"_a{i}"
        d[col] = "All" if a == "All" else d[a].astype(str)
        present = set(d[col])
        axes.append({"dim": a, "labels": [v for v in DIM_ORDER.get(a, sorted(present)) if v in present]})
        keys.append(col)
    agg_map = {"mean": "mean", "sum": "sum", "median": "median", "min": "min", "max": "max", "count": "count"}
    agg_op = agg_map.get(agg, "mean")
    if agg_op == "count":
        g = d.groupby(keys)[measure].agg(val="count", count="count")
    else:
        g = d.groupby(keys)[measure].agg(val=agg_op, count="count")
    cells = []
    for idx, row in g.iterrows():
        i, j, k = [axes[n]["labels"].index(idx[n]) for n in range(3)]
        cells.append({
            "i": i, "j": j, "k": k,
            "x": str(idx[0]), "y": str(idx[1]), "z": str(idx[2]),
            "value": round(float(row["val"]), 2), "count": int(row["count"])
        })
    vals = [c["value"] for c in cells]
    overall_val = round(float(d[measure].agg("count" if agg_op == "count" else agg_op)), 2)
    return {
        "axes": axes, "cells": cells, "measure": measure, "agg": agg_op,
        "vmin": min(vals) if vals else 0, "vmax": max(vals) if vals else 0,
        "total": len(d), "overall": overall_val
    }


# ───────────── Lab 2: 2D OLAP Explorer ─────────────
OLAP_DIMS = ["Country", "Academic_Level", "Most_Used_Platform", "Purpose_Of_Use", "Stress_Level", "Gender", "Age"]
OLAP_MEASURES = ["Mental_Health_Score", "Avg_Daily_Usage_Hours", "Daily_Unlocks", "Study_Hours", "Physical_Activity_Hours", "Sleep_Hours_Per_Night"]

def olap_explorer(op="Explore", x="Country", y="Most_Used_Platform", z="Stress_Level",
                  measure="Mental_Health_Score", agg="Average", sdim="none", sval="",
                  dice_filters="", across_dim="Academic_Level"):
    d = clean()
    if measure not in NUM:
        measure = "Mental_Health_Score"
    
    agg_dict = {"Average": "mean", "Sum": "sum", "Count": "count", "Minimum": "min", "Maximum": "max"}
    agg_func = agg_dict.get(agg, "mean")
    
    if x not in d.columns:
        x = "Country"
    if y not in d.columns or y == x:
        y = next((c for c in ["Most_Used_Platform", "Academic_Level", "Stress_Level", "Purpose_Of_Use", "Gender"] if c != x), "Most_Used_Platform")
    if z not in d.columns or z in (x, y):
        z = next((c for c in ["Stress_Level", "Academic_Level", "Gender", "Purpose_Of_Use", "Country"] if c not in (x, y)), "Stress_Level")
    
    dims = [x, y, z]
    
    active_filters = []
    
    # 1. Slice
    if op == "Slice" and sdim in d.columns and sval:
        d = d[d[sdim].astype(str) == str(sval)].copy()
        active_filters.append(f"{sdim} = '{sval}'")
    
    # 2. Dice
    if op == "Dice":
        if dice_filters:
            for part in dice_filters.split("|"):
                if ":" in part:
                    f_col, f_vals = part.split(":", 1)
                    f_col = f_col.strip()
                    val_list = [v.strip() for v in f_vals.split(",") if v.strip()]
                    if f_col in d.columns and val_list:
                        d = d[d[f_col].astype(str).isin(val_list)].copy()
                        active_filters.append(f"{f_col} IN ({', '.join(val_list)})")
        else:
            d = d[d["Academic_Level"].isin(["Undergraduate", "Graduate"]) & d["Purpose_Of_Use"].isin(["Education", "Networking"])].copy()
            active_filters.append("Academic_Level IN (Undergraduate, Graduate)")
            active_filters.append("Purpose_Of_Use IN (Education, Networking)")

    # 3. Drill-across
    if op == "Drill-across":
        adim = across_dim if across_dim in d.columns else "Academic_Level"
        g_usage = d.groupby(adim).agg(
            students=("Age", "size"),
            avg_usage_hrs=("Avg_Daily_Usage_Hours", "mean"),
            avg_unlocks=("Daily_Unlocks", "mean")
        ).round(2)
        g_wellbeing = d.groupby(adim).agg(
            avg_sleep_hrs=("Sleep_Hours_Per_Night", "mean"),
            avg_mental_score=("Mental_Health_Score", "mean"),
            avg_study_hrs=("Study_Hours", "mean")
        ).round(2)
        t = g_usage.join(g_wellbeing).reset_index()
        columns = [adim, "Students", "Avg Daily Usage (Hrs)", "Daily Unlocks", "Avg Sleep (Hrs)", "Avg Mental Health Score", "Avg Study (Hrs)"]
        t.columns = columns
        
        chart_labels = t[adim].astype(str).tolist()
        chart_series = [
            {"name": "Avg Daily Usage Hrs (Fact_Usage)", "values": t["Avg Daily Usage (Hrs)"].tolist()},
            {"name": "Avg Sleep Hrs (Fact_Wellbeing)", "values": t["Avg Sleep (Hrs)"].tolist()},
            {"name": "Avg Study Hrs (Fact_Wellbeing)", "values": t["Avg Study (Hrs)"].tolist()},
            {"name": "Avg Mental Health Score (Fact_Usage)", "values": t["Avg Mental Health Score"].tolist()}
        ]
        
        explanation = f"Drill-across is active across shared conformed dimension '{adim}'. Comparing Fact_Usage (screen time & unlocks) and Fact_Wellbeing (sleep, study hours & mental health score) across {len(t)} {adim} cohorts representing {len(d):,} students."
        
        return {
            "op": op,
            "columns": columns,
            "rows": t.values.tolist(),
            "chart": {"labels": chart_labels, "series": chart_series},
            "total_students": len(d),
            "explanation": explanation,
            "active_filters": active_filters
        }

    # 4. Roll-up
    if op == "Roll-up":
        g_detail = d.groupby([x, y])[measure].agg(["count", agg_func]).round(2).reset_index()
        g_detail.columns = [x, y, "Students", f"{agg} {measure}"]
        
        g_summary = d.groupby(x)[measure].agg(["count", agg_func]).round(2).reset_index()
        g_summary[y] = "(All / Rolled Up)"
        g_summary = g_summary[[x, y, "count", agg_func]]
        g_summary.columns = [x, y, "Students", f"{agg} {measure}"]
        
        tot_val = round(float(d[measure].agg(agg_func)), 2)
        g_total = pd.DataFrame([{x: "(Grand Total)", y: "(All)", "Students": len(d), f"{agg} {measure}": tot_val}])
        
        res = pd.concat([g_detail, g_summary, g_total], ignore_index=True)
        columns = [x, y, f"{agg} {measure}", "Students"]
        res = res[columns]
        
        g_sum_top = g_summary[g_summary[x] != "(Grand Total)"].sort_values("Students", ascending=False).head(10)
        chart_labels = g_sum_top[x].astype(str).tolist()
        chart_series = [{"name": f"{agg} {measure} (Rolled-up)", "values": g_sum_top[f"{agg} {measure}"].tolist()}]
        
        explanation = f"Roll-up aggregation performed: Aggregated from detailed level ({x} × {y}) to summary level ({x}) and Grand Total. Displays {agg.lower()} {measure.replace('_', ' ')} across {len(d):,} students."
        
        return {
            "op": op,
            "columns": columns,
            "rows": res.values.tolist(),
            "chart": {"labels": chart_labels, "series": chart_series},
            "total_students": len(d),
            "explanation": explanation,
            "active_filters": active_filters,
            "rollup_path": f"{y} (Detail) → {x} (Summary) → Grand Total"
        }

    # 5. Drill-down
    if op == "Drill-down":
        g = d.groupby([x, y, z])[measure].agg(["count", agg_func]).round(2).reset_index()
        columns = [x, y, z, f"{agg} {measure}", "Students"]
        g.columns = columns
        g = g.sort_values("Students", ascending=False)
        
        top12 = g.head(12)
        chart_labels = [f"{r[x]} · {r[y]}" for _, r in top12.iterrows()]
        chart_series = [{"name": f"{agg} {measure}", "values": top12[f"{agg} {measure}"].tolist()}]
        
        explanation = f"Drill-down expansion performed: Expanded higher-level summaries into granular multi-dimensional intersections ({x} × {y} × {z}). Discovered {len(g)} distinct subgroup combinations across {len(d):,} students."
        
        return {
            "op": op,
            "columns": columns,
            "rows": g.head(60).values.tolist(),
            "chart": {"labels": chart_labels, "series": chart_series},
            "total_students": len(d),
            "explanation": explanation,
            "active_filters": active_filters
        }

    # 6. Pivot
    if op == "Pivot":
        pv = d.pivot_table(index=x, columns=y, values=measure, aggfunc=agg_func).round(2).reset_index()
        columns = [x] + [str(c) for c in pv.columns[1:]]
        pv.columns = columns
        
        chart_labels = pv[x].head(10).astype(str).tolist()
        chart_series = [{"name": str(c), "values": [None if pd.isna(v) else float(v) for v in pv[c].head(10)]} for c in columns[1:6]]
        
        explanation = f"Pivot rearrangement applied: Rotated multidimensional axes placing '{x}' on horizontal rows and '{y}' across vertical series columns. Evaluates cross-tabulation of {agg.lower()} {measure.replace('_', ' ')}."
        
        pv_clean = pv.where(pd.notnull(pv), None)
        return {
            "op": op,
            "columns": columns,
            "rows": pv_clean.values.tolist(),
            "chart": {"labels": chart_labels, "series": chart_series},
            "total_students": len(d),
            "explanation": explanation,
            "active_filters": active_filters
        }

    # 7. Explore & Slice & Dice
    g = d.groupby([x, y, z])[measure].agg(students="count", val=agg_func).round(2).reset_index()
    columns = [x, y, z, f"{agg} {measure}", "Students"]
    g.columns = columns
    g = g.sort_values("Students", ascending=False)
    
    top_x = g[x].unique()[:8].tolist()
    unique_z = g[z].unique()[:6].tolist()
    
    chart_series = []
    for zv in unique_z:
        sub = g[g[z] == zv]
        vals = []
        for xv in top_x:
            match = sub[sub[x] == xv]
            vals.append(float(match[f"{agg} {measure}"].mean().round(2)) if not match.empty else None)
        chart_series.append({"name": str(zv), "values": vals})
        
    chart_labels = [str(xv) for xv in top_x]
    
    if op == "Slice":
        f_name = active_filters[0] if active_filters else f"{sdim} = '{sval}'"
        explanation = f"Slice is applied to {f_name}. The 2D visualization displays {agg.lower()} {measure.replace('_', ' ')} for each {x} × {y} × {z} combination among students matching this slice ({len(d):,} student records)."
    elif op == "Dice":
        f_desc = " AND ".join(active_filters) if active_filters else "Academic_Level & Purpose_Of_Use subsets"
        explanation = f"Dice filters applied: {f_desc}. The 2D analytical visualization isolates {len(d):,} student records and displays {agg.lower()} {measure.replace('_', ' ')} across {len(g)} combinations."
    else:
        explanation = f"The analysis currently compares {x} × {y} × {z} using {agg} {measure.replace('_', ' ')}. The result contains {len(d):,} student records across {len(g)} multi-dimensional combinations."
        
    return {
        "op": op,
        "columns": columns,
        "rows": g.head(60).values.tolist(),
        "chart": {"labels": chart_labels, "series": chart_series},
        "total_students": len(d),
        "explanation": explanation,
        "active_filters": active_filters
    }


# ───────────── Lab 2: CUBE / GROUPING SETS / drill-across ─────────────
def _fact_inventory(d):
    """Second fact table (lifestyle 'inventory' of hours) sharing conformed dims with Fact_Usage."""
    return d[["Academic_Level", "Most_Used_Platform", "Gender", "Study_Hours", "Physical_Activity_Hours", "Sleep_Hours_Per_Night"]]


def olap2(op="cube", measure="Mental_Health_Score", dims="Academic_Level,Most_Used_Platform"):
    from itertools import combinations
    if measure not in NUM:
        raise ValueError("bad measure")
    D = [x for x in dims.split(",") if x in DIMS][:3] or ["Academic_Level", "Most_Used_Platform"]
    d = clean()
    cols = D + ["students", "avg_" + measure]
    def agg(keys):
        if keys:
            g = d.groupby(list(keys))[measure].agg(["count", "mean"]).round(2).reset_index()
        else:
            g = pd.DataFrame([{"count": len(d), "mean": round(d[measure].mean(), 2)}])
        g = g.rename(columns={"count": "students", "mean": "avg_" + measure})
        for c in D:
            if c not in g: g[c] = "(all)"
        return g[cols]
    if op == "cube":   # every subset of dims = 2^n grouping sets
        sets = [c for r in range(len(D), -1, -1) for c in combinations(D, r)]
        title = f"CUBE({', '.join(D)}) · {len(sets)} grouping sets"
    elif op == "grouping_sets":  # explicit: each single dim + grand total
        sets = [(c,) for c in D] + [()]
        title = "GROUPING SETS (" + ", ".join(f"({c})" for c in D) + ", ())"
    elif op in ("dropcross", "drillacross"):
        f1 = d.groupby(["Academic_Level", "Most_Used_Platform"]).agg(
            students=("Age", "size"), avg_usage_hrs=("Avg_Daily_Usage_Hours", "mean"), avg_mental_score=("Mental_Health_Score", "mean"))
        fi = _fact_inventory(d).groupby(["Academic_Level", "Most_Used_Platform"]).agg(
            avg_study_hrs=("Study_Hours", "mean"), avg_activity_hrs=("Physical_Activity_Hours", "mean"), avg_sleep_hrs=("Sleep_Hours_Per_Night", "mean"))
        t = f1.join(fi).round(2).reset_index().sort_values("students", ascending=False)
        return {"title": "Drill-across: Fact_Usage ⋈ Fact_Lifestyle (Wellbeing) on Level × Platform",
                "note": "Fact_Usage (digital habits) and Fact_Lifestyle (daily wellbeing hours) are aggregated separately at the shared conformed dimensions, then joined side-by-side.",
                "columns": list(t.columns), "rows": t.values.tolist()}
    else:
        raise ValueError("unknown op")
    t = pd.concat([agg(s) for s in sets], ignore_index=True)
    t["grouping_id"] = [sum(1 << i for i, c in enumerate(D) if r[c] == "(all)") for _, r in t.iterrows()]
    return {"title": title, "note": "'(all)' marks a rolled-up dimension; grouping_id is the bitmask of rolled-up dims.",
            "columns": list(t.columns), "rows": t.values.tolist()}


# ───────────── Lab 3: visual encodings with variance observations ─────────────
def viz(x="Avg_Daily_Usage_Hours", y="Mental_Health_Score", cat="Most_Used_Platform"):
    d = clean()
    if x not in NUM or y not in NUM or cat not in CAT + [TARGET]:
        raise ValueError("bad column")
    g = d.groupby(cat)[y]
    box = []
    for k, s in g:
        q1, med, q3 = s.quantile([.25, .5, .75]); iqr = q3 - q1
        lo, hi = s[s >= q1 - 1.5 * iqr].min(), s[s <= q3 + 1.5 * iqr].max()
        box.append({"name": str(k), "min": float(lo), "q1": float(q1), "med": float(med), "q3": float(q3), "max": float(hi),
                    "outliers": int(((s < lo) | (s > hi)).sum()), "var": round(float(s.var()), 3), "std": round(float(s.std()), 3), "n": len(s)})
    box.sort(key=lambda b: b["med"])
    v = d[y].var()
    sm = d.sample(min(500, len(d)), random_state=1)
    return {"box": box, "hist": hist(d[x], 15), "line": g.mean().round(3).to_dict(), "bar": g.var().round(3).to_dict(),
            "pie": d[cat].value_counts().to_dict(), "scatter": sm[[x, y]].values.tolist(),
            "stats": {"mean": round(float(d[y].mean()), 3), "variance": round(float(v), 3), "std": round(float(d[y].std()), 3),
                      "corr": round(float(d[x].corr(d[y])), 3), "cv_%": round(float(d[y].std() / d[y].mean() * 100), 1),
                      "highest_var_group": max(box, key=lambda b: b["var"])["name"], "lowest_var_group": min(box, key=lambda b: b["var"])["name"]}}


# ───────────── Labs 4-6: target = Mental_Health_Score, inputs = the other 12 columns ─────────────
IN_NUM = ["Age", "Avg_Daily_Usage_Hours", "Daily_Unlocks", "Study_Hours", "Physical_Activity_Hours", "Sleep_Hours_Per_Night"]
IN_CAT = ["Gender", "Country", "Academic_Level", "Most_Used_Platform", "Purpose_Of_Use", "Stress_Level"]
MH = "Mental_Health_Score"
_rf = {}


def _X12(d):
    return pd.get_dummies(d[IN_NUM + IN_CAT], columns=IN_CAT, dtype=float)


def _group_importance(cols, vals):
    g = {}
    for c, v in zip(cols, vals):
        k = next((p for p in IN_CAT if c.startswith(p + "_")), c)
        g[k] = g.get(k, 0) + float(v)
    return sorted(g.items(), key=lambda t: -t[1])


def rf_fit():
    from sklearn.ensemble import RandomForestRegressor
    d = clean(); X = _X12(d); y = d[MH]
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42)
    m = RandomForestRegressor(200, min_samples_leaf=3, n_jobs=-1, random_state=42).fit(Xtr, ytr)
    p = m.predict(Xte)
    _rf.update(model=m, cols=list(X.columns), n=len(d))
    return {"r2": r2_score(yte, p), "mae": mean_absolute_error(yte, p), "mse": mean_squared_error(yte, p),
            "rmse": float(np.sqrt(mean_squared_error(yte, p))),
            "importance": _group_importance(X.columns, m.feature_importances_),
            "actual_vs_pred": [[float(a), float(b)] for a, b in zip(yte.values[:300], p[:300])]}


def rf_predict(vals):
    if "model" not in _rf: rf_fit()
    d = clean(); row = {}
    for c in IN_NUM: row[c] = float(vals[c])
    for c in IN_CAT: row[c] = str(vals[c])
    X = _X12(pd.concat([d[IN_NUM + IN_CAT], pd.DataFrame([row])], ignore_index=True)).iloc[[-1]].reindex(columns=_rf["cols"], fill_value=0)
    tr = _rf["model"].estimators_
    per = np.array([t.predict(X.values)[0] for t in tr])
    return {"score": round(float(per.mean()), 2), "low": round(float(np.percentile(per, 10)), 2), "high": round(float(np.percentile(per, 90)), 2)}


def regression4(x="Avg_Daily_Usage_Hours", test_size=0.2):
    r = regression("Mental_Health_Score", x, test_size=test_size); r["rf"] = rf_fit()
    d = clean(); Xm = _X12(d); y = d[MH]
    tr, te, ytr, yte = train_test_split(Xm, y, test_size=test_size, random_state=42)
    p = LinearRegression().fit(tr, ytr).predict(te)
    r["multiple"]["mse"] = float(mean_squared_error(yte, p))
    r["simple"]["mse"] = float(r["simple"]["rmse"] ** 2)
    r["multiple"].update(r2=r2_score(yte, p), mae=mean_absolute_error(yte, p), rmse=float(np.sqrt(mean_squared_error(yte, p))))
    r["options"] = {**{c: sorted(d[c].unique().tolist()) for c in IN_CAT}, "ORDER": ORDER,
                    "ranges": {c: [float(d[c].min()), float(d[c].max()), float(round(d[c].median(), 1))] for c in IN_NUM}}
    return r


def _mh_class(d):
    return d[MH].round().astype(int).astype(str)   # score classes 4..9


def _clf12():
    d = clean(); y = _mh_class(d); X = _X12(d)
    return d, X, y, train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)


def _res12(yte, pred):
    labels = sorted(set(yte)); rep = classification_report(yte, pred, labels=labels, output_dict=True, zero_division=0)
    return {"accuracy": accuracy_score(yte, pred), "labels": labels, "confusion": confusion_matrix(yte, pred, labels=labels).tolist(),
            "report": {l: {k: round(v, 3) for k, v in rep[l].items()} for l in labels}}


def tree12(max_depth=5):
    d, X, y, (Xtr, Xte, ytr, yte) = _clf12()
    m = DecisionTreeClassifier(max_depth=max_depth, random_state=42).fit(Xtr, ytr)
    r = _res12(yte, m.predict(Xte))
    raw = d[IN_NUM + IN_CAT].copy()
    for c in IN_CAT: raw[c] = raw[c].astype("category").cat.codes
    mi = mutual_info_classif(raw, y, discrete_features=[c in IN_CAT for c in raw.columns], random_state=42)
    r["mutual_info"] = sorted([[c, float(v)] for c, v in zip(raw.columns, mi)], key=lambda t: -t[1])
    r["importances"] = [[k, v] for k, v in _group_importance(X.columns, m.feature_importances_) if v > 0][:12]
    r["rules"] = export_text(m, feature_names=list(X.columns), max_depth=3)
    r.update(depth=int(m.get_depth()), leaves=int(m.get_n_leaves()), train_accuracy=float(m.score(Xtr, ytr)), target="Mental_Health_Score (rounded 4-9)")
    return r


def nb12():
    d, X, y, (Xtr, Xte, ytr, yte) = _clf12()
    m = GaussianNB().fit(Xtr, ytr); r = _res12(yte, m.predict(Xte))
    r["priors"] = {str(c): float(p) for c, p in zip(m.classes_, m.class_prior_)}
    return r


# ───────────── Lab 10: WEKA-style mini project ─────────────
def weka():
    from sklearn.preprocessing import KBinsDiscretizer
    d = clean()
    # 1 preprocessing + discretization (3 equal-frequency bins for each numeric column)
    disc = d.copy()
    kb = KBinsDiscretizer(3, encode="ordinal", strategy="quantile")
    disc[IN_NUM] = kb.fit_transform(d[IN_NUM]).astype(int)
    disc[IN_NUM] = disc[IN_NUM].replace({0: "Low", 1: "Mid", 2: "High"})
    disc["Score_Class"] = pd.qcut(d[MH], 3, labels=["Low", "Mid", "High"], duplicates="drop").astype(str)
    pre = {"rows_raw": len(df()), "rows_clean": len(d), "missing": int(df().isna().sum().sum()), "duplicates": int(df().duplicated().sum()),
           "bins": {c: [round(float(e), 2) for e in kb.bin_edges_[i]] for i, c in enumerate(IN_NUM)}, "class_dist": disc["Score_Class"].value_counts().to_dict(),
           "sample": disc[IN_NUM + IN_CAT + ["Score_Class"]].head(5).values.tolist(), "columns": IN_NUM + IN_CAT + ["Score_Class"]}
    # 2 J48-style tree (entropy, pruned) vs Naive Bayes, 10-fold CV
    from sklearn.model_selection import cross_val_predict, StratifiedKFold
    from sklearn.naive_bayes import CategoricalNB
    X = pd.get_dummies(disc[IN_NUM + IN_CAT]).astype(float); y = disc["Score_Class"]
    cv = StratifiedKFold(10, shuffle=True, random_state=42)
    models = {"J48 (C4.5-style tree)": DecisionTreeClassifier(criterion="entropy", min_samples_leaf=15, max_depth=6, random_state=42),
              "Naive Bayes": GaussianNB()}
    cmp = []
    for n, m in models.items():
        p = cross_val_predict(m, X, y, cv=cv); rep = classification_report(y, p, output_dict=True, zero_division=0)
        cmp.append({"model": n, "accuracy": float(accuracy_score(y, p)), "precision": rep["weighted avg"]["precision"], "recall": rep["weighted avg"]["recall"], "f1": rep["weighted avg"]["f1-score"]})
    # 3 K-Means k=3  4 association mining
    dd, Xs = _cluster_X(); km = KMeans(3, n_init=10, random_state=42).fit(Xs)
    return {"pre": pre, "compare": cmp, "kmeans": {"silhouette": float(silhouette_score(Xs, km.labels_, sample_size=1500, random_state=42)),
            "profile": _profile(dd, km.labels_), "points": _pca_points(Xs, km.labels_)}, "apriori": apriori_rules(0.15, 0.7, 10)}


def classifier_comparison(test_size=0.2):
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    d, X, y, (Xtr, Xte, ytr, yte) = _clf12()
    scaler = StandardScaler()
    Xtr_s = scaler.fit_transform(Xtr)
    Xte_s = scaler.transform(Xte)
    models = {
        "Decision Tree": (DecisionTreeClassifier(max_depth=5, random_state=42), Xtr, Xte),
        "Random Forest": (RandomForestClassifier(n_estimators=50, max_depth=5, random_state=42), Xtr, Xte),
        "Naive Bayes": (GaussianNB(), Xtr, Xte),
        "Logistic Regression": (LogisticRegression(max_iter=1000, random_state=42), Xtr_s, Xte_s)
    }
    results = []
    for name, (m, xtr, xte) in models.items():
        m.fit(xtr, ytr)
        pred = m.predict(xte)
        r = _res12(yte, pred)
        results.append({
            "model": name,
            "accuracy": round(float(r["accuracy"]), 4),
            "labels": r["labels"],
            "confusion": r["confusion"],
            "report": r["report"],
            "macro_f1": round(float(np.mean([v["f1-score"] for v in r["report"].values() if isinstance(v, dict) and "f1-score" in v])), 4)
        })
    return results

