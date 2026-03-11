---
name: cro
description: >-
  Conversion rate optimization toolkit for ecommerce pages. Lists all CRO
  commands and capabilities. Use when the user mentions CRO, conversion
  optimization, or ecommerce page improvements without specifying audit,
  build, scan, or compare.
disable-model-invocation: false
---

<objective>
Present the CRO toolkit commands and direct the user to the right one.
For automated callers: skip this router and invoke specific commands directly.
Never invoke another skill from this router. Only present options.
</objective>

<quick_start>
Available commands:

/cro:audit [url-or-path]           Full 4-phase CRO audit of an existing page
/cro:build [description]           Build a new ecommerce page from scratch
/cro:quick-scan [url-or-desc]      Quick scan — one cluster, 3-5 quick wins
/cro:compare [url] [competitor]    1:1 competitor comparison

Common flags: --auto, --min-priority, --platform, --export-report
</quick_start>

<instructions>
If $ARGUMENTS contains a URL or file path, suggest: "It looks like you want to audit a page. Run `/cro:audit $ARGUMENTS` to start."

If $ARGUMENTS contains a description of something to build, suggest: "It sounds like you want to build something new. Run `/cro:build $ARGUMENTS` to start."

Otherwise, present the command table above and ask: "What would you like to do?"
</instructions>
