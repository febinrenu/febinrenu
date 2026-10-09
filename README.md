<img src="assets/hero-level.svg" width="100%" alt="An auto-playing pixel-art level: a runner on a contribution-graph floor jumps over bugs named hallucination, prompt injection, uncalibrated P, dropped exception, uncited clause and straight-line guess, and bumps question blocks that pop coins named EVORA, PARALLAX, RECLAIM, SCOPECOMPOSE, PRISM and ASSETSTREAM."/>

### Febin Renu
Hyderabad, India

Software Developer at Entarch Solutions (remote, since Jan 2026) · Software Engineering Intern / Dev Lead at Grids Apps LLC (remote, since Jul 2026)
<br/>
Final-year CS undergrad at Karunya Institute of Technology and Sciences (2023–2027, CGPA 9.39)

<br/>

## What I build

Systems where something has to be decided under uncertainty, and the decision has to be cheap to audit — not "call an LLM and hope," a calibrated model with a cost function and a defined point where a human takes over. A payment-recovery engine that's allowed to conclude the right move is doing nothing. A medical second opinion that withholds the findings it can't prove. A camera search that says "no" when the footage says no. Underneath the product work, plain full-stack engineering with tests and CI, because none of the above ships without it.

<br/>

## Out-decide my model

This is a game you can play right here. Reclaim's whole argument is that a calibrated model with a cost function makes better recovery calls than "always retry." So here's a failed payment. Make the call. A toy version of Reclaim's model makes its own call on the same case, and both calls are scored by expected value at the true odds. Nobody wins on a lucky coin flip.

The model sees every field on the card. **It can't read the note.** That's your edge, if you use it.

Press a button and an issue opens with your move already filled in. Hit **Create**, and within about a minute a bot scores you against the model, updates this board and deals the next case. You need a GitHub account; that's all.

<!-- GAME:START -->
<img src="assets/game/case.svg?v=1" width="100%" alt="Case 1: ₹3,000 failed payment, do not honor, 1 prior retry, customer for 11 months, 2 past payments ok, via UPI. Note: opened the payment-link email three times. Humans ±₹0, model ±₹0."/>

<p align="center"><a href="https://github.com/febinrenu/febinrenu/issues/new?title=reclaim%7Crecover%7C1&body=Just%20press%20%2A%2ACreate%2A%2A%20%28or%20%2A%2ASubmit%20new%20issue%2A%2A%29.%20A%20bot%20scores%20your%20call%20against%20the%20model%20in%20about%20a%20minute%2C%20comments%20with%20the%20result%20and%20closes%20this."><img src="assets/game/btn-recover.svg" width="32%" alt="RECOVER"/></a><a href="https://github.com/febinrenu/febinrenu/issues/new?title=reclaim%7Cescalate%7C1&body=Just%20press%20%2A%2ACreate%2A%2A%20%28or%20%2A%2ASubmit%20new%20issue%2A%2A%29.%20A%20bot%20scores%20your%20call%20against%20the%20model%20in%20about%20a%20minute%2C%20comments%20with%20the%20result%20and%20closes%20this."><img src="assets/game/btn-escalate.svg" width="32%" alt="ESCALATE"/></a><a href="https://github.com/febinrenu/febinrenu/issues/new?title=reclaim%7Cleave%7C1&body=Just%20press%20%2A%2ACreate%2A%2A%20%28or%20%2A%2ASubmit%20new%20issue%2A%2A%29.%20A%20bot%20scores%20your%20call%20against%20the%20model%20in%20about%20a%20minute%2C%20comments%20with%20the%20result%20and%20closes%20this."><img src="assets/game/btn-leave.svg" width="32%" alt="LEAVE IT"/></a></p>

_No moves yet. The first click sets the scoreboard._
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

## What's real, and how you can check

