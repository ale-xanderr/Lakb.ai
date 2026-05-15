# Changelog

All notable changes to the **Lakb.ai** project will be documented in this file.

## [2.0.0] - 2026-05-14 (Production-Ready)

### Added
- **Swiping Interface (Software Fest RSC):** Implemented `SwipeCard` component for Tinder-like travel discovery.
- **"Mark as Done" Logic:** Users can now mark locations as visited, updating their profile history.
- **Interaction Service:** New service to record swipes and visited places in Supabase.
- **Logout Service:** Improved session management and cache cleanup.
- **Transportation Guidance:** AI-generated 2-paragraph transportation guides for all destinations.
- **CI/CD Pipeline:** GitHub Actions workflow for automated Android APK builds with secret injection.
- **Discover View:** New view dedicated to the swiping-based destination exploration.

### Changed
- **AI Engine Upgrade:** Migrated to **Google Gemini 2.5 Flash** with integration of **OpenWeather**, **Calendarific**, and **OpenAQ** APIs for context-aware itineraries.
- **AI Engine Refinement:** Gemini prompts now exclude visited places and prioritize liked locations.
- **UI/UX Overhaul:** Refreshed styling across all core views and components for a more modern aesthetic.
- **System Audit:** Comprehensive Engineering Review and System Audit report compiled.
- **Repository Maintenance:** Updated `.gitignore` to track documentation while securing Android build artifacts.

---

## [1.0.0] - 2025-12-10 (Software Engineering 1 Finals)

### Added
- **Supabase Integration:** Full migration from local storage to cloud-backed Supabase (PostgreSQL + Auth).
- **AI Itinerary Generator:** Integration with Google Gemini for personalized trip planning.
- **Real-time Discovery:** Google Places and Google Maps API integration for destination data.
- **State Management:** Implementation of specialized controllers (Auth, Places, Favorites, Profile).
- **Testing Suite:** Added 147 unit and integration tests with >70% coverage.
- **Connectivity Monitoring:** New module for real-time network state tracking.
- **Android Support:** Added deep-linking and OAuth callback support for mobile deployment.

### Fixed
- Navigation flow and view stacking issues.
- Rate limiting and error handling for external APIs.
- Duplicate file cleanup and project structure refactoring.

---

## [0.1.0] - 2025-10-25 (Initial Prototyping)

### Added
- **Project Initialization:** Basic Flet structure and repository setup.
- **Requirements:** Detailed SRS (Software Requirements Specification) documentation.
- **Core UI:** Preliminary login, home, and profile view prototypes.
- **Geolocation:** Initial implementation of location services.

---

**Note:** For a full list of commits, refer to the git history: `git log --oneline`.
