# Mastodon DMARC Survey

A survey of DMARC deployment acoss the top 1000 Mastodon instances by number of logins per week

## Motivation

As Mastodon has exploded in [popularity] spurred by Elon Musk's
takeover of Twitter, it has also become popular to send 
phishing [emails][phishing] to instance users.
A common phishing approach is to spoof the message from
domain, so the email falsy appears to come from a trusted domain
when the recipient opens it.

DMARC addresses this problem by providing receiving mail
servers with the ability to ensure that an email came frm a source
authorized by the domain owner.

This project is designed to allow end-users to quickly identify which
instance domains have DMARC enforced, so that can be factored in when
selecting an instance to join, which also provides an incentive for
instance administrators to implement DMARC on their domains as soon
as possible.

## Methodology
 
The Mastodon DMARC uses [instances.social API][instances] to fetch a list of the top 1000
instances by active user count,then [checkdmarc][checkdmarc] used to retrieve,
parse, and validate DNSSEC, SPF, and DMARC DNS records for those domains.

## SPF, DKIM, and DMARC

You can learn about SPF, DKIM, and DMARC in [Demystifying DMARC][Demystifying DMARC].

To get started, you add a DMARC policy record that tells receiving email servers what to do with email with a
message that has a message `From` address containing the domain, but has failed authentication.

For example, to set a monitor only policy for `example.com`, you would create the following DNS record 

```text
_dmarc.example.com TXT "v=DMARC1; p=none;"
```

| Policy (p value) | Description                                                                                              |
|------------------|----------------------------------------------------------------------------------------------------------|
| none             | Take no action (monitor only)                                                                            |
| quarantine       | Place the message in a system or user quarantine (the exact location is decided by the receiving server) |
| reject           | Reject the message completely                                                                            |

It is critical to ensure that all legitimate email sources sending as your domain are properly DKIM signed as your
domain before deploying DMARC with an enforced policy. For large organisations, identifying and configuring all of
those sources can be challenging.

Fortunately, most Mastodon instances are hosted on a dedicated domain with a few legitimate email sources. The easiest
way to make sure that emails from your Mastodon instance pass DMARC is to deploy a monitor only DMARC policy
record (p=none), nake each source email you (requestin, and checking the DMARC results in the message 
`Authentication-Results` and/or `Authentication-Results-Origional` headers.

For a more complete picture of who or what is sending as your domain, aggregate DMARC reports can be collected. These
reports are sent by some (but not all) mail servers to let domain owners know what servers are sending as their domain.
These reports contain information such as

- The IP address of the mail server
- The number of emails being sent
- Details on SPF, DKIM, and DMARC check results
- The name of the receiving organization

Adding the `rua` tag in the DMARC policy record specifies where these reports should be sent, for example

```text
_dmarc.example.com TXT "v=DMARC1; p=none; rua=mailto:dmarc@example.com"
```

Commercial and open source solutions are available to parse and analyze these reports, such as:

- [parsedmarc]
- [postmark]
- [dmarcian]

## DNSSEC

In addition to checking SPF, DKIM and DMARC records, the Mastodon DMARC servey
also checks for the deployment of [DNSSEC], a standard that prevents attackers from impersonating your domain.
To deploy DNSSEC, you simply add the proper DNS records provided by your domain
registrar to the nameservers that are hosting your DNS zone. If your DNS is also hosted
by your domain registrar (which is the case for most small sites), this can usually be enabled
with the flip of a toggle. Check your domain registrar's documentation or contact their support for more details.


## Licensing

The source code is licensed under the [Apache License 2.0][LICENSE].

Results and analysis posted here are licensed under the [Creative Commons Attribution 4.0 International Public License][cc-by-4.0]
unless noted otherwise.

[popularity]: https://web.archive.org/web/20221129122927/https://www.cnn.com/2022/11/05/tech/mastodon
[phishing]: https://web.archive.org/web/20230106053517/https://mstdn.social/@stux/109603992325592066
[Demystifying DMARC]: https://seanthegeek.net/459/demystifying-dmarc/
[instances]: https://instances.social/list/advanced
[checkdmarc]: https://domainaware.github.io/checkdmarc/
[parsedmarc]: https://domainaware.github.io/parsedmarc/
[postmark]: https://dmarc.postmarkapp.com/
[dmarcian]: https://dmarcian.com/
[LICENSE]: https://github.com/seanthegeek/mastodon-dmarc-survey/blob/main/LICENSE
[cc-by-4.0]: https://creativecommons.org/licenses/by/4.0/
