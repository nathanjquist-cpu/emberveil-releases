# 0.32.0 published and verified — 2 October 2026

The approved anatomical torso and grouped character editor are live as stable
v0.32.0. The existing launcher feed points to the complete Windows update.
All 33 exported-content release suites passed in run 37076500522, including save
safety and the new character-editor selection/rotation checks. The publisher
verified all five uploaded file digests and the live launcher manifest.

The 182,184,272-byte game pack matches the reviewed export, SHA-256
`a90baaf9527b7e7ac50e05cc8ddf0221b674c46a8c0b607521c5cc0b7bad27b3`.
Existing supported saves remain on format 16. No intermediate game versions are
needed; 0.31.0 remains available for rollback. Native visual review at 1080p and
720p passed before release. This is not a new Windows hardware benchmark.

---

# 0.14.1 publication verified

Private source **dc5cc0e8fe0adc16b6cbe16be4477b6951b7becc**, public request **6ea63b69afce8d28bb5abfb60c39d86e307ae73f**, hosted run **36511860884**, job **109225535331**. All seven exported-content gates passed. All five server asset digests and the live launcher feed were verified before stable/latest publication.

The published PCK is byte-identical to the local exported package used for the 68-check stealth/concealment and 87-check signature-perk regressions. The 51-check combat workload suite passed locally and against the hosted export. Native guard/caster wind-up and release captures show the old chest marker absent, with sword motion and the real fire projectile retained. These captures use Compatibility software rendering and do not measure hardware FPS. No player hand meshes or animation curves changed.

**Does this make sense?** The confusing ball was an intentional legacy attack-warning sphere in the shared enemy script, not a missing-texture or driver error. Its mesh/material and every visibility reference are removed from adventure and study. Combat timing, projectiles and save format 13 remain intact. Recovery branch checkpoint/before-0.14.1-orb-cleanup retains the prior source. The 0.14.0 user hardware results support the working High target and are stored separately; no performance improvement is claimed for the patch.

This patch uses the unchanged launcher and publishing pipeline. The actual Windows updater already passed 19 live checks for 0.14.0; that full installation test was not repeated for this small game-only patch. The hosted publisher fetched and verified the new live manifest and asset digests. The update is available through the existing launcher without manual ZIP handling.

---

# 0.14.0 publication verified

Hosted run **36509720705**, job **109218955318**, built private source **a3fee5598715ab0d161c1321d3f05e8368b559ba** after public request **a29f76b0e6cf1ea0312da1d76563727ed389f16c**. All seven exported gates passed. All five public asset digests were verified before promotion to stable/latest. The published PCK SHA-256 is `c9c52e6ba398ce53441be24f2f830b582c1082ae6edb21d7ee1f9092d4f3270a`, byte-identical to the locally tested exported package.

The actual Windows launcher 1.0.1 passed **19 live checks**, upgrading a disposable installation from 0.13.0 to 0.14.0. It downloaded **129,131,540 bytes**, reused **96,484,352 verified identical bytes**, checked both installed game hashes, retained both prior files, enabled Play, and correctly reported the second feed check as up to date. The real launcher state remained byte-identical and no game was launched. This verifies the updater, not Windows game graphics or FPS.

The first Windows harness copy corrupted the curly apostrophe in the expected up-to-date text through PowerShell's default text decoding. Download, activation, hashes and rollback retention passed, but the text assertion failed, so that run was rejected. Writing the original UTF-8 script directly and rerunning produced the clean 19-check pass; no launcher or game code was changed to satisfy the assertion.

**Does this make sense?** The user receives the update through the established launcher, without handling a ZIP or reauthorizing GitHub. Recovery branches preserve both the pre-change source and exact published revision. High is provisional; the new 3/6/9-actor benchmark is ready, but RTX 2070 SUPER Forward+ combat performance still requires the user's run. Held equipment and spell art remain the next pass after that measurement.

---

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
