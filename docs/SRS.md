
- **Frontend:** Flet (Python framework for cross-platform UI)  
- **Backend:** Python (API handling, AI logic, routing)  
- **Database:** MySQL (user accounts, itineraries, preferences)  
- **External Services:** Google Places API, Google Reviews API, TripAdvisor API  

---

## 🔍 Functional Requirements (Summary)

| ID | Function | Description |
|----|-----------|-------------|
| FR-001 | User Registration & Login | Supports Google, email, and guest login modes |
| FR-003 | AI-Based Travel Recommendation | Generates personalized suggestions |
| FR-004 | Location-Based Search | Uses geolocation to find nearby attractions |
| FR-005 | Travel Itinerary Generation | Builds itineraries using AI and user input |
| FR-006 | Travel Plan Editing | Enables users to save and edit itineraries |
| FR-007 | Maps & Routing Display | Provides route visualization using Google APIs |
| FR-008 | Destination Details | Shows information, photos, and reviews |
| FR-009 | Favorites & Saved Locations | Stores favorite destinations in profile |
| FR-010 | API Integration | Connects to Google Maps/Places and TripAdvisor APIs |

---

## ⚡ Non-Functional Requirements (Summary)

| Category | Description |
|-----------|-------------|
| **Performance** | Load search results within 5 seconds on stable internet |
| **Usability** | Simple, intuitive interface accessible to all users |
| **Security** | All transactions encrypted; credentials securely stored |
| **Reliability** | 99% uptime for core features |
| **Compatibility** | Android 10+ and iOS 15+ support |
| **Privacy** | Complies with Data Privacy Act of 2012 (RA 10173) |
| **Maintainability** | Code structured for easy updates and feature expansion |

---

## 🧩 Tech Stack

| Component | Technology |
|------------|-------------|
| **Frontend Framework** | Flet (Python) |
| **Backend** | Python |
| **Database** | MySQL |
| **APIs Used** | Google Places API, Google Reviews API, TripAdvisor API |
| **AI Integration** | Custom Python-based recommendation logic |
| **Platform** | Mobile (Android/iOS) and Web-compatible |

---

## 💡 Feasibility of APIs (Free Tiers)

| API | Free Tier Availability | Notes |
|------|-----------------------|-------|
| **Google Places API** | ✅ Yes – $200/month free usage credit | Sufficient for student projects and prototypes |
| **Google Reviews API** | ⚠️ Part of Google Places API | Review data can be accessed through Places endpoints |
| **TripAdvisor API** | ⚠️ Limited Access | Requires registration and approval; demo endpoints available |
| **OpenAI API (Optional)** | ✅ Yes (Free trial + pay-as-you-go) | Can enhance AI recommendations if integrated |

> 🔎 **Verdict:** All required APIs are **feasible for student or prototype use** with free tiers or limited trial usage.

---

## 🧑‍💻 Development Team
**Team LOCaiT**

| Role | Name |
| Project Manager | *(Sean Xander B. Aquino)* |
| Database Engineer | *(Lawrence Atienza)* |
| UI/UX Designer | *(Mark Joseph C. Orias)* |

---

## 🔒 Privacy & Compliance
Lakb.ai adheres to the **Data Privacy Act of 2012 (RA 10173)** and ensures that:
- Users provide consent before accessing GPS and personal data.  
- Sensitive data such as credentials and tokens are stored securely.  
- All communications between the client and server are encrypted (HTTPS).

---

## 🧱 Future Enhancements
- Integration with **OpenWeatherMap API** for weather-based itinerary adjustments.  
- Addition of **social sharing** and **community features** for travelers.  
- **Offline itinerary caching** for low-connectivity areas.  
- Enhanced **AI explainability** using recommendation transparency tools.

---

## 📄 References
A full list of references is maintained in the SRS, including:
- ISO/IEC/IEEE 29148:2018 – Requirements Engineering  
- Google Maps / Places API Documentation  
- TripAdvisor Developer Portal  
- OpenAI API Documentation  
- Data Privacy Act of 2012  
- OWASP Top 10 Mobile Application Security Risks (2023)

---

## 🧾 License
This project is developed as part of **CCCS 106 – Application Development and Emerging Technologies**.  
All rights reserved © 2025 **Team LOCaiT**.

---

