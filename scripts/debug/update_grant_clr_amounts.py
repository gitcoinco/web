from grants.models import Grant

eles = 'Prysm by Prysmatic Labs $4,306.03','MolochDAO $2,839.74','Uniswap $2,121.57','Cryptoeconomics.study - Free, Open-Source Blockchain Course $2,071.84','Lodestar (eth2.0 client) $1,702.61','ZoKrates $1,604.32','Plasma Group $1,572.80','Lighthouse: Ethereum 2.0 Client $1,460.16','EthHub - Ethereum Information Hub $1,407.90','ethers.js - Complete, Simple and Tiny $1,357.51','The Gitcoin Open Source Support Fund $999.87','Burner Wallet $984.69','Connext Network $738.26','Implement support for asyncio using Web3.py $542.66','Zero Knowledge Podcast $374.30','Gossipsub and Eth 2 / Shasper Development $344.54','ETH2.0 Implementers Call Notes $202.83','Yeeth $145.38','FISSION Codes $85.66','Vipnode $83.44','Whiteblock Testing $22.94','Ethereum All Core Devs community project management $17.11','Peepeth: social network for a better world $6.73','GrantOps $6.42','EVM Evolution $0.64','ChainID Network $0.06'
for ele in eles:
    arr = ele.split('$')
    title = arr[0].strip()
    amount = float(arr[1].replace(",", '').strip())

    grant = Grant.objects.filter(title=title, active=True).first()
    print(title,grant.pk, amount)
    grant.clr_matching = amount
    grant.save()    
