# ***CS 319 \- Information Assurance And Security*** 

Access Control System (Final Project)  
LAKB.AI – *Intelligent Travel Assistant Application*

**GROUP: LOCaiT**							         **SECTION: BSCS \- 3A** 

**GROUP MEMBERS:** 	AQUINO, SEAN XANDER B.   
ATIENZA, LAWRENCE  
ORIAS, MARK JOSEPH C.

1. # **Introduction**

   1. # **Summary**

   **LAKB.AI** is an *AI-powered travel recommendation system* designed to help users generate trip plans, discover destinations, and retrieve real-time information using geolocation, Google Places API, and AI recommendations. The system includes offline caching, secure API access handling, and role-based access to administrative features.

   The goal of LAKB.AI is to provide **fast, contextual, and intelligent trip planning** while maintaining strong privacy, access control, and data protection practices.

   2. ## **Purpose**

   This document defines the functional and non-functional requirements for the Lakb.ai, version 1.0. Its purpose is to provide a clear and consistent guide for the development team and to serve as the primary point of reference for project stakeholders regarding the system's intended behavior and capabilities.

   By clearly defining the requirements, it ensures seamless collaboration among the development team throughout the build process. It helps reduce misunderstandings and mishaps and ensures that the system’s development is aligned with its intended purpose.

   This document ensures that:

* Developers understand what to build  
* Designers understand what to visualize  
* Testers and Documentators understand what to validate

  3. ## **Scope**

  Lakb.ai is a mobile-first AI travel assistant (Android) that serves:

1. **Travelers & Tourists**

* Discover new destinations and activities based on preferences  
* Generate personalized multi-day itineraries  
* Access real-time weather, holidays, and air quality information  
* Save favorite places and sync across devices

2. **Local Residents**

* Explore hidden gems and local attractions  
* Find nearby points of interest  
* Discover new experiences in familiar areas

---

2. # **System Description**

   1. ## **Product Perspective**

   Lakb.ai is a **standalone mobile application (Android)** that integrates:

* AI recommendation engine  
* Google Places API (data, images, reviews, routing)  
* Geolocation services

  It uses user preferences \+ mood \+ real-time location to compute recommendations and itineraries.

  2. ## **Product Function**

  Core system functions:

* Location-based Point-of-Interest (POI) search  
* Preference filtering (budget, activity type, travel style)  
* Destination details with photos & metadata  
* AI-generated itineraries  
* Routing & maps  
* User accounts / saved favorites  
* Review aggregation (Google Place API)

  3. ## **Frameworks / Technologies Used & Rationale**

  **Flet (Python UI Framework)**

  Flet was out of choice given its centralized strength of creating platform-independent, visually appealing user interfaces with a single Python implementation. This decision drastically reduced the development time, removed the necessity to have independent native mobile and web development teams and enabled us to use our existing Python experience to write the backend logic as well as the frontend presentation.

  **AI / Generative Model (Gemini API)**

  The Gemini API is selected to be the central intelligence of LAKB.AI. Its sophisticated logic and formatted output features play a vital role in processing sophisticated, open-ended travel bookings and creating precise and tailored itineraries in a foreseeable, JSON form. Conversational planning is made possible through this model and it offers a rich user experience, as opposed to plain database lookups.

  **Google Places API / Maps / OpenWeather / OpenAQ / Calendarific**

  External APIs deliver real time context sensitive information. Google Places API is necessary to get correct location information, points of interest as well as navigational context. It includes OpenWeather to get instant weather predictions so that, as per the requirements, the AI could adjust clothing or activity suggestions, thus, being a significant component of a complete travel assistant.

  **Local Caching (JSON Fallback)**

  The application uses minimal local caching through JSON files and Flet's client storage for offline fallback scenarios:

* **Recent Searches:** Stored in Flet's `client_storage` for quick access  
* **Favorites Fallback:** Cached locally in `favorites.json` when offline  
* **Auth Tokens:** Stored in `client_storage` for session persistence  
* **User ID Caching:** In-memory caching to reduce redundant API calls

This caching strategy is minimal by design - large datasets like place information, maps, and full itineraries are NOT cached offline. The application prioritizes cloud synchronization over local storage.

  **SUPABASE (Primary Database)**

  Supabase (PostgreSQL) is the primary cloud database and authentication provider for the application:

* **Authentication:** Email/password and Google OAuth flows via Supabase Auth  
* **Database Tables:** Three main tables with Row Level Security (RLS):  
  * `profiles` - Extended user information (name, avatar, etc.)  
  * `favorites` - User-saved places with JSONB data  
  * `plans` - Travel itineraries with JSONB data  
* **Storage:** Profile avatars stored in Supabase Storage `avatars` bucket  
* **Real-time Sync:** Cross-device data synchronization  
* **Security:** Row Level Security ensures users only access their own data

  4. ## **Architecture & Module Overview**

  A clear and modular architecture of LAKB.AI allows maintaining, scaling, and separation of concerns. The application consists of the following major modules that interact mostly via the API Service Module:

  Authentication Module

  This module is user session management in case it is implemented. It does the email/password, or Google Sign-In, login processing, state of the session, and user registration and profile changes.

  **AI Engine Module**

  This is the main intelligence element of the application. Its main role is to process complicated queries of the user, and create multi-day context aware itineraries. It accepts user preferences, location, and merges API Service Module (weather, holidays, air quality) data to generate a structured JavaScript Object (JSON).

* Generates itineraries  
* Accepts user preferences and location  
* It combines data from the API Service Module (weather, holidays, air quality) to produce a structured JavaScript Object (JSON).  
* Produces trip summaries  
* Combines weather \+ holiday \+ air quality context  
  **API Service Module**

  This is the point of convergence of all external communications. It can handle authorized requests to all third-party services leaving no API keys on the client-side.

