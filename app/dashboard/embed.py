from django.http import HttpResponse, JsonResponse

import requests
from dashboard.models import Bounty
from economy.utils import convert_token_to_usdt
from github.utils import get_user, org_name
from PIL import Image, ImageDraw, ImageFont, ImageOps
from ratelimit.decorators import ratelimit


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
        currency_to_value[bounty.token_name] += bounty.value_true
    other_values = ", ".join(["{} {}".format(round(value, 2), token_name) for token_name, value in currency_to_value.items()])
    return True, "Total: {} issue{}, {} USD, {}".format(bounties.count(), 's' if bounties.count() != 1 else "", val_usdt, other_values)


@ratelimit(key='ip', rate='50/m', method=ratelimit.UNSAFE, block=True)
def stat(request, key):

    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    from matplotlib.figure import Figure
    from matplotlib.dates import DateFormatter
    from marketing.models import Stat
    from django.utils import timezone
    limit = 10
    weekly_stats = Stat.objects.filter(key=key).order_by('created_on')
    weekly_stats = weekly_stats.filter(created_on__hour=1, created_on__week_day=1).filter(created_on__gt=(timezone.now() - timezone.timedelta(weeks=7))) #weekly stats only

    daily_stats = Stat.objects.filter(key=key).filter(created_on__gt=(timezone.now() - timezone.timedelta(days=7))).order_by('created_on')
    daily_stats = daily_stats.filter(created_on__hour=1) #daily stats only

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
    could_not_find = Image.new('RGBA', (1, 1), (0, 0, 0, 0))
    err_response = HttpResponse(content_type="image/jpeg")
    could_not_find.save(err_response, "JPEG")

    # params
    repo_url = request.GET.get('repo', False)
    if not repo_url or 'github.com' not in repo_url:
        return err_response

    try:
        # get avatar of repo
        _org_name = org_name(repo_url)
        is_org_gitcoin = _org_name == 'gitcoinco'

        avatar = None
        filename = "{}.png".format(_org_name)
        filepath = 'assets/other/avatars/' + filename
        try:
            avatar = Image.open(filepath, 'r').convert("RGBA")
        except IOError:
            remote_user = get_user(_org_name)
            if not remote_user.get('avatar_url', False):
                return JsonResponse({'msg': 'invalid user'}, status=422)
            remote_avatar_url = remote_user['avatar_url']

            r = requests.get(remote_avatar_url, stream=True)
            chunk_size = 20000
            with open(filepath, 'wb') as fd:
                for chunk in r.iter_content(chunk_size):
                    fd.write(chunk)
            avatar = Image.open(filepath, 'r').convert("RGBA")

            # make transparent
            datas = avatar.getdata()

            newData = []
            for item in datas:
                if item[0] == 255 and item[1] == 255 and item[2] == 255:
                    newData.append((255, 255, 255, 0))
                else:
                    newData.append(item)

            avatar.putdata(newData)
            avatar.save(filepath, "PNG")

        # get issues
        length = request.GET.get('len', 10)
        super_bounties = Bounty.objects.current().filter(
            github_url__startswith=repo_url,
            network='mainnet',
            idx_status='open').order_by('-_val_usd_db')
        bounties = super_bounties[:length]

        # config
        bounty_height = 145
        bounty_width = 400
        font_path = 'marketing/quotify/fonts/'
        width = 1350
        height = 350
        spacing = 0
        line = "".join(["_" for ele in range(0, 47)])

        # setup
        img = Image.new("RGBA", (width, height), (255, 255, 255))
        black = (0, 0, 0)
        h1 = ImageFont.truetype(font_path + 'Futura-Bold.ttf', 28, encoding="unic")
        h2_thin = ImageFont.truetype(font_path + 'Futura-Normal.ttf', 22, encoding="unic")
        p = ImageFont.truetype(font_path + 'Futura-LightBT.ttf', 20, encoding="unic")

        # background
        ## config
        logo = 'assets/v2/images/header-bg-light.jpg'
        ## execute
        back = Image.open(logo, 'r').convert("RGBA")
        img_w, img_h = back.size
        bg_w, bg_h = img.size
        offset = 0, 0
        img.paste(back, offset)

        # repo logo
        ## config
        icon_size = (215, 215)
        ## execute
        img_w, img_h = avatar.size
        avatar.thumbnail(icon_size, Image.ANTIALIAS)
        bg_w, bg_h = img.size
        offset = 10, 10
        img.paste(avatar, offset, avatar)

        # gitcoin logo
        ## config
        logo = 'assets/v2/images/gitcoinco.png'
        ## execute
        back = Image.open(logo, 'r').convert("RGBA")
        back.thumbnail(icon_size, Image.ANTIALIAS)
        img_w, img_h = back.size
        bg_w, bg_h = img.size
        offset = 250, 10
        if not is_org_gitcoin:
            img.paste(back, offset, back)

        # plus sign
        ## config
        if not is_org_gitcoin:
            text = '+'
            # execute
            text = wrap_text(text, 20)
            draw = ImageDraw.Draw(img)
            img_w, img_h = img.size
            x = 225
            y = 60
            draw.multiline_text(align="center", xy=(x, y), text=text, fill=black, font=h1, spacing=spacing)
            draw = ImageDraw.Draw(img)

        # header
        ## config
        text = '{} Supports Funded Issues'.format(_org_name.title())
        # execute
        text = wrap_text(text, 30)
        draw = ImageDraw.Draw(img)
        img_w, img_h = img.size
        x = 10
        y = 200
        draw.multiline_text(align="left", xy=(x, y), text=text, fill=black, font=h1, spacing=spacing)
        draw = ImageDraw.Draw(img)

        ## config
        show_value, value = summarize_bounties(super_bounties)
        text = '{}\nPush Open Source Forward | Powered by Gitcoin.co'.format(wrap_text(value, 45) if show_value else "")
        # execute
        draw = ImageDraw.Draw(img)
        img_w, img_h = img.size
        x = 10
        y = 225
        draw.multiline_text(align="left", xy=(x, y), text=text, fill=black, font=h2_thin, spacing=12)
        draw = ImageDraw.Draw(img)

        # put bounty list in there
        i = 0
        for bounty in bounties:
            i += 1
            text = f"{line}\n{wrap_text(bounty.title_or_desc, 30)}\n\nWorth: " \
                   f"{round(bounty.value_true, 2)} {bounty.token_name} ({round(bounty.value_in_usdt, 2)} USD " \
                   f"@ ${round(convert_token_to_usdt(bounty.token_name), 2)}/{bounty.token_name})"
            # execute
            draw = ImageDraw.Draw(img)
            img_w, img_h = img.size
            line_size = 2
            x = 500 + (int((i-1)/line_size) * (bounty_width))
            y = 30 + (abs(i % line_size-1) * bounty_height)
            draw.multiline_text(align="left", xy=(x, y), text=text, fill=black, font=p, spacing=spacing)
            draw = ImageDraw.Draw(img)

        if bounties.count() == 0:

            text = "{}\n\n{}\n\n{}".format(line, wrap_text("No active issues. Post a funded issue at https://gitcoin.co", 50), line)
            # execute
            draw = ImageDraw.Draw(img)
            img_w, img_h = img.size
            x = 10
            y = 320
            draw.multiline_text(align="left", xy=(x, y), text=text, fill=black, font=p, spacing=spacing)
            draw = ImageDraw.Draw(img)

        if bounties.count() != 0:
            ## config
            text = 'Browse Issues @ https://gitcoin.co/explorer'
            # execute
            text = wrap_text(text, 20)
            draw = ImageDraw.Draw(img)
            img_w, img_h = img.size
            x = 10
            y = height - 50
            draw.multiline_text(align="center", xy=(x, y), text=text, fill=black, font=h2_thin, spacing=spacing)
            draw = ImageDraw.Draw(img)

        response = HttpResponse(content_type="image/jpeg")
        img.save(response, "JPEG")
        return response
    except IOError as e:
        print(e)
        return err_response


