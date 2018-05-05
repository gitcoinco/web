# Change Log

## [HEAD](https://github.com/gitcoinco/web/tree/HEAD)

[Full Changelog](https://github.com/gitcoinco/web/compare/pre-pr884...HEAD)

**Implemented enhancements:**

- Gitcoin Bot Enhancements [\#1040](https://github.com/gitcoinco/web/issues/1040)
- fixes https://github.com/gitcoinco/web/issues/1040 [\#1043](https://github.com/gitcoinco/web/pull/1043) ([owocki](https://github.com/owocki))
- drastically improve api read performance [\#1026](https://github.com/gitcoinco/web/pull/1026) ([owocki](https://github.com/owocki))
- bounty: unify modal designs [\#809](https://github.com/gitcoinco/web/pull/809) ([sethmcleod](https://github.com/sethmcleod))

**Fixed bugs:**

- Gitcoinbot work submitted message has weird formatting [\#1063](https://github.com/gitcoinco/web/issues/1063)

**Closed issues:**

- JSONDecodeError: Expecting value: line 1 column 1 \(char 0\) [\#1057](https://github.com/gitcoinco/web/issues/1057)
- Misalignment with arrows on new page [\#1056](https://github.com/gitcoinco/web/issues/1056)
- Cannot read property 'split' of undefined [\#1025](https://github.com/gitcoinco/web/issues/1025)
- Explorer multiselect "Any" option doesn't behave as expected [\#1011](https://github.com/gitcoinco/web/issues/1011)
- Unify Modal Designs [\#430](https://github.com/gitcoinco/web/issues/430)

**Merged pull requests:**

- fix toggle any filter [\#1065](https://github.com/gitcoinco/web/pull/1065) ([joshmorel](https://github.com/joshmorel))
- css: funding / killing form update  [\#1061](https://github.com/gitcoinco/web/pull/1061) ([thelostone-mc](https://github.com/thelostone-mc))
- gives staff the ability to remove users from a bounty [\#1042](https://github.com/gitcoinco/web/pull/1042) ([owocki](https://github.com/owocki))
- logs abandoned work and prevents users from starting new work bc of it [\#1039](https://github.com/gitcoinco/web/pull/1039) ([owocki](https://github.com/owocki))
- staggers cron start times [\#1034](https://github.com/gitcoinco/web/pull/1034) ([owocki](https://github.com/owocki))
- Slack Welcomebot on AWS Lambda [\#1017](https://github.com/gitcoinco/web/pull/1017) ([mbeacom](https://github.com/mbeacom))
- sets default search project status to 'any' [\#936](https://github.com/gitcoinco/web/pull/936) ([owocki](https://github.com/owocki))
- ftux: birth [\#889](https://github.com/gitcoinco/web/pull/889) ([thelostone-mc](https://github.com/thelostone-mc))
- WIP: Update FaucetRequest with FK to Profile [\#884](https://github.com/gitcoinco/web/pull/884) ([mbeacom](https://github.com/mbeacom))

## [pre-pr884](https://github.com/gitcoinco/web/tree/pre-pr884) (2018-04-30)
[Full Changelog](https://github.com/gitcoinco/web/compare/20180416...pre-pr884)

**Fixed bugs:**

- Faucet translation isn't rendering properly [\#1032](https://github.com/gitcoinco/web/issues/1032)
- NoReverseMatch: Reverse for 'viz\_index' not found. 'viz\_index' is not a valid view function or pattern name. [\#1022](https://github.com/gitcoinco/web/issues/1022)
- Gitcoin bot 2nd attempt doesn't render properly [\#991](https://github.com/gitcoinco/web/issues/991)
- BE tests currently failing [\#953](https://github.com/gitcoinco/web/issues/953)
- \[BUG\] The User Menu is Covered on TX Confirmation Screen [\#924](https://github.com/gitcoinco/web/issues/924)
- Gitcoinbot did not comment when bounty was posted [\#915](https://github.com/gitcoinco/web/issues/915)
- No unsupported network alert on bounty funding [\#773](https://github.com/gitcoinco/web/issues/773)
- Modify setup\_lang to use User [\#980](https://github.com/gitcoinco/web/pull/980) ([mbeacom](https://github.com/mbeacom))
- expiration tests fix [\#913](https://github.com/gitcoinco/web/pull/913) ([kziemianek](https://github.com/kziemianek))

**Closed issues:**

- DoesNotExist: Profile matching query does not exist. [\#1008](https://github.com/gitcoinco/web/issues/1008)
- AttributeError: 'AnonymousUser' object has no attribute 'profile' [\#1005](https://github.com/gitcoinco/web/issues/1005)
- testaroooooooo 123 [\#996](https://github.com/gitcoinco/web/issues/996)
- Updating user notification preferences fails and returns \(403\) CSRF verification failed [\#988](https://github.com/gitcoinco/web/issues/988)
- Resolve pytest / travis failures [\#987](https://github.com/gitcoinco/web/issues/987)
- error when submitting faucet request [\#979](https://github.com/gitcoinco/web/issues/979)
- TypeError: bad operand type for unary +: 'str' [\#976](https://github.com/gitcoinco/web/issues/976)
- AttributeError: 'NoneType' object has no attribute 'email' [\#954](https://github.com/gitcoinco/web/issues/954)
- test 123 [\#949](https://github.com/gitcoinco/web/issues/949)
- Issue explorer don't show issue in case gas price has been changed [\#945](https://github.com/gitcoinco/web/issues/945)
- ConnectionError: HTTPSConnectionPool\(host='ipfs.infura.io', port=5001\): Max retries exceeded with url: /api/v0/cat/QmXxkBASF92QvFFwChwZAECSRsjoMstMHJ2A9bwXuchXbA \(Caused by NewConnectionError\('\<urllib3.connection.VerifiedHTTPSConnection object at 0x7f6791 [\#932](https://github.com/gitcoinco/web/issues/932)
- Test is a test issue [\#929](https://github.com/gitcoinco/web/issues/929)
- As a user, I would should be informed when I no longer need to keep tip confirmation window open [\#928](https://github.com/gitcoinco/web/issues/928)
- AttributeError: 'JsonResponse' object has no attribute 'read' [\#921](https://github.com/gitcoinco/web/issues/921)
- AttributeError: 'LeaderboardRank' object has no attribute 'local\_avatar\_url' [\#914](https://github.com/gitcoinco/web/issues/914)
- Design Funder Landing Page [\#908](https://github.com/gitcoinco/web/issues/908)
- Test title [\#907](https://github.com/gitcoinco/web/issues/907)
- 404 after logout at profile page [\#905](https://github.com/gitcoinco/web/issues/905)
- Navbar responsive issue [\#903](https://github.com/gitcoinco/web/issues/903)
- as a submitter, i want to link my github PR when i submit work, so i can show off what i did [\#893](https://github.com/gitcoinco/web/issues/893)
- design - as a user, i want a quarterly 'my stats' email, so i can see my activity on the platform [\#892](https://github.com/gitcoinco/web/issues/892)
- `make fix` stylelint error [\#877](https://github.com/gitcoinco/web/issues/877)
- timezone issues with opened date [\#876](https://github.com/gitcoinco/web/issues/876)
- as a repo owner, i want to be able to approve people who've started work, so i can filter those who i want to work with [\#812](https://github.com/gitcoinco/web/issues/812)
- design - gitcoin.co/activity [\#804](https://github.com/gitcoinco/web/issues/804)
- Allow the user to set different language for the Gitcoin app [\#802](https://github.com/gitcoinco/web/issues/802)
- BadFunctionCallOutput: Could not decode contract function call getBountyData return data b'' for output\_types \['string'\] [\#742](https://github.com/gitcoinco/web/issues/742)
- BadFunctionCallOutput: Could not decode contract function call getBountyToken return data b'' for output\_types \['address'\] [\#727](https://github.com/gitcoinco/web/issues/727)
- BadFunctionCallOutput: Could not decode contract function call getFulfillment return data b'' for output\_types \['bool', 'address', 'string'\] [\#726](https://github.com/gitcoinco/web/issues/726)
- coding -  /mentors page [\#725](https://github.com/gitcoinco/web/issues/725)
- as a user, i want upvotes / downvotes on tool page, so i can cast my vote on gitcoin's tool direction [\#706](https://github.com/gitcoinco/web/issues/706)
- FieldError: Invalid order\_by arguments: \['-web3\_created/'\] [\#701](https://github.com/gitcoinco/web/issues/701)
- Gitcoin should monitoring issue pull request as well [\#696](https://github.com/gitcoinco/web/issues/696)
- refactor bounty.value\_in\_usdt into two functions [\#693](https://github.com/gitcoinco/web/issues/693)
- Notify Gitcoin/Funder that Developer is Starting Work [\#683](https://github.com/gitcoinco/web/issues/683)
- \(DESIGN\) As a user, I want a Blockchain Job Board so I can find professional work in the space [\#540](https://github.com/gitcoinco/web/issues/540)
- Handle multiple bounties per github issue URL [\#533](https://github.com/gitcoinco/web/issues/533)
- Fund an Issue Suggestion/FTUX [\#529](https://github.com/gitcoinco/web/issues/529)
- Display Tips on Leaderboard [\#522](https://github.com/gitcoinco/web/issues/522)
- How to Get Started \(Repo Maintainer\) [\#517](https://github.com/gitcoinco/web/issues/517)
- Http404 [\#481](https://github.com/gitcoinco/web/issues/481)
- new\_bounty marketing emails need to be moved to a background job [\#477](https://github.com/gitcoinco/web/issues/477)
- Clean Up Bounty Creation Flow [\#429](https://github.com/gitcoinco/web/issues/429)
- Functioning Search Field [\#412](https://github.com/gitcoinco/web/issues/412)
- As a core team member, i want to Track deploys & releases for faster debugging [\#405](https://github.com/gitcoinco/web/issues/405)
- \(unknown\): Uncaught this network is not supported in bounty\_address\(\) for gitcoin [\#362](https://github.com/gitcoinco/web/issues/362)
- Add slack bot integration [\#259](https://github.com/gitcoinco/web/issues/259)
- As a team member, I'd like to be on the /about page, so I can show off that I'm part of the team. [\#222](https://github.com/gitcoinco/web/issues/222)

**Merged pull requests:**

- fixes for https://gitcoincommunity.slack.com/archives/C8E45J5D0/p1525097521000711 [\#1024](https://github.com/gitcoinco/web/pull/1024) ([owocki](https://github.com/owocki))
- slack welcome messages [\#1012](https://github.com/gitcoinco/web/pull/1012) ([owocki](https://github.com/owocki))
- hotfix: wait for approval to issue bounty [\#1006](https://github.com/gitcoinco/web/pull/1006) ([owocki](https://github.com/owocki))
- adds rates estimate on bounty details page [\#998](https://github.com/gitcoinco/web/pull/998) ([owocki](https://github.com/owocki))
- Action URLS Cleanup \(and other goodies\) [\#983](https://github.com/gitcoinco/web/pull/983) ([owocki](https://github.com/owocki))
- Notify Gitcoin/Funder that Developer is Starting Work [\#981](https://github.com/gitcoinco/web/pull/981) ([darkdarkdragon](https://github.com/darkdarkdragon))
- unsupported network warnings when trying to do an aciton on a network we dont support [\#978](https://github.com/gitcoinco/web/pull/978) ([owocki](https://github.com/owocki))
- warnings when youre looking at a non mainnet bounty [\#977](https://github.com/gitcoinco/web/pull/977) ([owocki](https://github.com/owocki))
- pricing brackets [\#972](https://github.com/gitcoinco/web/pull/972) ([owocki](https://github.com/owocki))
- Adds bounty flow doc to readme [\#956](https://github.com/gitcoinco/web/pull/956) ([owocki](https://github.com/owocki))
- Add slack bot integration  [\#955](https://github.com/gitcoinco/web/pull/955) ([darkdarkdragon](https://github.com/darkdarkdragon))
- smarter github notifications [\#948](https://github.com/gitcoinco/web/pull/948) ([owocki](https://github.com/owocki))
- Tool modifications [\#944](https://github.com/gitcoinco/web/pull/944) ([mbeacom](https://github.com/mbeacom))
- track hours worked on fulfillment [\#942](https://github.com/gitcoinco/web/pull/942) ([owocki](https://github.com/owocki))
- about: Fix Origin Story [\#933](https://github.com/gitcoinco/web/pull/933) ([thelostone-mc](https://github.com/thelostone-mc))
- verboseness of gitcoinbot reminders [\#931](https://github.com/gitcoinco/web/pull/931) ([owocki](https://github.com/owocki))
- more feedback emails [\#930](https://github.com/gitcoinco/web/pull/930) ([owocki](https://github.com/owocki))
- bounty: hide timeline on cancelled bounties [\#922](https://github.com/gitcoinco/web/pull/922) ([thelostone-mc](https://github.com/thelostone-mc))
- fixes https://github.com/gitcoinco/web/issues/876 [\#919](https://github.com/gitcoinco/web/pull/919) ([owocki](https://github.com/owocki))
- make expiration status less inclusive [\#918](https://github.com/gitcoinco/web/pull/918) ([owocki](https://github.com/owocki))
- about: core team design revamp [\#916](https://github.com/gitcoinco/web/pull/916) ([thelostone-mc](https://github.com/thelostone-mc))
- navbar responsive issues [\#904](https://github.com/gitcoinco/web/pull/904) ([kziemianek](https://github.com/kziemianek))
- avatar cleanup - and adds the ability to blend in the gitcoin logo to an avatar [\#902](https://github.com/gitcoinco/web/pull/902) ([owocki](https://github.com/owocki))
- ability to add a pr link to work submission [\#900](https://github.com/gitcoinco/web/pull/900) ([owocki](https://github.com/owocki))
- nav + explorer fixes [\#890](https://github.com/gitcoinco/web/pull/890) ([thelostone-mc](https://github.com/thelostone-mc))
- Upgrade deb image to Stretch [\#888](https://github.com/gitcoinco/web/pull/888) ([mbeacom](https://github.com/mbeacom))
- Added team bios and community member links to /about page [\#887](https://github.com/gitcoinco/web/pull/887) ([jakerockland](https://github.com/jakerockland))
- WIP - d3 data viz experiments [\#886](https://github.com/gitcoinco/web/pull/886) ([owocki](https://github.com/owocki))
- dashboard: Tests cleanup. [\#857](https://github.com/gitcoinco/web/pull/857) ([cryptomental](https://github.com/cryptomental))
- preferred language [\#810](https://github.com/gitcoinco/web/pull/810) ([kziemianek](https://github.com/kziemianek))
- Initial commit for Search functionality [\#790](https://github.com/gitcoinco/web/pull/790) ([eswarasai](https://github.com/eswarasai))
- Tool voting [\#763](https://github.com/gitcoinco/web/pull/763) ([kziemianek](https://github.com/kziemianek))

## [20180416](https://github.com/gitcoinco/web/tree/20180416) (2018-04-16)
[Full Changelog](https://github.com/gitcoinco/web/compare/20180415master...20180416)

**Implemented enhancements:**

- Detect GitHub issue activity other than comments [\#458](https://github.com/gitcoinco/web/pull/458) ([JakeStoeffler](https://github.com/JakeStoeffler))

**Fixed bugs:**

- Cannot submit work [\#883](https://github.com/gitcoinco/web/issues/883)
- feedback crm just went a little haywire [\#873](https://github.com/gitcoinco/web/issues/873)

**Closed issues:**

- TypeError: Object of type '\_\_proxy\_\_' is not JSON serializable [\#844](https://github.com/gitcoinco/web/issues/844)
- Detect "Referencing" as "Work" [\#576](https://github.com/gitcoinco/web/issues/576)

**Merged pull requests:**

- Add admin link to navbar for staff and switch settings icon [\#899](https://github.com/gitcoinco/web/pull/899) ([mbeacom](https://github.com/mbeacom))
- adds tutorials on help page [\#898](https://github.com/gitcoinco/web/pull/898) ([owocki](https://github.com/owocki))
- Github comments when user is warned/removed \(in addition to the emails that are sent when this happens\) [\#897](https://github.com/gitcoinco/web/pull/897) ([owocki](https://github.com/owocki))

## [20180415master](https://github.com/gitcoinco/web/tree/20180415master) (2018-04-16)
[Full Changelog](https://github.com/gitcoinco/web/compare/pre-853...20180415master)

**Implemented enhancements:**

- Feature/refactor value in usdt [\#853](https://github.com/gitcoinco/web/pull/853) ([cryptomental](https://github.com/cryptomental))

**Fixed bugs:**

- Bounty details screen on mobile not responsive [\#759](https://github.com/gitcoinco/web/issues/759)

**Closed issues:**

- Incorrect dollar value shown for bounties [\#879](https://github.com/gitcoinco/web/issues/879)
- As a user, I want to break apart my email settings and my profile settings [\#795](https://github.com/gitcoinco/web/issues/795)

**Merged pull requests:**

- Update Travis pipeline to use new stages [\#885](https://github.com/gitcoinco/web/pull/885) ([mbeacom](https://github.com/mbeacom))
- identify trust wallet [\#882](https://github.com/gitcoinco/web/pull/882) ([kziemianek](https://github.com/kziemianek))
- new nav for auth/login for site [\#881](https://github.com/gitcoinco/web/pull/881) ([owocki](https://github.com/owocki))
- status update dates on the bounty model [\#878](https://github.com/gitcoinco/web/pull/878) ([owocki](https://github.com/owocki))
- new\_bounty emails [\#867](https://github.com/gitcoinco/web/pull/867) ([owocki](https://github.com/owocki))
- in my settings, i should be able to disguise myself from the leaderboard/having a profile [\#745](https://github.com/gitcoinco/web/pull/745) ([owocki](https://github.com/owocki))

## [pre-853](https://github.com/gitcoinco/web/tree/pre-853) (2018-04-12)
[Full Changelog](https://github.com/gitcoinco/web/compare/pre-django-auth-redux...pre-853)

**Fixed bugs:**

- admin login broken in prod [\#871](https://github.com/gitcoinco/web/issues/871)

**Closed issues:**

- AttributeError: 'NoneType' object has no attribute 'email' [\#872](https://github.com/gitcoinco/web/issues/872)
- This is a test bounty for demo purposes [\#868](https://github.com/gitcoinco/web/issues/868)
- As a user, I only want to receive 1 match email per day, so I dont unsubscribe [\#454](https://github.com/gitcoinco/web/issues/454)

**Merged pull requests:**

- Django Auth Redux [\#862](https://github.com/gitcoinco/web/pull/862) ([mbeacom](https://github.com/mbeacom))

## [pre-django-auth-redux](https://github.com/gitcoinco/web/tree/pre-django-auth-redux) (2018-04-11)
[Full Changelog](https://github.com/gitcoinco/web/compare/pre-django-auth-1...pre-django-auth-redux)

**Implemented enhancements:**

- responsive profile [\#825](https://github.com/gitcoinco/web/pull/825) ([kziemianek](https://github.com/kziemianek))

**Fixed bugs:**

- Broken profile markup [\#817](https://github.com/gitcoinco/web/issues/817)
- alpha tag confusion [\#792](https://github.com/gitcoinco/web/issues/792)
- Fixed heights in tips list [\#787](https://github.com/gitcoinco/web/issues/787)
- Funded issues are shown up as expiring in search results [\#783](https://github.com/gitcoinco/web/issues/783)
- fix for bouty details buttons padding [\#842](https://github.com/gitcoinco/web/pull/842) ([kziemianek](https://github.com/kziemianek))
- Bean/fix typos [\#829](https://github.com/gitcoinco/web/pull/829) ([StareIntoTheBeard](https://github.com/StareIntoTheBeard))

**Closed issues:**

- update can\_submit\_after\_expiration\_date  [\#855](https://github.com/gitcoinco/web/issues/855)
- Request Funding Increase [\#849](https://github.com/gitcoinco/web/issues/849)
- Expired bounty invalid days ago counter [\#839](https://github.com/gitcoinco/web/issues/839)
- Canceled Bounty gitcoinbot github message was wrong [\#838](https://github.com/gitcoinco/web/issues/838)
- bounty detail page - button padding is messed up at certain resolutions [\#836](https://github.com/gitcoinco/web/issues/836)
- IndexError: list index out of range [\#835](https://github.com/gitcoinco/web/issues/835)
- AssertionError: Cannot filter a query once a slice has been taken. [\#833](https://github.com/gitcoinco/web/issues/833)
- 'done' bounties should not have the time left field visible [\#824](https://github.com/gitcoinco/web/issues/824)
- comment needs left padding [\#823](https://github.com/gitcoinco/web/issues/823)
- RelatedObjectDoesNotExist: User has no profile. [\#820](https://github.com/gitcoinco/web/issues/820)
- Document and check all possible status values [\#816](https://github.com/gitcoinco/web/issues/816)
- Logo width is incorrect [\#808](https://github.com/gitcoinco/web/issues/808)
- Performance Updates [\#777](https://github.com/gitcoinco/web/issues/777)
- design - /mentors page [\#565](https://github.com/gitcoinco/web/issues/565)
- Update Gitcoin Email Designs [\#563](https://github.com/gitcoinco/web/issues/563)
- Code - /pitch pages [\#506](https://github.com/gitcoinco/web/issues/506)
- Price fluctuates on the explorer stats page [\#491](https://github.com/gitcoinco/web/issues/491)
- As a site admin, I want a Gitcoin Drip Marketing Campaign that explains our vision \(and how to use Gitcoin\) over time, so we can enable our users to be successful. [\#448](https://github.com/gitcoinco/web/issues/448)
- I want to see the progress of my newly created bounty tickets [\#422](https://github.com/gitcoinco/web/issues/422)
- Issue Explorer Details Page V2 [\#419](https://github.com/gitcoinco/web/issues/419)

**Merged pull requests:**

- Add ipdb and django shell access to docker setup [\#863](https://github.com/gitcoinco/web/pull/863) ([mbeacom](https://github.com/mbeacom))
- docker shell fixes [\#861](https://github.com/gitcoinco/web/pull/861) ([owocki](https://github.com/owocki))
- fix expiration tests [\#860](https://github.com/gitcoinco/web/pull/860) ([kziemianek](https://github.com/kziemianek))
- update can\_submit\_after\_expiration\_date  [\#856](https://github.com/gitcoinco/web/pull/856) ([owocki](https://github.com/owocki))
- fix for Expired bounty invalid days ago counter [\#840](https://github.com/gitcoinco/web/pull/840) ([owocki](https://github.com/owocki))
- bounty: hide progress bar on work done status [\#828](https://github.com/gitcoinco/web/pull/828) ([thelostone-mc](https://github.com/thelostone-mc))
- Fixes: https://github.com/gitcoinco/web/issues/792 [\#827](https://github.com/gitcoinco/web/pull/827) ([willsputra](https://github.com/willsputra))
- docker / github login instructions [\#822](https://github.com/gitcoinco/web/pull/822) ([owocki](https://github.com/owocki))
- todos should be falsy [\#821](https://github.com/gitcoinco/web/pull/821) ([owocki](https://github.com/owocki))
- Django auth [\#818](https://github.com/gitcoinco/web/pull/818) ([mbeacom](https://github.com/mbeacom))
- bug fix : bounty + landing + dashboard [\#807](https://github.com/gitcoinco/web/pull/807) ([thelostone-mc](https://github.com/thelostone-mc))
- bounty: added progress bar [\#764](https://github.com/gitcoinco/web/pull/764) ([thelostone-mc](https://github.com/thelostone-mc))
- bounty: mobile alignment fix [\#762](https://github.com/gitcoinco/web/pull/762) ([thelostone-mc](https://github.com/thelostone-mc))
- Email design update  [\#746](https://github.com/gitcoinco/web/pull/746) ([jakerockland](https://github.com/jakerockland))

## [pre-django-auth-1](https://github.com/gitcoinco/web/tree/pre-django-auth-1) (2018-04-06)
[Full Changelog](https://github.com/gitcoinco/web/compare/pre-django-auth...pre-django-auth-1)

**Implemented enhancements:**

- Profile should make use of the django user framework [\#312](https://github.com/gitcoinco/web/issues/312)

**Closed issues:**

- See what my last actions were when I logged in \(as bounty funder\). [\#423](https://github.com/gitcoinco/web/issues/423)

**Merged pull requests:**

- bounty: fixed avatar url + tooltip style [\#784](https://github.com/gitcoinco/web/pull/784) ([thelostone-mc](https://github.com/thelostone-mc))
- bounty : minor changes [\#768](https://github.com/gitcoinco/web/pull/768) ([thelostone-mc](https://github.com/thelostone-mc))
- Add django auth framework [\#574](https://github.com/gitcoinco/web/pull/574) ([mbeacom](https://github.com/mbeacom))

## [pre-django-auth](https://github.com/gitcoinco/web/tree/pre-django-auth) (2018-04-06)
[Full Changelog](https://github.com/gitcoinco/web/compare/20180404-template-1...pre-django-auth)

**Fixed bugs:**

- the big 'profile might need a redesign or some bugfixes' thread. [\#580](https://github.com/gitcoinco/web/issues/580)

**Closed issues:**

- "ReferenceError: Accounts is not defined" Error printed to console when sending a tip [\#806](https://github.com/gitcoinco/web/issues/806)
- As a user, I would like to view profile bounties, repos, etc in a paginated fashion [\#550](https://github.com/gitcoinco/web/issues/550)
- An easy way to read the list of funded issues on my profile page [\#424](https://github.com/gitcoinco/web/issues/424)

## [20180404-template-1](https://github.com/gitcoinco/web/tree/20180404-template-1) (2018-04-05)
[Full Changelog](https://github.com/gitcoinco/web/compare/20180404-template-0...20180404-template-1)

## [20180404-template-0](https://github.com/gitcoinco/web/tree/20180404-template-0) (2018-04-05)
[Full Changelog](https://github.com/gitcoinco/web/compare/20180404-base-template...20180404-template-0)

## [20180404-base-template](https://github.com/gitcoinco/web/tree/20180404-base-template) (2018-04-04)
[Full Changelog](https://github.com/gitcoinco/web/compare/pre-728...20180404-base-template)

**Closed issues:**

- Groundwork for Internationalization \(Translation of App to Other Languages\) [\#642](https://github.com/gitcoinco/web/issues/642)

**Merged pull requests:**

- stylelint:fix info in CONTRIBUTING.md [\#803](https://github.com/gitcoinco/web/pull/803) ([kziemianek](https://github.com/kziemianek))
- Limit Profile stat results to valid bounties [\#791](https://github.com/gitcoinco/web/pull/791) ([mbeacom](https://github.com/mbeacom))
- Fixes: https://github.com/gitcoinco/web/issues/642 [\#728](https://github.com/gitcoinco/web/pull/728) ([bakaoh](https://github.com/bakaoh))

## [pre-728](https://github.com/gitcoinco/web/tree/pre-728) (2018-04-04)
[Full Changelog](https://github.com/gitcoinco/web/compare/pre-684-responsive-cleanup...pre-728)

**Closed issues:**

- Responsive Design Issues On The Gitcoin Website [\#684](https://github.com/gitcoinco/web/issues/684)

## [pre-684-responsive-cleanup](https://github.com/gitcoinco/web/tree/pre-684-responsive-cleanup) (2018-04-04)
[Full Changelog](https://github.com/gitcoinco/web/compare/pre_web3_awareness_reafctor...pre-684-responsive-cleanup)

**Implemented enhancements:**

- 'my projects' tab should be greyed out if user is not logged in [\#769](https://github.com/gitcoinco/web/issues/769)
- Issue Explorer Detail [\#737](https://github.com/gitcoinco/web/issues/737)
- issue funder should be able to stop work [\#666](https://github.com/gitcoinco/web/issues/666)
- Investigate Image Compression Across Gitcoin for Performance Improvements  [\#608](https://github.com/gitcoinco/web/issues/608)
- inline validations [\#554](https://github.com/gitcoinco/web/issues/554)
- Need to be able to stop work bounties as the funder [\#463](https://github.com/gitcoinco/web/issues/463)
- standardbounties: automatically cross-process bounties posted to bounties.network to gitcoin [\#268](https://github.com/gitcoinco/web/issues/268)
- Static handling and cache invalidation [\#262](https://github.com/gitcoinco/web/issues/262)
- css: rebirth of the bounty [\#691](https://github.com/gitcoinco/web/pull/691) ([thelostone-mc](https://github.com/thelostone-mc))
- fixing some width, flex, and spacing issues as discovered in issue \#684 [\#688](https://github.com/gitcoinco/web/pull/688) ([joshmobley](https://github.com/joshmobley))
- changed all target=new to target=\_blank with rel=noopener [\#677](https://github.com/gitcoinco/web/pull/677) ([michelgotta](https://github.com/michelgotta))
- revamped tool page [\#672](https://github.com/gitcoinco/web/pull/672) ([owocki](https://github.com/owocki))
- Inline validations [\#571](https://github.com/gitcoinco/web/pull/571) ([KennethAshley](https://github.com/KennethAshley))

**Fixed bugs:**

- Getting an Error When Trying to Tip User [\#776](https://github.com/gitcoinco/web/issues/776)
- Issue Explorer Check-box Undone [\#744](https://github.com/gitcoinco/web/issues/744)
- after sending tip, blue alert that should have had a success message in it said 'undefined' [\#687](https://github.com/gitcoinco/web/issues/687)
- refresh\_bounties empty URL bug [\#686](https://github.com/gitcoinco/web/issues/686)
- TypeError: Object of type 'BountyFulfillment' is not JSON serializable [\#678](https://github.com/gitcoinco/web/issues/678)
- loading page is busted [\#653](https://github.com/gitcoinco/web/issues/653)
- KeyError: 'token' [\#649](https://github.com/gitcoinco/web/issues/649)
- standard bounties: multiple bounties per issue URL [\#251](https://github.com/gitcoinco/web/issues/251)
- standardbounties: if you try to fulfill a bounty that doesnt exist it spins forever [\#250](https://github.com/gitcoinco/web/issues/250)
- bug: need auto refresh on gitcoin submission pending page [\#179](https://github.com/gitcoinco/web/issues/179)
- explorer: added missing css stylesheet [\#747](https://github.com/gitcoinco/web/pull/747) ([thelostone-mc](https://github.com/thelostone-mc))
- html: removed extra css link from header.html [\#739](https://github.com/gitcoinco/web/pull/739) ([thelostone-mc](https://github.com/thelostone-mc))

**Closed issues:**

- test 123 [\#788](https://github.com/gitcoinco/web/issues/788)
- Really thin kill bounty screen [\#786](https://github.com/gitcoinco/web/issues/786)
- messed up CSS on https://gitcoin.co/funding/process [\#780](https://github.com/gitcoinco/web/issues/780)
- avatar\_url is wrong [\#779](https://github.com/gitcoinco/web/issues/779)
- Hardcoded year in emails copyright section. [\#765](https://github.com/gitcoinco/web/issues/765)
- Contributing Link in README.md doesn't work [\#755](https://github.com/gitcoinco/web/issues/755)
- Ratelimited [\#754](https://github.com/gitcoinco/web/issues/754)
- test 123 [\#752](https://github.com/gitcoinco/web/issues/752)
- NameError: name 'time' is not defined [\#751](https://github.com/gitcoinco/web/issues/751)
- NameError: name 'time' is not defined [\#750](https://github.com/gitcoinco/web/issues/750)
- test 123 [\#734](https://github.com/gitcoinco/web/issues/734)
- test 123 [\#722](https://github.com/gitcoinco/web/issues/722)
- test 123 [\#720](https://github.com/gitcoinco/web/issues/720)
- reverse bounties [\#719](https://github.com/gitcoinco/web/issues/719)
- 'accepted' time is wrong on bounty [\#714](https://github.com/gitcoinco/web/issues/714)
- Using docker to setup and got "localhost refused to connect" error, and ReadMe file is outdated [\#713](https://github.com/gitcoinco/web/issues/713)
- /explorer on mobile needs some alignment fixes [\#705](https://github.com/gitcoinco/web/issues/705)
- bounty explorer can be slow  [\#689](https://github.com/gitcoinco/web/issues/689)
- as a user, i want to ahve an 'in alpha' badge on alpha tools, so i can know which tools aren't yet GA [\#685](https://github.com/gitcoinco/web/issues/685)
- gitcoin.co/new issue page not responsive [\#679](https://github.com/gitcoinco/web/issues/679)
- Scope of task [\#670](https://github.com/gitcoinco/web/issues/670)
- test 123 [\#654](https://github.com/gitcoinco/web/issues/654)
- Emails with \[DEBUG\] header in prod [\#650](https://github.com/gitcoinco/web/issues/650)
- Faucet giving 500 when submissino [\#646](https://github.com/gitcoinco/web/issues/646)
- Update Gitcoin Weekly Newsletter [\#632](https://github.com/gitcoinco/web/issues/632)
- as a user, i want gitcoin to integrate standardbounties contribute\(\)  method, so i can contribute more funds to a bounty [\#617](https://github.com/gitcoinco/web/issues/617)
- Tidy Up Issue Explorer [\#601](https://github.com/gitcoinco/web/issues/601)
- as an administrator, id like to add faucet distributions to activity\_report, so i can track them [\#600](https://github.com/gitcoinco/web/issues/600)
- redesign embeddable widget for github reops [\#594](https://github.com/gitcoinco/web/issues/594)
- upgrade: font-awesome 5 [\#593](https://github.com/gitcoinco/web/issues/593)
- Add Gitcoin Newsletter Page [\#584](https://github.com/gitcoinco/web/issues/584)
- Latest News Updates [\#518](https://github.com/gitcoinco/web/issues/518)
- Clear and concise message about work started from Gitcoin Bot [\#508](https://github.com/gitcoinco/web/issues/508)
- Remove Subscribe to Funded Issues at top of Issue Detail Page [\#504](https://github.com/gitcoinco/web/issues/504)
- Longer titles are profile page overflow their bounds [\#501](https://github.com/gitcoinco/web/issues/501)
- gitcoinbot did not comment on github when `work\_done` event fired  [\#495](https://github.com/gitcoinco/web/issues/495)
- Issue explorer on mobile needs a quick cleanup [\#494](https://github.com/gitcoinco/web/issues/494)
- Exception: attempting to create a new bounty when is\_greater\_than\_x\_days\_old = True [\#485](https://github.com/gitcoinco/web/issues/485)
- People shouldn't be able to start work on more than 3 issues at a time [\#478](https://github.com/gitcoinco/web/issues/478)
- JSONDecodeError: Expecting value: line 1 column 1 \(char 0\) [\#467](https://github.com/gitcoinco/web/issues/467)
- BACKEND -- Gitcoin External Bounties tool [\#447](https://github.com/gitcoinco/web/issues/447)
- Clear Connection Between Notification and Error States [\#432](https://github.com/gitcoinco/web/issues/432)
- Consistent display of ETH and USD across app [\#421](https://github.com/gitcoinco/web/issues/421)
- To see only open issues [\#420](https://github.com/gitcoinco/web/issues/420)
- Consistent button styles across the app [\#416](https://github.com/gitcoinco/web/issues/416)
- Consistent H1 treatment [\#414](https://github.com/gitcoinco/web/issues/414)
- Clear and concise tooltips [\#410](https://github.com/gitcoinco/web/issues/410)
- Standardbounties expiration date treated differently than Gitcoin expiration date [\#393](https://github.com/gitcoinco/web/issues/393)
- Uncaught ReferenceError: getParam is not defined [\#390](https://github.com/gitcoinco/web/issues/390)
- Uncaught TypeError: Cannot read property 'coinbase' of undefined [\#389](https://github.com/gitcoinco/web/issues/389)
- Uncaught TypeError: Cannot read property 'accounts' of undefined [\#388](https://github.com/gitcoinco/web/issues/388)
- \(unknown\): 구문 오류 [\#385](https://github.com/gitcoinco/web/issues/385)
- \(unknown\): ':' is required. [\#383](https://github.com/gitcoinco/web/issues/383)
- JSONDecodeError: Expecting value: line 1 column 1 \(char 0\) [\#382](https://github.com/gitcoinco/web/issues/382)
- Error: Access is denied.
 [\#381](https://github.com/gitcoinco/web/issues/381)
- \(unknown\): Syntax error [\#376](https://github.com/gitcoinco/web/issues/376)
- \(CODE\) as a user, i want to see bounties from other platforms, so i can work on bounties outside of the gitcoin ecosysstem [\#372](https://github.com/gitcoinco/web/issues/372)
- Error: MetaMask detected another web3.
     MetaMask will not work reliably with another web3 extension.
     This usually happens if you have two MetaMasks installed,
     or MetaMask and another web3 extension. Please remove one
     and try again. [\#368](https://github.com/gitcoinco/web/issues/368)
- TypeError: an integer is required \(got type NoneType\) [\#360](https://github.com/gitcoinco/web/issues/360)
- Uncaught SyntaxError: Identifier 'slides' has already been declared [\#352](https://github.com/gitcoinco/web/issues/352)
- Uncaught SyntaxError: Identifier 'slides' has already been declared [\#349](https://github.com/gitcoinco/web/issues/349)
- Cannot read property '2' of null when submitting bounty [\#342](https://github.com/gitcoinco/web/issues/342)
- Test Issue [\#341](https://github.com/gitcoinco/web/issues/341)
- SyntaxError: expected expression, got '\*' [\#339](https://github.com/gitcoinco/web/issues/339)
- Uncaught ReferenceError: web3 is not defined [\#336](https://github.com/gitcoinco/web/issues/336)
- \(unknown\): uncaught exception: not supported [\#324](https://github.com/gitcoinco/web/issues/324)
- Uncaught TypeError: Cannot read property 'accounts' of undefined [\#318](https://github.com/gitcoinco/web/issues/318)
- Error: Web3ProviderEngine does not support synchronous requests. [\#307](https://github.com/gitcoinco/web/issues/307)
- Error: Syntax error, unrecognized expression: select\[name=deonomination [\#306](https://github.com/gitcoinco/web/issues/306)
- Uncaught ReferenceError: nextSlide is not defined [\#305](https://github.com/gitcoinco/web/issues/305)
- Uncaught ReferenceError: web3 is not defined [\#303](https://github.com/gitcoinco/web/issues/303)
- Uncaught SyntaxError: Unexpected token \* [\#302](https://github.com/gitcoinco/web/issues/302)
- \(unknown\): Syntax error [\#300](https://github.com/gitcoinco/web/issues/300)
- \(unknown\): Script error. [\#297](https://github.com/gitcoinco/web/issues/297)
- ReferenceError: Can't find variable: nextSlide [\#295](https://github.com/gitcoinco/web/issues/295)
- Uncaught ReferenceError: nextSlide is not defined [\#294](https://github.com/gitcoinco/web/issues/294)
- ReferenceError: Can't find variable: nextSlide [\#293](https://github.com/gitcoinco/web/issues/293)
- Uncaught ReferenceError: nextSlide is not defined [\#292](https://github.com/gitcoinco/web/issues/292)
- Uncaught ReferenceError: web3 is not defined [\#291](https://github.com/gitcoinco/web/issues/291)
- Uncaught ReferenceError: web3 is not defined [\#290](https://github.com/gitcoinco/web/issues/290)
- Uncaught ReferenceError: nextSlide is not defined [\#289](https://github.com/gitcoinco/web/issues/289)
- Uncaught TypeError: Cannot read property 'coinbase' of undefined [\#287](https://github.com/gitcoinco/web/issues/287)
- Uncaught TypeError: Cannot read property 'accounts' of undefined [\#286](https://github.com/gitcoinco/web/issues/286)
- flow to reject a claim and payout to someone else is kind of cumbersome [\#275](https://github.com/gitcoinco/web/issues/275)
- StandardBounties: The ability to ingest Bounties.Network Bounties [\#264](https://github.com/gitcoinco/web/issues/264)
- ERC20 batch tip send [\#233](https://github.com/gitcoinco/web/issues/233)
- improvement - filtering bounties for repository [\#232](https://github.com/gitcoinco/web/issues/232)
- Issue Explorer Usability tweak [\#227](https://github.com/gitcoinco/web/issues/227)
- Treat claimed issues as open [\#225](https://github.com/gitcoinco/web/issues/225)
- design: index of bounties from other bounty projects [\#221](https://github.com/gitcoinco/web/issues/221)
- Detect profile from Metamask/Github [\#214](https://github.com/gitcoinco/web/issues/214)
- funded issue links are long and clunky [\#201](https://github.com/gitcoinco/web/issues/201)
- Environment variable based settings [\#144](https://github.com/gitcoinco/web/issues/144)
- saving search UI is broken on iphone 7 [\#8](https://github.com/gitcoinco/web/issues/8)

**Merged pull requests:**

- explorer: updated label for issues with status done [\#785](https://github.com/gitcoinco/web/pull/785) ([thelostone-mc](https://github.com/thelostone-mc))
- bounty: process + kill bounty width fix [\#782](https://github.com/gitcoinco/web/pull/782) ([thelostone-mc](https://github.com/thelostone-mc))
- CSS clean up 🎉 [\#775](https://github.com/gitcoinco/web/pull/775) ([sethmcleod](https://github.com/sethmcleod))
- disable my projects filters if user not logged in [\#771](https://github.com/gitcoinco/web/pull/771) ([kziemianek](https://github.com/kziemianek))
- current year in copyright email section [\#766](https://github.com/gitcoinco/web/pull/766) ([kziemianek](https://github.com/kziemianek))
- Alpha Tag [\#758](https://github.com/gitcoinco/web/pull/758) ([willsputra](https://github.com/willsputra))
- bounty: css letter spacing fix for h1..h6 [\#757](https://github.com/gitcoinco/web/pull/757) ([thelostone-mc](https://github.com/thelostone-mc))
- Fixed Contributing Link in README.md [\#756](https://github.com/gitcoinco/web/pull/756) ([Sabihashaik](https://github.com/Sabihashaik))
- bounty: css fix for wonky contributor info [\#741](https://github.com/gitcoinco/web/pull/741) ([thelostone-mc](https://github.com/thelostone-mc))
- html: reordered css links [\#740](https://github.com/gitcoinco/web/pull/740) ([thelostone-mc](https://github.com/thelostone-mc))
- bounty: display submit only on starting work [\#738](https://github.com/gitcoinco/web/pull/738) ([thelostone-mc](https://github.com/thelostone-mc))
- \#679 - new issue responsive updates [\#735](https://github.com/gitcoinco/web/pull/735) ([joshmobley](https://github.com/joshmobley))
- fixed broken save search UI & missing save search text on mobile [\#731](https://github.com/gitcoinco/web/pull/731) ([willsputra](https://github.com/willsputra))
- accepted\_on date in fulfillment model [\#729](https://github.com/gitcoinco/web/pull/729) ([owocki](https://github.com/owocki))
- Optimize images in assets [\#724](https://github.com/gitcoinco/web/pull/724) ([mbeacom](https://github.com/mbeacom))
- handle multiple bounties per github url [\#723](https://github.com/gitcoinco/web/pull/723) ([owocki](https://github.com/owocki))
- Add image compression [\#712](https://github.com/gitcoinco/web/pull/712) ([cassidypignatello](https://github.com/cassidypignatello))
- bounty: review feedback added [\#711](https://github.com/gitcoinco/web/pull/711) ([thelostone-mc](https://github.com/thelostone-mc))
- workaround for web3 sync issues [\#709](https://github.com/gitcoinco/web/pull/709) ([owocki](https://github.com/owocki))
- twitter.com/gitcoinfeed [\#708](https://github.com/gitcoinco/web/pull/708) ([owocki](https://github.com/owocki))
- css: fixed explorer overflow on mobile [\#707](https://github.com/gitcoinco/web/pull/707) ([thelostone-mc](https://github.com/thelostone-mc))
- Fixes: https://github.com/gitcoinco/web/issues/687 [\#699](https://github.com/gitcoinco/web/pull/699) ([kziemianek](https://github.com/kziemianek))
- css: sidebar fixup [\#697](https://github.com/gitcoinco/web/pull/697) ([thelostone-mc](https://github.com/thelostone-mc))
- Issue funder can remove users from issue [\#675](https://github.com/gitcoinco/web/pull/675) ([kziemianek](https://github.com/kziemianek))
- Offchain Bounties [\#673](https://github.com/gitcoinco/web/pull/673) ([owocki](https://github.com/owocki))
- doc: corrected setup path [\#667](https://github.com/gitcoinco/web/pull/667) ([thelostone-mc](https://github.com/thelostone-mc))
- Records UserAction events for Tip, Start/Stop Work, and Bounty related things [\#664](https://github.com/gitcoinco/web/pull/664) ([owocki](https://github.com/owocki))
- People shouldn't be able to start work on more than 3 issues at a time [\#663](https://github.com/gitcoinco/web/pull/663) ([owocki](https://github.com/owocki))
- no faucet spoofing [\#662](https://github.com/gitcoinco/web/pull/662) ([owocki](https://github.com/owocki))
- no faucet spoofing [\#661](https://github.com/gitcoinco/web/pull/661) ([owocki](https://github.com/owocki))
- Add GeoIP2 and lang middleware [\#657](https://github.com/gitcoinco/web/pull/657) ([mbeacom](https://github.com/mbeacom))
- Adds testimonial video to landing page [\#645](https://github.com/gitcoinco/web/pull/645) ([owocki](https://github.com/owocki))
- Redesign and implementation of embed widget  [\#644](https://github.com/gitcoinco/web/pull/644) ([michelgotta](https://github.com/michelgotta))
- @gitcoinbot tune up! [\#641](https://github.com/gitcoinco/web/pull/641) ([zoek1](https://github.com/zoek1))
- use AGPLv3 license [\#638](https://github.com/gitcoinco/web/pull/638) ([gasolin](https://github.com/gasolin))
- fontawesome: upgrade to v5 [\#635](https://github.com/gitcoinco/web/pull/635) ([thelostone-mc](https://github.com/thelostone-mc))
- Refactors 3 requests down to 1 [\#634](https://github.com/gitcoinco/web/pull/634) ([owocki](https://github.com/owocki))
- Integrate StandardBounties increasePayout\(\) [\#626](https://github.com/gitcoinco/web/pull/626) ([msuess](https://github.com/msuess))
- Refactors shared.js / web3 awareness code for more sanity [\#625](https://github.com/gitcoinco/web/pull/625) ([owocki](https://github.com/owocki))
- explorer: updated view [\#621](https://github.com/gitcoinco/web/pull/621) ([thelostone-mc](https://github.com/thelostone-mc))
- Update all alerts to include new alert style [\#553](https://github.com/gitcoinco/web/pull/553) ([KennethAshley](https://github.com/KennethAshley))
- Environment variable setting handling [\#359](https://github.com/gitcoinco/web/pull/359) ([mbeacom](https://github.com/mbeacom))

## [pre_web3_awareness_reafctor](https://github.com/gitcoinco/web/tree/pre_web3_awareness_reafctor) (2018-03-16)
[Full Changelog](https://github.com/gitcoinco/web/compare/pre_faucet...pre_web3_awareness_reafctor)

**Implemented enhancements:**

- nav: redesigned the dropdown [\#629](https://github.com/gitcoinco/web/pull/629) ([thelostone-mc](https://github.com/thelostone-mc))
- explorer: updated tooltip [\#585](https://github.com/gitcoinco/web/pull/585) ([thelostone-mc](https://github.com/thelostone-mc))

**Fixed bugs:**

- AttributeError: 'NoneType' object has no attribute 'strip' [\#616](https://github.com/gitcoinco/web/issues/616)
- IndexError: list index out of range [\#613](https://github.com/gitcoinco/web/issues/613)
- profile\_details.html references nonexistent profile.js resulting in Http404 [\#612](https://github.com/gitcoinco/web/issues/612)
- KeyError: 'comment' [\#598](https://github.com/gitcoinco/web/issues/598)
- fix for empty github notification [\#622](https://github.com/gitcoinco/web/pull/622) ([owocki](https://github.com/owocki))
- Check dict existence in gitcoin bot payload view [\#599](https://github.com/gitcoinco/web/pull/599) ([mbeacom](https://github.com/mbeacom))

**Closed issues:**

- test 123 [\#595](https://github.com/gitcoinco/web/issues/595)
- Upgrade to the latest Django revision [\#583](https://github.com/gitcoinco/web/issues/583)
- Increase Code Coverage by 5% [\#408](https://github.com/gitcoinco/web/issues/408)
- Reminder to remove the legacy/\* application once those bounties are done [\#406](https://github.com/gitcoinco/web/issues/406)
- Uncaught Error: Web3ProviderEngine does not support synchronous requests. [\#340](https://github.com/gitcoinco/web/issues/340)
- addd logo to metamask contract metadata repo [\#320](https://github.com/gitcoinco/web/issues/320)
- Bot / Github integration Revamp MVP [\#152](https://github.com/gitcoinco/web/issues/152)
- In tip flow, sometimes we are not able to get the email address of the user from github [\#75](https://github.com/gitcoinco/web/issues/75)

**Merged pull requests:**

- css: dropdown fix [\#630](https://github.com/gitcoinco/web/pull/630) ([thelostone-mc](https://github.com/thelostone-mc))
- Enable ESLint in pre-commit and on Travis CI [\#624](https://github.com/gitcoinco/web/pull/624) ([mbeacom](https://github.com/mbeacom))
-     Sends followup emails after 48 emails to bounty fulfiller and submitter [\#610](https://github.com/gitcoinco/web/pull/610) ([owocki](https://github.com/owocki))
- tooltip: updated as per review comments [\#606](https://github.com/gitcoinco/web/pull/606) ([thelostone-mc](https://github.com/thelostone-mc))
- slack notifications upon start / stop work [\#591](https://github.com/gitcoinco/web/pull/591) ([owocki](https://github.com/owocki))
- destroys legacy bounty handling code \(except for on legacy kill bounty page\) [\#589](https://github.com/gitcoinco/web/pull/589) ([owocki](https://github.com/owocki))
- nav: redesigned the dropdown [\#586](https://github.com/gitcoinco/web/pull/586) ([thelostone-mc](https://github.com/thelostone-mc))
- General faucet cleanup [\#582](https://github.com/gitcoinco/web/pull/582) ([mbeacom](https://github.com/mbeacom))
- Feature/faucet -- with kevin's changes [\#581](https://github.com/gitcoinco/web/pull/581) ([owocki](https://github.com/owocki))
- removes optional add\_bcc option from mailer [\#579](https://github.com/gitcoinco/web/pull/579) ([owocki](https://github.com/owocki))
- explorer: added sort feature [\#578](https://github.com/gitcoinco/web/pull/578) ([thelostone-mc](https://github.com/thelostone-mc))
- Cleanup syntax and linting issues for backend code [\#577](https://github.com/gitcoinco/web/pull/577) ([mbeacom](https://github.com/mbeacom))
- css: refactored media queries [\#573](https://github.com/gitcoinco/web/pull/573) ([thelostone-mc](https://github.com/thelostone-mc))
- mocks expiration date on standardbounties [\#566](https://github.com/gitcoinco/web/pull/566) ([owocki](https://github.com/owocki))
- Writing coverage for marketing model, increasing coverage to 33% [\#524](https://github.com/gitcoinco/web/pull/524) ([leonprou](https://github.com/leonprou))
- ESLint configuration to help code with more style [\#468](https://github.com/gitcoinco/web/pull/468) ([michelgotta](https://github.com/michelgotta))
- BOT / GITHUB INTEGRATION REVAMP MVP [\#236](https://github.com/gitcoinco/web/pull/236) ([romanjesus](https://github.com/romanjesus))

## [pre_faucet](https://github.com/gitcoinco/web/tree/pre_faucet) (2018-03-09)
[Full Changelog](https://github.com/gitcoinco/web/compare/pre-clean-urls...pre_faucet)

**Implemented enhancements:**

- show tips on leaderboard / profiles [\#544](https://github.com/gitcoinco/web/pull/544) ([owocki](https://github.com/owocki))

**Closed issues:**

- IndexError: list index out of range [\#564](https://github.com/gitcoinco/web/issues/564)
- Explorer changes followup [\#555](https://github.com/gitcoinco/web/issues/555)
- Update Issue Explorer Front End [\#503](https://github.com/gitcoinco/web/issues/503)
- void [\#455](https://github.com/gitcoinco/web/issues/455)
- Show consistent top navigation across the app [\#415](https://github.com/gitcoinco/web/issues/415)
- Clear Distinction Between Web 3 States [\#413](https://github.com/gitcoinco/web/issues/413)

**Merged pull requests:**

- sendgrid event hooks [\#568](https://github.com/gitcoinco/web/pull/568) ([owocki](https://github.com/owocki))

## [pre-clean-urls](https://github.com/gitcoinco/web/tree/pre-clean-urls) (2018-03-07)
[Full Changelog](https://github.com/gitcoinco/web/compare/pre-clean-urls2...pre-clean-urls)

**Implemented enhancements:**

- cleaner funded issue urls [\#452](https://github.com/gitcoinco/web/pull/452) ([owocki](https://github.com/owocki))

## [pre-clean-urls2](https://github.com/gitcoinco/web/tree/pre-clean-urls2) (2018-03-07)
[Full Changelog](https://github.com/gitcoinco/web/compare/prefebint...pre-clean-urls2)

**Implemented enhancements:**

- As a user, I want the navigation bar to be consistent [\#548](https://github.com/gitcoinco/web/issues/548)
- Add form styles [\#514](https://github.com/gitcoinco/web/pull/514) ([KennethAshley](https://github.com/KennethAshley))
- Adding token conversion rate to bounties [\#387](https://github.com/gitcoinco/web/pull/387) ([bhenze](https://github.com/bhenze))

**Fixed bugs:**

- Is there still a problem with 'start work' carrying over from bounty to bounty? [\#519](https://github.com/gitcoinco/web/issues/519)
- Http404 raising frequently on profile view [\#492](https://github.com/gitcoinco/web/issues/492)
- AttributeError: 'NoneType' object has no attribute 'pk' [\#483](https://github.com/gitcoinco/web/issues/483)
- Integration branch triage issues [\#474](https://github.com/gitcoinco/web/issues/474)
- void [\#462](https://github.com/gitcoinco/web/issues/462)
- Added remove filter functionality for Search Tags [\#562](https://github.com/gitcoinco/web/pull/562) ([eswarasai](https://github.com/eswarasai))
- css : fixed display for devices below 380px [\#559](https://github.com/gitcoinco/web/pull/559) ([thelostone-mc](https://github.com/thelostone-mc))
- FIX: Replace selects with select2 and update arrow [\#539](https://github.com/gitcoinco/web/pull/539) ([KennethAshley](https://github.com/KennethAshley))

**Closed issues:**

- gitcoincobot doesnt work for ERC20 issues [\#536](https://github.com/gitcoinco/web/issues/536)
- Test [\#531](https://github.com/gitcoinco/web/issues/531)
- void [\#515](https://github.com/gitcoinco/web/issues/515)
- void [\#511](https://github.com/gitcoinco/web/issues/511)
- void [\#500](https://github.com/gitcoinco/web/issues/500)
- Consistent Form Styles Across the Gitcoin [\#498](https://github.com/gitcoinco/web/issues/498)
- As a user I'd like a cleaned up explorer page. [\#493](https://github.com/gitcoinco/web/issues/493)
- Version conflict when running tests [\#488](https://github.com/gitcoinco/web/issues/488)
- 'new work' comments appear twice on github issue from gitcoincobot [\#480](https://github.com/gitcoinco/web/issues/480)
- void [\#479](https://github.com/gitcoinco/web/issues/479)
- void [\#476](https://github.com/gitcoinco/web/issues/476)
- DoesNotExist: BountyFulfillment matching query does not exist. [\#471](https://github.com/gitcoinco/web/issues/471)
- void [\#470](https://github.com/gitcoinco/web/issues/470)
- void [\#469](https://github.com/gitcoinco/web/issues/469)
- Issues in 'Work Started' should be 'Open' [\#466](https://github.com/gitcoinco/web/issues/466)
- void [\#464](https://github.com/gitcoinco/web/issues/464)
- void [\#460](https://github.com/gitcoinco/web/issues/460)
- status not populating correctly on legacy issues [\#453](https://github.com/gitcoinco/web/issues/453)
- bust the cloudfront cache when an issue updates [\#446](https://github.com/gitcoinco/web/issues/446)
- Consistent tone and voice to communicate with me [\#439](https://github.com/gitcoinco/web/issues/439)
- Create Gitcoin UI Kit [\#437](https://github.com/gitcoinco/web/issues/437)
- Align Current State of the Issue Explorer [\#436](https://github.com/gitcoinco/web/issues/436)
- Update White Paper Page Select List [\#434](https://github.com/gitcoinco/web/issues/434)
- Create Consistent Form Styles [\#433](https://github.com/gitcoinco/web/issues/433)
- dashboard\_bountyfulfillment is not being updated properly [\#428](https://github.com/gitcoinco/web/issues/428)
- Clear understanding whether something is an error or informational [\#425](https://github.com/gitcoinco/web/issues/425)
- Show left rail radio filters when appropriate [\#411](https://github.com/gitcoinco/web/issues/411)
- TypeError: an integer is required \(got type NoneType\) [\#409](https://github.com/gitcoinco/web/issues/409)
- Fix lingering bounty\_fulfiller \(claimee\) references [\#401](https://github.com/gitcoinco/web/issues/401)
- HTML/CSS Touch ups on Bounty Details Page [\#399](https://github.com/gitcoinco/web/issues/399)
- Make Process Bounty page more user friendly [\#398](https://github.com/gitcoinco/web/issues/398)
- Wrong issue title in gitcoin.co [\#366](https://github.com/gitcoinco/web/issues/366)
- TypeError: an integer is required \(got type NoneType\) [\#332](https://github.com/gitcoinco/web/issues/332)
- standardbounties cleanup: multiple fulfillments [\#308](https://github.com/gitcoinco/web/issues/308)
- standardbounties cleanup: state issues [\#284](https://github.com/gitcoinco/web/issues/284)
- Coloradocoin receive page \(due Feb 1\) [\#261](https://github.com/gitcoinco/web/issues/261)
- Push Open Source Forward =\> Grow Open Source [\#238](https://github.com/gitcoinco/web/issues/238)
- design- /pitch page - where people can pitch project ideas [\#198](https://github.com/gitcoinco/web/issues/198)
- link profile in nav somewhere [\#191](https://github.com/gitcoinco/web/issues/191)
- show conv rate rate at time of posting [\#165](https://github.com/gitcoinco/web/issues/165)
- As a user, I'd like to be able to close my browser window after I submit a web3 tx, so I can do other things without canceling. [\#128](https://github.com/gitcoinco/web/issues/128)
- GitHub oauth in new funding flow [\#98](https://github.com/gitcoinco/web/issues/98)

**Merged pull requests:**

- review: added feedback for the explorer page [\#558](https://github.com/gitcoinco/web/pull/558) ([thelostone-mc](https://github.com/thelostone-mc))
- Unify navbar template [\#549](https://github.com/gitcoinco/web/pull/549) ([mbeacom](https://github.com/mbeacom))
- Add initial changelog [\#545](https://github.com/gitcoinco/web/pull/545) ([mbeacom](https://github.com/mbeacom))
- WIP: Feature/faucet [\#541](https://github.com/gitcoinco/web/pull/541) ([KennethAshley](https://github.com/KennethAshley))
- Fix unselectable icons on select2 selects [\#532](https://github.com/gitcoinco/web/pull/532) ([KennethAshley](https://github.com/KennethAshley))
- Add Wyvern \(WYV\) token [\#525](https://github.com/gitcoinco/web/pull/525) ([protinam](https://github.com/protinam))
- core:  Rebirth of the explorer [\#523](https://github.com/gitcoinco/web/pull/523) ([thelostone-mc](https://github.com/thelostone-mc))
- dashboard: base setup [\#505](https://github.com/gitcoinco/web/pull/505) ([thelostone-mc](https://github.com/thelostone-mc))
- Update web3 and eth-utils to fix issue 488 [\#489](https://github.com/gitcoinco/web/pull/489) ([jasonrhaas](https://github.com/jasonrhaas))
- html: removed left rails [\#486](https://github.com/gitcoinco/web/pull/486) ([thelostone-mc](https://github.com/thelostone-mc))
- Correct typos and grammatical errors [\#484](https://github.com/gitcoinco/web/pull/484) ([cpbennett4](https://github.com/cpbennett4))
- text: fixed typo [\#473](https://github.com/gitcoinco/web/pull/473) ([thelostone-mc](https://github.com/thelostone-mc))
- alert user to local env networks \#465 [\#472](https://github.com/gitcoinco/web/pull/472) ([ckhatri](https://github.com/ckhatri))
- Fix ES Linting issues for leaderboard.js [\#461](https://github.com/gitcoinco/web/pull/461) ([tra38](https://github.com/tra38))
- Fix isort-check build failure [\#459](https://github.com/gitcoinco/web/pull/459) ([JakeStoeffler](https://github.com/JakeStoeffler))
- launches web3 what / why video [\#449](https://github.com/gitcoinco/web/pull/449) ([owocki](https://github.com/owocki))
- easier tip redemption [\#396](https://github.com/gitcoinco/web/pull/396) ([owocki](https://github.com/owocki))
- \(WIP\) February integration branch [\#379](https://github.com/gitcoinco/web/pull/379) ([owocki](https://github.com/owocki))
- Add dummy external bounties [\#377](https://github.com/gitcoinco/web/pull/377) ([KennethAshley](https://github.com/KennethAshley))
- WIP -- COLO Coin Redemption [\#331](https://github.com/gitcoinco/web/pull/331) ([eswarasai](https://github.com/eswarasai))
- css: prettified bounty\_details page [\#323](https://github.com/gitcoinco/web/pull/323) ([thelostone-mc](https://github.com/thelostone-mc))

## [prefebint](https://github.com/gitcoinco/web/tree/prefebint) (2018-02-13)
[Full Changelog](https://github.com/gitcoinco/web/compare/pre_january2018_feature_integration2...prefebint)

**Closed issues:**

- Use BountyFulfillment for all fulfiller\_ references [\#402](https://github.com/gitcoinco/web/issues/402)
- Fix dashboard/notifications.py [\#400](https://github.com/gitcoinco/web/issues/400)
- feb integration branch - remove references to `Bounty.fulfiller\_` [\#397](https://github.com/gitcoinco/web/issues/397)
- "Are you still working on this?" [\#394](https://github.com/gitcoinco/web/issues/394)
- \(unknown\): Syntax error [\#391](https://github.com/gitcoinco/web/issues/391)
- MultipleObjectsReturned: get\(\) returned more than one Profile -- it returned 2! [\#386](https://github.com/gitcoinco/web/issues/386)
- This is a test issue for purposes of a demo during Consensys Mesh Retreat [\#384](https://github.com/gitcoinco/web/issues/384)
- Bounty creation transaction link points to rinkeby etherscan address. [\#370](https://github.com/gitcoinco/web/issues/370)
- Travis builds failing [\#367](https://github.com/gitcoinco/web/issues/367)
- AttributeError: 'NoneType' object has no attribute 'get' [\#361](https://github.com/gitcoinco/web/issues/361)
- Submitting work throws a "Math is not a function" [\#357](https://github.com/gitcoinco/web/issues/357)
- Profile Page needs to be sized up if it's smaller than it should be [\#355](https://github.com/gitcoinco/web/issues/355)
- Increase Code Coverage by 4% [\#353](https://github.com/gitcoinco/web/issues/353)
- RangeError: Maximum call stack size exceeded [\#351](https://github.com/gitcoinco/web/issues/351)
- RangeError: Maximum call stack size exceeded [\#350](https://github.com/gitcoinco/web/issues/350)
- html: setting max-width to 500px casues weird display [\#347](https://github.com/gitcoinco/web/issues/347)
- New funded issue form does not automatically add the URL from the querystring [\#346](https://github.com/gitcoinco/web/issues/346)
- SyntaxError: expected expression, got '\*' [\#338](https://github.com/gitcoinco/web/issues/338)
- as a user, i want to be able to process two bounties in multiple tabs so i can be efficient. [\#334](https://github.com/gitcoinco/web/issues/334)
- in activity\_report management command, add a `from\_address` and `to\_address` field [\#322](https://github.com/gitcoinco/web/issues/322)
- tip emails not going out [\#321](https://github.com/gitcoinco/web/issues/321)
- Issue summaries lose formatting like new lines [\#317](https://github.com/gitcoinco/web/issues/317)
- new bounty status [\#316](https://github.com/gitcoinco/web/issues/316)
- stanardbounties cleanup: tune rate limiter [\#281](https://github.com/gitcoinco/web/issues/281)
- standardbounties cleanup: why aren't 500 error emails to ADMINs working [\#279](https://github.com/gitcoinco/web/issues/279)
- This is a test issue for purposes of a demo during Rocky Mountain Blockchain [\#270](https://github.com/gitcoinco/web/issues/270)
- game mechanics for project wheatgrass [\#260](https://github.com/gitcoinco/web/issues/260)
- sometimes web3 buttons on the gitcoin interface take 60s to respond [\#226](https://github.com/gitcoinco/web/issues/226)
- code: signal to tell user that unclaimed issues may already be in progress [\#206](https://github.com/gitcoinco/web/issues/206)
- Code Faucet Page [\#184](https://github.com/gitcoinco/web/issues/184)
- twitter posts about new funded issues do not unfurl correctly [\#110](https://github.com/gitcoinco/web/issues/110)
- move to python3, django 2.0 [\#68](https://github.com/gitcoinco/web/issues/68)
- Bounty Life-cycle [\#61](https://github.com/gitcoinco/web/issues/61)

**Merged pull requests:**

- Fix migration conflict [\#395](https://github.com/gitcoinco/web/pull/395) ([mbeacom](https://github.com/mbeacom))
- rollbar: replaces \*\* with Math.pow [\#392](https://github.com/gitcoinco/web/pull/392) ([thelostone-mc](https://github.com/thelostone-mc))
- Increase code coverage [\#375](https://github.com/gitcoinco/web/pull/375) ([tyleryasaka](https://github.com/tyleryasaka))
- js: replaced \*\* with Math.pow\(\) [\#374](https://github.com/gitcoinco/web/pull/374) ([thelostone-mc](https://github.com/thelostone-mc))
- Default network should be mainnet [\#371](https://github.com/gitcoinco/web/pull/371) ([jasonrhaas](https://github.com/jasonrhaas))
- Update Docker image to support Windows [\#365](https://github.com/gitcoinco/web/pull/365) ([mbeacom](https://github.com/mbeacom))
- Changes Math to Math.pow for gwei-\>ether gas calculation [\#358](https://github.com/gitcoinco/web/pull/358) ([poffdeluxe](https://github.com/poffdeluxe))
- Use ImageOps.fit instead of Image.thumbnail  [\#356](https://github.com/gitcoinco/web/pull/356) ([poffdeluxe](https://github.com/poffdeluxe))
- css: set max-width to 100% to fix display [\#348](https://github.com/gitcoinco/web/pull/348) ([thelostone-mc](https://github.com/thelostone-mc))
- Modify static handling to use Whitenoise [\#345](https://github.com/gitcoinco/web/pull/345) ([mbeacom](https://github.com/mbeacom))
- css: prettified /help page [\#337](https://github.com/gitcoinco/web/pull/337) ([thelostone-mc](https://github.com/thelostone-mc))
- allows multiple pending transactions at once [\#335](https://github.com/gitcoinco/web/pull/335) ([owocki](https://github.com/owocki))
- html: replaced slack image with font-awesome icon [\#333](https://github.com/gitcoinco/web/pull/333) ([thelostone-mc](https://github.com/thelostone-mc))
- diff favicons in prod vs local [\#328](https://github.com/gitcoinco/web/pull/328) ([owocki](https://github.com/owocki))
- adds user action table, stats cleanup [\#327](https://github.com/gitcoinco/web/pull/327) ([owocki](https://github.com/owocki))
- Adjust email handling for tip flow [\#326](https://github.com/gitcoinco/web/pull/326) ([mbeacom](https://github.com/mbeacom))
- javascript: convert to es6 and make sure it passes linting [\#325](https://github.com/gitcoinco/web/pull/325) ([ethikz](https://github.com/ethikz))
- Kevin/new statuses [\#319](https://github.com/gitcoinco/web/pull/319) ([owocki](https://github.com/owocki))

## [pre_january2018_feature_integration2](https://github.com/gitcoinco/web/tree/pre_january2018_feature_integration2) (2018-01-29)
[Full Changelog](https://github.com/gitcoinco/web/compare/pre_january2018_feature_integration...pre_january2018_feature_integration2)

**Fixed bugs:**

- standardbounties cleanup: Github claim work comment/interest comment updating seems to fail [\#282](https://github.com/gitcoinco/web/issues/282)
- When attempting to sign up for gitcoin slack I get a CSRF Failure [\#276](https://github.com/gitcoinco/web/issues/276)

**Closed issues:**

- Error on DB restore [\#309](https://github.com/gitcoinco/web/issues/309)
- Uncaught ReferenceError: web3 is not defined [\#304](https://github.com/gitcoinco/web/issues/304)
- ReferenceError: web3 is not defined [\#299](https://github.com/gitcoinco/web/issues/299)
- ReferenceError: Can't find variable: web3 [\#298](https://github.com/gitcoinco/web/issues/298)
- ReferenceError: Can't find variable: web3 [\#296](https://github.com/gitcoinco/web/issues/296)
- Test issue from Rollbar [\#283](https://github.com/gitcoinco/web/issues/283)
- why are all the 404s 500ing [\#280](https://github.com/gitcoinco/web/issues/280)
- The first LIVE StandardBounties Bounty on Gitcoin [\#278](https://github.com/gitcoinco/web/issues/278)
- standardbounties: where do we store info that's not in the bounty detail spec? [\#253](https://github.com/gitcoinco/web/issues/253)
- standardbounties: migration plan [\#252](https://github.com/gitcoinco/web/issues/252)
- standardbounties: figure out how to massage expressed interest PR in  [\#249](https://github.com/gitcoinco/web/issues/249)
- new 404/500 error page [\#231](https://github.com/gitcoinco/web/issues/231)
- typography cleanup after PR 116 [\#151](https://github.com/gitcoinco/web/issues/151)

**Merged pull requests:**

- Modify slack email invitation handling [\#314](https://github.com/gitcoinco/web/pull/314) ([mbeacom](https://github.com/mbeacom))
- \(WIP\) January 2018 Multiple Integrations [\#240](https://github.com/gitcoinco/web/pull/240) ([mbeacom](https://github.com/mbeacom))

## [pre_january2018_feature_integration](https://github.com/gitcoinco/web/tree/pre_january2018_feature_integration) (2018-01-26)
[Full Changelog](https://github.com/gitcoinco/web/compare/v0.1...pre_january2018_feature_integration)

**Fixed bugs:**

- www.gitcoin.co doesnt work [\#254](https://github.com/gitcoinco/web/issues/254)

**Closed issues:**

- gh int: Add github logout method [\#266](https://github.com/gitcoinco/web/issues/266)
- standardbounties: support new IPFS schema [\#265](https://github.com/gitcoinco/web/issues/265)
- standardbounties: test ERC20 tokens  [\#257](https://github.com/gitcoinco/web/issues/257)
- standardbounties: regression test the twitter notifications, github comments, and emails [\#256](https://github.com/gitcoinco/web/issues/256)
- standardbounties: estimateGas\(\) [\#248](https://github.com/gitcoinco/web/issues/248)
- standardbounties: gas limit set too high [\#247](https://github.com/gitcoinco/web/issues/247)
- standardbounties: tx throws but the frontend thinks it succeeded anyway [\#246](https://github.com/gitcoinco/web/issues/246)
- standardbounties: integrate metamask gas estimates module [\#245](https://github.com/gitcoinco/web/issues/245)
- As a gitcoin founder, I want to send a demo funded issue, so I can demo the product to the mesh. [\#229](https://github.com/gitcoinco/web/issues/229)
- As a gitcoin founder, I want to send a demo funded issue, so I can demo the product to the mesh. [\#228](https://github.com/gitcoinco/web/issues/228)
- dataviz of gas costs vs confirmation time [\#209](https://github.com/gitcoinco/web/issues/209)
- design: waiting room quote while page is waiting for web3 updates [\#181](https://github.com/gitcoinco/web/issues/181)
- Code iOS landing page [\#174](https://github.com/gitcoinco/web/issues/174)
- core : contributing.md guideline + linter [\#65](https://github.com/gitcoinco/web/issues/65)
- Browser Extension Revamp [\#50](https://github.com/gitcoinco/web/issues/50)
- waiting room entertainment while tx mines [\#32](https://github.com/gitcoinco/web/issues/32)
- Mentors [\#30](https://github.com/gitcoinco/web/issues/30)

**Merged pull requests:**

- Update notifications.py [\#277](https://github.com/gitcoinco/web/pull/277) ([tommycox](https://github.com/tommycox))
- Add Rollbar error handling [\#274](https://github.com/gitcoinco/web/pull/274) ([mbeacom](https://github.com/mbeacom))
- doc: changed port to 8000 [\#272](https://github.com/gitcoinco/web/pull/272) ([thelostone-mc](https://github.com/thelostone-mc))
- doc: changed port to 8000 in github integration steps [\#271](https://github.com/gitcoinco/web/pull/271) ([thelostone-mc](https://github.com/thelostone-mc))
- Add initial pre-commit configuration [\#269](https://github.com/gitcoinco/web/pull/269) ([mbeacom](https://github.com/mbeacom))
- roundup email 20170116 [\#243](https://github.com/gitcoinco/web/pull/243) ([owocki](https://github.com/owocki))
- Fix the test suite isort failures [\#242](https://github.com/gitcoinco/web/pull/242) ([connorwarnock](https://github.com/connorwarnock))
- Changed bounties URL in JS to prevent 301 redirect [\#235](https://github.com/gitcoinco/web/pull/235) ([tossj](https://github.com/tossj))
- backend db &  API support to show how many comments exist for an issue [\#219](https://github.com/gitcoinco/web/pull/219) ([amites](https://github.com/amites))
- Gitcoin: Issue \#174 [\#207](https://github.com/gitcoinco/web/pull/207) ([Elaniobro](https://github.com/Elaniobro))
- Changed links to MetaMask Chrome extension to MetaMask website [\#204](https://github.com/gitcoinco/web/pull/204) ([tossj](https://github.com/tossj))
- Display random quote when a web3 transaction takes place [\#158](https://github.com/gitcoinco/web/pull/158) ([tra38](https://github.com/tra38))

## [v0.1](https://github.com/gitcoinco/web/tree/v0.1) (2018-01-10)
[Full Changelog](https://github.com/gitcoinco/web/compare/submit_working...v0.1)

**Closed issues:**

- test 123 [\#224](https://github.com/gitcoinco/web/issues/224)
- foo the bar [\#223](https://github.com/gitcoinco/web/issues/223)
- Error executing transaction [\#220](https://github.com/gitcoinco/web/issues/220)
- Search by nickname doesn't work [\#213](https://github.com/gitcoinco/web/issues/213)
- Design: Gitcoin Toolbox  [\#133](https://github.com/gitcoinco/web/issues/133)

## [submit_working](https://github.com/gitcoinco/web/tree/submit_working) (2018-01-09)
**Implemented enhancements:**

- In the admin, create a view that shows bounties and tips over time [\#20](https://github.com/gitcoinco/web/issues/20)
- Design a more aesthetically pleasing bounty detail page [\#17](https://github.com/gitcoinco/web/issues/17)
- bounty details page should have a 'back' button on it [\#7](https://github.com/gitcoinco/web/issues/7)
- clawback expired bounty interface [\#5](https://github.com/gitcoinco/web/issues/5)
- Expose psql port in docker stack [\#217](https://github.com/gitcoinco/web/pull/217) ([mbeacom](https://github.com/mbeacom))

**Fixed bugs:**

- Tips:  7 second delay when clicking on 'send tip' on the mainnet. [\#16](https://github.com/gitcoinco/web/issues/16)

**Closed issues:**

- Docker-based PostgreSQL port inaccessible locally [\#216](https://github.com/gitcoinco/web/issues/216)
- Toolbox page: launch it [\#196](https://github.com/gitcoinco/web/issues/196)
- design: signal to tell user that unclaimed issues may already be in progress [\#190](https://github.com/gitcoinco/web/issues/190)
- Disabled localStorage breaks Issue Explorer [\#188](https://github.com/gitcoinco/web/issues/188)
- code: `/mission` page [\#177](https://github.com/gitcoinco/web/issues/177)
- small module design: waiting room quote [\#175](https://github.com/gitcoinco/web/issues/175)
- Design: Faucet page [\#173](https://github.com/gitcoinco/web/issues/173)
- add `/addon/` as firefox addon redirection [\#170](https://github.com/gitcoinco/web/issues/170)
- claim:  gas limit is set over limit [\#169](https://github.com/gitcoinco/web/issues/169)
- Code HTML: Toolbox Page [\#168](https://github.com/gitcoinco/web/issues/168)
- Travis builds failing - ethereum dependency changes [\#163](https://github.com/gitcoinco/web/issues/163)
- oops [\#159](https://github.com/gitcoinco/web/issues/159)
- Csv export management command to spit out activity report [\#157](https://github.com/gitcoinco/web/issues/157)
- explore the idea of a gas faucet [\#153](https://github.com/gitcoinco/web/issues/153)
- In Issue Explorer, Double Quotes \("\) are Displayed instead of Correct Single Quotes \('\) [\#150](https://github.com/gitcoinco/web/issues/150)
- Travis builds failing on cytoolz [\#142](https://github.com/gitcoinco/web/issues/142)
- Design: Mission, values, vision, how we interact [\#139](https://github.com/gitcoinco/web/issues/139)
- design: ios gitcoin.co landing page [\#137](https://github.com/gitcoinco/web/issues/137)
- Double @ sign in github bot comments [\#131](https://github.com/gitcoinco/web/issues/131)
- Some of the buttons are glitchy and unpolished.  [\#126](https://github.com/gitcoinco/web/issues/126)
- remove uppercase text from text description [\#125](https://github.com/gitcoinco/web/issues/125)
- Pytest version conflict with ethereum package [\#123](https://github.com/gitcoinco/web/issues/123)
- Add missing migrations [\#121](https://github.com/gitcoinco/web/issues/121)
- Error in sync\_profile [\#120](https://github.com/gitcoinco/web/issues/120)
- Python comment linting and semicolon/unused import removal [\#119](https://github.com/gitcoinco/web/issues/119)
- Specify validation error for email validation checks [\#118](https://github.com/gitcoinco/web/issues/118)
- AnonymousUser [\#117](https://github.com/gitcoinco/web/issues/117)
- css: resize images to fit within the timeline container [\#107](https://github.com/gitcoinco/web/issues/107)
- /slack page content view does not fill page width on mobile [\#105](https://github.com/gitcoinco/web/issues/105)
- mail: tip amount rounded off to 2 decimals showing cause incorrect amount on mail [\#103](https://github.com/gitcoinco/web/issues/103)
- Transaction Underpriced when you try to receive a tip [\#101](https://github.com/gitcoinco/web/issues/101)
- bug: roadmap items shift to adjust for content on hover [\#100](https://github.com/gitcoinco/web/issues/100)
- expire email should be targeted to personas [\#96](https://github.com/gitcoinco/web/issues/96)
- Old Etherdelta API 50x frequently [\#94](https://github.com/gitcoinco/web/issues/94)
- Testing Strategy [\#90](https://github.com/gitcoinco/web/issues/90)
- Some models don't handle plurals correctly in admin [\#86](https://github.com/gitcoinco/web/issues/86)
- Problem on claimming a issue [\#82](https://github.com/gitcoinco/web/issues/82)
- Missleading button "Accept/reject claim" for non  founder of the issue [\#81](https://github.com/gitcoinco/web/issues/81)
- Database files not compatible with Postgres 10.x [\#78](https://github.com/gitcoinco/web/issues/78)
- Email heading messed up on mobile resolutions [\#77](https://github.com/gitcoinco/web/issues/77)
- Overhaul leaderboards page design [\#76](https://github.com/gitcoinco/web/issues/76)
- support ERC20 token conversion rates on tips/bounties funding [\#73](https://github.com/gitcoinco/web/issues/73)
- css: mailing list breathing space [\#66](https://github.com/gitcoinco/web/issues/66)
- bug: roadmap items move when hover over them [\#64](https://github.com/gitcoinco/web/issues/64)
- Code Testimonials into Landing page [\#63](https://github.com/gitcoinco/web/issues/63)
- Modify docker-compose.yml to reduce running/exited services / persistent volume [\#58](https://github.com/gitcoinco/web/issues/58)
- Add persistent volume for PostgreSQL data [\#57](https://github.com/gitcoinco/web/issues/57)
- Decrease Docker image size [\#56](https://github.com/gitcoinco/web/issues/56)
- The corners or \#upper\_left and .bounty don't line up  [\#54](https://github.com/gitcoinco/web/issues/54)
- auto-estimate USD amount on gitcoin.co/tip [\#53](https://github.com/gitcoinco/web/issues/53)
- Design a testimonials module on the landing page [\#52](https://github.com/gitcoinco/web/issues/52)
- Wrong issue info [\#51](https://github.com/gitcoinco/web/issues/51)
- Post funded issue to Craigslist [\#42](https://github.com/gitcoinco/web/issues/42)
- Issues should be displayed in decreasing order of value [\#40](https://github.com/gitcoinco/web/issues/40)
- Submit a funded issue \(or send a tip\) and provide feedback on the UX. [\#37](https://github.com/gitcoinco/web/issues/37)
- docker container for running locally [\#33](https://github.com/gitcoinco/web/issues/33)
- Mock up an Organization Overview page [\#31](https://github.com/gitcoinco/web/issues/31)
- Ops: Create cloudfront invalidation programmatically upon deploy in deploy.bash.  [\#19](https://github.com/gitcoinco/web/issues/19)
- Tip page link 404s [\#14](https://github.com/gitcoinco/web/issues/14)
- Demonstrate tipping via a video [\#12](https://github.com/gitcoinco/web/issues/12)
- draft a blog post about tim-berners lee [\#4](https://github.com/gitcoinco/web/issues/4)
- list of erc20 coins should be more elegant [\#3](https://github.com/gitcoinco/web/issues/3)
- Web3 bountydetails interface documentation [\#2](https://github.com/gitcoinco/web/issues/2)
- HTTP API Documentation [\#1](https://github.com/gitcoinco/web/issues/1)

**Merged pull requests:**

- remove duplicate viewport meta [\#218](https://github.com/gitcoinco/web/pull/218) ([gasolin](https://github.com/gasolin))
- Update PULL\_REQUEST\_TEMPLATE.md [\#215](https://github.com/gitcoinco/web/pull/215) ([Elaniobro](https://github.com/Elaniobro))
- css: shrunk vertical navbar +  refactoring [\#212](https://github.com/gitcoinco/web/pull/212) ([thelostone-mc](https://github.com/thelostone-mc))
- Add RDN Token support [\#210](https://github.com/gitcoinco/web/pull/210) ([ice09](https://github.com/ice09))
- metamask gas price preview [\#205](https://github.com/gitcoinco/web/pull/205) ([owocki](https://github.com/owocki))
- Gitcoin's Mission [\#203](https://github.com/gitcoinco/web/pull/203) ([eswarasai](https://github.com/eswarasai))
- add "setup database" section to documentation [\#199](https://github.com/gitcoinco/web/pull/199) ([galaxy233](https://github.com/galaxy233))
- Remove all-caps default in /tip \(yge\) [\#195](https://github.com/gitcoinco/web/pull/195) ([bumi](https://github.com/bumi))
- Add sane fallback for localStorage usage [\#189](https://github.com/gitcoinco/web/pull/189) ([eth-button](https://github.com/eth-button))
- html: fixed github repo link [\#187](https://github.com/gitcoinco/web/pull/187) ([thelostone-mc](https://github.com/thelostone-mc))
- add activity\_report management command [\#180](https://github.com/gitcoinco/web/pull/180) ([choochootrain](https://github.com/choochootrain))
- toolbox: coded design [\#172](https://github.com/gitcoinco/web/pull/172) ([thelostone-mc](https://github.com/thelostone-mc))
- carousel: fixed css  [\#167](https://github.com/gitcoinco/web/pull/167) ([thelostone-mc](https://github.com/thelostone-mc))
- Generate high-entropy secrets and codes [\#166](https://github.com/gitcoinco/web/pull/166) ([10a7](https://github.com/10a7))
- Pin cytoolz to 0.9.0 to fulfill ethereum new reqs [\#164](https://github.com/gitcoinco/web/pull/164) ([mbeacom](https://github.com/mbeacom))
- shared.js: Escape single quotes with &\#39; [\#162](https://github.com/gitcoinco/web/pull/162) ([adtac](https://github.com/adtac))
- TLDR section on landing page [\#161](https://github.com/gitcoinco/web/pull/161) ([owocki](https://github.com/owocki))
- add http://arcade.city  token base ARCD [\#155](https://github.com/gitcoinco/web/pull/155) ([ernaneluis](https://github.com/ernaneluis))
- docker: added node to configuration and css lint setup [\#147](https://github.com/gitcoinco/web/pull/147) ([thelostone-mc](https://github.com/thelostone-mc))
- Resolve Travis failures on dependency conflict [\#143](https://github.com/gitcoinco/web/pull/143) ([mbeacom](https://github.com/mbeacom))
- css: Quick style fix for buttons using the btn-info class [\#134](https://github.com/gitcoinco/web/pull/134) ([algae12](https://github.com/algae12))
- Glitches fixes and overall better buttons look and feel [\#127](https://github.com/gitcoinco/web/pull/127) ([algae12](https://github.com/algae12))
- Resolve false fail on Travis [\#124](https://github.com/gitcoinco/web/pull/124) ([mbeacom](https://github.com/mbeacom))
- General python cleanup [\#122](https://github.com/gitcoinco/web/pull/122) ([mbeacom](https://github.com/mbeacom))
- Remove all-caps \(text-uppercase\) classes [\#116](https://github.com/gitcoinco/web/pull/116) ([bumi](https://github.com/bumi))
- fix roadmap items shift \#100 [\#113](https://github.com/gitcoinco/web/pull/113) ([alx](https://github.com/alx))
- Remove misleading buttons on gitcoin UI [\#112](https://github.com/gitcoinco/web/pull/112) ([tra38](https://github.com/tra38))
- css: fixed overflow scroll on tip recieve page [\#109](https://github.com/gitcoinco/web/pull/109) ([thelostone-mc](https://github.com/thelostone-mc))
- css: resize images to fit within the timeline container [\#108](https://github.com/gitcoinco/web/pull/108) ([algae12](https://github.com/algae12))
- fix: rounded tip amount to 3 decimal places in mail [\#104](https://github.com/gitcoinco/web/pull/104) ([thelostone-mc](https://github.com/thelostone-mc))
- Add Travis and Codecov integrations [\#102](https://github.com/gitcoinco/web/pull/102) ([mbeacom](https://github.com/mbeacom))
- small fix for forcing the images of podium be bigger on leaderboard [\#99](https://github.com/gitcoinco/web/pull/99) ([ernaneluis](https://github.com/ernaneluis))
- doc: added contributing.md [\#97](https://github.com/gitcoinco/web/pull/97) ([thelostone-mc](https://github.com/thelostone-mc))
- Update get\_prices to use new etherdelta WS API [\#95](https://github.com/gitcoinco/web/pull/95) ([mbeacom](https://github.com/mbeacom))
- Simplify bounty management command [\#93](https://github.com/gitcoinco/web/pull/93) ([mbeacom](https://github.com/mbeacom))
- fix of issue \#76 Overhaul leaderboards page design [\#91](https://github.com/gitcoinco/web/pull/91) ([ernaneluis](https://github.com/ernaneluis))
- Fix display of plurals for some models in admin [\#88](https://github.com/gitcoinco/web/pull/88) ([mbeacom](https://github.com/mbeacom))
- PostgreSQL alpine and docker compose restart policies [\#85](https://github.com/gitcoinco/web/pull/85) ([mbeacom](https://github.com/mbeacom))
- Tips now show USD estimates [\#84](https://github.com/gitcoinco/web/pull/84) ([rajatkapoor](https://github.com/rajatkapoor))
- Fix grammer in alert on tip page [\#83](https://github.com/gitcoinco/web/pull/83) ([edkek](https://github.com/edkek))
- testimonial: added carousel on landing page [\#80](https://github.com/gitcoinco/web/pull/80) ([thelostone-mc](https://github.com/thelostone-mc))
- css: prettify the subscribe button [\#74](https://github.com/gitcoinco/web/pull/74) ([thelostone-mc](https://github.com/thelostone-mc))
- Update tip page to auto calculate USD [\#72](https://github.com/gitcoinco/web/pull/72) ([mbeacom](https://github.com/mbeacom))
- Cleanup python imports [\#71](https://github.com/gitcoinco/web/pull/71) ([mbeacom](https://github.com/mbeacom))
- Fix roadmap items move when hover over them. [\#67](https://github.com/gitcoinco/web/pull/67) ([sc0Vu](https://github.com/sc0Vu))
- Add psql persistence and remove redundant services [\#60](https://github.com/gitcoinco/web/pull/60) ([mbeacom](https://github.com/mbeacom))
- Decrease Docker image size [\#59](https://github.com/gitcoinco/web/pull/59) ([mbeacom](https://github.com/mbeacom))
- fix bounty definition height \#54 [\#55](https://github.com/gitcoinco/web/pull/55) ([Kielek](https://github.com/Kielek))
- Correct comma typo in statement of Gitcoin aliases [\#49](https://github.com/gitcoinco/web/pull/49) ([iamchrissmith](https://github.com/iamchrissmith))
- WEB3 API documentation [\#47](https://github.com/gitcoinco/web/pull/47) ([lawrencelink](https://github.com/lawrencelink))
- Minor Typo Error [\#45](https://github.com/gitcoinco/web/pull/45) ([k4m4](https://github.com/k4m4))
- Craigslist [\#44](https://github.com/gitcoinco/web/pull/44) ([rajatkapoor](https://github.com/rajatkapoor))
- HTTP Strict Transport Security [\#41](https://github.com/gitcoinco/web/pull/41) ([sergio-alonso](https://github.com/sergio-alonso))
- Standard pseudo-random generators are not suitable for security/cryptographic purposes. [\#39](https://github.com/gitcoinco/web/pull/39) ([sergio-alonso](https://github.com/sergio-alonso))
- Update link on image [\#15](https://github.com/gitcoinco/web/pull/15) ([bransbury](https://github.com/bransbury))
- add dropdown menu search via select2, fix \#3 [\#13](https://github.com/gitcoinco/web/pull/13) ([gasolin](https://github.com/gasolin))
- Fix space, typo and rename [\#11](https://github.com/gitcoinco/web/pull/11) ([gamwe6](https://github.com/gamwe6))
- Send tips in one step via Gitcoin.co [\#10](https://github.com/gitcoinco/web/pull/10) ([owocki](https://github.com/owocki))
- Fix instruction for running locally [\#9](https://github.com/gitcoinco/web/pull/9) ([cifvts](https://github.com/cifvts))
- Documents API Fields & Filter/Sort URL Parameters [\#6](https://github.com/gitcoinco/web/pull/6) ([anglinb](https://github.com/anglinb))



\* *This Change Log was automatically generated by [github_changelog_generator](https://github.com/skywinder/Github-Changelog-Generator)*
