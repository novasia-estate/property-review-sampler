# Selection contract

The budget counts rows, not property groups. A required group costs all its rows. After mandatory groups, candidates are ordered by newly covered joint strata (descending), current coverage counts (ascending), row cost (ascending), seeded SHA-256 and group ID. A stratum is counted once per selected group even if a group repeats the same language. Inputs are not modified.

Changing row content changes the population fingerprint. Changing only input order does not. The seed only resolves ties; it is not a statistical randomisation guarantee. Small strata can be prioritised over common ones, so defects in this queue cannot be extrapolated to the full catalogue.

Keep the original input and audit together privately. The tool makes no network requests. Export files can contain the supplied catalogue data; share them deliberately.
