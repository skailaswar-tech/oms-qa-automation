# AI Testing Thought Process

## 1. How would I test a system with non-deterministic AI outputs?

I would test the output against defined quality criteria rather than expecting an exact string every time. I would use a representative set of prompts, check required facts and format, evaluate relevance and safety, and run regression cases against a saved evaluation set. Where possible, I would use measurable thresholds and human review for ambiguous cases. I would also test edge cases, prompt variations, and repeated runs to understand output variability.

## 2. What challenges differ from traditional testing?

Traditional software often has deterministic expected results, while AI output can vary for the same input. This makes exact-match assertions less useful and requires quality rubrics, tolerance ranges, and evaluation datasets. Results can also change when models, prompts, or underlying data change, so version tracking and regression evaluation are important. AI testing additionally needs attention to hallucinations, bias, safety, and the difficulty of defining a single correct answer.