* Google Places Search: Processes search results, place details, images downloading, and map URL generation.   
* Place Details  
* Maps URL generation  
* AI (Gemini) requests  
* Weather, Air Quality, Holidays

  **State Management**

  Custom state controllers manage application state and data flow:

* `auth_state_controller` - Authentication session management  
* `places_state_controller` - Place search results and caching  
* `favorites_state_controller` - User favorites synchronization  
* `profile_state_controller` - User profile data  
* `app_state_manager` - Global application state  
* `service_manager` - Service dependency injection

  **UI / Views Module**

  This is the presentation layer that is constructed with Flet framework. It is in charge of the visualization of any visual content and processing of user input. It is the main application views:

* Home: This is the first area of quick search and customized content.  
* Search Results  
* Destination Page: Full information of a chosen POI.  
* Plan Builder: This is where the user enters his/her preferences and is shown the completed itinerary.  
* Generated Plan Summary

  5. ## **Implemented Features**

  ### **Core Features (CCCS 106 - Application Development)**

* **AI-Powered Trip Generation:** Multi-day itineraries generated using Google Gemini API with context-aware recommendations  
* **Real-time Place Search:** Google Places API integration with category filtering (Hotels, Restaurants, Attractions, Parks, Shopping, Nightlife)  
* **Location-Based Discovery:** GPS integration with proximity search and "Popular in [Location]" queries  
* **Interactive Maps \u0026 Routing:** Google Maps integration with distance calculation, directions, and route visualization  
* **Destination Details:** Comprehensive information pages with photos, ratings, reviews, hours, contact info  
* **My Plans (Save/Load):** Persistent storage and management of generated travel itineraries in Supabase  
* **Favorites Management:** Save/remove destinations with cross-device synchronization via Supabase  
* **Geolocation Tracking:** Real-time location updates with device GPS integration (permission-based)

  ### **Security Features (CS 319 - Information Assurance)**

* **Strong Authentication:**  
  * Email/password with bcrypt hashing via Supabase  
  * Google OAuth integration (PKCE flow)  
  * Guest mode for limited exploration  
  * Session timeout and inactivity handling  
* **Role-Based Access Control (RBAC):** Three user tiers (Guest, Regular User, Admin) with enforced permissions  
* **Protected Data Handling:**  
  * Row Level Security (RLS) on all Supabase tables  
  * Encrypted credential storage  
  * CSRF protection through secure token handling  
* **Secure Session Management:** Automatic timeout, token refresh, secure storage in `client_storage`  
* **Password Management:** Change password with current password verification  
* **Profile Privacy:** Users can only access their own data (profiles, favorites, plans)

  ### **AI & Emerging Technology Integration

 (CCCS 106 Enhancement)**

* **Google Gemini AI:** Natural language processing for itinerary generation and travel suggestions  
* **Context-Aware Recommendations:** Personalized suggestions based on user preferences, location, mood, and interests  
* **Weather Integration:** OpenWeather API for real-time weather forecasts influencing activity recommendations  
* **Holiday Awareness:** Calendarific API integration for public holiday information  
* **Air Quality Data:** OpenAQ API for outdoor activity safety recommendations  
* **Intelligent Query Parsing:** AI-powered parsing of destination search queries  
* **Smart Date Suggestions:** Automated date recommendation based on holidays and weather

  ### **User Experience Features**

* **Profile Management:**  
  * View/edit personal information (name, email)  
  * Profile picture upload to Supabase Storage  
  * Account metadata display  
* **Settings \u0026 Preferences:**  
  * Theme toggle (light/dark mode)  
  * Language preferences  
  * Notification settings  
  * Privacy controls  
* **Navigation:** Bottom navigation bar with Home, Favorites, Plan Trip, and Profile sections  
* **Guest Mode:** Browse and search without account creation (limitations apply)  
* **Multi-page UI:** Reactive interface with dynamic views and navigation routing

  ### **Data Management \u0026 Persistence**

* **Cloud-First Architecture:** Supabase (PostgreSQL) as primary database  
* **Limited Offline Support:**  
  * JSON fallback for favorites (`favorites.json`)  
  * Auth token caching in `client_storage`  
  * Recent search history preservation  
* **Cross-Device Sync:** Real-time synchronization of favorites and plans via Supabase  
* **Persistent Storage:** All user data (profiles, favorites, plans) stored with Row Level Security  
* **CRUD Operations:** Full create, read, update, delete functionality for plans and favorites

  6. ## **Role-Based Access Model**

  The application implements a three-tier access control system with distinct permissions for different user types:

  **Guest User (Unauthenticated)**

  Guests can explore the app without creating an account but have limited functionality:

* **Search Destinations:** Full access to location-based search and place discovery  
* **View Place Details:** Can view comprehensive information about destinations including:  
  * Photos and ratings  
  * Operating hours and contact information  
  * Reviews and descriptions  
  * Map previews and directions  
* **Basic Exploration:** Browse categories and filter search results  
* **Limitations:** Cannot save favorites, create trip plans, or access profile features. All data is session-only and not persisted.

  **Regular User (Authenticated)**

  Authenticated users (via Email/Password or Google OAuth) have full access to all application features:

* **Trip Planning:** Create, save, and manage AI-generated multi-day travel itineraries  
* **Favorites Management:** Bookmark destinations and sync across devices via Supabase  
* **Saved Plans:** Persistent storage of all generated itineraries in Supabase `plans` table  
* **Profile Management:**  
  * Update personal information (name, email)  
  * Change password  
  * Upload and manage profile avatar (stored in Supabase Storage)  
