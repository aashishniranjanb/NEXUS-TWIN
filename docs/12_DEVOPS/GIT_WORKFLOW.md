# GIT WORKFLOW

| Field | Value |
|---|---|
| Status | Level-1 (authoritative) |
| Owner | Shared |
| Applies to | All three laptops |

---

## 1. Purpose

Keep three people working in parallel without overwriting each other, and keep `main`
demonstrable at every moment.

## 2. The rule

> `main` must always run the demo.

If `main` is broken, all three people are blocked and nobody can show anything. That is a worse
state than any individual feature being late.

## 3. Branches

```
main
├── feature/ai-pipeline              Laptop 1
├── feature/backend-simulation       Laptop 2
└── feature/frontend-command-center  Laptop 3
```

| Branch | Owner | Directories |
|---|---|---|
| `feature/ai-pipeline` | Laptop 1 | `ai/`, `data/` |
| `feature/backend-simulation` | Laptop 2 | `services/api/`, `simulation/`, `agents/`, `database/` |
| `feature/frontend-command-center` | Laptop 3 | `apps/web/` |

`shared/contracts/` and `docs/` are shared. Changes there are announced before the commit.

**Nobody commits directly to `main`.** Directory ownership means the three branches rarely touch
the same files, which is what makes merges cheap.

## 4. Daily loop

```
git checkout main
git pull origin main
git checkout feature/your-branch
git merge main            # take main's changes early and often
# work
git add -A
git commit -m "type: description"
git push origin feature/your-branch
# open PR -> quick review -> merge
```

Merge `main` into your feature branch at the start of every work block. A branch that has not
seen `main` for six hours is a merge conflict waiting to happen at the worst time.

## 5. Commit messages

```
<type>: <what changed>
```

| Type | Use |
|---|---|
| `feat` | New capability |
| `fix` | Bug fix |
| `contract` | Change in `shared/contracts/` — **always announce first** |
| `docs` | Documentation |
| `test` | Tests |
| `chore` | Config, dependencies, tooling |

Examples:

```
feat: domino propagation with storage-based ETA
fix: clamp spillover risk to [0,1]
contract: add mechanism field to SpilloverNode
```

## 6. Contract changes

The most expensive mistake available to this team is a silent field rename.

Procedure:

1. Message both other members with the exact before and after.
2. Update `shared/contracts/`, the Pydantic schema, and the fixtures in the **same commit**.
3. Prefix the commit `contract:`.
4. Merge to `main` immediately — do not sit on a contract change in a feature branch.
5. Both other members pull `main` before continuing.

Additive changes are safe. Renames and type changes are not, and require the full procedure.

## 7. Pull requests

| Requirement | Detail |
|---|---|
| Title | Same format as a commit message |
| Description | What changed, what to test |
| Size | Prefer several small PRs over one large one |
| Review | One other member; a two-minute look, not a code audit |
| Tests | Contract tests must pass before merge |
| Merge | Squash merge to keep `main` history readable |

Reviews are fast by design. The purpose is to catch a contract break or a broken build, not to
debate style under time pressure.

## 8. Never commit

| Item | Why |
|---|---|
| `data/raw/` | Large, and available from the source |
| `*.pkl`, `*.parquet` | Regenerable artifacts |
| `.env` | Secrets |
| `node_modules/`, `__pycache__/`, `.next/` | Build output |
| `game/unity/` changes | Frozen backup demo |

`data/samples/corridor_sample.csv` **is** committed, because tests and DEMO mode need it.

## 9. Conflict resolution

| Conflict | Resolution |
|---|---|
| In your own directory | Resolve yourself |
| In `shared/contracts/` | Stop, talk to the other member, resolve together — never guess |
| In `docs/` | Owner of the document decides |
| In a lockfile | Regenerate rather than hand-merge |

## 10. Tags

Tag before anything risky:

```
git tag -a demo-ready-v1 -m "Full P0 demo working"
git push origin demo-ready-v1
```

Tag after every clean full dry run. A tag is a guaranteed rollback point, and having one before
the presentation is worth more than any single additional feature.

## 11. Failure modes

| Failure | Recovery |
|---|---|
| `main` broken | Revert the merge immediately, fix on a branch. Revert first, diagnose second. |
| Contract drift | Contract tests fail; roll back to the last passing commit |
| Lost work | `git reflog` |
| Large accidental commit | `git rm --cached`, update `.gitignore`, recommit |
| Merge conflict in a lockfile | Delete, regenerate, commit |

## 12. Testing

Before every push: the app runs locally, contract tests pass, no console errors.
Before every merge to `main`: the demo still completes.

## 13. Acceptance criteria

1. Three feature branches exist and are used.
2. No direct commits to `main`.
3. Every contract change carries the `contract:` prefix and updates all three artifacts together.
4. `main` runs the demo at any point in the last 24 hours.
5. At least one `demo-ready` tag exists before presenting.

## 14. Future work

GitHub Actions running contract and unit tests on PR; protected `main` with required checks;
Conventional Commits with an automated changelog.
