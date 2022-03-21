from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.utils import timezone
from django.utils.cache import patch_response_headers

import requests
from dashboard.models import Bounty
from git.utils import get_user, org_name
from PIL import Image, ImageDraw, ImageFont
from ratelimit.decorators import ratelimit

AVATAR_BASE = 'assets/other/avatars/'


def wrap_text(text, w=30):
    new_text = ""
    new_sentence = ""
    for word in text.split(" "):
        delim = " " if new_sentence != "" else ""
        new_sentence = new_sentence + delim + word
        if len(new_sentence) > w:
            new_text += "\n" + new_sentence
            new_sentence = ""
    new_text += "\n" + new_sentence
    return new_text


def summarize_bounties(bounties):
    val_usdt = sum(bounties.values_list('_val_usd_db', flat=True))

    if val_usdt < 1:
        return False, ""

    currency_to_value = {bounty.token_name: 0.00 for bounty in bounties}
    for bounty in bounties:
        currency_to_value[bounty.token_name] += float(bounty.value_true)
    other_values = ", ".join([
        f"{round(value, 2)} {token_name}"
        for token_name, value in currency_to_value.items()
    ])
    is_plural = 's' if bounties.count() > 1 else ''
    return True, f"Total: {bounties.count()} issue{is_plural}, {val_usdt} USD, {other_values}"


@ratelimit(key='ip', rate='50/m', method=ratelimit.UNSAFE, block=True)
def stat(request, key):

    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    from matplotlib.figure import Figure
    from matplotlib.dates import DateFormatter
    from marketing.models import Stat
    limit = 10
    weekly_stats = Stat.objects.filter(key=key).order_by('created_on')
    # weekly stats only
    weekly_stats = weekly_stats.filter(
        created_on__hour=1,
        created_on__week_day=1
    ).filter(
        created_on__gt=(timezone.now() - timezone.timedelta(weeks=7))
    )

    daily_stats = Stat.objects.filter(key=key) \
        .filter(
            created_on__gt=(timezone.now() - timezone.timedelta(days=7))
        ).order_by('created_on')
    daily_stats = daily_stats.filter(created_on__hour=1)  # daily stats only

    stats = weekly_stats if weekly_stats.count() < limit else daily_stats

    fig = Figure(figsize=(1.6, 1.5), dpi=80, facecolor='w', edgecolor='k')
    ax = fig.add_subplot(111)
    x = []
    y = []
    for stat in stats:
        x.append(stat.created_on)
        y.append(stat.val)
    x = x[-1 * limit:]
    y = y[-1 * limit:]
    ax.plot_date(x, y, '-')
    ax.set_axis_off()
    ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
    if stats.count() > 1:
        ax.set_title("Usage over time", y=0.9)
    else:
        ax.set_title("(Not enough data)", y=0.3)
    fig.autofmt_xdate()
    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response)
    return response


