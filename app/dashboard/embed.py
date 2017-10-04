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


@ratelimit(key='ip', rate='5/m', method=ratelimit.UNSAFE, block=True)
def embed(request):
    # default response 
    could_not_find = Image.new('RGBA', (1, 1), (0,0,0,0))
    err_response = HttpResponse(content_type="image/jpeg")
    could_not_find.save(err_response, "JPEG")

    # params
    repo_url = request.GET.get('repo', False)
    if not repo_url or 'github.com' not in repo_url:
        return err_response

    #get avatar of repo
    _org_name = org_name(repo_url)
    print(_org_name)
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
        avatar = Image.open(filepath, 'r')

    #get issues
    bounties = Bounty.objects.filter(github_url__startswith = repo_url, current_bounty=True).order_by('-web3_created')[:10]

    #try:
    if True:
        #config
        bounty_height = 105
        font_path = 'marketing/quotify/fonts/'
        width = 500
        height_offset = ((max(bounties.count(), 1) + 1) * (bounty_height))
        height = 250 + height_offset
        spacing = 0
        line = "".join(["_" for ele in range(0,47)])

        #setup
        img = Image.new("RGBA", (width, height), (255, 255, 255))
        white = (255, 255, 255)
        black = (0, 0, 0)
        h1 = ImageFont.truetype(font_path + 'Futura-Bold.ttf', 48, encoding="unic")
        h1_thin = ImageFont.truetype(font_path + 'Futura-Normal.ttf', 48, encoding="unic")
        h2_thin = ImageFont.truetype(font_path + 'Futura-Normal.ttf', 28, encoding="unic")
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
        img.paste(back, offset, back)

        # plus sign
        ## config
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
        text = 'Funded Issues'
        #execute 
        text = wrap_text(text, 20)
        draw = ImageDraw.Draw(img)
        img_w, img_h = img.size
        x = 10
        y = 200
        draw.multiline_text(align="center", xy=(x, y), text=text, fill=black, font=h1, spacing=spacing)
        draw = ImageDraw.Draw(img)


        ## config
        text = 'Powered by Gitcoin.co'
        #execute 
        text = wrap_text(text, 20)
        draw = ImageDraw.Draw(img)
        img_w, img_h = img.size
        x = 10
        y = 260
        draw.multiline_text(align="center", xy=(x, y), text=text, fill=black, font=h2_thin, spacing=spacing)
        draw = ImageDraw.Draw(img)

        # put bounty list in there
        i = 0
        for bounty in bounties:
            i += 1
            value_eth = str(round(bounty.value_in_eth/10**18,2)) + "ETH" if bounty.value_in_eth else ""
            value_in_usdt = str(round(bounty.value_in_usdt/10**18,2)) + "USDT" if bounty.value_in_usdt else ""
            value_native = "{} {}".format(round(bounty.value_true, 2), bounty.token_name)

            value = "{}, {}".format(value_eth, value_in_usdt)
            if not value_eth:
                value = value_native
            text = "{}\n{}\n\nWorth: {}".format(line, wrap_text(bounty.title_or_desc, 52), value)
            #execute 
            draw = ImageDraw.Draw(img)
            img_w, img_h = img.size
            x = 10
            y = 210 + (i * bounty_height)
            draw.multiline_text(align="left", xy=(x, y), text=text, fill=black, font=p, spacing=spacing)
            draw = ImageDraw.Draw(img)

        if bounties.count() == 0:

            text = "{}\n\n Post a funded issue at https://gitcoin.co\n\n{}".format(line, line)
            #execute 
            draw = ImageDraw.Draw(img)
            img_w, img_h = img.size
            x = 10
            y = 320
            draw.multiline_text(align="left", xy=(x, y), text=text, fill=black, font=p, spacing=spacing)
            draw = ImageDraw.Draw(img)



        response = HttpResponse(content_type="image/jpeg")
        img.save(response, "JPEG")
        return response
    #except IOError as e:
    #    print(e)
    #    return err_response
