import datar.all as r
# delay import as this is only available in celery envs
import pandas as pd
from datar.core.factory import func_factory


@func_factory("agg", "x")
def my_paste(x):
    return ", ".join(x)


@func_factory("agg", "x")
def my_len(x):
    return len(x)


@func_factory("agg", "x")
def my_head(x, n=1):
    return x[0:n]


def compute_apu_scores(
    gc, stamp_field_names, grouping_fieldnames, grouping_fieldnames_1
):
    grouping_fields = [r.f[fieldname] for fieldname in grouping_fieldnames]
    grouping_fields_1 = [r.f[fieldname] for fieldname in grouping_fieldnames_1]
    stamp_fields = [r.f[fieldname] for fieldname in stamp_field_names]

    pca_dat = gc >> r.select(~r.f[grouping_fields_1])

    method_combos = (
        gc
        >> r.select(~r.f[grouping_fields])
        >> r.pivot_longer(
            cols=[stamp_fields], names_to="Authentication", values_to="Value"
        )
        >> r.filter(r.f.Value)
        >> r.group_by(r.f.user_id)
        >> r.summarise(
            Combo=my_paste(r.f.Authentication), Num=my_len(r.f.Authentication)
        )
        >> r.group_by(r.f.Combo)
        >> r.summarise(Count=r.n(), Num=my_head(r.f.Num))
        >> r.arrange(r.desc(r.f.Count))
        >> r.group_by(r.f.Num)
        >> r.mutate(
            Prop=r.f.Count / r.sum(r.f.Count),
            Weight=1 - r.f.Prop,
            Score=r.f.Weight * (1 / pca_dat.shape[1]) + (r.f.Num / pca_dat.shape[1]),
        )
        >> r.arrange(r.desc(r.f.Num), r.desc(r.f.Count))
    )

    method4_prelim = (
        gc
        >> r.select(~r.f[grouping_fields])
        >> r.pivot_longer(
            cols=[stamp_fields], names_to="Authentication", values_to="Value"
        )
        >> r.filter(r.f.Value)
        >> r.group_by(r.f.user_id)
        >> r.summarise(Combo=my_paste(r.f.Authentication))
        >> r.left_join(method_combos)
    )

    method4 = gc >> r.select(r.f.user_id) >> r.left_join(method4_prelim)

    method4["Score"].fillna(0, inplace=True)
    method4 = method4[method4["Combo"].notnull()]

    return method4
