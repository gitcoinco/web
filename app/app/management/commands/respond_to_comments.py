from django.core.management.base import BaseCommand
from app.github import GitHubAPI
from django.conf import settings


def respond_to_comment(comment, response_text, reaction='heart'):
    is_already_responded_to = comment['reactions']['total_count'] > 0
    if is_already_responded_to:
        return False
    comment_from_username = comment['user']['login']
    issue_url_array = comment['issue_url'].split('/')
    user = issue_url_array[4]
    repo = issue_url_array[5]
    issue_num = issue_url_array[7]
    comment_num = comment['id']

    response_text = "@{}, {}".format(comment_from_username, response_text)
    response = GitHubAPI.post_issue_comment_reaction(user, repo, comment_num, reaction)    
    response = GitHubAPI.post_issue_comment(user, repo, issue_num, response_text)    
    return True


def err_msg(comment):
    respond_to_comment(comment, "I don't understand.  Try `{} help` to see the comments I can process.".format('@' + settings.GITHUB_API_USER),"confused")


def process_comment(comment):
    parsed_body = comment['body'].split(' ')
    print(parsed_body)
    if parsed_body[0] != ('@' + settings.GITHUB_API_USER):
        err_msg(comment)
        return
    elif parsed_body[1].lower() == 'help':
        help_menu_body = "I am @{}, a bot that tips **Gitcoin (GTC)** on your behalf.\n".format(settings.GITHUB_API_USER) + \
        "\n" +\
        "<hr>" +\
        "Here are the commands I understand:\n" +\
        "\n" +\
        " * `tip <user> <amount>` -- tips another github user *<amount>* gitcoin.\n" +\
        " * `help` -- displays a help menu\n" +\
        "<hr>" +\
        "\n" +\
        "\n" +\
        "**Gitcoin (GTC)** is a cryptocurrency with real value that can be exchanged for BTC, USD, or any other currency in the world." +\
        "\n" +\
        "<br>" +\
        " Learn more @ [https://gitcoin.co](https://gitcoin.co)\n" +\
        "\n" +\
        ":zap::heart:, {}\n".format("@"+settings.GITHUB_API_USER) +\
        "\n" +\
        "\n" 
        respond_to_comment(comment, help_menu_body, "+1")
        return
    elif parsed_body[1].lower() == 'tip':
        to_user = parsed_body[2].replace('@','')
        amount = parsed_body[3]

        user_response = GitHubAPI.get_user(to_user)
        does_user_exist = user_response.get('message','') != 'Not Found'
        does_sending_user_have_enough_balance = True #TODO
        does_sending_user_have_wallet = True #TODO
        if not does_user_exist:
            respond_to_comment(comment, "No such user.  Please try again. ", "confused")
        elif not amount.isdigit():
            respond_to_comment(comment, "Invalid Amount.  Please try again. ", "confused")
        elif not does_sending_user_have_wallet:
            respond_to_comment(comment, "You do not have a wallet.  Set one up at https://gitcoin.co/get ", "confused")
        elif not does_sending_user_have_enough_balance:
            respond_to_comment(comment, "You do not have enough GTC. Please try again. ", "confused")
        else:
            blockchain_url = "https://etherscan.io/tx/0x97f01c5380f72b15272b4a06a3970c5c2259bbd77909e720e4cc25edbe0c276e" #TODO
            response = "Sent *{}* Gitcoin to {}.  See it on the blockchain at {}".format(amount, "@" + to_user, blockchain_url )
            respond_to_comment(comment, response, "heart")
    else:
        err_msg(comment)
        return
    return


class Command(BaseCommand):

    help = 'gets github comments'

    def handle(self, *args, **options):
        
        comments = GitHubAPI.get_issue_comments('owocki', 'gitcoin')
        print('got {} comments'.format(len(comments)))
        for comment in comments:
            should_respond_to_comment = '@' + settings.GITHUB_API_USER in comment.get('body') \
                and settings.GITHUB_API_USER != comment['user']['login']
            print(should_respond_to_comment)
            if should_respond_to_comment:
                process_comment(comment)