def avatar(request):
    # default response
    could_not_find = Image.new('RGBA', (1, 1), (0, 0, 0, 0))
    err_response = HttpResponse(content_type="image/jpeg")
    could_not_find.save(err_response, "JPEG")

    # params
    repo_url = request.GET.get('repo', False)
    if not repo_url or 'github.com' not in repo_url:
        return err_response

    try:
        # get avatar of repo
        _org_name = org_name(repo_url)

        avatar = None
        filename = "{}.png".format(_org_name)
        filepath = 'assets/other/avatars/' + filename
        try:
            avatar = Image.open(filepath, 'r').convert("RGBA")
        except IOError:
            remote_user = get_user(_org_name)
            if not remote_user.get('avatar_url', False):
                return JsonResponse({'msg': 'invalid user'}, status=422)
            remote_avatar_url = remote_user['avatar_url']

            r = requests.get(remote_avatar_url, stream=True)
            chunk_size = 20000
            with open(filepath, 'wb') as fd:
                for chunk in r.iter_content(chunk_size):
                    fd.write(chunk)
            avatar = Image.open(filepath, 'r').convert("RGBA")

            # make transparent
            datas = avatar.getdata()

            newData = []
            for item in datas:
                if item[0] == 255 and item[1] == 255 and item[2] == 255:
                    newData.append((255, 255, 255, 0))
                else:
                    newData.append(item)

            avatar.putdata(newData)
            avatar.save(filepath, "PNG")

        width, height = (215, 215)
        img = Image.new("RGBA", (width, height), (255, 255, 255))

        ## config
        icon_size = (215, 215)
        ## execute
        avatar = ImageOps.fit(avatar, icon_size, Image.ANTIALIAS)
        bg_w, bg_h = img.size
        offset = 0, 0
        img.paste(avatar, offset, avatar)

        response = HttpResponse(content_type="image/jpeg")
        img.save(response, "JPEG")
        return response
    except IOError as e:
        print(e)
        return err_response
