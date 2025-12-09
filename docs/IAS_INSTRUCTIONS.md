# Access Control System (Final Project)

## 1. Project Overview

You will design and implement a secure Access Control System for a small organization. The core objective is to demonstrate sound security engineering practices: strong authentication, proper authorization (RBAC), protected data handling, and extensibility for future security controls.

You must choose **ONE** of the following implementation tracks:

- **Flask Web Application** (traditional browser-based system)
- **Flet Cross-Platform Application** (desktop/mobile/web using a single Python codebase)

Your selection should influence architecture, UI patterns, and deployment considerations. You are encouraged to justify your framework choice in your report.

## 2. Minimum Functional Requirements (Baseline – must be implemented)

All teams must implement these baseline capabilities (adapted appropriately for Flask or Flet):

### User Authentication
- Secure login/logout
- Password hashing (e.g., bcrypt / werkzeug security)
- Protection against credential stuffing (basic lockout or throttling)

### Role-Based Access Control (RBAC)
- At least Admin and Regular User roles
- Enforce role restrictions at both UI and server / controller layer

### User Management (Admin only)
- Create users (with initial role)
- List users
- Disable / delete users

### Profile Management (Self-service)
- View & edit profile fields (name, email, etc.)
- Change password (with current password verification)
- Profile picture upload (validate type/size)

### Security & Session Controls
- CSRF protection (Flask: WTForms/Flask-WTF or manual tokens; Flet: design stateful mitigation for unsafe actions)
- Session timeout / inactivity handling
- Cache control headers (Flask) OR equivalent in Flet for sensitive views

### Data Layer
- SQLite (may abstract to allow future DB migration)
- Use SQLAlchemy ORM (recommended for Flask; acceptable in Flet backend layer)

### Logging (Baseline)
- Authentication success/failure
- Administrative actions (user create/delete/role change)

### Secure Configuration
- Secrets (e.g., SECRET_KEY) not hard-coded in repository (use .env with example file)

## 3. Optional Enhancement Areas (Select at least THREE for full credit potential)

Pick and implement at least 3; more may earn bonus if well-executed:

- **Two-Factor Authentication** (email, TOTP, or SMS gateway simulation)
- **Password Policy** (complexity, reuse prevention, expiration, breach check via k-Anonymity API optional)
- **Advanced RBAC** (custom roles + permission matrix UI)
- **Audit Log Viewer** (filter by actor, date range, action type)
- **REST API** (token-based or OAuth2) with least-privilege scopes
- **Single Sign-On** (OAuth2 / OIDC with Google or GitHub) – still retain local admin bootstrap
- **User Activity Monitoring** (last login, failed attempts, geo/IP display)
- **Automated Backup & Restore** (scheduled export + documented restore path)
- **Multi-Tenancy** (org separation: data scoping + admin boundaries)
- **Reporting & Analytics** (charts for usage, role distribution)
- **Secure Password Reset** (signed time-bound token email flow)
- **Secrets Vault Integration** (e.g., environment abstraction, mocking Vault)

Document clearly which enhancements you selected and why.

## 4. Framework Track Guidelines

### 4.1 Flask Track

**Recommended Structure:**

```
project/
  app/__init__.py
  app/models.py
  app/auth/routes.py
  app/admin/routes.py
  app/profile/routes.py
  app/security/utils.py
  app/templates/... (Jinja2)
  app/static/
  migrations/
  tests/
```

**Key Libraries (suggested):**
- Flask, Flask-Login, Flask-WTF, SQLAlchemy, bcrypt / passlib, python-dotenv

### 4.2 Flet Track

**Design Considerations:**
- Single-page reactive UI with navigation views (login, dashboard, admin panel)
- Encapsulate service layer (auth_service, user_service)
- Enforce RBAC in both UI element visibility and backend action handlers
- Still use SQLAlchemy for persistence (run in background thread if needed)

**Suggested Directory Layout:**

```
project/
  core/ (services, security, config)
  ui/ (views, components)
  models/
  assets/ (default avatars)
  tests/
```

## 5. Security Engineering Expectations

Include (and explain in report):

