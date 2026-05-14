# Final Project

**Course:** APPLICATION DEVELOPMENT AND EMERGING TECHNOLOGIES (CCCS 106)  
**Joint Collaboration:** CS 3110 – Software Engineering (Team Process & Engineering Practices)  
**Project Title:** Emerging Tech Flet Framework  
**Assessment Type:** Project & Final Examination Equivalent  
**Term:** AY 2025–2026 (Finals)

---

## 1. Project Overview

You will design and build a **cross‑platform application** using the **Flet framework** (Python + Flutter rendering) that demonstrates solid understanding of application development fundamentals and the integration of at least one emerging technology component (e.g., simple AI-powered feature, real-time data streaming, IoT interaction, offline-first strategy, lightweight data analytics, or cloud-backed sync). 

The application must be:
- **Useful and purposeful**
- Reflect **collaborative software engineering practices** in partnership with CS 3110
- Run on at least one of these targets: **Desktop, Web, or Mobile (Android/iOS)**

---

## 2. Core Objectives

By completing this project, students must demonstrate:

1. **Competent use of the Flet UI framework** (layouting, navigation, state management, event handling)
2. **Implementation of data persistence** (local file, SQLite, JSON storage, cloud backend, or lightweight API service)
3. **Integration of one emerging technology** (see Section 6) with a meaningful, non-trivial user-facing feature
4. **Application of basic software engineering practices** (version control workflow, modular code structure, documentation, testing)
5. **Delivery of a functional, usable interface** with attention to accessibility and responsiveness
6. **Collaborative workflow** (role assignments, commit discipline, visible task tracking, code reviews where feasible)

---

## 3. Scope & Feature Expectations

### Minimum Requirements

Your application must include at minimum:

- **Clear, problem-driven purpose** (e.g., productivity tool, learning assistant, habit tracker, dashboard, lightweight business utility, community mini‑platform, etc.)
- **Minimum of 3 core user flows** (e.g., add/view/edit/delete items; authenticate/login; search/filter; generate/export output; analyze input)
- **Stateful UI with reactive updates** (e.g., dynamic lists, form validation, progressive feedback, theme toggle, etc.)
- **Persistent data layer** (local or remote) – Must gracefully handle empty, loading, and error states
- **Emerging tech feature** (see examples) integrated into a meaningful workflow (not a gimmick button)
- **Basic error handling & input validation**
- **Navigation structure** (multi-page, tabbed, or routed pattern in Flet)
- **Configuration or settings panel** (e.g., preferences, theme, account info)

### Optional Enhancements

*(Note: REQUIRED enhancement commitments are defined in Section 16)*

- Authentication (mock, local, or real provider)
- Basic analytics (usage counters, session logs)
- Export (CSV / PDF / report summary)
- Notifications (where supported)
- Role-based or multi-user simulation

---

## 4. Team & Collaboration Structure

Teams should align with CS 3110 partner allocations. 

### Suggested Roles

*(Members may hold dual roles in small teams [3-4 members])*

- **Product Lead** / Vision & Feature Prioritization
- **UI/UX & Accessibility Designer**
- **Lead Developer** (Flet Architecture)
- **Data & Integration Engineer** (storage + emerging tech)
- **QA / Test Coordinator**
- **Documentation & Release Manager**

### Requirements

- Each member must **contribute code** (traceable via commits)
- Each member must provide a **short reflective note** (see Section 11)
- Use a **shared Git repository**
- Maintain a **readable commit history** (avoid giant monolithic pushes)

---

## 5. Architecture & Technical Guidelines

### Sample Structure

*(Adapt as needed)*

```
/app
    main.py             # entry point
    /views              # page/view components
    /components         # reusable widgets
    /services           # data access, APIs, emerging tech integration
    /models             # data classes / DTOs
    /state              # controllers / managers
    /storage            # persistence helpers (sqlite.py, file_store.py, etc.)
    /tests              # unit / functional tests
    /assets             # images, icons, etc.
```

### Design Principles

- Use **modular functions or classes** for separation of concerns
- **Avoid putting all logic in the main file**
- State management approaches may include:
  - Simple in-memory controllers
  - Observer patterns
  - Flet's built-in reactive controls
- **Document your chosen approach**

---

## 6. Emerging Technology Component (Choose ≥ 1)

Select and integrate **one** of:

1. **AI-assisted feature** (e.g., text summary, categorization, simple rule-based or lightweight model inference; if using external APIs ensure fallback handling)
2. **Real-time or event-driven updates** (WebSocket feed, simulated IoT sensor stream, or push-like updates)
3. **Data visualization** (interactive charts reflecting live or processed user data with insights—not just static bars)
4. **Cloud sync or remote API consumption** with caching layer
5. **Offline-first strategy** (queue updates, retry logic)
6. **Edge / device integration** (camera snapshot classification, geolocation where permission allows)
7. **Micro-analytics or recommendation logic**

> **Important:** The feature must be purposeful (e.g., "AI auto-tagging tasks based on description," **not** "Random AI text generator")

---

## 7. Data Persistence Requirements

Implement **one** of:

- **Local JSON or structured file** + abstraction layer
- **SQL/SQLite database** (recommended for relational needs)
- **Cloud** (Firebase, Supabase, or custom lightweight REST server) with local caching

### Requirements

- Provide **initialization script** or automated first-run setup
- Handle **corrupt/missing data gracefully**

---

## 8. Testing & Quality Assurance

### Minimum Expectations

- **At least 3 unit tests** (core logic/data functions)
- **At least 2 functional/integration tests** (e.g., create/edit lifecycle, emerging tech workflow simulation)
- **Manual exploratory test checklist** (submitted in documentation)

> **Note:** If a feature cannot be auto-tested (e.g., API with paid key), mock it.

