# textx-lang-pyflies changelog

All _notable_ changes to this project will be documented in this file.

The format is based on _[Keep a Changelog][keepachangelog]_, and this project
adheres to _[Semantic Versioning][semver]_.

Everything that is documented in the [official docs][textXDocs] is considered
the part of the public API.

Backward incompatible changes are marked with **(BIC)**. These changes are the
reason for the major version increase so when upgrading between major versions
please take a look at related PRs and issues and see if the change affects you.

## [Unreleased]

[Unreleased]: https://github.com/pyflies/pyflies/compare/0.5.0...HEAD


## [0.5.0] (released: 2021-01-12)

### Fixed

- `target` block values can be of any pyFlies base type (e.g. `Point`).
- Parsing of component scoped target mappings. E.g.
  ```
  target ... {
    keyboard.red = left
  }
  ```

[0.5.0]: https://github.com/pyflies/pyflies/compare/0.4.2...0.5.0


## [0.4.2] (released: 2020-11-12)

### Fixed

- Parsing of CRLF line endings in condition tables. This problem was triggered
  on Windows which uses CRLF line endings by default preventing condition tables
  from being parsed ([e7291126]).

[e7291126]: https://github.com/pyflies/pyflies/commit/e7291126
[0.4.2]: https://github.com/pyflies/pyflies/compare/0.4.1...0.4.2


## [0.4.1] (released: 2020-11-09)

### Added

- Mental rotation example

### Fixed

- Require keywords to be matched on word boundaries (turn `autokwd` feature of
  textX). The problem was that keywords are recognized if being start of the
  larger word (like `or` in `orientation`).
- Consider component parameter non-constant if it contains message
  sub-expression. Constant param expressions are set on the component before the
  test run and are not changed afterwards. The bug was that expression like
  `1..100 choose` would be treated as constant although a new random value
  should be calculated for each trial.

### Changed

- Docs improvements

[0.4.1]: https://github.com/pyflies/pyflies/compare/0.4.0...0.4.1


## [0.4.0] (released: 2020-11-01)

- Complete rework/redesign of the language:
  - expressions, global and test level variables
  - condition table expressions with expansion (loop, cycling)
  - Markdown table syntax
  - trial phases
  - components description using components DSL
  - flow definition with repetitions
  - ...

- Added log and csv generators.
- [VS Code integration](https://github.com/pyflies/vscode-pyflies) and
  [PsychoPy](https://github.com/pyflies/pyflies-psychopy) generator as a
  separate projects.


[0.4.0]: https://github.com/pyflies/pyflies/compare/v0.3...0.4.0

[keepachangelog]: https://keepachangelog.com/
[semver]: https://semver.org/spec/v2.0.0.html
[textXDocs]: http://textx.github.io/textX/latest/
