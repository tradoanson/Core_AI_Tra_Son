# VERSIONING WORKFLOW — append-only releases

## Branching
- `main`: stable integration branch.
- `release/v0.1.1-governance`: governance changes only.
- `release/vX.Y.Z`: each future version.
- Do not overwrite existing source files merely to create a new version; modify through reviewed commits on a new branch, preserving history and previous immutable tags.
- `v0.1.0` must not be tagged as certified until evidence is available.

## Repeatable release steps
1. Fetch and inventory repository tree, current HEAD SHA, existing tags, source paths and tests.
2. Create new release branch from last accepted release commit.
3. Implement additive changes, write new tests, record change entries.
4. Run `python -m unittest discover -s tests -p "test_*.py" -v` and document actual counts. If no tests discovered, FAIL.
5. Run GitHub Actions on branch; attach run URL and commit SHA to `acceptance/ACCEPTANCE_vX.Y.Z.md`.
6. Open PR; merge only after checks and review.
7. Create immutable tag `vX.Y.Z`; publish release with evidence and checksum.
8. Rollback by checking out previous immutable tag; do not overwrite prior versions.

## Explicit safeguards
- Workflow never pushes commits, creates tags, publishes packages or deploys.
- CI failures must remain failures; do not use `continue-on-error` or `|| true` for tests.
- Historical release records are append-only; corrections use a new dated addendum.
- CI tests are not proof of successful live integration.

## Audit fields
Date, actor, authorization, branch, commit SHA, changed paths, test command, observed result, CI run URL, approval and rollback target.
