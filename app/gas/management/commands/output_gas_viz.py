import datetime
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

import boto
from boto.s3.key import Key
from gas.models import GasProfile
from numpy import array
from perftools.models import JSONStore


def convert_to_movie():
    command = "ffmpeg -framerate 30 -pattern_type glob -i 'cache/frames/*.jpg' -c:v libx264 -pix_fmt yuv420p cache/out.mp4"
    print("converting to movie")
    os.system(command)


def clear_cache():
    # TODO: This whole method and utilization needs modified to use S3 storage... not local.
    # We can't be using local storage moving forward.
    command = "mkdir cache"
    os.system(command)
    command = "mkdir cache/frames"
    os.system(command)
    command = "rm cache/frames/*.jpg"
    os.system(command)
    command = "rm cache/*.jpg"
    os.system(command)
    command = "rm cache/*.mp4"
    os.system(command)

def upload_to_s3():
    def percent_cb(complete, total):
        import sys
        sys.stdout.write('.')
        sys.stdout.flush()

    filepath = 'cache/out.mp4'
    s3 = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
    bucket = s3.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)
    k = Key(bucket)
    k.key = 'gas_price_viz.mp4'
    k.set_contents_from_filename(filepath, cb=percent_cb, num_cb=10)
    k.set_acl('public-read')
    return k.generate_url(expires_in=0, query_auth=False)


def get_color(j, k, num_items_to_show_at_a_time):
    c1 = (3 * ((k/num_items_to_show_at_a_time) / 10.0)) + 0.6
    jsub = j % 100 if int(j / 100) % 2 == 0 else 100 - (j % 100)
    c2 = (3 * (((jsub)/100) / 10.0)) + 0.6
    color = [c1, c2, c2]
    return color


def sub_array(val, i):
    return [[x[i], x[i], x[i], x[i]] for x in val]


class Command(BaseCommand):

    help = 'gets observations and visualizes them in 3d'

    def handle(self, *args, **options):
        from mpl_toolkits.mplot3d import Axes3D
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        vantage_point = 'med'
        rotate = True
        last_degrees = 275
        invert_colors = False
        max_gas = 50
        package = {}
        for gp in GasProfile.objects.filter(gas_price__lt=max_gas, created_on__gt=timezone.now() - timezone.timedelta(days=7)).order_by('created_on'):
            key = gp.created_on.strftime("%Y-%m-%dT%H:%M:00")
            new_time = datetime.datetime.strptime(key, "%Y-%m-%dT%H:%M:00")
            if key not in package.keys():
                package[key] = []
            new_pkg = [float(gp.gas_price), -1 * int(new_time.strftime("%s")), float(gp.mean_time_to_confirm_minutes)]
            package[key].append(new_pkg)

        clear_cache()

        # Divide into X, Y, Z
        keys = list(package.keys())
        arr = list(package.values())
        num_items_to_show_at_a_time = 50
        for j in range(num_items_to_show_at_a_time, len(arr)):
            print(j)
            key = f"Ethereum Mainnet Gas Tradeoffs\n Gas Prices (x axis) vs Time to Confirm (y axis) vs Time (z axis) \n {keys[j]}\n\nMade with <3 at Gitcoin.\nhttps://gitcoin.co/gas"
            facecolor = '#274150' if invert_colors else 'white'
            fig = plt.figure(figsize=(16, 9), dpi=200, facecolor=facecolor, edgecolor='k')
            ax = fig.add_subplot(111, projection='3d', title=key, facecolor=facecolor)
            if invert_colors:
                axiscolor = 'white'
                ax.spines['bottom'].set_color(axiscolor)
                ax.spines['top'].set_color(axiscolor)
                ax.spines['right'].set_color(axiscolor)
                ax.spines['left'].set_color(axiscolor)
                ax.tick_params(axis='x', colors=axiscolor)
                ax.tick_params(axis='y', colors=axiscolor)
                ax.tick_params(axis='z', colors=axiscolor)
                ax.yaxis.label.set_color(axiscolor)
                ax.xaxis.label.set_color(axiscolor)
                ax.zaxis.label.set_color(axiscolor)
                ax.title.set_color(axiscolor)
            ax.set_ylabel('Time (unixtime)')
            ax.set_xlabel('Gas Price (gwei)')
            ax.set_zlabel('Time To Confirm (min)')


            X = []
            Y = []
            Z = []
            for k in range(0, num_items_to_show_at_a_time):
                val = arr[j-k]
                tmp = []
                for i in range(0, 3):
                    sa = sub_array(val, i)
                    tmp.append(sa + [x for x in reversed(sa)])
                X = tmp[0]
                Y = tmp[1]
                Z = tmp[2]
                color = get_color(j, k, num_items_to_show_at_a_time)
                ax.plot_wireframe(array(X), array(Y), array(Z), rstride=10, cstride=10, color=color, alpha=1-(k/num_items_to_show_at_a_time))

            if rotate:
                delta = 1 if int(j / 350) % 2 != 0 else -1
                degrees = last_degrees + (delta * 1.0 / 20.0)
                last_degrees = degrees

            if vantage_point == 'low':
                z_angle = 2
            if vantage_point == 'med':
                z_angle = 5
            if vantage_point == 'high':
                z_angle = 10
            ax.view_init(z_angle, degrees)
            filename = str(j).rjust(10, '0')
            png_file = f'cache/frames/{filename}.jpg'
            plt.savefig(png_file)
            plt.close()
        convert_to_movie()
        url = upload_to_s3()
        print(url)