---

## 9. Documentation Deliverables

Submit a `/docs` folder (or README.md if small) containing:

1. **Project Overview & Problem Statement**
2. **Feature List & Scope Table** (what's in/out)
3. **Architecture Diagram** (simple block diagram is fine; include Flet + data + emerging tech layer)
4. **Data Model** (ERD or JSON schema overview)
5. **Emerging Tech Explanation** (why chosen, how integrated, limitations)
6. **Setup & Run Instructions** (including dependency install and platform targets)
7. **Testing Summary** (how to run, coverage notes)
8. **Team Roles & Contribution Matrix**
9. **Risk / Constraint Notes & Future Enhancements**
10. **Individual Reflection** (per member: 150–200 words)

---

## 10. Presentation & Demonstration

### Live Presentation (10–15 minutes)

| Section | Duration | Content |
|---------|----------|---------|
| Problem & Audience | 2 min | Context and target users |
| Architecture & Tech Stack | 2 min | System design overview |
| Core Feature Walkthrough | 4–6 min | Demo of main functionality |
| Emerging Tech Deep Dive | 3 min | Technical details of integration |
| Lessons Learned + Future Work | 1–2 min | Reflections and next steps |

Be prepared for a **short Q&A** (faculty may probe architecture & design choices).

---

## 11. Submission Package

Deliver via **LeOns** / **Git repository URL** (public or invited access) that contains:

- **Documentation** (as per Section 9)
- **Slide (PDF)** (hyperlink)
- **Demo video — YouTube** (Embed Video in README.md)

**Deadline:** Final Exam Week  
*(Late penalties apply unless prior approval)*

---

## 12. Evaluation

Assessed using the rubric.  
**Total score = 100 points**

Weighted categories reflect:
- Technical depth
- Product value
- Engineering discipline

---

## 13. Academic Integrity & Originality

- All code must be **original or properly cited**
- Use of **AI assistants must be disclosed** in documentation (what portions were AI-suggested)
- **Plagiarism** or uncredited template lifting will result in penalties

---

## 14. Suggested Timeline (9-Week Plan)

| Week | Milestone Focus | Key Outputs |
|------|----------------|-------------|
| **1** | Ideation & Scoping | Problem statement, target users, enhancement shortlist draft, repo initialized, initial backlog |
| **2** | Design Foundations | Wireframes, user flows, architecture & component diagram, initial data model (ERD / schema), risk register |
| **3** | Core Infrastructure | Persistence layer scaffold, navigation shell, state management pattern chosen & prototyped, CI/test harness setup |
| **4** | Core Features Sprint 1 | Implement first CRUD flow(s), validation layer, baseline unit tests (≥1–2), emerging tech feasibility spike/prototype |
| **5** | Core Features Sprint 2 | Remaining CRUD flows, error handling patterns, emerging tech integration in functional form, initial integration test(s) |
| **6** | Enhancement Implementation | Build required enhancements (multi-platform/visualization/security/offline/testing), refine emerging tech feature, performance sanity checks |
| **7** | Polish & Depth | UI/UX refinement, accessibility pass, second required enhancement completion, analytics/logging (if chosen), expand test coverage |
| **8** | Stabilization & Docs | Full documentation draft (all sections), coverage report, regression & exploratory test pass, demo script outline |
| **9** | Finalization & Delivery | Packaging (builds/APK/web deploy), final QA, presentation slides & recording, submission bundle prepared |

---

## 15. Minimum Acceptance Criteria (Pass Threshold)

To qualify for a **passing project grade (≥ 60%)**, the app must:

- ✅ Launch successfully in one supported target
- ✅ Provide at least two working data-bound user flows
- ✅ Persist and retrieve data between sessions
- ✅ Include an implemented emerging tech feature (not stubbed)
- ✅ Contain basic documentation (setup + feature summary)

> **Warning:** Projects failing to meet these may be returned for revision with penalty or receive a failing mark.

---

## 16. Required Enhancement Set

In addition to base functionality, each team **MUST implement at least two (2)** of the following enhancement categories. These are now part of graded evaluation (see rubric category: Enhancement Implementation):

1. **Multi-platform deploy** (e.g., desktop + web or mobile)
2. **Advanced caching/offline or sync strategy** (retry queue, conflict resolution, delta updates)
3. **Complex visualization/dashboard insights** (interactive, drill-down, or aggregated analytics)
4. **Security-oriented feature** (encryption at rest, secure credential handling, role simulation, permission gating)
5. **High test coverage initiative** (≥ 70% of core non-UI logic with meaningful assertions)

### Clarifications

- **Multi-platform deploy** counts only if both targets functionally mirror core flows
- **Caching/offline** must demonstrate an offline interaction followed by sync reconciliation
- **Visualization** must derive insight (not just raw counts); include at least one derived metric
- **Security feature** must be purposeful (e.g., hashed credential store, role-based UI gating) and documented
- **Test coverage** claim must include a coverage report and exclusion rationale (if any)

Teams may implement more than two; only the **strongest two** will be primarily graded if others are partial.

---

## 17. Tooling Recommendations

- **Python 3.11+**
- **Flet** latest stable
- **Optional:**
  - `sqlite3`
  - `pydantic`
  - `requests`
  - `websockets`
  - Lightweight AI API SDK
- **Diagram tooling:**
  - draw.io
  - Excalidraw
  - Mermaid
- **Version control:**
  - Git branching (feature branches + PR reviews)

---

## 18. Acceptance Statement

By submitting, the team certifies:
- **Originality**
- Acknowledges **rubric-based evaluation**
- Consents to potential **academic showcase** (with credit)

---

**Good luck building something meaningful with Flet—focus on clarity, quality, and a purposeful emerging tech integration!** 🚀
