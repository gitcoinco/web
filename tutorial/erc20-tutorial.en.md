# ERC20 Token Profile Submission Guideline

*Check [Token Profile Guideline](../README.md)*

## Requirements
### Information Preparation
#### Complete project information and related blockchain media reports are appreciated, including but not limited to the following items:

- Official announcement: (see details in **[Completeness and Accuracy of the information](https://github.com/consenlabs/token-profile/blob/master/tutorial/erc20-tutorial.en.md#completeness-and-accuracy-of-the-information)**)
- Project team background:
- Project basic information:
- Media publications:
- Supported Exchanges:
- Suggested Gas limit setting (default is 60,000):

#### Token Profile Submission:
Sample Pull Request (PR): https://github.com/consenlabs/token-profile/pull/1636/files


### Requirements to the information
#### Completeness and Accuracy of the information
You are responsible for the information you submitted. Please ensure that the token information submitted is concise and accurate. Please refer to the sample PR. Complete information of your project can help imToken team understand your project better, which may speed up the review process. 

In order to ensure the authenticity of the information submitted, please publish an announcement on your website or official social media channels and attach the corresponding link in “Official announcement”. We recommended a format similar to the following:
>\#imToken #1636
We are providing XXX token’s information on imToken. After completion, you can see the logo and full information inside imToken’s Token Manager.

Note:
- 1636 is the PR number, as in: https://github.com/consenlabs/token-profile/pull/1636 
This number is the key to verify yourself as the rightful editor of the information to imToken.
- The token information can only be changed after the official verification

#### Logo Design Requirements
- Size: 120x120 pixels
- Transparent background PNG format
- Brand logo horizontally and vertically centered, as shown below.

![example](./logo.png)


## How it works
*We recommend that you complete the procedures with your developers*

1. Fork the repo to your own github account


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


4. Add a new json file to the erc20 directory, named by your token contract address. Please note the contract address should be done with capitalization with [checksum](https://github.com/ethereum/EIPs/blob/master/EIPS/eip-55.md) 
  For example:
  *0xf90f1648926005A8bb3ed8ec883164De7F768743.json* [Checksum tool](https://ethsum.netlify.com/)


5. Please ensure to use UTF-8 encoding in the json file to avoid Travis-CI build error.The contract address in the json also needs to use **checksum**.Please check the template file to fill in the complete token information: [$template.json](../erc20/$template.json)


6. Add the token logo to images directory, name it by the token contract address with **checksum** .

7. Commit and push the information to your repo
  For example:
```
git add -A
git commit -m “Add xxx token”
git push origin xxx-token
```


8. Under your repo page, click the “New pull request” button. Then, attach the detailed  project information, official announcement and related blockchain media reports. This includes but not limited to the following: (Official announcement; Project team background; Project basic information; Media publications; Supported Exchanges; Suggested Gas limit setting).

   Sample PR: https://github.com/consenlabs/token-profile/pull/1636 

9. We will review your PR as soon as possible. If there is no problem with your PR, we will merge it into our master branch. And then your token profile will display in the current imToken App


## Frequently asked questions

### How to display token price:
In imToken, the current displayed token prices are provided by the block.cc API. If you want your project’s token price to be displayed in imToken, your token price must be supported on block.cc and you have to provide us the corresponding link in your GitHub submission. 

Sample: https://github.com/consenlabs/token-profile/issues/3595 


### Regarding Duplicated Token Names or Contract Amendment

In imToken 1.0, if duplicated token names are found, imToken team will add a number after the token name for the project, like TFT1, TFT2 etc. If you wish to remove the number, we need to claim, this is a very dangerous operation. Removing the number is not advisable, as amending the token name will cause the token to disappear from imToken display and may cause unnecessary panic among users. For tokens with many holders, we recommend the token project to suggest to your users, to download and use imToken 2.0, as imToken 2.0 distinguish tokens via contract address. Therefore, this mitigates the problem of duplicated token names.

If there are update requests due to contract amendment, follow the checklist:
 
1. make an official announcement for the upgrade of the contract
2. submit a new PR in GitHub: 
   - desaturate the old logo
(In Photoshop: image - adjustments - desaturate)
   - resubmit new token contract’s json and logo
3. share your announcement link under the comment section in the PR
 
imToken team will evaluate the situation.

### Unable to search via contract address
If you can't search via the contract address, please check if there is no successful transaction records. Besides, please verify your contract information on [Etherscan] (https://etherscan.io/), then we can help you manually add it.

## Copyright

2020&copy;imToken PTE. LTD.
