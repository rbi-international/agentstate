# Proposed protocol amendments

Status: proposals only, not adopted protocol changes. `EXPERIMENT_BASE.md` remains
unchanged and authoritative. Current event/snapshot structure and nullability
remain unchanged. These proposals introduce no behavioral thresholds or results.

Any adopted structural amendment needs a protocol/schema version bump, migration
note, regenerated schemas, and reviewed compatibility tests. Preserve immutable
raw traces; migrated records are new derived artifacts with explicit provenance.
Never reconstruct unavailable historical evidence by inventing values.

## Unknown versus observed-zero counts

Limitation: several snapshot count fields require integers, while collection may
not establish those counts. Zero is observed absence, not unknown. Illustration
values alone do not establish that every framework can measure every count.

Proposed change: permit explicit null for currently non-null measurement counts,
or introduce a versioned measurement-status mechanism distinguishing known,
unknown, and unavailable. Choose one representation through protocol review.
Retain nonnegative constraints for known values and prohibit zero imputation.

Migration impact: update consuming features and missingness handling. Keep old
zeros where observation provenance supports them; flag unsupported historical
zeros for review rather than automatically reinterpreting every zero as null.

## Nullable seeds when not controllable

Limitation: `AgentEvent.source.seed` requires an integer even when an engine or
framework cannot control or report a seed. The draft manifest already supports
an explicitly uncontrollable seed being null; the event contract does not.

Proposed change: make event seed nullable and add metadata describing whether it
was controllable, requested, and effective/reported. Separate a requested seed
from claims of deterministic execution. Keep identity/provenance out of inputs.

Migration impact: preserve verified existing seeds; mark unavailable historical
seed/control evidence explicitly unknown. Update event consumers and manifests
to maintain consistent seed semantics without fabricating a zero seed.

## Unknown versus empty collection lists

Limitation: empty file/error lists do not distinguish successful collection with
no entries from absent, failed, partial, or unsupported collection.

Proposed change: add versioned collection status/coverage metadata, or allow null
lists for unknown collection while reserving empty lists for observed emptiness.
Select semantics for each list and explicitly represent partial coverage.

Migration impact: audit historical collector coverage; do not assume every empty
list is exhaustive. Update validators and consumers to preserve unknown/partial
states, and retain original records alongside any reviewed derived migration.

## Ordered events and cutoff provenance

Limitation: snapshot `recent_events` currently holds event details without event
IDs, steps, or timestamps. `agent_summary` has no input-prefix provenance. Neither
the shape nor field filtering proves that content predates the snapshot cutoff.

Proposed change: define an ordered prefix and cutoff contract, with event references
and observation positions in provenance metadata. Record the exact source prefix,
summary generation version/configuration, and input-prefix boundary. Distinguish
observation time from later ingestion time. Keep these references outside encoder
inputs and define a separate policy for terminal-state analysis.

Migration impact: reconstruct ordering/cutoffs only from retained evidence. Mark
unverifiable summaries/events ineligible pending review. Any changed recent-event
shape requires versioning and explicit adapters; never silently insert/drop events.

## Test-measurement provenance

Limitation: the signed integer `test_delta` cannot establish that its two failing
counts came from comparable measurements. Count changes can result from changed
collection, skips, commands, dependencies, or environments.

Proposed change: add versioned measurement records/references for test-population
identity, collection and execution results, command/configuration, environment,
repository state, observation position, and comparison/reference rule. Define how
collection/skip differences and relevant environment changes are accounted for.
Use the documented observation convention: previous comparable failing count
minus current failing count; unknown comparability implies null. Define no
behavioral labels or thresholds from this observation.

Migration impact: retain supported deltas; quarantine or produce reviewed derived
records with null deltas where provenance is insufficient. Record the comparison
rule version and reference selection; do not recompute raw traces in place.

## Runtime records, artifacts, and dirty-worktree provenance

Limitation: the manifest is pre-run configuration, not a complete runtime record.
A Git commit cannot describe uncommitted or untracked code. Actual timestamps,
trace locations, failures, and outcome are not fully represented there.

Proposed change: define a separate versioned run record linked to the frozen
manifest, recording actual start/end times, environment/software verification,
resource observations, failure/terminal outcome, and immutable raw-artifact
references with integrity hashes. Link derived artifacts to raw inputs and their
transformation versions. Capture dirty status and a reviewed diff/content inventory
or reproducible code snapshot for relevant tracked and untracked files, excluding
credentials and generated artifacts. Keep outcome labels and artifact references
outside encoder inputs. Separate artifact provenance from storage implementation.

Migration impact: distinguish configuration-only historical records from complete
runs. Attach available provenance without inventing runtime times or outcomes;
mark unavailable artifacts/code state explicitly unknown. Plan separate artifact
storage and retention; this proposal does not implement either.
