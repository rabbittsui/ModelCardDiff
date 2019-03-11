"""The pass or refuse decision.

The gate runs four checks against a card and a schema:

1. Every required section exists and is non-empty.
2. Every capability claim cites an evaluation (no uncited claims), and every
   cited evaluation exists in the results (no dangling citations).
3. Every quoted metric value appears in the results (no claim quotes a metric
   absent from the results).
4. Every stated limitation is distinct (no boilerplate duplicates).

The gate returns a :class:`GateResult` carrying the ordered list of findings.
The decision is ``passed`` when there are no findings. Findings are produced in
