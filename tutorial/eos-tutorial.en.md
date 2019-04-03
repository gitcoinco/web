# EOS Token Profile Submission Guideline

*Check [Token Profile Guideline](../README.md)*

## Requirements
### Information Preparation
#### Complete project information and related blockchain media reports are appreciated, this includes but not limited to the following items:

- Project team background:
- Project basic information:
- Media publications:
- Supported Exchanges:


#### Token Profile Submission:
Sample Pull Request (PR): https://github.com/consenlabs/token-profile/pull/3475/files

### Requirements to the information
#### Completeness and Accuracy of the information
You are responsible for the information you submitted. Please ensure that the token information, is concise and accurate. Please check the sample PR. Complete information of your project can help imToken team understand your project better, which speed up the review process. 


#### Logo Design Requirements
- Size: 120x120 pixels
- Transparent background PNG format
- Brand logo horizontally and vertically centered, as shown below.

![example](./logo.png)


## How it works
*We recommend that you complete the procedures with your developers*

1. Fork the repo to your own github account.


2. Clone the repo from your own account, please note: do no clone the origin one directly, but clone the repo you forked
```
git clone git@github.com:xxxxxxxx/token-profile.git
cd token-profile/
```


3. Create a new branch (file) and switch to a new branch named by your token symbol
  For example:
```
git branch xxx-token
git checkout xxx-token
```


4. Add a new json file to the eos-token directory, named by **symbol@accountname**. 
  For example:
  *PUB@publytoken11.json*


5. Please ensure to use UTF-8 encoding in the json file to avoid Travis-CI build error. Please check the template file to fill in the complete token information: [$template.json](../erc20/$template.json)


6. Add the token logo to images directory, name it by **symbol@accountname** as well.


7. Commit and push the information to your repo
  For example:
```
git add -A
git commit -m “Add xxx token”
git push origin xxx-token
```


8. Under your repo page, click the “New pull request” button. Then, attach the detailed  project information and related blockchain media reports. This includes but not limited to the following: (Project team background; Project basic information; Media publications; Supported Exchanges).

   Sample PR: https://github.com/consenlabs/token-profile/pull/3475


9. We will review your PR as soon as possible. If there is no problem with your PR, we will merge it into our master branch. And then your token profile will display in the current imToken App

## Frequently asked questions

### How to display token price:
In imToken, the current displayed token prices are provided by the block.cc API. If you want your project’s token price to be displayed in imToken, your token price must be supported on block.cc and you have to provide us the corresponding link. Please refer to this page for more information: https://mifengcha.com/q/eth 

## Related
* [EOSPark](https://github.com/BlockABC/eos-tokens)
* [Newdex](https://newdex.io)

## Copyright

2019&copy;imToken PTE. LTD.