* **Cross-Device Sync:** All user data synchronized in real-time via Supabase  
* **Search History:** Recent searches cached in `client_storage`  
* **Offline Access:** Favorites cached locally in `favorites.json` for offline viewing

  **Admin (External Monitoring)**

  Administrators monitor and manage the system through the **Supabase Dashboard** (external to the app):

* **Database Monitoring:** View and analyze data in Supabase tables:  
  * `profiles` - User account information  
  * `favorites` - User-saved destinations  
  * `plans` - Generated travel itineraries  
* **User Management:** Monitor user registrations, authentication logs, and session activity  
* **API Usage Tracking:** Monitor Google API quotas and billing through Google Cloud Console  
* **Storage Management:** View and manage uploaded avatars in Supabase Storage  
* **Security Policies:** Review and update Row Level Security (RLS) policies  
* **No In-App Dashboard:** All administrative functions performed via Supabase web interface

  **Developer Role (Development Environment)**

  During application development, developers have access to debugging and configuration tools:

* **Debug Logging:** Application prints detailed debug information to console:  
  * Authentication flow status  
  * API request/response details  
  * State management changes  
  * Error stack traces  
* **Environment Configuration:** Direct access to modify:  
  * `.env` file for API keys and credentials  
  * `config.py` for application settings  
  * Supabase project settings  
* **Testing Tools:** Ability to test with different user states (guest, authenticated)  
* **Database Access:** Direct database queries via Supabase dashboard for debugging  
* **Build Configuration:** Modify APK build settings in `build_apk.py` and `pyproject.toml`

  7. ## **Design Decisions / Trade-offs**

* **Cloud-First Architecture:** Prioritized Supabase cloud database for data persistence and authentication with minimal JSON fallback for offline scenarios.  
* **Stateless AI:** The system does not retain user conversation history, generating plans on-demand to reduce storage overhead.  
* **Sanitized Inputs:** All API calls use strict input validation to prevent injection attacks and minimize token wastage.

---

3. # **Specific Requirements** 

   1. ## **Functional Requirements (FR)**

* FR-001: User Registration and Login: Support login via Email/password, Google Sign-In, and Guest mode.  
* FR-002: User Profile Management: Users can update Personal info, Preferences, and Saved destinations.  
* FR-003: AI-Based Travel Recommendations: AI suggests Destinations, Events, Activities, and Mood-based suggestions.  
* FR-004: Location-Based Search: Using geolocation for Nearby POIs, Restaurants, Attractions, and Experience spots.  
* FR-005: Travel Itinerary Generation: AI-generated multi-day plans based on Budget, Duration, and Preferred experiences.  
* FR-006: Travel Plan Editing & Saving: CRUD operations on itineraries (Save, Edit, Delete).  
* FR-007: Maps and Routing: Features include Directions, Travel time, and Distance.  
* FR-008: Destination Details: Displays Photos, Ratings, Reviews, Operating hours, and Contact & address.  
* FR-009: Favorites System: Users can bookmark places.  
* FR-010: Third-Party API Integration: Uses Google Places, Maps, OpenWeather, OpenAQ, Calendarific, and generative LLM (Gemini).

  2. ## **Non-Functional Requirements (NFR)**

* NFR-001: Performance: Search and recommendations must load within 5 seconds under stable internet.  
* NFR-002: Usability: UI must be understandable without a tutorial; Navigation must remain consistent across pages.  
* NFR-003: Security: Encrypted API calls, Secure token storage, No API keys stored in client-side code.  
* NFR-004: Reliability: 99% uptime target; Must gracefully fail when APIs are unavailable.  
* NFR-005: Compatibility: Android 10+, iOS 15+, Browser support (Chrome, Safari, Firefox, Edge).  
* NFR-006: Scalability: Should handle growth in Users, Search queries, and API requests.  
* NFR-007: Privacy Compliance: Must abide by RA 10173 — Data Privacy Act; Location access must request user consent.  
* NFR-008: Maintainability: Modularized code, Easily replaceable AI model or API keys, Clear folder structure.

---

4. # **Technical Documentation** 

   1. ## **System Architecture Diagram** 

## 

   2. ## **Threat Model & Security Controls**

   This section documents the potential security risks for LAKB.AI and the corresponding controls implemented to mitigate them.

   **Possible Threats**

* API key exposure  
* Unauthorized access to saved plans  
* Role bypass  
* Cache tampering  
* Data leakage through logs  
* Injection attacks  
* AI misuse  
* Location spoofing  
  **Security Controls Implemented**

* .env for API keys  
* Centralized configuration using Config class  
* Sanitized API inputs  
* No storage of sensitive user data  
* Minimal geolocation retention  
* Secure DB query patterns (SQLAlchemy ORM)  
* Access control checks for admin screens  
* Error-safe fallbacks

---

5. # **User Manual**

   1. ## **Installation & Setup**

      1. **Clone the repository:**

         https://github.com/ale-xanderr/Lakb.ai

         cd lakb.ai

      2. **Create and activate a Python virtual environment (Windows PowerShell):**

         python \-m venv .venv

         venv\\Scripts\\Activate.ps1

      3. **Install dependencies**

      pip install \-e .

      4. **Configure environment variables**

         cp .env.example .env

         \# Edit .env with your API keys and credentials

         Required environment variables:

         \- SUPABASE\_URL \- Your Supabase project URL

         \- SUPABASE\_KEY \- Supabase anonymous key

         \- GOOGLE\_PLACES\_API\_KEY \- Google Places API key

         \- GOOGLE\_MAPS\_API\_KEY \- Google Maps API key

         \- GEMINI\_API\_KEY \- Google Gemini API key

   2. ## **Supabase Setup: Authentication and Database Integration**

   The application requires a Supabase project with authentication and database tables configured.

      1. **Create Supabase Project**

