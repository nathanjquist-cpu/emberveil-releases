# Emberveil releases

Public Windows downloads and the update feed for Emberveil, a first-person fantasy RPG prototype.

The game launcher reads `releases/latest/download/release.json`. Stable releases contain the game EXE, PCK, standalone ZIP, credits ZIP and that manifest. The game source and private recovery history are not stored here.

## Publishing a tested build

1. Commit `requests/VERSION.json` with the tested ZIP size/SHA-256, exact game hashes, launcher manifest and release notes. This does not publish an update. The connected GitHub app can submit this small text file.
2. Create a release with tag **`staging-vVERSION`**, target **main**, attach the approved **`Emberveil-Windows-Prototype-VERSION.zip`**, check **Set as a pre-release**, and publish the prerelease. Wait for the ZIP upload to finish first. Do not mark it as Latest.
3. The **Publish tested Emberveil build** workflow starts automatically. It verifies the approved ZIP and inner game hashes, prepares the five launcher assets, uploads to a separate stable draft, checks GitHub's asset digests, and only then publishes **`vVERSION`** as Latest.
4. Confirm the Actions run succeeds, then use the launcher to Check for updates. The workflow validates the public feed; a real launcher download/activation check is a separate release gate.

For the current build, use `staging-v0.13.0` and `Emberveil-Windows-Prototype-0.13.0.zip`.

You can also select **Actions → Publish tested Emberveil build → Run workflow**, enter the version, and choose **verify** or **publish**. Verify reads the staging ZIP without changing releases. Rerun publish to resume an interrupted draft. Published versions are never overwritten or silently downgraded. Staging prereleases remain available for recovery and are never selected by the normal launcher feed.

## Authentication and the initial handoff

Publishing runs on GitHub using the job's built-in `GITHUB_TOKEN` with repository Contents write permission. No personal token is saved in code, game files, or chat. You do not sign in to GitHub CLI for the workflow itself.

The tested ZIP still has to reach GitHub. Upload it in the GitHub release page while signed in, or use a locally authenticated GitHub CLI. A sign-in on your own persistent computer can be reused for future file transfers; a sign-in inside a disposable build workspace may be lost. This workflow does not grant the ChatGPT connector a binary-upload capability and does not compile the private game source.

## Validation

`python3 -m unittest discover -s tests -v` checks exact runtime bytes, changed downloads, unsafe/source ZIP members, wrong launcher URLs, version downgrades, deterministic credits, server-digest mismatches and interrupted uploads that must stay unpublished. Each workflow run also checks the current public manifest against GitHub's game-asset digests.

**Does this make sense?** An incomplete staging upload cannot replace a working launcher release. The requested version and exact tested bytes must agree before publication. The current launcher URL, existing stable downloads and player saves remain intact. No visual game assets or runtime code are changed by this publishing setup.
