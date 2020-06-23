# Sample fixtures

These files are hand authored test vectors, not production model cards. They
exist to exercise every branch of the gate and diff logic. The numbers in the
Results sections are invented for the test and are not measurements of any real
model.

## Files

- `schema.txt` requirements schema listing five required sections.
- `complete.card` a card that passes the gate: every required section is
  present and non-empty, every capability claim cites a result that exists, the
  four limitations are distinct, and no claim quotes a metric absent from the
  results.
- `incomplete.card` a card that the gate refuses. It omits the required
  Limitations section, includes one capability claim that cites nothing
  (the 64 megabytes memory claim), and includes one claim that cites
  `eval-sota`, an evaluation that never appears in the Results section.
- `complete-v2.card` a second version of the complete card used for the diff.
  Relative to `complete.card` it adds one capability claim (the escalation
