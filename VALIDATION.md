# Automatic source builds — 0.13.0

## Intended result

Nathan opens the existing launcher, installs the offered update and plays. Building and publishing must require no player ZIP download, ZIP upload or repeated GitHub sign-in.

## Verified before the first hosted release

- Persistent GitHub CLI sign-in is stored in the Windows credential store.
- The source repository is private; public downloads remain in this repository.
- A read-only source deploy key is configured. Publication uses the job's own GITHUB_TOKEN; no personal token is stored in workflow secrets.
- The private import reconstructed the exact reviewed source and verified all 610 file hashes before committing it to main. The source recovery preflight and full import both passed on GitHub.
- Delivery documentation was updated after import; runtime code and art remained unchanged. The reviewed source digest was refreshed to include those documentation changes.
- Local fresh export and five exported-content suites passed. Progression checked 203 assertions, sword checks covered 602 cases, and two-handed checks covered 6,024 cases. Character and adventure save-safety checks passed.
- The existing publisher's ten focused regression tests passed, covering corrupted/mismatched assets, unsafe ZIP members, launcher URLs, version ordering, server digests and interrupted publication.

## Does this make sense?

The public request pins an immutable private revision. A changed source file fails the digest gate before publication. Source access is read-only. All exported-content gates must pass, then all five uploaded assets must match their recorded hashes before the draft can become latest. The launcher URL and save locations remain the same. Historical releases provide recovery points.

Headless checks establish exported behavior, not graphical quality or Windows GPU performance. The original 0.13.0 visual review remains with the private source, and the new Base / High / Extreme comparison still needs Nathan's hardware results.

## Completed hosted release and live Windows check

[Hosted build 36503990253](https://github.com/nathanjquist-cpu/emberveil-releases/actions/runs/36503990253) completed successfully. It built private source commit `be9bfffcf2cb2606decfd1644668c7f9c8323d2a` with reviewed source digest `a58279d95dd50f8d5b09ab1fa12e0a0e2e892d64f011075bdfee8fd6ff4cd505`. Fresh import/export and all five exported-content suites passed. All five server asset digests matched before [v0.13.0](https://github.com/nathanjquist-cpu/emberveil-releases/releases/tag/v0.13.0) became the stable latest release. The live manifest matched both game asset sizes and hashes.

The unchanged Windows launcher 1.0.1 then passed 19 checks in a disposable installation. It installed the verified 0.12.1 fixture, detected 0.13.0 through the production HTTPS feed, downloaded and SHA-256-verified 225,607,188 bytes, activated the new version, retained both previous files, and reported up to date with Play enabled. The real launcher installation's state file remained unchanged; no player saves were accessed or modified by the test.

This is an actual Windows launcher execution and update check. The test did not launch the Windows game or measure GPU performance. There is no new claim about frame rate or graphics quality.

**Final sense check:** the requested player flow now works without manually moving an update ZIP. Source remains private, builds run on GitHub, the existing launcher URL still works, and earlier releases remain available for recovery. The player needs no new launcher or publishing login.
