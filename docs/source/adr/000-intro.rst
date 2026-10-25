ADR Introduction
================

Architectural Design Records (ADRs) are short documents that capture a single architectural or design decision, its context, and its consequences. Less is more: keep them brief.

These are the ADRs of the Smarter Python SDK. They follow the Smarter platform's own `ADRs <https://github.com/smarter-sh/smarter/tree/main/docs/source/adr>`__: where the SDK applies a platform decision, its ADR says so and links to it, and adapts it to a library that runs in other people's software. The platform's decisions about its own runtime (Django, Docker, Kubernetes, the database, Celery, React, templates, feature flags, internationalization) don't apply to the SDK and are not repeated here.

See: `Michael Nygard's ADRs <https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions.html>`__

Guidelines for writing ADRs
---------------------------

- **One decision per ADR.**
- **Be concise.** Focus on clarity and brevity.
- **State the context:** the forces that led to the decision.
- **List the alternatives**, and why they weren't chosen.
- **Explain the decision**, and **describe its consequences**, positive and negative.
- **Use simple language**, for future contributors without today's context.
- **Use the same format** as the others: Status, Context, Decision, Alternatives Considered, Consequences, Related ADRs.
- **Reference related ADRs.**
- **Don't rewrite history.** When a decision changes, add an ADR that supersedes the old one, and set the old one's status to *Superseded by ADR-NNN*.
- **Keep the numbering aligned** with the other SDKs and the smarter cli: a decision that every SDK shares takes this SDK's number. A shared decision made later takes the next number free in every repository, which is why 020 and 021 (language-specific ADRs of the Node.js and Go SDKs) are unused here.
