import datetime
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

import matplotlib.pyplot as plt
import numpy as np
import squarify  # pip install squarify (algorithm for treemap)
from gas.management.commands.output_gas_viz import clear_cache, convert_to_movie, upload_to_s3
from grants.models import Contribution, Grant
from numpy import array
from perftools.models import JSONStore

colors = ["#011f4b", "#03396c", "#005b96", "#6497b1", '#b3cde0', '#d3ddf0', '#DDDDDD']
# hack to make infinite
for i in range(0, 3):
    colors = colors + colors + colors + colors + colors + colors + colors + colors

label_spec = 'handle'
label_spec = 'titles'

graph_type = 'chart'
graph_type = 'tree'
graph_type = 'scatter'

opposing_axis = 'counts'
opposing_axis = 'clr'

days_ago = 12

aggregation_function=sum

def get_graph_plot(d1, this_date, limit=5):
    amounts, labels, counts, total_amount = get_tree_plot(d1, this_date, limit=limit, append_amounts_to_labels=False)

    crowd_amounts = []
    match_amounts = []

    for label in labels:
        contributions = Contribution.objects.filter(subscription__network='mainnet', subscription__grant__title=label, created_on__lt=this_date, created_on__gt=d1)
        if label_spec == 'handle':
            contributions = Contribution.objects.filter(subscription__network='mainnet', subscription__contributor_profile__handle=label, created_on__lt=this_date, created_on__gt=d1)
        crowd_contributions = contributions.values_list('subscription__amount_per_period_usdt', flat=True)
        match_contributions = contributions.none().values_list('subscription__amount_per_period_usdt', flat=True)
        crowd_amounts.append(float(aggregation_function(crowd_contributions)))
        match_amounts.append(float(aggregation_function(match_contributions)))

    return crowd_amounts, match_amounts, labels, total_amount


def clr_amount_at_time(grant, d1):
    jsonstores = JSONStore.objects.filter(
        created_on__gt=(d1-timezone.timedelta(hours=1)),
        created_on__lte=d1,
        view='clr_contribution',
        key=f'{grant.id}',
        )
    if jsonstores.exists():
        jsonstore = jsonstores.first()
        return jsonstore.data[0][1]

    return 0

def get_tree_plot(d1, this_date, limit=5, append_amounts_to_labels=True):
    contributions = Contribution.objects.filter(subscription__network='mainnet', created_on__lt=this_date,  created_on__gt=d1)
    total_amount = 0
    plot_me = {}
    counts = {}
    for cont in contributions:
        key = cont.subscription.grant.title
        if label_spec == 'handle':
            key = cont.subscription.contributor_profile.handle
        if not counts.get(key, None):
            counts[key] = []
        if not plot_me.get(key, None):
            plot_me[key] = 0
        if opposing_axis == 'counts':
            counts[key].append(cont.subscription.pk)
        else:
            counts[key] = [clr_amount_at_time(cont.subscription.grant, this_date)]
            #if cont.subscription.grant.pk == 25:
            #    print(key, this_date, counts[key],)
        if aggregation_function == sum:
            plot_me[key] += float(cont.subscription.amount_per_period_usdt)
            total_amount += float(cont.subscription.amount_per_period_usdt)
        else:
            plot_me[key] += 1
            total_amount += 1

    # phantom contribs
    from grants.models import PhantomFunding
    contributions = PhantomFunding.objects.filter(grant__network='mainnet', created_on__lt=this_date,  created_on__gt=d1)
    for cont in contributions:
        key = cont.grant.title
        if label_spec == 'handle':
            key = cont.profile.handle
        if not counts.get(key, None):
            counts[key] = []
        if not plot_me.get(key, None):
            plot_me[key] = 0
        if opposing_axis == 'counts':
            counts[key].append(cont.pk)
        else:
            counts[key] = [clr_amount_at_time(cont.grant, this_date)]
        if aggregation_function == sum:
            plot_me[key] += float(cont.value)
            total_amount += float(cont.value)
        else:
            plot_me[key] += 1
            total_amount += 1


    sorted_by_value = sorted(plot_me.items(), key=lambda kv: kv[1], reverse=True)
    sizes = []
    labels = []
    return_counts = []
    for sv in sorted_by_value:
        if len(sizes) > limit:
            continue
        if sv[1]:
            sizes.append(sv[1])
            label = sv[0]
            if opposing_axis == 'counts':
                return_counts.append(len(set(counts[label])))
            else:
                return_counts.append(sum((counts[label])))
            if append_amounts_to_labels:
                _label = label
                label = f"{label}\n\${round(sv[1])} "
                if opposing_axis == 'clr':
                    clr_sum = round(((counts[_label][0])))
                    label += f"+ \${clr_sum} CLR"
            labels.append(label)
    return sizes, labels, return_counts, total_amount

