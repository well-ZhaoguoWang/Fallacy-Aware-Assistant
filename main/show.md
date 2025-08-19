## 🎯 Fallacy-aware Response Generation Flow  
After identifying the fallacies, the system generates gentle 
and inspiring intervention suggestions in the following steps:
```mermaid
flowchart TD
    %% ---------- Nodes ----------
    Start([Start<br/>Fallacy Identified])
    Collect[Collect&nbsp;Inputs<br/>(user_input, type,<br/>reasoning, evidence_list,<br/>suggestion_type)]
    Prompt[Build Structured Prompt]
    Generate[Controlled Generation<br/>(LLM&nbsp;T=0.6&nbsp;N=3)]
    Rank[Filter &amp; Rank<br/>(select best)]
    Evidence{Evidence<br/>available?}
    Attach[Attach Evidence<br/>Hyperlinks]
    Output[Return JSON<br/>{ "suggestion": "..." }]
    End((End))

    %% ---------- Links ----------
    Start --> Collect --> Prompt --> Generate --> Rank --> Evidence
    Evidence -- Yes --> Attach --> Output --> End
    Evidence -- No  --> Output --> End
