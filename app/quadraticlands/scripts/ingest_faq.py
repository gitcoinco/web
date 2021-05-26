###
# Script is used to populate QuadLandsFAQ
# docker-compose exec web python3 app/manage.py runscript ingest_coupons.py
#
####

from quadraticlands.models import QuadLandsFAQ  # imports the model

QuadLandsFAQ.objects.all().delete() # clear the table

faqs = [
    {
        'position': '1',
        'question': 'Why is Gitcoin launching a token?',
        'answer': '''<p>The short answer is we know we need to decentralize, and GTC is the best way to do that. Increasingly, more people and projects are using Gitcoin to build and fund digital public goods, and as Gitcoin becomes more popular we are faced with governance questions. </p>

<p>We do not want to be a centralized arbiter, making decisions best left to the community. So we launched GTC to allow the community to actively participate in governing Gitcoin.</p>'''
    },
    {
        'position': '2',
        'question': 'What is the GTC Issuance?',
        'answer': '''<p>100mm tokens: </p>
<p>
<li>50% allocated to the Community Treasury (future builders).</li>
<li>50% allocated to active community members, team members, and investors (past builders).</li>
<li>For a specific allocation breakdown, please see <a href='https://gitcoin.co/quadraticlands/about'>gitcoin.co/quadraticlands/about</a> .</li></p>.'''
    },
    {
        'position': '3',
        'question': 'How do I claim my tokens?',
        'answer': "Follow the instructions <a href='https://gitcoin.co/quadraticlands/missions'>here</a>."
    },
    {
        'position': '4',
        'question': 'Why don’t I have tokens?',
        'answer': "Tokens were airdropped to people who have been active on Gitcoin.co through bounties, hackathons, and grants. If this describes you but you didn’t receive tokens and you think that’s in error, please reach out to the Gitcoin Team in <a href='http://discord.gg/gitcoin'>Discord</a>."
    },
    {
        'position': '5',
        'question': 'What types of things can the community govern with GTC?',
        'answer': 'At first, the community will be able to decide things that have to do with Gitcoin Grants Rounds, like round size and ratification. Gradually the community will govern all aspects of Gitcoin including product features and how the treasury will be allocated.'
    },
    {
        'position': '6',
        'question': 'What is the Gitcoin Stewards Delegation Program?',
        'answer': '''<p>So far one of the biggest challenges of DAO governance is maintaining an active community, which is crucial for legitimacy. To that end, Gitcoin is launching a liquid democracy through a Stewardship Delegation program. How it works:</p>
<p></p>
<p><li>GTC holders have voting rights proportional to the amount of tokens they hold. They may assign their voting rights to community Stewards to vote on their behalf, without giving up their tokens</li>
<li>Stewards are active community members who participate in governance. Their influence is directly determined by the community. The more voting rights assigned to them, the more trust the community has in their stewardship.</li>
<li>Some of Ethereum’s most trusted members have volunteered to be the first Gitcoin Stewards, but anyone may become a Steward simply by accepting voting rights.</li></p>'''
    },
    {
        'position': '7',
        'question': 'Tell me more about Stewardship.',
        'answer': '''<p>The Gitcoin Governance ecosystem is a delegated voting system (liquid democracy) which allows token holders to delegate their voting power to someone else. Community members who have had tokens delegated to them are Stewards, and may vote in on/off chain governance proposals.</p>

<p>Token holders may delegate their voting power to themselves if they wish to participate as Stewards. Stewards who alone or with a group meet quorum (1mm token supply) may submit governance proposals that call for a vote.</p>'''
    },
    {
        'position': '8',
        'question': 'Where does governance happen?',
        'answer': '''<p><li><a href='http://Discord.gg/gitcoin'>Discord</a> is for chatting with your peers and building soft consensus on your ideas. </li>
<li><a href='https://gov.gitcoin.co/'>Gov.gitcoin.co</a> is where governance proposals and discussion happens.</li>
<li><a href='https://snapshot.org/#/gitcoindao.eth'>Snapshot</a> is used for off-chain voting and discussion.</li>
<li><a href='https://www.withtally.com/governance/gitcoin'>Tally</a> is used for on-chain voting.</li></p>'''
    },
    {
        'position': '9',
        'question': 'How do I get involved in governance?',
        'answer': '''Join <a href='http://Discord.gg/gitcoin'>Discord</a> to engage with the community. If you have tokens, delegate them to a community Steward or to yourself if you wish to participate as a Steward. Discuss governance proposals on <a href='https://gov.gitcoin.co/'>gov.gitcoin.co</a>,  or vote on Snapshot <a href='https://snapshot.org/#/gitcoindao.eth'>Snapshot</a>, or <a href='https://www.withtally.com/governance/gitcoin'>Tally</a>.'''
    },
    {
        'position': '10',
        'question': 'What are governance workstreams?',
        'answer': '''These are working groups created around objectives. At the start there will be four workstreams: Public Goods Funding, Ant-Fraud Detection, Progressive Decentralization, and Special Projects. Workstreams will be created/archived as community Stewards see fit. For a larger discussion around Stewards and workstreams, please visit <a href='https://gov.gitcoin.co/'>gov.gitcoin.co</a>.'''
    },
    {
        'position': '11',
        'question': 'What is GitcoinDAO?',
        'answer': 'GitcoinDAO is the community governed org that will be responsible for the future of Gitcoin. We hope it’s the vessel that will take us to Quadratic Lands, the ideal future state where public goods are democratically allocated and appropriately funded.'
    },
    {
        'position': '12',
        'question': 'Will you eventually dissolve Gitcoin as a company?',
        'answer': 'Maybe. Or maybe Gitcoin Holdings will continue on, curating grants or collections. Who knows? But governance over the Gitcoin treasury will eventually be handed over to the community.'
    }
]


for faq in faqs:
    _faq = QuadLandsFAQ(
        position = faq['position'],
        question = faq['question'],
        answer = faq['answer'],
    )
    _faq.save()


print('FAQs Ingested')

exit()