* Go to [https://supabase.com](https://supabase.com) and create a free account  
* Create a new project and note your project URL and API keys  
* Copy the `SUPABASE_URL` and `SUPABASE_KEY` (anon/public key) to your `.env` file

  2. **Configure Authentication**

     Enable Authentication Providers:

* In your Supabase dashboard, navigate to **Authentication → Providers**  
* Enable **Email** provider (enabled by default)  
* Enable **Google** provider:  
  * Create OAuth credentials in Google Cloud Console  
  * Add authorized redirect URI: `https://<your-project-ref>.supabase.co/auth/v1/callback`  
  * Add the Google OAuth Client ID and Client Secret to Supabase  
* Configure Site URL and Redirect URLs:  
  * Site URL: `http://localhost:8550` (for development)  
  * Redirect URLs: Add `http://localhost:8550/oauth_callback` and `lakbai://oauth_callback` (for Android deep linking)

    3. **Create Database Table**

    Run the following SQL queries in the Supabase SQL Editor (**Database → SQL Editor**):

    Create Profiles Table:

| \-- Profiles table for extended user information CREATE TABLE profiles (   id UUID REFERENCES auth.users(id) PRIMARY KEY,   email TEXT NOT NULL,   first\_name TEXT DEFAULT '',   last\_name TEXT DEFAULT '',   avatar\_url TEXT,   created\_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),   updated\_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() ); \-- Enable Row Level Security ALTER TABLE profiles ENABLE ROW LEVEL SECURITY; \-- Allow users to read their own profile CREATE POLICY "Users can view own profile"   ON profiles FOR SELECT   USING (auth.uid() \= id); \-- Allow users to insert their own profile CREATE POLICY "Users can insert own profile"   ON profiles FOR INSERT   WITH CHECK (auth.uid() \= id); \-- Allow users to update their own profile CREATE POLICY "Users can update own profile"   ON profiles FOR UPDATE   USING (auth.uid() \= id); |
| :---- |

    Create Favorites Table:

| \-- Favorites table for user-saved places CREATE TABLE favorites (   id BIGSERIAL PRIMARY KEY,   user\_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,   place\_id TEXT NOT NULL,   data JSONB NOT NULL,   created\_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),   UNIQUE(user\_id, place\_id) ); \-- Create index for faster queries CREATE INDEX idx\_favorites\_user\_id ON favorites(user\_id); CREATE INDEX idx\_favorites\_place\_id ON favorites(place\_id); \-- Enable Row Level Security ALTER TABLE favorites ENABLE ROW LEVEL SECURITY; \-- Allow users to view their own favorites CREATE POLICY "Users can view own favorites"   ON favorites FOR SELECT   USING (auth.uid() \= user\_id); \-- Allow users to insert their own favorites CREATE POLICY "Users can insert own favorites"   ON favorites FOR INSERT   WITH CHECK (auth.uid() \= user\_id); \-- Allow users to delete their own favorites CREATE POLICY "Users can delete own favorites"   ON favorites FOR DELETE   USING (auth.uid() \= user\_id); |
| :---- |

  Create Plans Table:

| \-- Plans table for travel itineraries CREATE TABLE plans (   id BIGSERIAL PRIMARY KEY,   user\_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,   title TEXT NOT NULL,   description TEXT,   image\_url TEXT,   data JSONB NOT NULL,   created\_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),   updated\_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() ); \-- Create index for faster queries CREATE INDEX idx\_plans\_user\_id ON plans(user\_id); \-- Enable Row Level Security ALTER TABLE plans ENABLE ROW LEVEL SECURITY; \-- Allow users to view their own plans CREATE POLICY "Users can view own plans"   ON plans FOR SELECT   USING (auth.uid() \= user\_id); \-- Allow users to insert their own plans CREATE POLICY "Users can insert own plans"   ON plans FOR INSERT   WITH CHECK (auth.uid() \= user\_id); \-- Allow users to update their own plans CREATE POLICY "Users can update own plans"   ON plans FOR UPDATE   USING (auth.uid() \= user\_id); \-- Allow users to delete their own plans CREATE POLICY "Users can delete own plans"   ON plans FOR DELETE   USING (auth.uid() \= user\_id); |
| :---- |

    4. **Configure Storage for Profile Images**

* In Supabase dashboard, go to Storage  
* Create a new bucket named `avatars`  
* Make the bucket public (for profile image access)  
* Set up RLS policies for the storage bucket:

| \-- Allow authenticated users to upload their own avatars CREATE POLICY "Users can upload own avatar"   ON storage.objects FOR INSERT   WITH CHECK (     bucket\_id \= 'avatars'      AND auth.uid()::text \= (storage.foldername(name))\[1\]   ); \-- Allow users to update their own avatars CREATE POLICY "Users can update own avatar"   ON storage.objects FOR UPDATE   USING (     bucket\_id \= 'avatars'      AND auth.uid()::text \= (storage.foldername(name))\[1\]   ); \-- Allow public read access to avatars CREATE POLICY "Public avatar access"   ON storage.objects FOR SELECT   USING (bucket\_id \= 'avatars'); |
| :---- |

  5. **Verify Database Setup**

  After running all SQL queries, verify that:

