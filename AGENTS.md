# Project Instructions

These guidelines are adapted from the referenced Andrej Karpathy coding guidelines. They prioritize caution and clarity over speed; use judgment for trivial tasks.

## Think Before Coding

- State important assumptions explicitly.
- If multiple interpretations would materially change the result, explain them and ask before proceeding.
- Mention simpler alternatives and push back when a requested approach appears unnecessarily complex.
- Surface uncertainty instead of hiding it.

## Simplicity First

- Make the minimum change that solves the request.
- Do not add unrequested features.
- Avoid abstractions for one-time use.
- Do not add configurability or flexibility without a demonstrated need.
- Do not add defensive handling for scenarios that cannot occur in this project.
- If an implementation is becoming much larger than necessary, simplify it before finishing.

## Surgical Changes

- Touch only files and lines required by the request.
- Do not refactor, reformat, or "improve" adjacent code that is unrelated.
- Match the existing project style.
- If unrelated dead code is discovered, mention it rather than removing it.
- Remove imports, variables, or functions made unused by your own changes; leave pre-existing unused code alone.
- Every changed line should be directly traceable to the request.

## Goal-Driven Execution

- Define concrete, verifiable success criteria before implementing multi-step work.
- For bugs, reproduce the problem with a test or other reliable check before fixing it when practical.
- For new behavior, add or update focused tests when the project has a test suite.
- Verify the result with the narrowest relevant checks, then report what was run and whether it passed.
