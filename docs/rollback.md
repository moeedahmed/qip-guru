# Rollback — QIP Guru

QIP Guru is distributed as a versioned PyPI/GitHub package (`qip`/`qip-guru`
console entry points), not a hosted service. There is no live deployment,
database, or bot to roll back — "rollback" here means reverting a bad
release or a bad commit on `main`.

## Bad commit on `main` (not yet released)

```bash
git log --oneline -5           # identify the bad commit
git revert <bad-commit-sha>    # new commit that undoes it, never rewrite history on main
./scripts/verify_release.sh    # confirm the revert is green before pushing
```

## Bad published release (PyPI / GitHub release)

QIP Guru has no auto-update or live install; users pin a version. There is
no in-place "unpublish" story:

1. Do not delete or overwrite the bad release artifact/tag.
2. Fix forward: cut a new patch version with the fix, verified by
   `./scripts/verify_release.sh`.
3. Update `CHANGELOG.md` noting the bad version and the fix version, so
   users pinned to a range know to move.

## No migrations to roll back

QIP Guru owns no database and applies no schema migrations (see
"Migration safety" in `AGENTS.md`) — there is never a migration-rollback
step.

## Fast checklist

- [ ] Bad commit/version identified
- [ ] `./scripts/verify_release.sh` passes on the fix before it is
      committed/tagged
- [ ] `CHANGELOG.md` updated
- [ ] Root cause noted in the revert or fix commit message
