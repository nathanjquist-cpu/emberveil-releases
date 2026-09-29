# Emberveil releases

Public Windows downloads and the update feed for Emberveil, a first-person fantasy RPG prototype.

## For players

Open the existing Emberveil launcher, check for updates, install the offered version and select Play. Players do not upload game ZIPs, run publishing commands or sign in to GitHub. The launcher continues to use `releases/latest/download/release.json` in this repository.

Stable releases contain the game EXE, PCK, optional standalone ZIP, credits ZIP and update manifest. Game source and recovery history stay private.

## Current patch — 0.14.1

The pink/purple ball at enemies' chests was a prototype attack-warning marker. It is removed from both the adventure and Graphics study. Actual attack animations, timing and projectiles remain. Use the launcher to update; a full graphics comparison rerun is not needed for this cleanup.

## Graphics baseline — 0.14.0

In Graphics study select **High**, **Forward+ (restart)** and **1920 × 1080**, then **Compare combat · 3 / 6 / 9 actors**. Keep the game in the foreground for three minutes fifteen seconds, then Copy comparison results. The isolated scene measures active enemy AI, collisions, blocking and projectiles. It preserves journey saves. High is provisional until the combat hardware results are reviewed; richer held equipment and spell art follow that check.

## Automatic builds and publication

1. The developer commits reviewed changes to the private `nathanjquist-cpu/emberveil-source` repository and records the exact reviewed source digest and version in `ci/release.json`.
2. The developer updates this repository's `build-request.json` with that immutable private commit SHA and version.
3. **Build private source and update launcher** checks out that revision, downloads the checksum-pinned Godot 4.5.2 toolchain, exports the Windows game and tests its exported content.
4. After all gates pass, the workflow uploads the five download assets to a draft, verifies their server SHA-256 digests and promotes the release to Latest. The existing launcher then offers it normally.

The workflow can also be rerun from Actions. Source pinning, version checks and upload verification prevent an incomplete build from replacing the working release. Published mismatched versions and downgrades are rejected. Older releases remain available for recovery.

The former player-side staging ZIP handoff has been replaced by this source-build workflow. Historical staging requests and publisher tests remain as development records; they are not required to update or play.

## Authentication

Publication uses GitHub Actions' built-in `GITHUB_TOKEN`. Private-source checkout uses a read-only deploy key restricted to the source repository, stored in `EMBERVEIL_SOURCE_DEPLOY_KEY`. Credentials are not included in game files, code or download manifests. There is no routine login step for each build, and Nathan's PC does not need to stay online while GitHub builds or publishes.

The source key and account access can still be revoked. The workflow emits build summaries and does not publish private source logs or source artifacts.

## Verification

Exported-content gates cover character and adventure saves, progression, sword cuts and two-handed animation. Every source file contributes to the approved digest; all public download assets must match their build evidence and server digests. These checks do not replace visual review or a hardware performance benchmark.

See `VALIDATION.md` for the current hosted-run and live launcher verification status.
