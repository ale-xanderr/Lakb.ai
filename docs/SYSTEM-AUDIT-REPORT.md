# **Final Engineering Review: System Audit Report**

**Course:** Software Engineering 2  
**Project Name:** Lakb.ai - AI-Powered Travel Discovery and Planning System  
**Version:** 2.0 (Production-Ready)  
**Team Name:** Team LOCaiT  
**Date:** May 14, 2026

## **1\. Executive Summary**

Lakb.ai has evolved from a conceptual prototype in Software Engineering 1 to a production-ready application. Built with the Flet framework (Python + Flutter rendering), the system integrates Google Gemini AI for personalized itinerary generation and Google Places/Maps APIs for discovery. A significant milestone in Version 2.0 is the full implementation of the **RSC (Recommendations, Suggestions, and Comments)** defined during the Software Fest, which introduced high-engagement features like a swiping discovery interface, interactive itinerary completion ("Mark as Done"), and advanced AI preference refinement that excludes previously visited locations.

## **2\. System Architecture & Infrastructure**

### **2.1 Infrastructure Map**

| Component | Technology Stack | Deployment Environment |
| :---- | :---- | :---- |
| Frontend | Flet (Python + Flutter) | Android (APK), Desktop (Windows/Linux) |
| Backend API | Python Services (Httpx) | Serverless (Supabase Edge Functions / Client-side) |
| Database | PostgreSQL | Supabase Cloud |
| AI Engine | Google Gemini AI | Google AI Studio |
| Auth Service | Supabase Auth (JWT/OAuth2) | Supabase Cloud |

## **3\. RSC Implementation & Software Fest Enhancements**

### **3.1 Discovery Swiping Interface**
A specialized `SwipeCard` component was implemented in Flet, enabling a Tinder-like discovery experience. 
*   **Interaction Logging:** Swipes are recorded via the `InteractionService` into the `swipes` table, categorizing locations as 'like' or 'dislike'.
*   **Adaptive Learning:** These interactions are used as context in future AI prompts to refine destination relevance based on individual taste.

### **3.2 "Mark as Done" & Itinerary Management**
The active itinerary UI now includes a "Mark as Done" feature for visited destinations.
*   **Persistent History:** Marking a place as "done" updates the `visited_places` table in Supabase.
*   **AI Exclusion:** The `AIEngine` explicitly filters out "visited_places" from new generation cycles, ensuring users are never recommended the same location twice for different trips.

### **3.3 Enhanced Transportation & Location Details**
Destination profiles have been enriched with practical guidance:
*   **Transport Guides:** AI-generated 2-paragraph guides explaining how to reach and navigate specific destinations (Airport, Jeepney, Tricycle, Walking).
*   **Contextual Details:** Inclusion of suggested visiting times and why a specific location fits the user's current mood and style.

## **4\. Performance & Stress Test Audit**

### **4.1 Test Results & Bottlenecks**

* **Average Response Time:** ~200ms for core service operations.  
* **System Breaking Point:** Limited by external API rate limits (Google Gemini/Places).
* **Optimizations Implemented:** 
    * **Reactive State Controllers:** Optimized UI updates for the swiping interface.
    * **Asynchronous API Calls:** Parallel fetching of weather, air quality, and holiday data to minimize generation latency.
    * **Supabase Upsert Logic:** Optimized database writes for high-frequency swipe actions.

## **5\. DevOps & Reliability Audit**

### **5.1 CI/CD Pipeline (GitHub Actions)**

The system utilizes an automated **GitHub Actions** workflow (`android-build.yml`) to ensure continuous integration and reliable distribution:
1.  **Environment Orchestration:** On every push to the `main` branch, a runner is provisioned with **JDK 17**, **Python 3.11**, and the **Flutter SDK**.
2.  **Automated Testing:** The test suite (`pytest`) is executed to validate 147 tests. A quality gate prevents builds if core unit tests fail or if coverage drops below 70%.
3.  **Secure Secret Injection:** GitHub Secrets are dynamically injected into a temporary `src/core/build_secrets.py` file. This ensures API keys for Gemini, Google Places, and Supabase are securely baked into the APK without being exposed in the source code.
4.  **Automated Android Build:** The workflow executes `flet build apk` with configured deep-linking parameters (`lakbai://oauth_callback`).
5.  **Artifact Distribution:** Successfully built APKs are versioned with the current date and commit hash, then uploaded as GitHub artifacts for immediate testing and deployment.

## **6\. Security & Code Quality Audit**

### **6.1 Security Hardening**

* **Auth:** JWT/OAuth2 via Supabase with bcrypt hashing.
* **RLS (Row Level Security):** Strict PostgreSQL policies ensure user data isolation for `swipes`, `visited_places`, and `plans`.
* **Config Security:** All API keys are isolated in `.env` files and excluded from source control.

## **7\. Deployment Runbook (Disaster Recovery)**

1. **Build from Scratch:** Clone repo, install dependencies, configure `.env`, and apply SQL migrations in `docs/rsc_migrations.sql`.
2. **Rollback:** Revert to stable git tag and re-execute the build pipeline.
3. **Log Access:** Python tracebacks for local debugging; Supabase API logs for cloud/database monitoring.

## **8\. Conclusion & Future Roadmap**

Version 2.0 successfully delivers on all Software Fest RSC requirements. 

**Future Roadmap (v3.0):**
* **Collaborative Planning:** Sharing itineraries with other users.
* **Dynamic Weather Alerts:** Proactive itinerary adjustments based on real-time weather changes.
* **Global Scalability:** Full multi-language support and internationalization.
