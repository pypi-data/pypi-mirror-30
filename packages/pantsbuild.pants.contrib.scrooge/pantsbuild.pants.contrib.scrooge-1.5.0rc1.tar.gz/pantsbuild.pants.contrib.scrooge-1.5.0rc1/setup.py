
# DO NOT EDIT THIS FILE -- AUTOGENERATED BY PANTS
# Target: ContribPlugin(BuildFileAddress(contrib/scrooge/src/python/pants/contrib/scrooge/BUILD, plugin))

from setuptools import setup

setup(**
{   'classifiers': [   'Intended Audience :: Developers',
                       'License :: OSI Approved :: Apache Software License',
                       'Operating System :: MacOS :: MacOS X',
                       'Operating System :: POSIX :: Linux',
                       'Programming Language :: Python',
                       'Topic :: Software Development :: Build Tools',
                       'Topic :: Software Development :: Code Generators'],
    'description': 'Scrooge thrift generator pants plugins.',
    'entry_points': {   'pantsbuild.plugin': [   'register_goals = pants.contrib.scrooge.register:register_goals']},
    'install_requires': [   'twitter.common.collections<0.4,>=0.3.1',
                            'pantsbuild.pants==1.5.0rc1'],
    'license': 'Apache License, Version 2.0',
    'long_description': "Pants is an Apache2 licensed build tool written in Python.\n\nThe latest documentation can be found `here <http://pantsbuild.org/>`_.\n\n1.5.x Stable Releases\n=====================\n\nThis document describes releases leading up to the ``1.5.x`` ``stable`` series.\n\n1.5.0rc1 (03/14/2018)\n---------------------\n\nBugfixes\n~~~~~~~~\n\n* Render a warning rather than failing `list` when no targets are matched (#5598)\n  `PR #5598 <https://github.com/pantsbuild/pants/pull/5598>`_\n\n* [pantsd] Repair stale sources invalidation case. (#5589)\n  `PR #5589 <https://github.com/pantsbuild/pants/pull/5589>`_\n\nRefactoring, Improvements, and Tooling\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n* Further --changed optimization (#5579)\n  `PR #5579 <https://github.com/pantsbuild/pants/pull/5579>`_\n\n* [pantsd] Don't compute TargetRoots twice. (#5595)\n  `PR #5595 <https://github.com/pantsbuild/pants/pull/5595>`_\n\n* [coursier] use same artifact cache override as ivy (#5586)\n  `PR #5586 <https://github.com/pantsbuild/pants/pull/5586>`_\n\n1.5.0rc0 (03/07/2018)\n---------------------\n\nRefactoring, Improvements, and Tooling\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n* Cleanup v1 changed code. (#5572)\n  `PR #5572 <https://github.com/pantsbuild/pants/pull/5572>`_\n\n* Improve the performance of v2 changed. (#5571)\n  `PR #5571 <https://github.com/pantsbuild/pants/pull/5571>`_\n\n* Delete obsolete README. (#5573)\n  `PR #5573 <https://github.com/pantsbuild/pants/pull/5573>`_\n\n* Improve interpreter constraint tests and docs. (#5566)\n  `PR #5566 <https://github.com/pantsbuild/pants/pull/5566>`_\n\n* Engine is a workspace (#5555)\n  `PR #5555 <https://github.com/pantsbuild/pants/pull/5555>`_\n\n* Native engine is a stripped cdylib (#5557)\n  `PR #5557 <https://github.com/pantsbuild/pants/pull/5557>`_\n\n* Don't overwrite cffi files if they haven't changed (#5553)\n  `PR #5553 <https://github.com/pantsbuild/pants/pull/5553>`_\n\n* Don't install panic handler when RUST_BACKTRACE=1 (#5561)\n  `PR #5561 <https://github.com/pantsbuild/pants/pull/5561>`_\n\n* Only shift once, not twice (#5552)\n  `Issue #5551 <https://github.com/pantsbuild/pants/issues/5551>`_\n  `PR #5552 <https://github.com/pantsbuild/pants/pull/5552>`_\n\n* Prepare 1.4.0rc4 (#5569)\n  `PR #5569 <https://github.com/pantsbuild/pants/pull/5569>`_\n\n* [pantsd] Daemon lifecycle invalidation on configurable glob watches. (#5550)\n  `PR #5550 <https://github.com/pantsbuild/pants/pull/5550>`_\n\n* Set thrifty build_file_aliases (#5559)\n  `PR #5559 <https://github.com/pantsbuild/pants/pull/5559>`_\n\n* Better `PantsRunIntegrationTest` invalidation. (#5547)\n  `PR #5547 <https://github.com/pantsbuild/pants/pull/5547>`_\n\n* Support coverage of pants coverage tests. (#5544)\n  `PR #5544 <https://github.com/pantsbuild/pants/pull/5544>`_\n\n* Tighten `PytestRun` coverage plugin. (#5542)\n  `PR #5542 <https://github.com/pantsbuild/pants/pull/5542>`_\n\n* One additional change for 1.4.0rc3. (#5549)\n  `PR #5549 <https://github.com/pantsbuild/pants/pull/5549>`_\n\n* Provide injectables functionality in a mixin. (#5548)\n  `PR #5548 <https://github.com/pantsbuild/pants/pull/5548>`_\n\n* Revert a bunch of remoting PRs (#5543)\n  `PR #5543 <https://github.com/pantsbuild/pants/pull/5543>`_\n\n* Prep 1.4.0rc3 (#5545)\n  `PR #5545 <https://github.com/pantsbuild/pants/pull/5545>`_\n\n* CLean up fake options creation in tests. (#5539)\n  `PR #5539 <https://github.com/pantsbuild/pants/pull/5539>`_\n\n* Don't cache lmdb_store directory (#5541)\n  `PR #5541 <https://github.com/pantsbuild/pants/pull/5541>`_\n\nNew Features\n~~~~~~~~~~~~\n\n* Thrifty support for pants (#5531)\n  `PR #5531 <https://github.com/pantsbuild/pants/pull/5531>`_\n\nDocumentation Updates\n~~~~~~~~~~~~~~~~~~~~~\n\n* Fix documentation code blocks. (#5558)\n  `PR #5558 <https://github.com/pantsbuild/pants/pull/5558>`_\n\n\n1.5.0.dev5 (03/02/2018)\n-----------------------\n\nNew Features\n~~~~~~~~~~~~\n\n* Add ability for pants to call coursier with the new url attribute (#5527)\n  `PR #5527 <https://github.com/pantsbuild/pants/pull/5527>`_\n\n* Don't force inherit_path to be a bool (#5482)\n  `PR #5482 <https://github.com/pantsbuild/pants/pull/5482>`_\n  `PR #444 <https://github.com/pantsbuild/pex/pull/444>`_\n\nBugfixes\n~~~~~~~~\n\n* [pantsd] Repair end to end runtracker timing for pantsd runs. (#5526)\n  `PR #5526 <https://github.com/pantsbuild/pants/pull/5526>`_\n\nRefactoring, Improvements, and Tooling\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n* Generate a single python source chroot. (#5535)\n  `PR #5535 <https://github.com/pantsbuild/pants/pull/5535>`_\n\n* Improve py.test covered paths reporting. (#5534)\n  `PR #5534 <https://github.com/pantsbuild/pants/pull/5534>`_\n\n* Improve test reporting in batched partitions. (#5420)\n  `PR #5420 <https://github.com/pantsbuild/pants/pull/5420>`_\n\n* Fix non-exportable library target subclasses (#5533)\n  `PR #5533 <https://github.com/pantsbuild/pants/pull/5533>`_\n\n* Cleanups for 3bdd5506dc3 that I forgot to push before merging. (#5529)\n  `PR #5529 <https://github.com/pantsbuild/pants/pull/5529>`_\n\n* New-style BinaryTool Subsystems for isort and go distribution. (#5523)\n  `PR #5523 <https://github.com/pantsbuild/pants/pull/5523>`_\n\n* Use rust logging API (#5525)\n  `PR #5525 <https://github.com/pantsbuild/pants/pull/5525>`_\n\n* Add comment about significance of unsorted-ness of sources (#5524)\n  `PR #5524 <https://github.com/pantsbuild/pants/pull/5524>`_\n\n* cloc never executes in the v2 engine (#5518)\n  `PR #5518 <https://github.com/pantsbuild/pants/pull/5518>`_\n\n* Robustify `PantsRequirementIntegrationTest`. (#5520)\n  `PR #5520 <https://github.com/pantsbuild/pants/pull/5520>`_\n\n* Subsystems for the ragel and cloc binaries (#5517)\n  `PR #5517 <https://github.com/pantsbuild/pants/pull/5517>`_\n\n* Move Key interning to rust (#5455)\n  `PR #5455 <https://github.com/pantsbuild/pants/pull/5455>`_\n\n* Don't reinstall plugin wheels on every invocation. (#5506)\n  `PR #5506 <https://github.com/pantsbuild/pants/pull/5506>`_\n\n* A new Thrift binary tool subsystem. (#5512)\n  `PR #5512 <https://github.com/pantsbuild/pants/pull/5512>`_\n\n1.5.0.dev4 (02/23/2018)\n-----------------------\n\nNew Features\n~~~~~~~~~~~~\n\n* Fix up remote process execution (#5500)\n  `PR #5500 <https://github.com/pantsbuild/pants/pull/5500>`_\n\n* Remote execution uploads files from a Store (#5499)\n  `PR #5499 <https://github.com/pantsbuild/pants/pull/5499>`_\n\nPublic API Changes\n~~~~~~~~~~~~~~~~~~\n\n* Redesign JavaScript Style Checker to use ESLint directly (#5265)\n  `PR #5265 <https://github.com/pantsbuild/pants/pull/5265>`_\n\n* A convenient mechanism for fetching binary tools via subsystems (#5443)\n  `PR #5443 <https://github.com/pantsbuild/pants/pull/5443>`_\n\n* Qualify kythe target names with 'java-'. (#5459)\n  `PR #5459 <https://github.com/pantsbuild/pants/pull/5459>`_\n\nBugfixes\n~~~~~~~~\n\n* [pantsd] Set the remote environment for pantsd-runner and child processes. (#5508)\n  `PR #5508 <https://github.com/pantsbuild/pants/pull/5508>`_\n\n* Don't special-case python dists in resolve_requirements(). (#5483)\n  `PR #5483 <https://github.com/pantsbuild/pants/pull/5483>`_\n\n* Add a dependency on the pants source to the integration test base target (#5481)\n  `PR #5481 <https://github.com/pantsbuild/pants/pull/5481>`_\n\n* fix/integration test for pants_requirement() (#5457)\n  `PR #5457 <https://github.com/pantsbuild/pants/pull/5457>`_\n\n* Never allow the shader to rewrite the empty-string package. (#5461)\n  `PR #5461 <https://github.com/pantsbuild/pants/pull/5461>`_\n\n* Bump release.sh to pex 1.2.16. (#5460)\n  `PR #5460 <https://github.com/pantsbuild/pants/pull/5460>`_\n\n* fix/tests: subsystems can't declare dependencies on non-globally-scoped subsystems (#5456)\n  `PR #5456 <https://github.com/pantsbuild/pants/pull/5456>`_\n\n* Fix missing interpreter constraints bug when a Python target does not have sources (#5501)\n  `PR #5501 <https://github.com/pantsbuild/pants/pull/5501>`_\n\nDocumentation Updates\n~~~~~~~~~~~~~~~~~~~~~\n\n* Fix reference html/js: expand/collapse toggle in Firefox (#5507)\n  `PR #5507 <https://github.com/pantsbuild/pants/pull/5507>`_\n\nRefactoring, Improvements, and Tooling\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n* Delete unused old python pipeline classes. (#5509)\n  `PR #5509 <https://github.com/pantsbuild/pants/pull/5509>`_\n\n* Make the export task use new python pipeline constructs. (#5486)\n  `PR #5486 <https://github.com/pantsbuild/pants/pull/5486>`_\n\n* Remote command execution returns a Future (#5497)\n  `PR #5497 <https://github.com/pantsbuild/pants/pull/5497>`_\n\n* Snapshot is backed by LMDB not tar files (#5496)\n  `PR #5496 <https://github.com/pantsbuild/pants/pull/5496>`_\n\n* Local process execution happens in a directory (#5495)\n  `PR #5495 <https://github.com/pantsbuild/pants/pull/5495>`_\n\n* Snapshot can get FileContent (#5494)\n  `PR #5494 <https://github.com/pantsbuild/pants/pull/5494>`_\n\n* Move materialize_{file,directory} from fs_util to Store (#5493)\n  `PR #5493 <https://github.com/pantsbuild/pants/pull/5493>`_\n\n* Remove support dir overrides (#5489)\n  `PR #5489 <https://github.com/pantsbuild/pants/pull/5489>`_\n\n* Upgrade to rust 1.24 (#5477)\n  `PR #5477 <https://github.com/pantsbuild/pants/pull/5477>`_\n\n* Simplify python local dist handling code. (#5480)\n  `PR #5480 <https://github.com/pantsbuild/pants/pull/5480>`_\n\n* Remove some outdated test harness code that exists in the base class (#5472)\n  `PR #5472 <https://github.com/pantsbuild/pants/pull/5472>`_\n\n* Tweaks to the BinaryTool subsystem and use it to create an LLVM subsystem (#5471)\n  `PR #5471 <https://github.com/pantsbuild/pants/pull/5471>`_\n\n* Refactor python pipeline utilities (#5474)\n  `PR #5474 <https://github.com/pantsbuild/pants/pull/5474>`_\n\n* Fetch the buildozer binary using a subsystem. (#5462)\n  `PR #5462 <https://github.com/pantsbuild/pants/pull/5462>`_\n\n* Narrow the warnings we ignore when compiling our cffi (#5458)\n  `PR #5458 <https://github.com/pantsbuild/pants/pull/5458>`_\n\n1.5.0.dev3 (02/10/2018)\n-----------------------\n\nNew Features\n~~~~~~~~~~~~\n* Python distribution task for user-defined setup.py + integration with ./pants {run/binary/test} (#5141)\n  `PR #5141 <https://github.com/pantsbuild/pants/pull/5141>`_\n\nRefactoring, Improvements, and Tooling\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n* Bundle all kythe entries, regardless of origin. (#5450)\n  `PR #5450 <https://github.com/pantsbuild/pants/pull/5450>`_\n\n\n1.5.0.dev2 (02/05/2018)\n-----------------------\n\nNew Features\n~~~~~~~~~~~~\n* Allow intransitive unpacking of jars. (#5398)\n  `PR #5398 <https://github.com/pantsbuild/pants/pull/5398>`_\n\nAPI Changes\n~~~~~~~~~~~\n* [strict-deps][build-graph] add new predicate to build graph traversal; Update Target.strict_deps to use it (#5150)\n  `PR #5150 <https://github.com/pantsbuild/pants/pull/5150>`_\n\n* Deprecate IDE project generation tasks. (#5432)\n  `PR #5432 <https://github.com/pantsbuild/pants/pull/5432>`_\n\n* Enable workdir-max-build-entries by default. (#5423)\n  `PR #5423 <https://github.com/pantsbuild/pants/pull/5423>`_\n\n* Fix tasks2 deprecations to each have their own module. (#5421)\n  `PR #5421 <https://github.com/pantsbuild/pants/pull/5421>`_\n\n* Console tasks can output nothing without erroring (#5412)\n  `PR #5412 <https://github.com/pantsbuild/pants/pull/5412>`_\n\n* Remove a remaining old-python-pipeline task from contrib/python. (#5411)\n  `PR #5411 <https://github.com/pantsbuild/pants/pull/5411>`_\n\n* Make the thrift linter use the standard linter mixin. (#5394)\n  `PR #5394 <https://github.com/pantsbuild/pants/pull/5394>`_\n\nBugfixes\n~~~~~~~~\n* Fix `PytestRun` to handle multiple source roots. (#5400)\n  `PR #5400 <https://github.com/pantsbuild/pants/pull/5400>`_\n\n* Fix a bug in task logging in tests. (#5404)\n  `PR #5404 <https://github.com/pantsbuild/pants/pull/5404>`_\n\n* [pantsd] Repair console interactivity in pantsd runs. (#5352)\n  `PR #5352 <https://github.com/pantsbuild/pants/pull/5352>`_\n\nDocumentation Updates\n~~~~~~~~~~~~~~~~~~~~~\n* Document release reset of master. (#5397)\n  `PR #5397 <https://github.com/pantsbuild/pants/pull/5397>`_\n\nRefactoring, Improvements, and Tooling\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n* Make the Kythe Java indexer emit JVM nodes. (#5435)\n  `PR #5435 <https://github.com/pantsbuild/pants/pull/5435>`_\n\n* Release script allows wheel listing (#5431)\n  `PR #5431 <https://github.com/pantsbuild/pants/pull/5431>`_\n\n* Get version from version file not by running pants (#5428)\n  `PR #5428 <https://github.com/pantsbuild/pants/pull/5428>`_\n\n* Improve python/rust boundary error handling (#5414)\n  `PR #5414 <https://github.com/pantsbuild/pants/pull/5414>`_\n\n* Factor up shared test partitioning code. (#5416)\n  `PR #5416 <https://github.com/pantsbuild/pants/pull/5416>`_\n\n* Set the log level when capturing logs in tests. (#5418)\n  `PR #5418 <https://github.com/pantsbuild/pants/pull/5418>`_\n\n* Simplify `JUnitRun` internals. (#5410)\n  `PR #5410 <https://github.com/pantsbuild/pants/pull/5410>`_\n\n* [v2-engine errors] Sort suggestions for typo'd targets, unique them when trace is disabled (#5413)\n  `PR #5413 <https://github.com/pantsbuild/pants/pull/5413>`_\n\n* No-op ivy resolve is ~100ms cheaper (#5389)\n  `PR #5389 <https://github.com/pantsbuild/pants/pull/5389>`_\n\n* Process executor does not require env flag to be set (#5409)\n  `PR #5409 <https://github.com/pantsbuild/pants/pull/5409>`_\n\n* [pantsd] Don't invalidate on surface name changes to config/rc files. (#5408)\n  `PR #5408 <https://github.com/pantsbuild/pants/pull/5408>`_\n\n* [pantsd] Break out DPR._nailgunned_stdio() into multiple methods. (#5405)\n  `PR #5405 <https://github.com/pantsbuild/pants/pull/5405>`_\n\n* Sort the indexable targets consistently. (#5403)\n  `PR #5403 <https://github.com/pantsbuild/pants/pull/5403>`_\n\n\n1.5.0.dev1 (01/26/2018)\n-----------------------\n\nNew Features\n~~~~~~~~~~~~\n\n* [pantsd] Add RunTracker stats. (#5374)\n  `PR #5374 <https://github.com/pantsbuild/pants/pull/5374>`_\n\nAPI Changes\n~~~~~~~~~~~\n\n* [pantsd] Bump to watchman 4.9.0-pants1. (#5386)\n  `PR #5386 <https://github.com/pantsbuild/pants/pull/5386>`_\n\nBugfixes\n~~~~~~~~\n\n* Single resolve with coursier (#5362)\n  `Issue #743 <https://github.com/coursier/coursier/issues/743>`_\n  `PR #5362 <https://github.com/pantsbuild/pants/pull/5362>`_\n  `PR #735 <https://github.com/coursier/coursier/pull/735>`_\n\n* Repoint the 'current' symlink even for valid VTs. (#5375)\n  `PR #5375 <https://github.com/pantsbuild/pants/pull/5375>`_\n\n* Do not download node package multiple times (#5372)\n  `PR #5372 <https://github.com/pantsbuild/pants/pull/5372>`_\n\n* Fix calls to trace (#5366)\n  `Issue #5365 <https://github.com/pantsbuild/pants/issues/5365>`_\n  `PR #5366 <https://github.com/pantsbuild/pants/pull/5366>`_\n\nDocumentation Updates\n~~~~~~~~~~~~~~~~~~~~~\n\n* Update the rust readme. (#5393)\n  `PR #5393 <https://github.com/pantsbuild/pants/pull/5393>`_\n\n* Update our JVM-related config and documentation. (#5370)\n  `PR #5370 <https://github.com/pantsbuild/pants/pull/5370>`_\n\nRefactoring, Improvements, and Tooling\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n* Apply goal-level skip/transitive options to lint/fmt tasks. (#5383)\n  `PR #5383 <https://github.com/pantsbuild/pants/pull/5383>`_\n\n* [pantsd] StoreGCService improvements. (#5391)\n  `PR #5391 <https://github.com/pantsbuild/pants/pull/5391>`_\n\n* Remove unused field (#5390)\n  `PR #5390 <https://github.com/pantsbuild/pants/pull/5390>`_\n\n* Extract CommandRunner struct (#5377)\n  `PR #5377 <https://github.com/pantsbuild/pants/pull/5377>`_\n\n* [pantsd] Repair pantsd integration tests for execution via pantsd. (#5387)\n  `PR #5387 <https://github.com/pantsbuild/pants/pull/5387>`_\n\n* fs_util writes to remote CAS if it's present (#5378)\n  `PR #5378 <https://github.com/pantsbuild/pants/pull/5378>`_\n\n* Add back isort tests (#5380)\n  `PR #5380 <https://github.com/pantsbuild/pants/pull/5380>`_\n\n* Fix fail-fast tests. (#5371)\n  `PR #5371 <https://github.com/pantsbuild/pants/pull/5371>`_\n\n* Store can copy Digests from local to remote (#5333)\n  `PR #5333 <https://github.com/pantsbuild/pants/pull/5333>`_\n\n1.5.0.dev0 (01/22/2018)\n-----------------------\n\nNew Features\n~~~~~~~~~~~~\n\n* add avro/java contrib plugin to the release process (#5346)\n  `PR #5346 <https://github.com/pantsbuild/pants/pull/5346>`_\n\n* Add the mypy contrib module to pants release process (#5335)\n  `PR #5335 <https://github.com/pantsbuild/pants/pull/5335>`_\n\n* Publish the codeanalysis contrib plugin. (#5322)\n  `PR #5322 <https://github.com/pantsbuild/pants/pull/5322>`_\n\nAPI Changes\n~~~~~~~~~~~\n\n* Remove 1.5.0.dev0 deprecations (#5363)\n  `PR #5363 <https://github.com/pantsbuild/pants/pull/5363>`_\n\n* Deprecate the Android contrib backend. (#5343)\n  `PR #5343 <https://github.com/pantsbuild/pants/pull/5343>`_\n\n* [contrib/scrooge] Add exports support to scrooge (#5357)\n  `PR #5357 <https://github.com/pantsbuild/pants/pull/5357>`_\n\n* Remove superfluous --dist flag from kythe indexer task. (#5344)\n  `PR #5344 <https://github.com/pantsbuild/pants/pull/5344>`_\n\n* Delete deprecated modules removable in 1.5.0dev0. (#5337)\n  `PR #5337 <https://github.com/pantsbuild/pants/pull/5337>`_\n\n* An --eager option for BootstrapJvmTools. (#5336)\n  `PR #5336 <https://github.com/pantsbuild/pants/pull/5336>`_\n\n* Deprecate the v1 engine option. (#5338)\n  `PR #5338 <https://github.com/pantsbuild/pants/pull/5338>`_\n\n* Remove the target labels mechanism  (#5320)\n  `PR #5320 <https://github.com/pantsbuild/pants/pull/5320>`_\n\n* Remove wiki-related targets from contrib and back to docgen (#5319)\n  `PR #5319 <https://github.com/pantsbuild/pants/pull/5319>`_\n\n* Get rid of the is_thrift and is_test target properties. (#5318)\n  `PR #5318 <https://github.com/pantsbuild/pants/pull/5318>`_\n\n* First of a series of changes to get rid of target labels. (#5312)\n  `PR #5312 <https://github.com/pantsbuild/pants/pull/5312>`_\n\nBugfixes\n~~~~~~~~\n\n* Fix a silly bug when computing indexable targets. (#5359)\n  `PR #5359 <https://github.com/pantsbuild/pants/pull/5359>`_\n\n* [pantsd] Repair daemon wedge on log rotation. (#5358)\n  `PR #5358 <https://github.com/pantsbuild/pants/pull/5358>`_\n\nRefactoring, Improvements, and Tooling\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n* A lightweight mechanism for registering options at the goal level. (#5325)\n  `PR #5325 <https://github.com/pantsbuild/pants/pull/5325>`_\n\n* Ensure test report results are always exposed. (#5368)\n  `PR #5368 <https://github.com/pantsbuild/pants/pull/5368>`_\n\n* Add error_details proto (#5367)\n  `PR #5367 <https://github.com/pantsbuild/pants/pull/5367>`_\n\n* Store can expand directories into transitive fingerprints (#5331)\n  `PR #5331 <https://github.com/pantsbuild/pants/pull/5331>`_\n\n* Store can tell what the EntryType of a Fingerprint is (#5332)\n  `PR #5332 <https://github.com/pantsbuild/pants/pull/5332>`_\n\n* Protobuf implementation uses Bytes instead of Vec (#5329)\n  `PR #5329 <https://github.com/pantsbuild/pants/pull/5329>`_\n\n* Store and remote::ByteStore use Digests not Fingerprints (#5347)\n  `PR #5347 <https://github.com/pantsbuild/pants/pull/5347>`_\n\n* Garbage collect Store entries (#5345)\n  `PR #5345 <https://github.com/pantsbuild/pants/pull/5345>`_\n\n* Port IsolatedProcess implementation from Python to Rust - Split 1  (#5239)\n  `PR #5239 <https://github.com/pantsbuild/pants/pull/5239>`_\n\n* python2: do not resolve requirements if no python targets in targets closure (#5361)\n  `PR #5361 <https://github.com/pantsbuild/pants/pull/5361>`_\n\n* Store takes a reference, not an owned type (#5334)\n  `PR #5334 <https://github.com/pantsbuild/pants/pull/5334>`_\n\n* Bump to pex==1.2.16. (#5355)\n  `PR #5355 <https://github.com/pantsbuild/pants/pull/5355>`_\n\n* Reenable lighter contrib sanity checks (#5340)\n  `PR #5340 <https://github.com/pantsbuild/pants/pull/5340>`_\n\n* Use helper functions in tests (#5328)\n  `PR #5328 <https://github.com/pantsbuild/pants/pull/5328>`_\n\n* Add support for alternate packages in the pex that is built. (#5283)\n  `PR #5283 <https://github.com/pantsbuild/pants/pull/5283>`_\n\n* List failed crates when running all rust tests (#5327)\n  `PR #5327 <https://github.com/pantsbuild/pants/pull/5327>`_\n\n* More sharding to alleviate flaky timeout from integration tests (#5324)\n  `PR #5324 <https://github.com/pantsbuild/pants/pull/5324>`_\n\n* Update lockfile for fs_util (#5326)\n  `PR #5326 <https://github.com/pantsbuild/pants/pull/5326>`_\n\n* Implement From in both directions for Digests (#5330)\n  `PR #5330 <https://github.com/pantsbuild/pants/pull/5330>`_\n\nDocumentation Updates\n~~~~~~~~~~~~~~~~~~~~~\n\n* add mypy to list of released plugins in docs (#5341)\n  `PR #5341 <https://github.com/pantsbuild/pants/pull/5341>`_\n\n* Incorporate the more-frequent-stable release proposal (#5311)\n  `PR #5311 <https://github.com/pantsbuild/pants/pull/5311>`_\n",
    'name': 'pantsbuild.pants.contrib.scrooge',
    'namespace_packages': ['pants', 'pants.contrib'],
    'package_data': {   },
    'package_dir': {   '': 'src'},
    'packages': [   'pants',
                    'pants.contrib',
                    'pants.contrib.scrooge',
                    'pants.contrib.scrooge.tasks'],
    'url': 'https://github.com/pantsbuild/pants',
    'version': '1.5.0rc1',
    'zip_safe': True}
)