| Area | What's actually there | Proof |
|---|---|---|
| Applied ML | scikit-learn, XGBoost, LSTM forecasting | [AssetStream](https://github.com/febinrenu/AssetStream), [ml-loan](https://github.com/febinrenu/ml-loan), [Bitcoin-LSTM](https://github.com/febinrenu/Bitcoin-Price-Prediction-using-LSTM): public, live |
| Decision systems | calibrated logistic regression + expected-value optimization | [Reclaim](https://github.com/febinrenu/reclaim): public, 574 tests, CI. Also the game above |
| Medical imaging, verified | deletion tests, temperature scaling + conformal sets, second reader, leakage audit, hash-chained audit trail | [PARALLAX](https://github.com/febinrenu/PARALLAX): public, live, hackathon team build |
| Multi-camera video | detection, tracking, cross-camera re-ID, natural-language retrieval with evidence | [EVORA](https://github.com/febinrenu/EVORA): public, live, hackathon team build, measured on MEVA and WILDTRACK |
| Legal NLP + policy simulation | statute parsing, span-grounded rule extraction, tax microsimulation | [PRISM](https://github.com/febinrenu/PRISM): public |
| RAG research | conditional knowledge conflicts: detect, scope, compose | [ScopeCompose](https://github.com/febinrenu/ScopeCompose): public, research in progress, no results to quote yet. Plus Hugging Face Agents and LangChain/LlamaIndex RAG coursework |
| Full-stack product | Next.js/Django/Node, Postgres/Redis/MongoDB, Docker | 7 live deployments (two are static demos of local systems), listed below |
| Agentic AI / LLM orchestration | AWS Bedrock multi-agent system, confidence-based routing | current role. Real, but the code is a client's, not public |
| Cloud infra (Terraform, K8s, Helm) | full IaC pipeline with CI/CD, monitoring | resume project (PromptForge): live demo, repo not public |
| Computer vision | customer-behavior modeling project | Intel Unnati industrial training, Feb–Apr 2025. No public repo |
| Research curiosity | measuring whether prompt instability costs inference energy | [Computational Entropy Lab](https://github.com/febinrenu/comp_entropy): public |

I'd rather show you this table than let "AI Engineer" do the talking. Some of the above I can point you straight at the code for. Some of it I can't, and I'd rather say so than blur the line.

<br/>

## EVORA

<img src="assets/evora-cams.svg" alt="Animated illustration of EVORA: four camera feeds with ticking clocks. A question types itself out, a scan sweeps the feeds, and a circle lands on a red car at the main gate in camera 1. The answer shows camera, time, clip and reasons, a dotted track follows one person from camera 2 to camera 4, and a badge reads local only, faces blurred." width="100%"/>

Ask a set of cameras a question in plain language. [Live](https://evora-ivory.vercel.app), [source](https://github.com/febinrenu/EVORA). Footage is indexed once. Then *"did a red car pass the main gate in the last hour?"* comes back with a camera, a time, a playable clip with the object circled, and the reasons. When it meets a place it has never heard of ("main gate"), it asks once, you draw the line, and it never asks again. When the footage doesn't support an answer, it says so and shows the nearest miss. It runs on one laptop with an 8 GB GPU. With the privacy switch on, nothing leaves the machine and faces are blurred. Measured on one MEVA site: Hit@5 of 0.72 on dev and 0.69 on test, and negative precision of 1.00 on dev, where a frame-similarity baseline scores 0.00. That same baseline matches it on plain object presence, the sets are small, and the repo says all of this. Hackathon team build.

<br/>

## PARALLAX

<img src="assets/parallax-chain.svg" alt="Animated illustration of PARALLAX: a chest film with two highlighted regions. Eight checks light up in turn. Finding A passes all eight and reaches the report as Doctor, consider. Finding B fails the deletion test, because blurring its region barely moves its confidence, and is stamped withheld: the heatmap was decoration. A SHA-256 receipt chain fills along the bottom." width="100%"/>

A medical second opinion that has to prove every finding before a doctor sees it. [Live](https://parallax-two-xi.vercel.app), [source](https://github.com/febinrenu/PARALLAX). It reads a chest X-ray, brain MRI, skin dermoscopy or bone X-ray along with the clinical notes, and every finding has to survive eight independent checks:

1. It has to point at something.
2. Blurring what it points at has to lower its confidence.
3. It has to hold up under eight perturbations.
4. It gets temperature scaling and conformal sets.
5. An independent second reader (MedGemma) looks too.
6. The notes are checked with exact character spans, and any instructions injected into them are quarantined.
7. The report sentences are templates that code fills from evidence ids.
8. Every step joins a SHA-256 hash chain.

The uncomfortable number is the one I'd lead with: only about 42% of brain and 44% of skin findings pass the deletion test, so the rest are withheld rather than shown. A leakage audit found that 71% of an "external" brain set were near-duplicates of the training data. Only the 1,644 clean images count. Decision support only, not a medical device. Hackathon team build.

<br/>

## PRISM

<img src="assets/prism-trace.svg" alt="Animated illustration of PRISM, not a result: a paraphrased section 87A rebate clause is extracted twice, by an expert coding and by a language model that read the older regime's figures. Simulated effective tax rates by income decile match everywhere except deciles 5 to 7, and a trace line runs from the diverging bars back to the exact words in the clause." width="100%"/>

When a language model extracts the rules of an Indian tax statute, does simulating those rules reach the same policy conclusions as an expert's coding of the same law? And when it doesn't, which clause is responsible? [Source](https://github.com/febinrenu/PRISM). Statute PDFs become a legal AST: sections, provisos, explanations and schedules, with exact offsets. Rules are extracted and grounded to exact spans, and a quote that isn't in the statute is rejected. Those rules become executable tax parameters and run on a weighted taxpayer population that reproduces the official Income Tax Return Statistics. The output is revenue, decile effective rates, Gini, Kakwani and Reynolds–Smolensky, across five Finance Act reforms. The visual is illustrative: it shows the kind of divergence PRISM exists to trace, not a reported result.

<br/>

## ScopeCompose

<img src="assets/scopecompose.svg" alt="Animated illustration of ScopeCompose: passage A says international transactions carry a 3% fee, passage B says fees are waived for premium-tier cardholders. Source selection answers 3% and deletes the exception branch, suppression 1 of 1. ScopeCompose labels the conflict conditional, finds a refinement, and composes both: premium-tier waived, otherwise 3%, suppression 0 of 1." width="100%"/>

Final-year research, two members. [Source](https://github.com/febinrenu/ScopeCompose). Conflict-aware RAG systems notice that two passages disagree and resolve it by picking the more credible source. Take "international transactions carry a 3% fee" and "fees are waived for premium cardholders." Both are true, under different scopes, so picking one silently deletes the exception, and answer-correctness metrics can't see the deletion. ScopeCompose detects conditional conflicts as their own type, recovers the conditions that govern them, and composes a scoped answer that keeps every valid branch. It also adds a metric that makes the deletion measurable: Suppression Rate. Status, honestly: the pipeline is built and has 501 tests. Annotation and live runs are in progress, so there are no results to quote yet.

<br/>

## Reclaim

<img src="assets/reclaim-engine.svg" alt="Animated diagram of Reclaim's real pipeline: failed-payment, abandoned-checkout, and overdue-invoice events flow into a risk engine (calibrated logistic regression plus expected-value optimization, 0.69 ROC-AUC), which routes most events to recover or do-nothing and a minority to human escalation, producing 1.42 times the net recovery of retrying every payment across 574 automated tests." width="100%"/>

A risk-aware revenue recovery engine — [live](https://reclaim-lac-six.vercel.app), [source](https://github.com/febinrenu/reclaim). Most retry logic assumes recovering a failed payment is always worth attempting. Reclaim prices each action instead: a calibrated model estimates recovery probability, an expected-value calculation weighs it against the cost of trying, and the system is free to decide the correct answer is to leave it alone. TypeScript, Next.js, PostgreSQL, Razorpay, idempotent webhooks, a human-escalation budget for the cases too risky to automate.

<br/>

## AssetStream

<img src="assets/assetstream-curve.svg" alt="Line chart illustrating AssetStream's remarketing model: a naive straight-line, age-only depreciation estimate compared against a usage-telemetry-informed curve that ends at a higher retained value, drawn continuously." width="100%"/>

An AI-powered Equipment-as-a-Service platform — [live](https://assetstream-frontend.onrender.com), [source](https://github.com/febinrenu/AssetStream). Simulates lease originations, IoT-driven usage billing, and end-of-lease remarketing for leased industrial equipment. A Django + Celery + Redis engine turns live telemetry into invoices on a billing cycle; a scikit-learn regression model prices resale value so the remarketing call isn't a guess. Next.js/TypeScript frontend, Groq LLM integration, fully Dockerized.

<br/>

## Computational Entropy Lab

<img src="assets/entropy-wave.svg" alt="Two continuously scrolling waveforms illustrating the hypothesis under test: a smooth, low-instability prompt signal above a jagged, high-instability one, next to illustrative energy-cost indicators. Represents the open research question, not a proven result." width="100%"/>

A FastAPI/React research platform testing a specific hypothesis: does semantic instability in a prompt carry a measurable inference-energy cost? [Source](https://github.com/febinrenu/comp_entropy). It's explicit about the line between real and synthetic — demo data is flagged `measurement_source: synthetic_simulation` in the API so it's never mistaken for a result. Built because the question was interesting, not because anyone asked for it.

<br/>

## Real, not yet public

**[PromptForge](https://prompt-forge-frontend.vercel.app)** — a prompt discovery/testing platform across multiple LLMs, backed by a 10-service NestJS microservices architecture on a Terraform-provisioned K3s cluster with Helm, HPA autoscaling, and a full CI/CD pipeline (lint → test → Docker → Trivy scan → zero-downtime deploy). Repo is private; the live app is the proof.

**AskVid-Pro** — answers free-form questions about short videos with timestamped citations, built on a 4-bit QLoRA-fine-tuned Video-LLaMA2 with OpenCLIP/FAISS retrieval, evaluated on MSRVTT-QA and NEXT-QA. Deployed via Streamlit on Hugging Face Spaces; repo is private.

<br/>

## Other builds

- **[QuantroCode](https://github.com/febinrenu/QuantroCode)** — multi-tenant POS/ERP SaaS in PHP/Vue: custom domains, pharmacy batch tracking, POS hardware integration, client billing portal.
- **BlogHaven** — MERN blogging platform, role-based auth, moderation workflows, admin analytics. [Live](https://bloghaven-draft.netlify.app).
- **[Bitcoin-LSTM](https://github.com/febinrenu/Bitcoin-Price-Prediction-using-LSTM)** — early ML work: an LSTM forecaster evaluated on MSE/RMSE, not a trading signal.

<br/>

## Toolbox

**Languages**
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black)
![PHP](https://img.shields.io/badge/PHP-777BB4?style=flat-square&logo=php&logoColor=white)
![Java](https://img.shields.io/badge/Java-ED8B00?style=flat-square&logo=openjdk&logoColor=white)
![C](https://img.shields.io/badge/C-A8B9CC?style=flat-square&logo=c&logoColor=black)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat-square&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=flat-square&logo=css3&logoColor=white)

**Frontend**
![React](https://img.shields.io/badge/React-61DAFB?style=flat-square&logo=react&logoColor=black)
![Next.js](https://img.shields.io/badge/Next.js-000000?style=flat-square&logo=nextdotjs&logoColor=white)
![Vue.js](https://img.shields.io/badge/Vue.js-4FC08D?style=flat-square&logo=vuedotjs&logoColor=white)
![Angular](https://img.shields.io/badge/Angular-DD0031?style=flat-square&logo=angular&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind%20CSS-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white)

**Backend & APIs**
![Node.js](https://img.shields.io/badge/Node.js-339933?style=flat-square&logo=nodedotjs&logoColor=white)
![Express](https://img.shields.io/badge/Express-000000?style=flat-square&logo=express&logoColor=white)
![Django](https://img.shields.io/badge/Django-092E20?style=flat-square&logo=django&logoColor=white)
![NestJS](https://img.shields.io/badge/NestJS-E0234E?style=flat-square&logo=nestjs&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=flat-square&logo=flask&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)

**AI & ML**
![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=flat-square&logo=pytorch&logoColor=white)
![TensorFlow](https://img.shields.io/badge/TensorFlow-FF6F00?style=flat-square&logo=tensorflow&logoColor=white)
![Keras](https://img.shields.io/badge/Keras-D00000?style=flat-square&logo=keras&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=flat-square&logo=scikitlearn&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?style=flat-square&logo=opencv&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat-square&logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?style=flat-square&logo=numpy&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=flat-square)
![Hugging Face](https://img.shields.io/badge/Hugging%20Face-FFD21E?style=flat-square&logo=huggingface&logoColor=black)
![AWS Bedrock](https://img.shields.io/badge/AWS%20Bedrock-232F3E?style=flat-square&logo=amazonaws&logoColor=white)

**Data & infra**
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=flat-square&logo=mysql&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-47A248?style=flat-square&logo=mongodb&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=flat-square&logo=redis&logoColor=white)

**Cloud & DevOps**
![AWS](https://img.shields.io/badge/Amazon%20AWS-232F3E?style=flat-square&logo=amazonaws&logoColor=white)
![Terraform](https://img.shields.io/badge/Terraform-7B42BC?style=flat-square&logo=terraform&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)
![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?style=flat-square&logo=kubernetes&logoColor=white)
![Ansible](https://img.shields.io/badge/Ansible-EE0000?style=flat-square&logo=ansible&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-2088FF?style=flat-square&logo=githubactions&logoColor=white)
![Google Cloud](https://img.shields.io/badge/Google%20Cloud-4285F4?style=flat-square&logo=googlecloud&logoColor=white)
![Oracle Cloud](https://img.shields.io/badge/Oracle%20Cloud-F80000?style=flat-square&logo=oracle&logoColor=white)
![Prometheus](https://img.shields.io/badge/Prometheus-E6522C?style=flat-square&logo=prometheus&logoColor=white)
![Grafana](https://img.shields.io/badge/Grafana-F46800?style=flat-square&logo=grafana&logoColor=white)
![Nginx](https://img.shields.io/badge/Nginx-009639?style=flat-square&logo=nginx&logoColor=white)

**Tools**
![Git](https://img.shields.io/badge/Git-F05032?style=flat-square&logo=git&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)
![Jupyter](https://img.shields.io/badge/Jupyter-F37626?style=flat-square&logo=jupyter&logoColor=white)

<br/>

<img src="assets/continue.svg" width="100%" alt="An arcade continue screen counting down from 9 to 0, then flashing insert coin."/>

**SMAHI-ER**, IEEE, June 2026 — a multi-agent hypergraph framework for resilient human-machine manufacturing. [10.1109/IEHNS68708.2026.11607072](https://doi.org/10.1109/IEHNS68708.2026.11607072)
First Rank, 9.54 SGPA (May 2024) · Second Rank, 9.42 SGPA (Dec 2023) — Karunya Institute

[GitHub](https://github.com/febinrenu) · [LinkedIn](https://www.linkedin.com/in/febin-renu/) · [febinrenu7@gmail.com](mailto:febinrenu7@gmail.com)
