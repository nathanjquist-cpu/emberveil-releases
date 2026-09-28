# Publishing setup validation — 28 September 2026

Workflow commit: `00d61f3d126f1e20ddc86d8d85a529edace2988e`.
Recovery branch: `checkpoint-before-actions-20260928` preserves the original downloads repository.

- Ten focused local tests passed, including interrupted uploads staying unpublished, wrong hashes, source/path rejection, wrong launcher URLs and downgrade prevention.
- The actual 0.13.0 Windows ZIP was opened and verified against the committed request. Its EXE and PCK match the tested manifest byte for byte. The five derived release assets were prepared successfully. The credits ZIP is deterministic and retains every bundled license.
- Hosted run [36497238311](https://github.com/nathanjquist-cpu/emberveil-releases/actions/runs/36497238311) passed the same tests and inspected the current public launcher manifest against GitHub's EXE/PCK asset digests using the built-in job token.
- The publishing job was correctly skipped on this setup push. No new stable release was published. The current feed remains v0.12.1.

## Does this make sense?

The intended result is automatic authenticated publication after a tested ZIP reaches GitHub. There are no private source files or reusable credentials in this repository. Failed verification or an interrupted upload cannot change the launcher feed; uploads first go into a separate stable draft. Existing stable releases are retained.

## Pending first live publication

Upload the approved `Emberveil-Windows-Prototype-0.13.0.zip` to a published prerelease tagged `staging-v0.13.0`, targeted at main. That event runs the publishing job. Binary transfer cannot currently be performed by the connected GitHub app; neither the build workspace nor the connected Windows PC had an installed authenticated GitHub CLI. A browser upload or a persistent local CLI sign-in is still required for that handoff.

Actual release-write permission, the first automatic upload/promotion, and a live 0.12.1-to-0.13.0 launcher download/activation remain unverified until that upload happens. This setup is not a claim of a completed game release or a source-to-release build pipeline.
