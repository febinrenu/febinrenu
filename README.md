<a href="https://febin-renu.vercel.app"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/calibre/header-dark.svg"/><img src="assets/calibre/header-light.svg" width="100%" alt="Febin K Renu, Calibre FKR-26. An open-caseback watch movement turns beside the name: a gear train at true ratios, a balance wheel swinging, an escape wheel ticking. Calibrated models, honest negatives, and show their work. Software Developer at Entarch Solutions; Software Engineering Intern and Dev Lead at Grids Apps LLC; B.Tech CSE at Karunya Institute, CGPA 9.39; published SMAHI-ER at IEEE IEHNS 2026; based in Hyderabad, India."/></picture></a>

<br/>

<picture><source media="(prefers-color-scheme: dark)" srcset="assets/calibre/dividers/i-dark.svg"/><img src="assets/calibre/dividers/i-light.svg" width="100%" alt="I. Calibration: what I build, and how I decide."/></picture>

**I build systems that decide under uncertainty, and leave a trail you can audit.**

Not "call an LLM and hope": a calibrated model, a cost function, and a defined point where a human takes over. A payment-recovery engine that's allowed to conclude the right move is doing nothing. A medical second opinion that withholds the findings it can't prove. A camera search that says "no" when the footage says no. Underneath the product work, plain full-stack engineering with tests and CI, because none of the above ships without it.

