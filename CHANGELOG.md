# Changelog

##

- Fix typo in the `User-Agent` header
- Swap the order of the CSV `error` and `warning` fields
- Fix bug where `spf_valid` was always false
- Increase DNS timeout from `0.5` seconds to `1.0` seconds
- Add default values to the CLI help

## 1.1.0

- Rename the `active_users` field name provided by instances.social to the more accurate mame `logins_per_week` (see https://github.com/TheKinrar/instances/issues/143)
- Rename the `statuses` field name provided by instances.social to the current mame `posts` 
- Add the fields `dnssec`, `spf_valid`, `warnings`, and `errors`

## 1.0.0

- Initial release