* All three tables (`profiles`, `favorites`, `plans`) exist  
* Row Level Security (RLS) is enabled on all tables  
* Storage bucket `avatars` is created and accessible  
* Authentication providers (Email, Google) are enabled

  3. ## **Running the application**

     Development Testing (Desktop):

     *\# For quick testing during development only*

     Desktop:

     flet run src\\[main.py](http://main.py)

     Web:

     flet run src\\[main.py](http://main.py) \-- web \-- port 8550

     Android APK Build (Primary Platform):

     python build\_apk.py

  4. ## **Usage Guide**

* Launch the app. You should see a splash screen and then the login/register screen.  
* Sign in using Google or email *(if Supabase & Google OAuth is configured)*. You can also continue as a guest where supported.  
* Home screen features:  
  * Search bar: type a place, category, or nearby search.  
  * Category tabs & filters: narrow results by type (e.g., food, attractions, landmarks).  
  * Destination cards: view place details, photos, and quick actions.  
  * Favorites: save places to your favorites *(requires logged-in user for persistence).*  
  * Plan Trip: create a date-range and parameters; generate an AI itinerary.  
  * Profile / Settings: edit users details, password and save.   
* Plan trip flow:  
  * Open "Plan Trip" from the navigation or floating action button.  
  * Select dates, preferences (budget, activity types) and request an itinerary.  
  * The AI engine will propose a plan — you can save it to your profile or export/share it.  
  * The generated plan trip will be available in a minute.

---

6. # **Limitations & Future Work**

   1. ## **Limitations**

* Limited offline support: the app does not provide full offline caching of place data, maps, or itineraries. Some UI state is stored in Flet's \`client\_storage\` (recent searches, tokens) but large datasets are not cached for offline use.  
* Maps, place photos and routing rely on Google APIs (\`GOOGLE\_PLACES\_API\_KEY\`, \`MAPS\_STATIC\_API\_KEY\`) and related billing/quotas. Missing or restricted API access will result in degraded map/photo features.  
* AI suggestions are powered by the configured LLM provider (the repo references \`GEMINI\_API\_KEY\` / generative endpoints). The current AI engine produces helpful but sometimes generic itineraries and summaries — advanced personalization and multi-pass planning are limited.  
* Authentication & persistence depend on Supabase: the app integrates Supabase for OAuth (Google) and email/password flows. When Supabase credentials are not configured, authentication, profile sync, and favorites persistence will not work (the app still runs in a degraded/local-only mode).  
* PKCE / OAuth caveat: the Supabase PKCE flow stores a \`code\_verifier\` in the running client instance. If you restart the app after initiating OAuth in the browser but before the callback completes, the code exchange may fail and require re-initiating the login flow.  
* **No admin dashboard:** there is currently no built-in admin/control panel for managing destinations, users, or content from inside the app UI.  
* **Limited automated tests and CI:** the repository has minimal or no automated tests or CI configured to validate features across changes.

  2. ## **Future Work**

* **Offline-first & sync:** add local caching for search results, destination details, and saved itineraries, plus background synchronization to Supabase when connectivity returns.  
* **Improved AI personalization:** refine the AI engine to use user history, saved favorites, and contextual signals (weather, local events) for more customized and non-generic itineraries.  
* **Transport routing & Directions:** integrate Google Directions (or an alternative) to provide multimodal routing (walking, driving, transit) and estimated travel times between itinerary stops.  
* **Real-time alerts & notifications:** add push notifications or in-app alerts for itinerary changes, weather warnings, or travel disruptions.  
* **Sharing and export:** implement email/SMS sharing, calendar export (iCal), and deep links for saving/sharing itineraries.  
* Admin panel & moderation tools: add a dedicated web admin dashboard for curating destinations, managing users, and viewing analytics and not just relying on ***supabase dashboard***.  
* **Multi-device sync and offline merge:** improve how user data (favorites, plans) syncs across devices and handles conflict resolution when offline edits occur.  
* **Observability & testing:** add structured logging, error reporting (Sentry or similar), unit/integration tests, and CI pipelines to maintain code quality.

**DATABASE DIAGRAM**

*Supabase public tables schema*

**![][image1]**

**![][image2]**

**ERD?\!?\!\!**

[image1]: <data:image/png;base64,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pWtM+u2+ZcuW2e2K356FtiW69qm/fao1NOqSRnvssYetuvTcc8/ZNl1U3z0+ZMgQe3kr3XeVnETvWaHxV7/6ldluu+3MDjvsYN+b37/61WWu3N+6KL9udd3OX/ziF+aAAw6w51O7x59//nl7BYWf/vSn9r2prVu3buaaa66xl++aMWOGveD7jjvuaM4888x2A6Jel7v/xBNP2GpReh0PPfRQ9NBY734iNTTqQ6gPs99eK60IeqFpbwgoEq0PqkYSIzRqI/D111/X3Y+jnY/W/1j9tba2mm+++cZutKrZuAFFESs06lzFavbXulj8LbfcYh588EF7LVD/cdH6rysWzJw5045MOu56lT5Nn5zOn17bJn1x9N9fraFRAVAhbODAgaZ79+62rVxofPTRR+00utUXVoWzTTfd1Nxzzz32+ql33XVX0H+50KiQedxxx9myoJtvvrltU2DcbLPNzLhx4+xr0oXd1a7QqDKkum7rggULbHgcM2aM7UPlRP3/mQyNen/6P5dddpntI3ZorHc/kRoaY9ELrPfwtCpD+G1ZaceVvMBuDA888ICtY+u3J1177bWlyhLvvfee/dD506A43M4iRmjMA71HDk8DbcUKjbVatGhR2WpK5UKgLoTvT5tleqfW0KiRO43i7bXXXnYfrrZyoVE0CujuK5z98pe/LP196KGHBv2XC4264L4C6M0332wHwFavXt1mJNP55JNPbGi88sorS30oWO65555lA6ALjZqHt956a6ldRQvKPac9nbFdzU1odGXEVKUhS61Z0Qpy2mmn2fSuIe5kaNSQ8zbbbGM/kPpb344OOeQQ+6Fy1SY++ugjc8IJJ5idd97ZDB482LZddNFFtjzYlltuaYeVXZ9qP/roo822225rh6VdJQn3wVKf+uC5//fiiy/ak2H1GvTtR4cEXeUIVZFQuw4V+O8JcWkZltuIptEomt+WhtAYTgMUTaNCYzOoNTT+7ne/s7eff/55KTTedtttdv+o+yeddFKb0Kh9s7vvn9OofbxulQ3c8zWoo32u7muZuNCoOuMabNK5oO7/6jCywqTrTyOEeo5C4/Dhw0vtkyZNsrcaZdxll12C/5kcaTz88MNL95UzCI0Z3pCuyZb8W9dp86ephkKZvkUooOnWBbyXXnrJDtW//fbb9puEvin06dPHXHLJJZa+0ej16zwIfSDHjx9v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XZE+I+392FGVvLSu+O21+vjjj80TTzwRtGfx7LPPlqpH1YPQiLwgNAINRGgMpylHVXmmT5/eps3/uxq6gO8RRxxhJkyYYKZOnWr69etn2xTmDjroIHsxf12TU9dzVSAcO3asGTdunH1ut27dStftdGVGFQD1+Keffmqn2X777c3jjz9uTjrpJLPXXnvZvlXCVKHnpZdeSg2NZ555pv2/b7/9trnooots24knnmgOP/zwaBUwmpl+7HjJJZfYC+Zr+aoQg8pz/uUvfzGrV6+20yhUqu2FF14wo0aNsm1aj1y76+v222+3/aj8q/6+4447zDXXXGOuvPJK265l9tVXX9nr8V599dV2nqvqly7D9fDDD9vr+eparnruxIkTzX333WdGjhxp/1aFsyuuuMKWIlVfumCyKyU6aNAgc++99wbvrRxCI/KC0Ag0EKExnKac9gLiv/71r3bbK5kxY0abCk8KBqoIkawYpWC44447lqY5+OCD7e1TTz1l34PKiibLkLqRRr23v//97/a+qg1tuummwf9LC43qS9UkNCKmEKu2c845pzAjjarI1V4Nd1VkcqFR1+l9+eWXbTlZV93iscces7daPm456kuBblXYwfWjEJocaVT40+i1Sr+pHKhCo5bhX//6V1tG7/XXX7fTJUuMusom+kLR3kijLvTvqoxVg9CIvCA0Ag1EaAyn8amc6JQpU4L2pPZ23OW89tprbUKcgocLja7t2muvNX379i29TgU/tffs2dP+rdGp9kKjathqlMo9TyOOqkdeS2jcaaedSofI999/f3tbpNDol/Z0/NCo5ajw7kq/ufrvSZqPCt8aXXTP1bJyAVMUPhX+dF8jhgqNGjnWyKPaXnnlFXubLDGnoKlbTafpXbs+R7fcckvwOtK47QChEc2uIaERwEaExnTTpk0L2pzkKFK1NIK0884729KgCqVqSwY70WHqbbfd1uywww42DKrtD3/4g9lmm21syNBz3bQKk6phr/sqObrnnnuaQw891B6OVpteow5377LLLrZ86aOPPhq8JkfPUVlTHd7u06ePbdMo14EHHlhTOM4zjR5rtPfpp58utaWFRq1HQ4cOtYe3VUNebTp0rUPWTz75ZGn90q0qjal/Bb4PP/zQHmLWNGPGjCkbGvUFQCVHk+dbanRSIVF9LVu2zFxwwQWlQ9T/+Mc/gvdVjtsOEBrR7BoSGv3HgKIiNIbTlOMOOSbpnMLkqFGe9OjRI+BGsNB8kiONsREakReERqCBCI3hNJXoUKILjzoPzX8cyCNCI/KC0Ag0EKExnCaNfvyiX1LrcKL/GJBHhEbkBaERaCBCYzgNUDSERuRFamjUISBd/sFvr5VWBJ1wzo4C2Ejrw8KFC6OERv1yU+fExTr3Sj8mUH/1vi5HlyDRDxn0OgmNwEaxQqOuKRljf+3oxz2xtifaluj1xexPP0Ty27PQtklZJ9Z1UPU+Y54+o3O3Y823evcTqaExa8c+rQj6BSI7CmAjrQ+6zlyM0OhG8fz2rGL3p22JMNIItBUrNMZcXyXW/l/qfW++mP25bVOs/vTaYs47d13QGOrdrqeGxlj0Qjk8DbTldhYxQmMeuA0WoRHYKFZoBDparkKju55as9B13aqtOetfPLhausiw31Ykqr6gkl9+e1dBaAynAYqG0Ii8yE1o1PkBqv05b9684LFYah2y7ejQqHNTTjnllKC9q0peNNfRfFPNXr89i2TpsHrFusgyoTGcBigaQiPyIhehUZfXSP6tS27401TjiCOOMPvss4+ZMGGCrdbQr18/GyQU5lRKTBUgVLXh7LPPthUfVLlBz9N14bp162bLUd12223miy++sCem6nmqHKBpVKZKFQNU13Svvfay71XnNKiKg0KPbiuFxjPPPNPst99+5s0337Slwy666CLz3nvvmRNPPNHMnj072gm6zUpfCC655BJbxsvVEta8VGWFv/zlL6XpdCFntanSwzPPPGPns2oHq23y5Ml2mpaWFnP77bfbvp577jnbdscdd9gRS7V9+umntu3uu++2QdVVflAlCE338MMP2woROplZI716bSNHjrTLQycQqw89rlvRc10ViEGDBgXvrRJCYzgNUDSERuRF04fGmTNnBm2i4OjCRbUU/PwV0oXG5DQqHSYq5aU2jXZdeumlZo899jD9+/e3IULtbqRR70n33fN034UP9//0S9RKoVElsQ4++GAbWvfee+82NWf9absqhS6/TVQ+zN1XXVrNKwXyyy67zJbtUoAbPXq0DXgKmloeatNoYPIEYn+kUaXZVAP4wQcftL9gdjVkFSLVrvJh+h/uhGaVEHPPbW+kUf+/1lMoih4aAfyI0Ig8aOrQmLYDfvvtt9vdeZej0OZGLTWKpNFFPzT27du3tBK7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Tnt//PjxbcqH/fnPf7aVG/70pz+V6lm+8cYb9iK7++yzj60Y4ELj73//ezvt2WefbcssaRr15UKdriP3m9/8xlacuPvuu0v/X7VNNe3RRx+dGhonTpxottxyS7PffvvZv1Xeyv0Pf9quor16szH59WbrUWvZunKKGhr1nlXdQ3W3/WmAItE6oHVBJQg78gLiQAxNHxr/9a9/tRsS22tLUyk0um94ChZqV7moXXfdtfTcO+64oxQaFVz17fDkk082Bx10kG0755xzStPuuOOOpVq1V1xxhTn44IPtRYOTZb8qhUYF0aeeesrWN1WZrMmTJ9v2rj7SWC40qnyYuz9//nx7gWfVRR4yZIitBqJSY/p8jRkzxgZ2Be6pU6fatmSJOT80uotD60uClperIfvXv/7VTJgwwbz++uvmsssuM59//rkd8UzWtm0vNGq04LrrrgvaKylaaBR3iFrvW8tRn3dXlx4oCn3m9dnXOqB1QYGxKNsA5FfTh8aZM2cGbVIuTFZSKTS6ad555x3bfu6555pjjjmm1K4Q4kKjQuB2221n9t57b7P//vvbtmRo7Natmx2JFNWm1YijatOOHDmyNE2l0KgAc+mll5o99tjD9O/f34YgtRMa/9ce1lTNWW1gFehU61WjwKNHj7anCMyaNct+xtSmYOfCu/ihUWFw0qRJdgRY3/ZdaFTNWbWr5qz+h/v2ry8S7rnthUb9/1pPodBrLVpoFM3TZHBUrWDVZgaKQp950Tqg7VTRtgHIp6YOjfPmzQvaknT4uJYQpSC4yy672ADYt2/fNqHxpJNOMjNmzLBhUAHwiy++MFtttZX9HypurwDoQuNZZ51l5s6da7beeutSaNSIop6vUatevXqZCy+80Fat6NevnznjjDNs8Ntss83s673mmmsqhkaNmClszp4925xyyiml0LjpppuaoUOHBtN3FZqHOkzjbzgrhcZHH320VHtYI3167gcffGA3ymobNWpU6bm33HJLmw2zQqNuv/rqKxv2yoVGjW5qdDl53qpbJo4+I8m/q1XU0OjerwuPoh0nUBTuc88II/KkqUOjJGvNJrmgEENypLGz6RxHnz8NGic50tgRihoafe79A0XirwdAs2v60CgKjsm/dS6IP009GhkaP/vss4A/DRqH0AgAwI9SQ6N+LBDjshjaIeoQYJbQKDqHUYeVn3zyyeAx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AAC5CI0AAADIRWhExWlrawvKAKe+vt40NjYG5QCA0hAaUVFeffXVoAyd/fDDD+bRRx+1yy+99JL57LPPgm22R2+++abZsmVL4ee6ujrzySefBNtVohtvvNGsXLnSfuXFTTfdFKzfnl111VXmvPPOM+eee665+uqrg/UA+g+hERXjySefNC+88IL5+uuvg3W9cdpppwVlfenbb78NyvrSxx9/bF577TW7PG3aNPPzzz8H2/TEAQccYDZu3BiUx5g0aVJQlpJC8q+//mpqa2vNrFmzzIwZM8w///xj5s+fXwjQpRg9enSfH0N3dFxuuaampuTgePzxx5vjjjuu8PN///1ny4YMGRJs67v11ls7/fzjjz/a515yySXBtimcf/75NjCKwqO/fqBdd911Zo899rDnnytTe+y///7Btr4DDzyw08/qB/VLT/oBGAiERpSl1tZWs2rVqsLP8+bNM5dffrm9WLa0tHTa9osvvii6XC76KzTedddd5uabbzZXXHGFnZ3R8kUXXWRuuOEGM3HixGB7+f33380RRxwRlMvw4cN7HRoVNP2yYh5//PGgrBTV1dXBeSEKjnrcsGFDsM5d5B955BFz//33B+vLgWYYs4Exq1hwnDJlinn33XftsvreX59VrL16Elb80OikDo06h7OBMRsci8046mMrJ5xwguno6DBnn322WbBgQbBNbyj0qT4tqz5/fdYpp5zSKTTKPffcE2zn80OjqF960g/AQCA0ouxodswta3bxoYceCrbJckFR/+Lo+eefL5QffPDB5quvvgq21wu8HufMmWMvCnrel19+aT788ENbvmbNGvuod/0q17IuGtkZSoXao446yn5+btGiRd1eoBUa//jjD7NixYpC2fXXX29/7/Tp0+2FftmyZeb000+363TMfh29oTDhgoaCo78+yw+NOmbXDkOHDrWhUe31+uuv24vyxRdfbNdde+21hc+W6ljc87u62PkXUD80aiZPj2rXrVu3Bs/vztq1a+3js88+a2/hqu7169fbep555hm7rlgo9EPjK6+8Yo4++mhb9sYbb3QKJqrTHUOxNtp3330L22q5oaHBbu/aRv3s//48v/32W1Dme/rppzv9rHPpmmuuscHRnZNjxoyxjzr/NAPmtu1JaHT7kB0LqkPt+9hjjxXOB/FDoxtnOk/mzp0b/K7u6Pf6YdGXfVPpfo/Kjj322EJoVB9qhripqcmceOKJdju/n/3f7agfVZ8LocX62S33JDSqDXR+z54925x66qm2zIVGvY64kFssNPqvF9l1QH8iNKKs6EXVL9OtRr8sS6FRF7IRI0bY2QlXPn78+GBbyYZGzcppWeEpO0up4KrbTgoi+lkXDf/zcU899ZR58MEHbTD79NNPg9/jvPzyy2bHHXfsVHb44YfbOnUr6pZbbrFl2hddGHTR8+voCQVF3brUjKxm3rSsNtBjVzOGfmj86aefCsvu9rT2XfsqCspap9DotlN4cMv+xc7xL6B+aFy8eLF9nDlzZvDcnrr99tvNwoULjd44KCgoJE2ePLmwzt8+GxofeOABGybcLNovv/xSCPGSDY3F2sgPEwqNardsP/u/vyfUd36ZU1VVFdx6V6BwwSlFaFyyZEkwFlwbaRZ3zz33LGybDY0K8tnzprtw1hX3OcZiit2mdm9iFJq1XiFst912K7ShxqEe/X7W4/Llywv76o5j2LBh9lEBXPUV62e33JPQqOCq1zL1xz777GPLsjON7s1isdBY7PUCGAiERpSVTZs2BWWa5fLLsrq6JZ2dsczKC40XXHCBfdQtTQVDLesF+/vvvw/q0kXbD0A+Nyul3+subAq3mr3RxVUBz217xhlnFC5ksSZMmFBYfuutt4L1WX5o1IXNfQZSF1xdKE8++eTCjJ3bt2xozB7/IYccYmdNFX6zv8e/gF555ZWdfpYzzzzTXHrppUF5Hv2ltNp17Nixtj3/+usve6t+3bp1hRlXfbzBf54u3nqejl/7nA0TCgDuPJFsaCzWRgpPCms6bpUpNOojAe5NjJsNjVHsNrQCo18mbhZK++JCowJHc3Ozue222zqFxmL1KMyorL293f6sMaLH7Fg455xzzObNm21bZWey9aZNs3LuZ503btk/H3pK7ecHxuy5l5X9VoWDDjoomGk86aST7Dq/n/16HBcaFUJVn47B9bP+IE/97LYdNWqUeeeddwrtJm4W2JWpPVSH/mDL1e1Co8ahu8Mhfj909XoB9DdCI8qO3nEr7HzzzTf2tmU5f31K3q3z3tBFz5/NjKGLolsu9XNd/cldVP3yntCMmD4moFnDP//809x77722vNjHE1KK+dxnDH22UX85rUCc95GD7Q1/PQ2UD0IjypJmhhQcszMX5USzkvo8pGYh/HUx9FmlkSNHBuUx9Lk+t6yvnfHXlxvto4599erVwbrecoHqiSeesI9d/RFJKin/wjyPZvrcjO9gM3Xq1MIbAQADh9AIAACAXIRGAAAA5NpBt/8AAACA7uygv8gCAAAAuvM/pETz8zrOeL0AAAAASUVORK5CYII=>

[image2]: <data:image/png;base64,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0ggAMBFIIwC0DNIIADARSCMAtAzSCAAwEUgjALQM0ggAMBFIIwC0DNIIADARSCMAtAzSCAAwEUgjALQM0ggAMBFIIwC0DNIIADARSCMAtAzSCAAwEUgjALQM0ggAMBFIIwC0DNIIADARSCMAtAzSCAAwEUgjALQM0ggAMBFIIwC0DNIIADARSCMAtAzSCAAwEUgjALQM0ggAMBFIIwC0DNIIADARSCMAtAzSCAAwEUgjALQM0ggAMBFIIwC0DNIIADARSCMAtAzSCAAwEUgjALQM0ggAMBFIIwC0DNIIADARSCMAtAzSCAAwEUgjALQM0ggAMBFIIwC0DNIIADARSCMAtAzSCAAwEUgjALQM0ggAMBFIIwC0DNIIADARSCMAtAzSCAAwEUgjALQM0ggAMBFIIwC0DNIIADARSCMAtAzSCAAwEUgjALQM0ggAMBFIIwC0DNIIADARSCMAtAzSCAAwEUgjALQM0ggAMBFIIwC0DNIIADARSCMAtAzSCAAwEUgjALQM0ggAMBFIIwC0DNIIADARSCMAtAzSCAAwEUgjALQM0ggAMBFIIwC0DNIIADARSCMAtAzSCAAwEUgjALQM0ggAMBFIIwC0DNIIADARSCMAtAzSCAAwEUgjALQM0ggAMBFIIwC0DNIIADARSCMAtAzSCAAwEUgjALQM0ggAMBFIIwC0DNIIADARSCMAtAzSCAAwEUgjALQM0ggAMBFIIwC0DNIIADARSCMAtAzSCAAwEUgjALQM0ggAMBFIIwC0DNIIADARSCMAtAzSCAAwEUgjALQM0ggAMBFIIwC0DNIIADARSCMAtAzSCAAwEUgjALQM0ggAMBFIIwC0DNIIADARSCMAtAzSCAAwEUgjALQM0ggAMBFIIwC0DNIIADARSCMAtAzSCAAwEUgjALQM0ggAMBFIYz2+efts9sU3E7L5+cbH8qe3HZBGAICJQBrH5/HvnDwQf+n3ZrNv3zWbPXI3IZubb39uNvu7t578zP799/OnefNBGgEAJgJpHJevvPcHIzf54EzIJkefWX12WwNpBACYCKRxXHTQ/cpfLB+QCWkh9//JyT98WgJpBACYCKRxPB69/6Q06lrGfDAmpIU8/MmTn2FdYtEKSCMAwEQgjeNx4obZ7KG/Wj4QE9JSJI36LLcC0ggAMBFI43gwyki2Ib6juhWQRgCAiUAax2NX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>