@ratelimit(key='ip', rate='50/m', method=ratelimit.UNSAFE, block=True)
def embed(request):
    # default response
    could_not_find = Image.new('RGB', (1, 1), (0, 0, 0, 0))
    err_response = HttpResponse(content_type="image/jpeg")
    could_not_find.save(err_response, "JPEG")

    # Get maxAge GET param if provided, else default on the small side
    max_age = int(request.GET.get('maxAge', 3600))

    # params
    repo_url = request.GET.get('repo', False)
    if not repo_url or 'github.com' not in repo_url:
        return err_response

    try:
        badge = request.GET.get('badge', False)
        if badge:
            open_bounties = Bounty.objects.current() \
                .filter(
                    github_url__startswith=repo_url,
                    network='mainnet',
                    idx_status__in=['open']
                )

            tmpl = loader.get_template('svg_badge.txt')
            response = HttpResponse(
                tmpl.render({'bounties_count': open_bounties.count()}),
                content_type='image/svg+xml',
            )
            patch_response_headers(response, cache_timeout=max_age)
            return response

        # get avatar of repo
        _org_name = org_name(repo_url)

        avatar = None
        filename = f"{_org_name}.png"
        filepath = 'assets/other/avatars/' + filename
        try:
            avatar = Image.open(filepath, 'r').convert("RGBA")
        except IOError:
            remote_user = get_user(_org_name)
            if not hasattr(remote_user, 'avatar_url'):
                return JsonResponse({'msg': 'invalid user'}, status=422)
            remote_avatar_url = remote_user.avatar_url

            r = requests.get(remote_avatar_url, stream=True)
            chunk_size = 20000
            with open(filepath, 'wb') as fd:
                for chunk in r.iter_content(chunk_size):
                    fd.write(chunk)
            avatar = Image.open(filepath, 'r').convert("RGBA")

            # make transparent
            datas = avatar.getdata()

            new_data = []
            for item in datas:
                if item[0] == 255 and item[1] == 255 and item[2] == 255:
                    new_data.append((255, 255, 255, 0))
                else:
                    new_data.append(item)

            avatar.putdata(new_data)
            avatar.save(filepath, "PNG")

        # get issues
        length = request.GET.get('len', 10)
        super_bounties = Bounty.objects.current() \
            .filter(
                github_url__startswith=repo_url,
                network='mainnet',
                idx_status__in=['open', 'started', 'submitted']
            ).order_by('-_val_usd_db')
        bounties = super_bounties[:length]

        # config
        bounty_height = 200
        bounty_width = 572
        font = 'assets/v2/fonts/futura/FuturaStd-Medium.otf'
        width = 1776
        height = 576

        # setup
        img = Image.new("RGBA", (width, height), (255, 255, 255))
        draw = ImageDraw.Draw(img)
        black = (0, 0, 0)
        gray = (102, 102, 102)
        h1 = ImageFont.truetype(font, 36, encoding="unic")
        h2_thin = ImageFont.truetype(font, 36, encoding="unic")
        p = ImageFont.truetype(font, 24, encoding="unic")

        # background
        background_image = 'assets/v2/images/embed-widget/background.png'
        back = Image.open(background_image, 'r').convert("RGBA")
        offset = 0, 0
        img.paste(back, offset)

        # repo logo
        icon_size = (184, 184)
        avatar.thumbnail(icon_size, Image.ANTIALIAS)
        offset = 195, 148
        img.paste(avatar, offset, avatar)

        img_org_name = ImageDraw.Draw(img)
        img_org_name_size = img_org_name.textsize(_org_name, h1)

        img_org_name.multiline_text(
            align="left",
            xy=(287 - img_org_name_size[0] / 2, 360),
            text=_org_name,
            fill=black,
            font=h1,
        )

        draw.multiline_text(
            align="left",
            xy=(110, 410),
            text="supports funded issues",
            fill=black,
            font=h1,
        )

        # put bounty list in there
        i = 0
        for bounty in bounties[:4]:
            i += 1
            # execute
            line_size = 2

            # Limit text to 28 chars
            text = f"{bounty.title_or_desc}"
            text = (text[:28] + '...') if len(text) > 28 else text

            x = 620 + (int((i-1)/line_size) * (bounty_width))
            y = 230 + (abs(i % line_size-1) * bounty_height)
            draw.multiline_text(align="left", xy=(x, y), text=text, fill=black, font=h2_thin)

            unit = 'day'
            num = int(round((bounty.expires_date - timezone.now()).days, 0))
            if num == 0:
                unit = 'hour'
                num = int(round((bounty.expires_date - timezone.now()).seconds / 3600 / 24, 0))
            unit = unit + ("s" if num != 1 else "")
            draw.multiline_text(
                align="left",
                xy=(x, y - 40),
                text=f"Expires in {num} {unit}:",
                fill=gray,
                font=p,
            )

            bounty_eth_background = Image.new("RGBA", (200, 56), (231, 240, 250))
            bounty_usd_background = Image.new("RGBA", (200, 56), (214, 251, 235))

            img.paste(bounty_eth_background, (x, y + 50))
            img.paste(bounty_usd_background, (x + 210, y + 50))

            tmp = ImageDraw.Draw(img)

            bounty_value_size = tmp.textsize(f"{round(bounty.value_true, 2)} {bounty.token_name}", p)

            draw.multiline_text(
                align="left",
                xy=(x + 100 - bounty_value_size[0]/2, y + 67),
                text=f"{round(bounty.value_true, 2)} {bounty.token_name}",
                fill=(44, 35, 169),
                font=p,
            )

            bounty_value_size = tmp.textsize(f"{round(bounty.value_in_usdt_now, 2)} USD", p)

            draw.multiline_text(
                align="left",
                xy=(x + 310 - bounty_value_size[0]/2, y + 67),
                text=f"{round(bounty.value_in_usdt_now, 2)} USD",
                fill=(45, 168, 116),
                font=p,
            )

        # blank slate
        if bounties.count() == 0:
            draw.multiline_text(
                align="left",
                xy=(760, 320),
                text="No active issues. Post a funded issue at: https://gitcoin.co",
                fill=gray,
                font=h1,
            )

        if bounties.count() != 0:
            text = 'Browse issues at: https://gitcoin.co/explorer'
            draw.multiline_text(
                align="left",
                xy=(64, height - 70),
                text=text,
                fill=gray,
                font=p,
            )

            draw.multiline_text(
                align="left",
                xy=(624, 120),
                text="Recently funded issues:",
                fill=(62, 36, 251),
                font=p,
            )

            _, value = summarize_bounties(super_bounties)
            value_size = tmp.textsize(value, p)

            draw.multiline_text(
                align="left",
                xy=(1725 - value_size[0], 120),
                text=value,
                fill=gray,
                font=p,
            )

            line_table_header = Image.new("RGBA", (1100, 6), (62, 36, 251))

            img.paste(line_table_header, (624, 155))

        # Resize back to output size for better anti-alias
        img = img.resize((888, 288), Image.LANCZOS)

        # Return image with right content-type
        response = HttpResponse(content_type="image/png")
        img.save(response, "PNG")
        patch_response_headers(response, cache_timeout=max_age)
        return response
    except IOError as e:
        print(e)
        return err_response