<sub>NOW</sub>&nbsp; Software Developer at Entarch Solutions (remote, since Jan 2026) · Software Engineering Intern / Dev Lead at Grids Apps LLC (remote, since Jul 2026)<br/>
<sub>STUDY</sub>&nbsp; Final-year CS at Karunya Institute of Technology and Sciences, 2023–2027, CGPA 9.39<br/>
<sub>EXPLORING</sub>&nbsp; conditional knowledge conflicts in retrieval (a paper in preparation), and checks a model has to pass before anyone trusts it<br/>
<sub>OPEN TO</sub>&nbsp; full-time engineering, AI/ML and platform roles from May 2027 · [portfolio](https://febin-renu.vercel.app) · [febinrenu7@gmail.com](mailto:febinrenu7@gmail.com)

<br/>

<picture><source media="(prefers-color-scheme: dark)" srcset="assets/calibre/dividers/ii-dark.svg"/><img src="assets/calibre/dividers/ii-light.svg" width="100%" alt="II. Provenance: what is real, and how you can check."/></picture>

| Area | What's actually there | Proof |
|---|---|---|
| Decision systems | calibrated logistic regression + expected-value optimization | [Reclaim](https://github.com/febinrenu/reclaim): public, 574 tests, CI. Also the Wager below |
| Medical imaging, verified | deletion tests, temperature scaling + conformal sets, second reader, leakage audit, hash-chained audit trail | [PARALLAX](https://github.com/febinrenu/PARALLAX): public, live, hackathon team build |
| Multi-camera video | detection, tracking, cross-camera re-ID, natural-language retrieval with evidence | [EVORA](https://github.com/febinrenu/EVORA): public, live, hackathon team build, measured on MEVA and WILDTRACK |
| Legal NLP + policy simulation | statute parsing, span-grounded rule extraction, tax microsimulation | [PRISM](https://github.com/febinrenu/PRISM): public |
| RAG research | conditional knowledge conflicts: detect, scope, compose | [ScopeCompose](https://github.com/febinrenu/ScopeCompose): public, research in progress, no results to quote yet. Plus Hugging Face Agents and LangChain/LlamaIndex RAG coursework |
| Applied ML | scikit-learn, XGBoost, LSTM forecasting | [AssetStream](https://github.com/febinrenu/AssetStream), [ml-loan](https://github.com/febinrenu/ml-loan), [Bitcoin-LSTM](https://github.com/febinrenu/Bitcoin-Price-Prediction-using-LSTM): public |
| Full-stack product | Next.js/Django/Node, Postgres/Redis/MongoDB, Docker | 7 live deployments (two are static demos of local systems), listed below |
| Agentic AI / LLM orchestration | AWS Bedrock multi-agent system, confidence-based routing | current role. Real, but the code is a client's, not public |
| Cloud infra (Terraform, K8s, Helm) | full IaC pipeline with CI/CD, monitoring | PromptForge: live demo, repo not public |
| Computer vision | customer-behavior modeling project | Intel Unnati industrial training, Feb–Apr 2025. No public repo |
| Research curiosity | measuring whether prompt instability costs inference energy | [Computational Entropy Lab](https://github.com/febinrenu/comp_entropy): public |

I'd rather show you this table than let "AI Engineer" do the talking. Some of the above I can point you straight at the code for. Some of it I can't, and I'd rather say so than blur the line.

<br/>

<picture><source media="(prefers-color-scheme: dark)" srcset="assets/calibre/dividers/iii-dark.svg"/><img src="assets/calibre/dividers/iii-light.svg" width="100%" alt="III. Complications: each work, drawn as the mechanism it is."/></picture>

Each project below is drawn as the watch complication that does the same job. Every number on a plate comes from that project's own README. Where a plate is an illustration, it says so on the plate.

<a href="https://github.com/febinrenu/EVORA"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/calibre/plates/01-evora-dark.svg"/><img src="assets/calibre/plates/01-evora-light.svg" width="100%" alt="Complication 1, Evora: four camera sub-dials with sweeping scan hands. On camera 1, main gate, the hand finds a red car and a lume ring blooms; a dotted trace follows one person from camera 2 to camera 4; the answer reads found, camera 1, 14:32:07. Hit@5 0.72 dev and 0.69 test on one MEVA site; negative precision 1.00 on dev against 0.00 for a frame-similarity baseline; runs on one 8 GB laptop with faces blurred."/></picture></a>

**[Evora](https://github.com/febinrenu/EVORA)**: ask a set of cameras a question in plain language ([live](https://evora-ivory.vercel.app)). It answers with a camera, a time, a clip with the object circled, and the reasons. When the footage doesn't support an answer, it says so and shows the nearest miss. A frame-similarity baseline matches it on plain object presence, the sets are small, and the repo says all of this. Hackathon team build.

<a href="https://github.com/febinrenu/PARALLAX"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/calibre/plates/02-parallax-dark.svg"/><img src="assets/calibre/plates/02-parallax-light.svg" width="100%" alt="Complication 2, Parallax: a certification dial with eight ruby jewels, one per check. Hand A passes all eight and reaches Doctor, consider; hand B stops at the deletion test and is withheld: the heatmap was decoration. About 42% of brain and 44% of skin findings pass the deletion test; a leakage audit found 71% of an external set were near-duplicates. Decision support only."/></picture></a>

**[Parallax](https://github.com/febinrenu/PARALLAX)**: a medical second opinion that has to prove every finding before a doctor sees it ([live](https://parallax-two-xi.vercel.app)). A finding has to point at something. Blurring what it points at has to lower its confidence. It has to survive perturbation, calibration and a second reader, and every step joins a SHA-256 hash chain. The number I'd lead with is the uncomfortable one: most brain and skin findings fail the deletion test, so they're withheld rather than shown. Decision support only, not a medical device. Hackathon team build.

<a href="https://github.com/febinrenu/reclaim"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/calibre/plates/03-reclaim-dark.svg"/><img src="assets/calibre/plates/03-reclaim-light.svg" width="100%" alt="Complication 3, Reclaim: a Swiss lever escapement, the escape wheel ticking as the balance swings, with a selector moving between recover, escalate and leave it. Calibrated logistic regression and an expected-value decision where doing nothing is allowed: 1.42 times the net recovery of retrying every payment, 0.69 ROC-AUC, 574 automated tests with CI."/></picture></a>

**[Reclaim](https://github.com/febinrenu/reclaim)**: risk-aware revenue recovery ([live](https://reclaim-lac-six.vercel.app)). Most retry logic assumes recovering a failed payment is always worth attempting. Reclaim prices each action instead, and it's free to decide the right answer is to leave it alone. TypeScript, Next.js, PostgreSQL, Razorpay, idempotent webhooks, and a human-escalation budget for the cases too risky to automate.

<a href="https://github.com/febinrenu/ScopeCompose"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/calibre/plates/04-scopecompose-dark.svg"/><img src="assets/calibre/plates/04-scopecompose-light.svg" width="100%" alt="Complication 4, ScopeCompose: a planetary differential. The carrier, the query, drives three planets; the sun carries the general rule, a 3% fee on international transactions, and the ring carries the exception, waived for premium-tier cardholders. A selector keeps one branch; a differential keeps both. Pipeline built with 501 tests, no results yet."/></picture></a>

**[ScopeCompose](https://github.com/febinrenu/ScopeCompose)**: final-year research, two members. Conflict-aware RAG resolves disagreements by picking the more credible source. For a rule and its exception that silently deletes the exception, and answer-correctness metrics can't see the deletion. ScopeCompose composes a scoped answer that keeps every valid branch, and adds a metric for the deletion: Suppression Rate. Status, honestly: the pipeline is built, and annotation and live runs are in progress.

<a href="https://github.com/febinrenu/PRISM"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/calibre/plates/05-prism-dark.svg"/><img src="assets/calibre/plates/05-prism-light.svg" width="100%" alt="Complication 5, Prism, illustrative and not a reported result: a rack reads a paraphrased section 87A rebate clause and drives ten income-decile gauges with expert and LLM needles. They agree except in deciles 5 to 7, and a trace runs back to the words ₹25,000 in the clause."/></picture></a>

**[Prism](https://github.com/febinrenu/PRISM)**: when a language model extracts the rules of an Indian tax statute, does simulating those rules reach the same policy conclusions as an expert's coding of the same law? And when it doesn't, which clause is responsible? Statutes become a legal AST, rules are grounded to exact spans, and they run on a taxpayer population that reproduces the official Income Tax Return Statistics. The plate shows the kind of divergence Prism exists to trace, not a reported result.

<a href="https://github.com/febinrenu/AssetStream"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/calibre/plates/06-assetstream-dark.svg"/><img src="assets/calibre/plates/06-assetstream-light.svg" width="100%" alt="Complication 6, AssetStream, curves illustrative: a power-reserve gauge of retained value from new to retire. An age-only hand falls to 22 while the telemetry-informed hand stops at 38, and a billing-cycle sub-dial ticks below."/></picture></a>

**[AssetStream](https://github.com/febinrenu/AssetStream)**: Equipment-as-a-Service for leased industrial equipment ([live](https://assetstream-frontend.onrender.com)). A Django + Celery + Redis engine turns IoT telemetry into invoices on a billing cycle. A scikit-learn model prices resale value, so the remarketing call isn't a guess. Next.js/TypeScript front end, Groq LLM integration, fully Dockerized.

<a href="https://github.com/febinrenu/comp_entropy"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/calibre/plates/07-entropy-dark.svg"/><img src="assets/calibre/plates/07-entropy-light.svg" width="100%" alt="Complication 7, Computational Entropy Lab, traces illustrative: a smooth low-instability prompt signal and a jagged high-instability one scroll beside energy gauges with a question mark between them. An open hypothesis, not a result."/></picture></a>

**[Computational Entropy Lab](https://github.com/febinrenu/comp_entropy)**: a FastAPI/React platform testing one question: does semantic instability in a prompt carry a measurable inference-energy cost? Demo data is flagged `measurement_source: synthetic_simulation` in the API, so it's never mistaken for a result. Built because the question was interesting, not because anyone asked for it.

<br/>

<picture><source media="(prefers-color-scheme: dark)" srcset="assets/calibre/dividers/iv-dark.svg"/><img src="assets/calibre/dividers/iv-light.svg" width="100%" alt="IV. In the vault: real, not yet public."/></picture>

**[PromptForge](https://prompt-forge-frontend.vercel.app)**: prompt discovery and testing across multiple LLMs. It runs on a 10-service NestJS architecture on a Terraform-provisioned K3s cluster with Helm, HPA autoscaling and a full CI/CD pipeline (lint → test → Docker → Trivy scan → zero-downtime deploy). The repo is private; the live app is the proof.

**AskVid-Pro**: answers free-form questions about short videos with timestamped citations. Built on a 4-bit QLoRA-fine-tuned Video-LLaMA2 with OpenCLIP/FAISS retrieval, evaluated on MSRVTT-QA and NEXT-QA, and deployed on Hugging Face Spaces. The repo is private.

**QuantroCode**: multi-tenant POS/ERP SaaS in PHP/Vue, with custom domains, pharmacy batch tracking, POS hardware integration and a client billing portal. The repo is private.

<sub>ALSO</sub>&nbsp; [BlogHaven](https://github.com/febinrenu/bloghaven), a MERN platform with role-based auth and moderation ([live](https://bloghaven-draft.netlify.app)) · [Bitcoin-LSTM](https://github.com/febinrenu/Bitcoin-Price-Prediction-using-LSTM), early ML work evaluated on MSE/RMSE, not a trading signal

<br/>

<a name="out-decide-my-model"></a>
<picture><source media="(prefers-color-scheme: dark)" srcset="assets/calibre/dividers/v-dark.svg"/><img src="assets/calibre/dividers/v-light.svg" width="100%" alt="V. The Wager: out-decide my model, live."/></picture>

A game you can play right here. Reclaim's whole argument is that a calibrated model with a cost function makes better recovery calls than "always retry." So here's a failed payment: make the call. A toy version of Reclaim's model makes its own call on the same case, and both are scored by expected value at the true odds. Nobody wins on a lucky coin flip.

The model sees every field on the card. **It can't read the note.** That's your edge, if you use it. Press a plaque and an issue opens with your move filled in. Hit **Create**, and within about a minute a bot scores you against the model, updates this board and deals the next case.

<!-- GAME:START -->
<picture><source media="(prefers-color-scheme: dark)" srcset="assets/calibre/wager/case-dark.svg?v=2"/><img src="assets/calibre/wager/case-light.svg?v=2" width="100%" alt="Case 2: ₹8,850 failed payment, do not honor, 0 prior retries, customer for 31 months, 0 past payments ok, via UPI. Note: updated their card in the profile yesterday. Humans ±₹0, model ±₹0."/></picture>

<p align="center"><a href="https://github.com/febinrenu/febinrenu/issues/new?title=reclaim%7Crecover%7C2&body=Just%20press%20%2A%2ACreate%2A%2A%20%28or%20%2A%2ASubmit%20new%20issue%2A%2A%29.%20A%20bot%20scores%20your%20call%20against%20the%20model%20in%20about%20a%20minute%2C%20comments%20with%20the%20result%20and%20closes%20this."><picture><source media="(prefers-color-scheme: dark)" srcset="assets/calibre/wager/plaque-recover-dark.svg"/><img src="assets/calibre/wager/plaque-recover-light.svg" width="32%" alt="RECOVER"/></picture></a><a href="https://github.com/febinrenu/febinrenu/issues/new?title=reclaim%7Cescalate%7C2&body=Just%20press%20%2A%2ACreate%2A%2A%20%28or%20%2A%2ASubmit%20new%20issue%2A%2A%29.%20A%20bot%20scores%20your%20call%20against%20the%20model%20in%20about%20a%20minute%2C%20comments%20with%20the%20result%20and%20closes%20this."><picture><source media="(prefers-color-scheme: dark)" srcset="assets/calibre/wager/plaque-escalate-dark.svg"/><img src="assets/calibre/wager/plaque-escalate-light.svg" width="32%" alt="ESCALATE"/></picture></a><a href="https://github.com/febinrenu/febinrenu/issues/new?title=reclaim%7Cleave%7C2&body=Just%20press%20%2A%2ACreate%2A%2A%20%28or%20%2A%2ASubmit%20new%20issue%2A%2A%29.%20A%20bot%20scores%20your%20call%20against%20the%20model%20in%20about%20a%20minute%2C%20comments%20with%20the%20result%20and%20closes%20this."><picture><source media="(prefers-color-scheme: dark)" srcset="assets/calibre/wager/plaque-leave-dark.svg"/><img src="assets/calibre/wager/plaque-leave-light.svg" width="32%" alt="LEAVE IT"/></picture></a></p>

<p align="center"><sub>No moves yet. The first visitor sets the scoreboard.</sub></p>
<!-- GAME:END -->

<details>
<summary><b>How it's scored</b></summary>
<br/>

With amount **A** and true recovery probability **p**:

- **RECOVER** = p·A·(1 − c) − 0.03·A − ₹20 − (1 − p)·0.40·A. A failed retry burns goodwill. c = 0.5 when the reason is suspected fraud, because half of that money gets charged back later.
- **ESCALATE** = p′·A − 0.03·A − ₹1,200 − (1 − p′)·0.10·A, where p′ = p + 0.20·(1 − p). A human closes a fifth of the gap, catches the fraud, and costs real time.
- **LEAVE IT** = 0, on purpose.

The model's p comes from a logistic regression over the fields on the card. The true p adds the note's effect and a little noise. The model takes the best action at *its* p, then both calls are scored at the true p, and the scoreboard is the running sum.

These are synthetic cases and a toy replica of Reclaim's decision logic, not its production model. The engine is public in [`game/engine.py`](game/engine.py). Reading it to win is learning the model, which is the point.
</details>

<br/>

<picture><source media="(prefers-color-scheme: dark)" srcset="assets/calibre/dividers/vi-dark.svg"/><img src="assets/calibre/dividers/vi-light.svg" width="100%" alt="VI. Specification: instruments in daily use."/></picture>

<picture><source media="(prefers-color-scheme: dark)" srcset="assets/calibre/specification-dark.svg"/><img src="assets/calibre/specification-light.svg" width="100%" alt="Movement specification, the tech stack in eight registers. Languages: TypeScript, Python, JavaScript, Java, PHP, SQL, C, HTML and CSS. Interfaces: React, Next.js, Vue.js, Angular, Tailwind CSS. Services: Node.js, Express, NestJS, Django, FastAPI, Flask, Laravel. Data: PostgreSQL, MySQL, MongoDB, Redis, SQLite. Intelligence: PyTorch, TensorFlow, Keras, scikit-learn, OpenCV, Pandas, NumPy, LangChain, Hugging Face, AWS Bedrock. Cloud: AWS (Lambda, SQS, CDK), Google Cloud, Oracle Cloud. Delivery: Docker, Kubernetes, Helm, Terraform, Ansible, GitHub Actions. Observatory: Prometheus, Grafana, Nginx, Git, Jupyter, Streamlit."/></picture>

<br/>

<picture><source media="(prefers-color-scheme: dark)" srcset="assets/calibre/dividers/vii-dark.svg"/><img src="assets/calibre/dividers/vii-light.svg" width="100%" alt="VII. Ledger: a year of public work, refreshed weekly."/></picture>

<picture><source media="(prefers-color-scheme: dark)" srcset="assets/calibre/ledger-dark.svg"/><img src="assets/calibre/ledger-light.svg" width="100%" alt="Ledger: the last twelve months of public GitHub contributions drawn as a perpetual calendar, one spoke per week and one ring per weekday, with figures for active days, longest run, busiest day and public repositories, and a language reserve by bytes across public repositories. A snapshot redrawn weekly by a GitHub Action, not live."/></picture>

<sub>A snapshot from the GitHub API, redrawn every week by [an Action](.github/workflows/ledger.yml). Not live, and it counts public work only.</sub>

<br/>

<picture><source media="(prefers-color-scheme: dark)" srcset="assets/calibre/colophon-dark.svg"/><img src="assets/calibre/colophon-light.svg" width="100%" alt="Colophon: a caseback window with the winding rotor swinging. Every mark above is typeset code, drawn as SVG by Python that ships in this repository and set in Bodoni Moda and Martian Mono, outlined into paths."/></picture>

**SMAHI-ER**, IEEE IEHNS, June 2026: a multi-agent hypergraph framework for resilient human-machine manufacturing. [10.1109/IEHNS68708.2026.11607072](https://doi.org/10.1109/IEHNS68708.2026.11607072)<br/>
First Rank, 9.54 SGPA (May 2024) · Second Rank, 9.42 SGPA (Dec 2023), Karunya Institute

[Portfolio](https://febin-renu.vercel.app) · [GitHub](https://github.com/febinrenu) · [LinkedIn](https://www.linkedin.com/in/febin-renu/) · [febinrenu7@gmail.com](mailto:febinrenu7@gmail.com)
