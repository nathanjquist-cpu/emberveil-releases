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

## Pending at workflow installation

The first hosted build, public 0.13.0 publication and live launcher activation test are pending. They will be recorded here only after completion.
