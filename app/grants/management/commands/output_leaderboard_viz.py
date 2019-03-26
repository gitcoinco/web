import datetime
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from grants.models import Grant, Contribution
from numpy import array
from gas.management.commands.output_gas_viz import convert_to_movie, clear_cache, upload_to_s3
import matplotlib.pyplot as plt
import squarify    # pip install squarify (algorithm for treemap)
import numpy as np

colors = ["#011f4b", "#03396c", "#005b96", "#6497b1", '#b3cde0', '#d3ddf0', '#DDDDDD']
# hack to make infinite
for i in range(0, 3):
    colors = colors + colors + colors + colors + colors + colors + colors + colors


def get_graph_plot(this_date, limit=5):
    amounts, labels, counts, total_amount = get_tree_plot(this_date, limit=limit, append_amounts_to_labels=False)

    crowd_amounts = []
    match_amounts = []

    for label in labels:
        contributions = Contribution.objects.filter(subscription__network='mainnet', subscription__grant__title=label, created_on__lt=this_date)
        matching_usernames = ['ceresstation', 'owocki', 'vs77bb']
        kwargs = {
            'subscription__contributor_profile__handle__in': matching_usernames
        }
        crowd_contributions = contributions.exclude(**kwargs).values_list('subscription__amount_per_period_usdt', flat=True)
        match_contributions = contributions.filter(**kwargs).values_list('subscription__amount_per_period_usdt', flat=True)
        crowd_amounts.append(float(sum(crowd_contributions)))
        match_amounts.append(float(sum(match_contributions)))

    return crowd_amounts, match_amounts, labels, total_amount


def get_tree_plot(this_date, limit=5, append_amounts_to_labels=True):
    contributions = Contribution.objects.filter(subscription__network='mainnet', created_on__lt=this_date)
    total_amount = 0
    sums = {}
    counts = {}
    for cont in contributions:
        key = cont.subscription.grant.title
        if not counts.get(key, None):
            counts[key] = []
        if not sums.get(key, None):
            sums[key] = 0
        counts[key].append(cont.subscription.pk)
        sums[key] += float(cont.subscription.amount_per_period_usdt)
        total_amount += float(cont.subscription.amount_per_period_usdt)

    sorted_by_value = sorted(sums.items(), key=lambda kv: kv[1], reverse=True)
    sizes = []
    labels = []
    return_counts = []
    for sv in sorted_by_value:
        if len(sizes) > limit:
            continue
        if sv[1]:
            sizes.append(sv[1])
            label = sv[0]
            return_counts.append(len(set(counts[label])))
            if append_amounts_to_labels:
                label = f"{label}\n${round(sv[1])}"
            labels.append(label)
    return sizes, labels, return_counts, total_amount

class Command(BaseCommand):

    help = 'outputs grants leaderboard over time'

    def handle(self, *args, **options):
        graph_type = 'scatter'
        graph_type = 'tree'
        graph_type = 'chart'
        clear_cache()

        d1 = Contribution.objects.first().created_on
        d2 = timezone.now()

        for i in range((d2 - d1).days + 1):
            this_date = d1 + timezone.timedelta(days=i)
            _plt = plt
            _plt.figure(figsize=(20, 10))
            this_date_str = this_date.strftime("%Y-%m-%d")
            if graph_type == 'chart':

                crowd, matching, labels, total_amount = get_graph_plot(this_date)
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
                    sizes, labels, _, total_amount = get_tree_plot(this_date, limit=99999999)
                    for j in range(0, len(labels)):
                        if len(labels) > 6:
                            if j > (len(labels)*1/3):
                                labels[j] = labels[j][0:6] + '\n...'
                    squarify.plot(sizes=sizes, label=labels, alpha=.7, color=colors)
                    _plt.axis('off')
                except Exception as e:
                    print(e)
            else:
                sizes, labels, counts, total_amount = get_tree_plot(this_date, limit=99999999)
                if not len(sizes):
                    continue
                x = sizes
                y = counts
                _colors = colors[0:len(sizes)]
                _plt.scatter(x, y, c=_colors, s=sizes, alpha=0.3,
                            cmap='viridis')
                _plt.legend((0, 0), ('Crowd', 'Matching'))
                _plt.xlabel('Value of all Contributions')
                _plt.ylabel('Num Contributors')
                _plt.axis([-1, 10000, -1, 40])
                for j in range(0, len(sizes)):
                    _plt.text(sizes[j]+.03, counts[j]+.03, labels[j], fontsize=9)


            title = f"Gitcoin Grants Funding at {this_date_str}: ${round(total_amount)}"
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