- **Threat Model** (basic STRIDE table or list of key threats + mitigations)
- **Input Validation & Sanitization** strategy
- **Password hashing algorithm & parameters** (cost factor justification)
- **Session management controls** (timeout, renewal, cookie flags if Flask)
- **Logging & Monitoring** scope
- **Error handling** (no sensitive leakage)
- **Defense against common OWASP Top 10** issues relevant to scope

## 6. Testing Requirements

**Minimum:**
- Unit tests for: user creation, auth flow, role enforcement
- At least one test for each selected enhancement
- Manual test matrix (table) for: login, failed login, password change, role-only route access

**Recommended:**
- Integration test simulating full login → restricted action
- Static analysis / lint pass (flake8 or ruff) + formatting (black)

## 7. Documentation Deliverables

### Project Report (PDF)
- Executive Summary
- Framework Chosen & Rationale
- Implemented Features (baseline + enhancements)
- Architecture & Module Overview (with diagram)
- Threat Model & Security Controls
- Design Decisions / Trade-offs
- Limitations & Future Work

### Technical Documentation
- System architecture diagram
- Database schema ERD
- API spec (if API implemented)
- Configuration & environment variable reference

### User Manual
- Installation & setup (Flask run / Flet run instructions)
- Admin vs Regular User capabilities
- Screenshots / annotated UI

### Code Documentation
- README with quick start, features list, chosen enhancements
- requirements.txt (or pyproject.toml if using Poetry)
- Inline docstrings for core services

### Testing Documentation
- Test plan & coverage summary
- How to execute test suite

### Presentation (10–15 min)
- Slides (problem, solution, demo, security, future work)
- Live or recorded demo

## 8. Submission Guidelines

- Code via public (or invited) GitHub repository – clean commit history
- Tag a release `v1.0-final` before submission
- PDFs: Report, User Manual, Architecture Diagram(s), Slides
- Optional: short demo video link (unlisted) if live demo impractical
- Submit links/files through LMS by deadline

## 9. Evaluation Criteria (Rubric Overview)

| Area | Weight | Description |
|------|--------|-------------|
| Baseline Feature Completion | 25% | All required core features implemented & functional |
| Security Implementation | 20% | Proper hashing, RBAC enforcement, session controls, mitigations |
| Enhancement Depth | 15% | Quality + completeness of selected optional features |
| Code Quality & Architecture | 10% | Modularity, readability, adherence to patterns |
| Documentation Quality | 15% | Clarity, completeness, diagrams, rationale |
| Testing Rigor | 10% | Coverage, meaningful cases, reproducibility |
| Presentation & Demo | 5% | Clarity, professionalism, time management |

## 10. Recommended Timeline

| Week | Goal |
|------|------|
| 1 | Finalize framework selection + threat model draft |
| 2 | Implement authentication + user model |
| 3 | RBAC + admin management UI |
| 4 | Profile management + baseline logging |
| 5 | Enhancements (feature 1) |
| 6 | Enhancements (feature 2) + testing expansion |
| 7 | Hardening, documentation, diagrams |
| 8 | Final polish, presentation prep, release tag |

## 11. Suggested Technology Choices

| Concern | Flask Track | Flet Track |
|---------|-------------|------------|
| Auth & Sessions | Flask-Login, secure cookies | Custom session manager / in-memory + DB fallback |
| Forms / Validation | WTForms / flask-wtf | Custom validators in event handlers |
| UI Layer | Jinja2 templates + Bootstrap | Flet controls & reactive updates |
| State Management | Request-scoped, server memory | Flet view/page state objects |
| Packaging | venv + requirements.txt | same |

## 12. Quality & Academic Integrity

All code must be your original work (libraries allowed). Cite any external snippets or templates. AI assistance must be acknowledged in the report (section: Tooling & Assistance) with description of prompts and human validation.

## 13. Getting Started Checklist

- [ ] Choose framework (Flask / Flet) & justify
- [ ] Initialize repository + LICENSE + README
- [ ] Create virtual environment & dependency file
- [ ] Draft threat model & baseline architecture
- [ ] Implement auth → RBAC → user mgmt → profile
- [ ] Add logging & security headers / controls
- [ ] Implement enhancements
- [ ] Write tests & run lint/format
- [ ] Complete documentation & diagrams
- [ ] Prepare presentation & demo data

---

**Begin early, iterate frequently, and treat security as a design requirement—not an afterthought. Good luck building a secure and maintainable Access Control System!**
