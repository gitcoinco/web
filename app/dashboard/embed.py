from ratelimit.decorators import ratelimit
from django.http import HttpResponse
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw
from app.github import org_name, get_user
import requests
from dashboard.models import Bounty


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
    return True, "Total: {} issue{}, {} USDT, {}".format(bounties.count(), 's' if bounties.count() != 1 else "", val_usdt, other_values)


@ratelimit(key='ip', rate='50/m', method=ratelimit.UNSAFE, block=True)
def embed(request):
    # default response 
    could_not_find = Image.new('RGBA', (1, 1), (0,0,0,0))
    err_response = HttpResponse(content_type="image/jpeg")
    could_not_find.save(err_response, "JPEG")

    # params
    repo_url = request.GET.get('repo', False)
    if not repo_url or 'github.com' not in repo_url:
        return err_response

    try:
        #get avatar of repo
        _org_name = org_name(repo_url)
        is_org_gitcoin = _org_name == 'gitcoinco'

        avatar = None
        filename = "{}.png".format(_org_name)
        filepath = 'assets/other/avatars/' + filename
        try:
            avatar = Image.open(filepath, 'r')
        except IOError:
            remote_user = get_user(_org_name)
            remote_avatar_url = remote_user['avatar_url']

            r = requests.get(remote_avatar_url, stream=True)
            chunk_size = 20000
            with open(filepath, 'wb') as fd:
                for chunk in r.iter_content(chunk_size):
                    fd.write(chunk)
            avatar = Image.open(filepath, 'r').convert("RGBA")

            #make transparent
            datas = avatar.getdata()

            newData = []
            for item in datas:
                if item[0] == 255 and item[1] == 255 and item[2] == 255:
                    newData.append((255, 255, 255, 0))
                else:
                    newData.append(item)

            avatar.putdata(newData)
            avatar.save(filepath, "PNG")

        #get issues
        length = request.GET.get('len', 10)
        super_bounties = Bounty.objects.filter(github_url__startswith=repo_url, 
            current_bounty=True, 
            network='mainnet', 
            idx_status='open').order_by('-_val_usd_db')
        bounties = super_bounties[:length]

        #config
        bounty_height = 145
        bounty_width = 400
        font_path = 'marketing/quotify/fonts/'
        width = 1350
        height = 350
        spacing = 0
        line = "".join(["_" for ele in range(0,47)])

        #setup
        img = Image.new("RGBA", (width, height), (255, 255, 255))
        white = (255, 255, 255)
        black = (0, 0, 0)
        h1 = ImageFont.truetype(font_path + 'Futura-Bold.ttf', 28, encoding="unic")
        h1_thin = ImageFont.truetype(font_path + 'Futura-Normal.ttf', 28, encoding="unic")
        h2_thin = ImageFont.truetype(font_path + 'Futura-Normal.ttf', 22, encoding="unic")
        p = ImageFont.truetype(font_path + 'Futura-LightBT.ttf', 20, encoding="unic")
        p_bold = ImageFont.truetype(font_path + 'Futura-Bold.ttf', 20, encoding="unic")

        # background
        ## config
        logo = 'assets/v2/images/header-bg-light.jpg'
        ## execute
        back = Image.open(logo, 'r')
        img_w, img_h = back.size
        bg_w, bg_h = img.size
        offset = 0,0
        img.paste(back, offset)

        # repo logo
        ## config
        icon_size = (215, 215)
        ## execute
        img_w, img_h = avatar.size
        avatar.thumbnail(icon_size, Image.ANTIALIAS)
        bg_w, bg_h = img.size
        offset = 10,10
        img.paste(avatar, offset, avatar)

        # gitcoin logo
        ## config
        logo = 'assets/v2/images/gitcoinco.png'
        ## execute
        back = Image.open(logo, 'r')
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
            #execute 
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
        #execute 
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
        #execute 
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
            value_eth = str(round(bounty.value_in_eth/10**18,2)) + "ETH" if bounty.value_in_eth else ""
            value_in_usdt = str(round(bounty.value_in_usdt,2)) + "USDT" if bounty.value_in_usdt else ""
            value_native = "{} {}".format(round(bounty.value_true, 2), bounty.token_name)

            value = "{}, {}".format(value_eth, value_in_usdt)
            if not value_eth:
                value = value_native
            text = "{}{}\n{}\n\nWorth: {}".format("", line, wrap_text(bounty.title_or_desc, 30), value)
            #execute 
            draw = ImageDraw.Draw(img)
            img_w, img_h = img.size
            line_size =2
            x = 500 + (int((i-1)/line_size) * (bounty_width))
            y = 30 + (abs(i%line_size-1) * bounty_height)
            draw.multiline_text(align="left", xy=(x, y), text=text, fill=black, font=p, spacing=spacing)
            draw = ImageDraw.Draw(img)

        if bounties.count() == 0:

            text = "{}\n\n{}\n\n{}".format(line, wrap_text("No active issues. Post a funded issue at https://gitcoin.co", 50), line)
            #execute 
            draw = ImageDraw.Draw(img)
            img_w, img_h = img.size
            x = 10
            y = 320
            draw.multiline_text(align="left", xy=(x, y), text=text, fill=black, font=p, spacing=spacing)
            draw = ImageDraw.Draw(img)

        if bounties.count() != 0:
            ## config
            text = 'Browse Issues @ https://gitcoin.co/explorer'
            #execute 
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
    could_not_find = Image.new('RGBA', (1, 1), (0,0,0,0))
    err_response = HttpResponse(content_type="image/jpeg")
    could_not_find.save(err_response, "JPEG")

    # params
    repo_url = request.GET.get('repo', False)
    if not repo_url or 'github.com' not in repo_url:
        return err_response

    try:
        #get avatar of repo
        _org_name = org_name(repo_url)

        avatar = None
        filename = "{}.png".format(_org_name)
        filepath = 'assets/other/avatars/' + filename
        try:
            avatar = Image.open(filepath, 'r')
        except IOError:
            remote_user = get_user(_org_name)
            remote_avatar_url = remote_user['avatar_url']

            r = requests.get(remote_avatar_url, stream=True)
            chunk_size = 20000
            with open(filepath, 'wb') as fd:
                for chunk in r.iter_content(chunk_size):
                    fd.write(chunk)
            avatar = Image.open(filepath, 'r').convert("RGBA")

            #make transparent
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
        white = (255, 255, 255)
        black = (0, 0, 0)


        ## config
        icon_size = (215, 215)
        ## execute
        img_w, img_h = avatar.size
        avatar.thumbnail(icon_size, Image.ANTIALIAS)
        bg_w, bg_h = img.size
        offset = 0,0 
        img.paste(avatar, offset, avatar)


        response = HttpResponse(content_type="image/jpeg")
        img.save(response, "JPEG")
        return response
    except IOError as e:
        print(e)
        return err_response

