<div align="center">

<img src="docs/assets/logo.svg" width="180" alt="ModelCardDiff logo" />

# ModelCardDiff

**Gate and compare model cards against a requirements schema** - check a card for completeness, diff two versions, and fail CI when the story changes.

[![ci](https://github.com/rabbittsui/ModelCardDiff/actions/workflows/ci.yml/badge.svg)](https://github.com/rabbittsui/ModelCardDiff/actions/workflows/ci.yml)
![license](https://img.shields.io/badge/license-MIT-blue)
![python](https://img.shields.io/badge/python-3.11%2B-blue)

</div>

<table align="center">
  <thead>
    <tr>
      <th>Required</th>
      <th>Present in the sample card</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>Overview</td><td>yes</td></tr>
    <tr><td>Intended Use</td><td>yes</td></tr>
    <tr><td>Capabilities</td><td>yes</td></tr>
    <tr><td>Limitations</td><td>yes</td></tr>
    <tr><td>Results</td><td>yes</td></tr>
  </tbody>
</table>

ModelCardDiff gates a model card against a declared requirements schema, and it
compares two versions of a card to classify what changed. It reads a card in a
small structured format, checks that the card is complete and honest, and gives
a clear pass or refuse with reasons. When you have two versions of the same
card it tells you which changes are safe editing and which ones quietly weaken
the record, because a limitation removed without comment is the change most
worth catching.

The table above is not illustrative. It is the result of the real gate run
against `samples/complete.card` using `samples/schema.txt`, reproduced later in
this document with the command and its verbatim output.

## The problem

A model card is a document that describes what a model does, what it should be
used for, and where it falls short. Two things go wrong with model cards over
time, and both are quiet.

The first is that a card makes a capability claim that no evaluation supports.
Someone writes "reaches state of the art quality on every public benchmark" and
there is no result in the card that measures it. The claim reads well and cites
nothing, or cites an evaluation that does not appear in the results. A reader
skimming the card has no way to tell a backed claim from an unbacked one.

The second is that a card loses a limitation between versions. A model had a
known weakness, the weakness was written down, and in the next revision the
sentence is gone. Nobody announced the removal. The model may still have the
weakness. A plain text diff would show the deletion buried among reworded
sentences and updated numbers, and it is easy to miss.

ModelCardDiff exists for those two failures. It refuses a card that is
incomplete or makes an unbacked claim, and when it compares two versions it
raises a removed limitation and a regressed metric to the top of the report
rather than leaving them in a wall of line changes.

## What the tool checks

The gate runs four checks. A card passes only when all four hold.

1. Every required section named by the schema exists in the card and has a
   non-empty body.
2. Every capability claim cites an evaluation, and every cited evaluation
   appears in the Results section. A claim that cites nothing is an uncited
   claim. A claim that cites an id no result provides is a dangling citation.
3. No claim quotes an exact metric value that no result carries. A claim that
   states a bound, such as "accuracy above 0.90", is a threshold and is not
   required to equal a result. A claim that states an exact value, such as
   "accuracy of 0.99", must match a result value.
4. Every stated limitation is distinct. Two limitations that reduce to the same
   content words after removing stopwords are treated as boilerplate repetition
   rather than two separate limitations.

The diff classifies every change between two versions into exactly one of four
kinds: an added claim, a removed limitation, a metric regression, or an
editorial change. The direction that counts as a regression depends on the
metric. For a rate whose name contains `confusion`, `error`, `loss`, or
`latency`, a rise is a regression. For everything else a fall is a regression.

## Install and run

The tool is pure Python 3.11 with no third party dependencies. You can run it
straight from the source tree by putting `src` on the path.

```
set PYTHONPATH=src
python -m modelcarddiff version
```

On a POSIX shell the first line is `export PYTHONPATH=src` instead. Installing
the package with pip also installs a `modelcarddiff` console script.

```
pip install .
modelcarddiff version
```

## The card format

A card is Markdown with a small set of conventions. The parser lives in
`src/modelcarddiff/card.py`.

- `# Title` on the first heading line is the card title.
- `## Section Name` starts a section. Its body is every line until the next
  `##` heading.
- A capability claim is a bullet in the Capabilities section written as
  `- claim: <text> (cites: <eval-id>)`. The `(cites: <eval-id>)` suffix is
  optional. A claim without it is an uncited claim.
- A limitation is any bullet in the Limitations section.
- A result is a line in the Results section written as
  `<eval-id> = <metric-name> <value>`. The value is read as a number when it
  parses as one, otherwise it is kept as text.

Here is the Capabilities and Results section of `samples/complete.card`, which
shows a claim citing a result that exists.

```
## Capabilities

- claim: Classifies the eight supported intents with accuracy above 0.90 on the held out split. (cites: eval-intent-accuracy)

## Results

eval-intent-accuracy = accuracy 0.93
```

## The schema format

A schema is a list of directives, one per line, parsed by
`src/modelcarddiff/schema.py`. Blank lines and lines beginning with `#` are
ignored.

```
require Overview
require Intended Use
require Capabilities
require Limitations
require Results
```

Each `require` names a section that must exist and be non-empty. Section names
are matched case insensitively. A duplicate `require` is collapsed, so listing
a section twice does not report it twice.

## Commands

The command line interface is argparse based, defined in
`src/modelcarddiff/cli.py`. There are four subcommands.

| Command | Arguments | Purpose |
| --- | --- | --- |
| `gate` | `<schema> <card>` | Check a card against a schema and pass or refuse. |
| `diff` | `<old> <new>` | Compare two card versions and classify each change. |
| `claims` | `<card>` | Show which evaluation each capability claim cites. |
| `version` | none | Print the package version. |

## Worked example: gating the sample cards

The complete card satisfies every check. This is the run that fills the table
at the top of this document.

```
python -m modelcarddiff gate samples/schema.txt samples/complete.card
```

```
PASS complete.card: all checks satisfied
```

The incomplete card is authored to fail three ways at once: it omits the
required Limitations section, it makes a memory claim that cites nothing, and it
makes a benchmark claim that cites an evaluation the results never define.

```
python -m modelcarddiff gate samples/schema.txt samples/incomplete.card
```

```
REFUSE incomplete.card: 3 finding(s)
  [missing-section] required section 'Limitations' is missing
  [uncited-claim] (line 16) claim cites no evaluation: Runs comfortably within 64 megabytes of memory on the target device.
  [dangling-citation] (line 17) claim cites 'eval-sota' which is not in results: Reaches state of the art quality on every public benchmark.
```

## Worked example: diffing two versions

The second version of the complete card adds a claim, drops a limitation, and
regresses two metrics. The diff separates the change that matters from the
change that does not.

```
python -m modelcarddiff diff samples/complete.card samples/complete-v2.card
```

```
diff complete.card -> complete-v2.card: 5 change(s)
  [added claim] Supports a new escalation intent bringing the total to nine classes.
  [removed limitation] The refund and billing classes share vocabulary and are confused more often than other pairs.
  [metric regression] eval-intent-accuracy accuracy fell from 0.93 to 0.91
  [metric regression] eval-refund-billing-confusion confusion_rate rose from 0.11 to 0.14
  [editorial] result added: eval-escalation-recall recall 0.82
```

```
summary: 1 added claim, 1 removed limitation, 2 metric regression, 1 editorial
```

The removed limitation is the refund and billing confusion note. Nothing in the
prose announced its removal. The two regressions move in opposite numeric
directions, accuracy down and confusion rate up, and the tool reports both as
regressions because it knows a higher confusion rate is worse.

The `claims` command shows the citation state of each claim on its own. Here it
is on the incomplete card.

```
python -m modelcarddiff claims samples/incomplete.card
```

```
claims for incomplete.card: 3
  CITES    eval-intent-accuracy         Classifies the eight supported intents with accuracy above 0.88 on the held out split.
  UNCITED  -                            Runs comfortably within 64 megabytes of memory on the target device.
  DANGLING eval-sota                    Reaches state of the art quality on every public benchmark.
summary: 1 resolved, 1 uncited, 1 dangling
```

## Reading the reports

Each finding and each change should trigger a specific action.

| Finding or change | What it means | What to do |
| --- | --- | --- |
| `missing-section` | A required section is absent. | Add the section with real content. |
| `empty-section` | A required section exists but has no body. | Write the section or remove the requirement. |
| `uncited-claim` | A capability claim cites no evaluation. | Add a citation to a result, or soften the claim. |
| `dangling-citation` | A claim cites an id no result defines. | Add the missing result, or fix the id. |
| `unmatched-metric` | A claim quotes an exact value no result carries. | Correct the number or the result. |
| `duplicate-limitation` | Two limitations say the same thing. | Merge them or write a distinct second limitation. |
| added claim | A new capability was asserted. | Confirm it is backed before shipping. |
| removed limitation | A known weakness was dropped. | Confirm the weakness is genuinely gone. |
| metric regression | A result moved in the worse direction. | Decide whether the regression is acceptable. |
| editorial | Wording or a non-regressing value changed. | Read for accuracy, no gate action needed. |

## Output format, field by field

The gate report is line oriented so it diffs cleanly in git.

| Line | Fields | Meaning |
| --- | --- | --- |
| header | `PASS <card>: ...` or `REFUSE <card>: <n> finding(s)` | Overall result and finding count. |
| finding | `  [<code>] (line <n>) <message>` | One finding, indented, with its code and source line when known. |

The diff report has a header, one line per change, and a summary.

| Line | Fields | Meaning |
| --- | --- | --- |
| header | `diff <old> -> <new>: <n> change(s)` | The two versions and the change count. |
| change | `  [<label>] <detail>` | One classified change. |
| summary | `summary: <a> added claim, <b> removed limitation, ...` | Counts by kind. |

The claims report has a header, one line per claim, and a summary.

| Line | Fields | Meaning |
| --- | --- | --- |
| header | `claims for <card>: <n>` | The card and its claim count. |
| claim | `  <STATUS> <target> <text>` | Status is CITES, UNCITED, or DANGLING. |
| summary | `summary: <a> resolved, <b> uncited, <c> dangling` | Counts by status. |

## Exit codes

| Code | Meaning |
| --- | --- |
| 0 | Clean. The gate passed, or the diff found no regression. |
| 1 | Findings present. The gate refused, or the diff found a regression. |
| 2 | Usage error, including a malformed schema. |

The diff exits 1 only on a metric regression, not on a removed limitation. A
removed limitation is always shown and always worth reading, but the numeric
gate for continuous integration is the regression. If you want to fail a build
on a dropped limitation as well, grep the output for `removed limitation`.

<img src="docs/assets/logo.svg" alt="ModelCardDiff wordmark, modelcard in dark ink and diff in green" width="240" />

## Limitations

The tool is deliberately small, and it does not do several things.

- It does not judge whether a claim is true, only whether it cites an
  evaluation that exists. A card can cite a result that is itself wrong, and the
  gate will pass it.
- It does not read the value of a bound. A claim of "accuracy above 0.90" passes
  whether the cited result is 0.93 or 0.05. The bound is treated as prose, not
  compared against the number.
- The distinctness check compares content words after removing a fixed stopword
  list. Two limitations that describe genuinely different problems using the
  same vocabulary could be flagged, and two that use different words for the
  same idea could be missed. It catches lightly reworded boilerplate, not
  semantic paraphrase.
- The regression direction is decided by a fixed list of metric name fragments.
  A metric whose name does not contain one of those fragments is assumed to be
  better when higher. A metric where lower is better but whose name is unusual
  will be misclassified.
- The card format is a small convention, not a standard. It does not read the
  richer schemas used by hosted model card tools, and it does not emit them.
- Multi-line claim and limitation bullets are read only up to the first physical
  line. A bullet whose text wraps onto a second line loses the continuation.

These limits are the cost of a tool that runs offline in a few milliseconds with
no dependencies. The checks it does run, it runs deterministically.

## The claim citation diagram

The diagram below is built from the real claims in `samples/incomplete.card`
and the single result that card provides. The left column is the three
capability claims. The right column is the results. A solid green connector is a
claim that resolves to a result that exists. The dashed connector is the
dangling citation to `eval-sota`, which no result defines. The amber box is the
uncited claim, the memory claim that cites nothing, marked because it is the
first thing a reviewer should look at.

![Claim to evaluation citations for the sample card: the accuracy claim cites
eval-intent-accuracy which exists, the memory claim is uncited and marked in
amber, and the benchmark claim cites eval-sota which is absent.](docs/assets/claim-citations.svg)

Every label and number in the diagram is copied from the sample card and matches
the output of `modelcarddiff claims samples/incomplete.card` shown above.

## Design decisions

**A bound is not an exact quote.** The first version of the metric check flagged
every number in a claim that did not equal a result. That refused the complete
card, because "accuracy above 0.90" does not equal the measured 0.93. The check
now looks at the word before the number. A comparison word (above, under, at
least, and the like) marks a bound, which is prose the tool does not verify. A
number stated directly is an exact quote that must match. The rejected
alternative, comparing every number, punished honest threshold language and made
the gate unusable for normal cards.

**Removed limitation does not set the exit code.** It would be tempting to fail
the build on a dropped limitation. The problem is that a limitation is
legitimately removed when the weakness is genuinely fixed, and that is a normal
part of model improvement. Failing on it would train people to stop writing
limitations so the diff stays quiet, which is the opposite of the goal. The tool
always shows the removal prominently and leaves the decision to a human, while
reserving the hard exit code for a metric regression, which is a number and not
a judgement.

**Regression direction is a name heuristic, not configuration.** A configurable
per metric direction would be more precise, but it would also be one more file
to keep in sync with the card, and a stale configuration is worse than a
transparent heuristic. The tool encodes the common cases (a rising error, loss,
latency, or confusion rate is worse) and documents the assumption so a
misclassification is visible rather than hidden in a config nobody reads.

**Line oriented output over structured output.** The reports are plain lines,
not JSON. The tool is meant to sit in a pull request and a terminal, where a
clean textual diff is more useful than a machine format. A structured output
mode is on the roadmap, but the default stays readable.

## Repository layout

```
modelcarddiff/
  README.md                     this file
  LICENSE                       MIT, holder "Xiaoxiao Cui", 2026
  CHANGELOG.md                  release notes
  pyproject.toml                packaging, console script entry point
  .gitignore                    ignore rules
  src/modelcarddiff/
    __init__.py                 package version
    __main__.py                 python -m modelcarddiff entry point
    cli.py                      argparse subcommands and exit codes
    card.py                     parse the card into sections, claims, results
    schema.py                   requirements schema and section resolution
    claims.py                   citation resolution and the claim level checks
    gate.py                     the pass or refuse decision
    diff.py                     version comparison and change classification
    report.py                   line oriented rendering of every command
  tests/
    test_card.py                card parser tests
    test_schema.py              schema and section resolution tests
    test_claims.py              citation, metric quote, distinctness tests
    test_gate.py                gate decision tests
    test_diff.py                diff classification tests
    test_cli.py                 end to end CLI and exit code tests
  samples/
    README.md                   how each fixture was constructed
    schema.txt                  five required sections
    complete.card               a card that passes the gate
    incomplete.card             a card the gate refuses
    complete-v2.card            a second version for the diff
  docs/assets/
    logo.svg                    wordmark
    claim-citations.svg         the real claim to citation diagram
```

## Glossary

- **Card**: the model card document being gated or diffed.
- **Section**: a `## Heading` and its body.
- **Claim**: a capability assertion in the Capabilities section.
- **Result**: an evaluation line in the Results section, an id, a metric, and a
  value.
- **Citation**: the `(cites: <eval-id>)` link from a claim to a result.
- **Uncited claim**: a claim with no citation.
- **Dangling citation**: a citation to an id no result defines.
- **Bound**: a number in a claim introduced by a comparison word, treated as a
  threshold rather than an exact value.
- **Regression**: a result value that moved in the worse direction between
  versions.
- **Editorial change**: any change that is not an added claim, a removed
  limitation, or a regression.

## Integration notes

In continuous integration, run the gate on the card and let the exit code fail
the job.

```
python -m modelcarddiff gate schema.txt model-card.md
```

To catch regressions between the merge base and the branch, run the diff on the
two versions of the card and let a regression fail the job.

```
python -m modelcarddiff diff base-card.md head-card.md
```

Because the output is line oriented, you can also diff two runs in git. Save the
gate output to a file, commit it next to the card, and a later change to the
card produces a small readable diff in that file.

## Verification

Run the test suite from the project root with the source tree on the path.

```
set PYTHONPATH=src
python -m unittest discover -s tests -v
```

The suite has 45 tests across six files. `test_card.py` covers the parser,
including titles, cited and uncited claims, numeric and text results, and empty
section detection. `test_schema.py` covers directive parsing, duplicate
collapsing, and section resolution. `test_claims.py` covers citation
resolution, the bound versus exact value metric check, and limitation
distinctness. `test_gate.py` covers each finding code and deterministic output.
`test_diff.py` covers the four change kinds and the regression direction rules.
`test_cli.py` runs every subcommand end to end and asserts the exit codes.

Every SVG under `docs/assets/` parses as XML, and a search across the project
for the em dash character returns nothing.

## Roadmap

These are directions, not dated promises.

- An optional structured output mode for the reports.
- A way to read the value behind a bound and warn when a cited result is far
  from the stated threshold.
- A configurable metric direction map, layered on top of the name heuristic so
  the default stays zero configuration.
- Support for multi-line claim and limitation bullets.

## License

MIT. See [LICENSE](LICENSE). The copyright holder is "the ModelCardDiff
authors", year 2026.

<!-- draft note 982 -->
