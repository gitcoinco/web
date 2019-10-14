# Gitcoin Security Bounty Program

Gitcoin is an open-source marketplace with our code available for inspection and research. If you discover a severe bug affecting the privacy, data, or security of our users we ask that you disclose responsibly and privately. For security related vulnerabilities we reward researchers for private and professional disclosure.

Non-security issues (style issues, gas optimizations) are not eligible for this bounty.

## Guidelines
Participating in our security bounty program requires you to follow our guidelines. Responsible investigation and reporting includes, but not limited to the following:

- Don't download, modify, or destroy other users' data.

- Don't cause a denial-of-service on our platform through exploits, vulnerabilities, traffic, or causing issues with our technology providers.

- Don't repeatedly request updates on your reports. Gitcoin is a small team and constant requests for updates can render your report ineligible. Allow us up to 7 days to respond to your emails.

- Do only use your own account to test issues in production. You can also download our open source code and run your own instance to research and test for vulnerabilities.

- Social engineering attacks, DDOS, physical access, spearfishing, etc. are not eligible.

- Payouts will be made to the first individuals who submit a report.

The Gitcoin team has the final say in all determinations of bounty payouts including severity, classification, amount, whether the report falls under our guidelines, etc.

Vulnerabilities should be disclosed directly to the Gitcoin team by emailing engineering@gitcoin.co - reports should not be made publically or to any third party. These communications must remain confidential to be eligible.

Threats, ransom demands, unprofessional language, etc. of any kind will automatically disqualify you from participating in the program.

The only domain eligible for the bounty program is https://gitcoin.co - no subdomains, related services, etc. are within the scope of the program.
Vulnerabilities found in support services (ex: Slack, Wordpress, etc.) are not eligible.

## Vulnerability Scope
Any significant vulnerability may be eligible for an award provided it follows the guidelines set in this document.

Some examples of eligible issues are:

- Cross-Site Request Forgery (CSRF)

- Cross-Site Scripting (XSS)

- Code Executions

- SQL Injection

- Server Side Request Forgery (SSRF)

- Privilege Escalations

- Authentication Bypasses

- Data Leaks

Some examples of ineligible issues are:

- Rate Limiting

- Stack Traces

- Self-XSS

- Man in the Middle (MiTM) Attacks

- Denial of Service Attacks

- Cache Poisoning

- Clickjacking

- Missing DNS Records

- Brute Force Attacks

- Vulnerabilities in third party services or third party platforms

- Vulnerabilities in past versions of the software

- Vulnerabilities affecting outdated browsers or operating systems

Eligible Reports must contain enough information and a proof of concept code or screenshots. After a report is made and confirmed, efforts will be made to fix the issue. Researchers agree to assist in the testing of the fixes.

Vulnerability severity is judged by the [OWASP model](https://www.owasp.org/index.php/OWASP_Risk_Rating_Methodology)

![OWASP evaluation chart](https://gitcoincontent.s3-us-west-2.amazonaws.com/owasp.png)

Payouts will be awarded in ETH and converted from USD at the time of payout - please include your Ethereum address and Gitcoin username when submitting a report:

Critical: $600

High: $225

Medium: $125

Low: $30