class Command(BaseCommand):

    help = 'outputs grants leaderboard over time'

    def handle(self, *args, **options):
        clear_cache()

        d1 = timezone.now() - timezone.timedelta(days=days_ago)
        d2 = timezone.now()

        for i in range((d2 - d1).days * 24 + 1):
            this_date = d1 + timezone.timedelta(hours=i)
            #print(this_date)
            _plt = plt
            _plt.figure(figsize=(20, 10))
            this_date_str = this_date.strftime("%Y-%m-%d %H:%M")
            if graph_type == 'chart':

                crowd, matching, labels, total_amount = get_graph_plot(d1, this_date)
                if not len(crowd):
                    continue

                try:
                    N = len(crowd)
                    ind = np.arange(N)    # the x locations for the groups
                    width = 0.35       # the width of the bars: can also be len(x) sequence

                    p1 = _plt.bar(ind, crowd, width, color=colors[0])
                    p2 = _plt.bar(ind, matching, width, bottom=crowd, color=colors[4])
                    _plt.ylabel('Funding')
                    _plt.xticks(ind, labels)
                    _plt.legend((p1[0], p2[0]), ('Crowd', 'Matching'))
                except Exception as e:
                    print(e)
                    raise e
            elif graph_type == 'tree':

                # write the tree plot
                try:
                    sizes, labels, _, total_amount = get_tree_plot(d1, this_date, limit=99999999)
                    for j in range(0, len(labels)):
                        if len(labels) > 6:
                            if j > (len(labels)*1/3):
                                labels[j] = labels[j][0:6] + '\n...'
                    squarify.plot(sizes=sizes, label=labels, alpha=.7, color=colors)
                    _plt.axis('off')
                except Exception as e:
                    print(e)
            else:
                sizes, labels, counts, total_amount = get_tree_plot(d1, this_date, limit=99999999)
                if not len(sizes):
                    continue
                x = sizes
                y = counts
                _colors = colors[0:len(sizes)]
                _plt.scatter(x, y, c=_colors, s=sizes, alpha=0.3,
                            cmap='viridis')
                _plt.legend((0, 0), ('Crowd', 'Matching'))
                _plt.xlabel('Value of all Contributions (\$\$)')
                if opposing_axis == 'counts':
                    _plt.ylabel('Num Contributors')
                    y_axis_height = 40
                else:
                    _plt.ylabel('CLR Match Estimate ($)')
                    y_axis_height = max(counts) + 1000
                x_axis_height = max(sizes) + 1000
                _plt.axis([-1, x_axis_height, -1, y_axis_height])
                for j in range(0, len(sizes)):
                    _plt.text(sizes[j]+.03, counts[j]+.03, labels[j], fontsize=9)


            title = f"Gitcoin Grants CLR Round 3 Funding at {this_date_str}: ${round(total_amount)}"
            _plt.title(title)
            filename = str(i).rjust(10, '0')
            png_file = f'cache/frames/{filename}.jpg'
            print(this_date, filename)
            _plt.tight_layout()
            _plt.savefig(png_file)
            _plt.close()
        convert_to_movie(framerate=10)
        #url = upload_to_s3()
        #print(url)
