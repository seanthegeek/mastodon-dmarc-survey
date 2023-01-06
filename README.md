# Mastodon DMARC Survey
A survey of DMARC deployment acoss the top 1000 Mastodon instances by number of active users

## Motivation

As Mastodon has exploded in popularity[popularity] spurred by Elon Musk's
takeover of Twitter, it has also become popular to send 
phishing [emails][phishing] to instance users.
A common phishing approach is to spoof the message from
domain, so the email falsy appears to come from a trusted domain
when the recipient opens it.

DMARC [addresses this problem][DMARC] by providing receiving mail
servers with the ability to ensure that an email came frm a source
authorized by the domain owner.

This project is designed to allow end-users to quickly identify which
instance domains have DMARC enforced, so that can be factored in when
selecting an instance to join, which also provides an incentive for
instance administrators to implement DMARC on their domains as soon
as possible.

## Methodology
 
Use [instances.social API][instances] to fetch a list of the top 1000
instances by active user count,then use [checkdmarc][checkdmarc] to retrieve,
parse, and validate DMARC DNS records for those .

## Licensing

The source code is licensed under the [Apache License 2.0][LICENSE].

Results and analysis posted here are licensed under the [Creative Commons Attribution 4.0 International Public License][cc-by-4.0]
unless noted otherwise.

[popularity]: https://web.archive.org/web/20221129122927/https://www.cnn.com/2022/11/05/tech/mastodon
[phishing]: https://web.archive.org/web/20230106053517/https://mstdn.social/@stux/109603992325592066
[DMARC]: https://seanthegeek.net/459/demystifying-dmarc/
[instances]: https://instances.social/list/advanced
[checkdmarc]: https://domainaware.github.io/checkdmarc/
[LICENSE]: https://github.com/seanthegeek/mastodon-dmarc-survey/blob/main/LICENSE
[cc-by-4.0]: https://creativecommons.org/licenses/by/4.0/
