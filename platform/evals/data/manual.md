# System Manual for Smart Campus Energy Management System

## 1. System Overview and Capabilities

The Smart Campus Energy Management System is a multi-agent, conversational platform designed to optimize energy consumption across campus facilities. It integrates real-time monitoring, data analytics, and conversational AI to empower students, staff, and administrators with actionable insights and controls.

**Core Capabilities:**
- Real-time monitoring of energy usage across buildings and zones
- Historical data logging, analysis, and pattern detection
- Dynamic decision-making for energy optimization
- Conversational agents tailored for different user roles
- Feedback-based learning and system adaptation

---

## 2. User Roles and Access Levels

| Role       | Permissions                                                                 |
|------------|-------------------------------------------------------------------------------|
| Student    | View room-level energy data, submit feedback, access FAQs and suggestions    |
| Staff      | Access department-level usage, request system actions, view HVAC zones       |
| Admin      | Full dashboard access, approve overrides, manage settings and automations    |

---

## 3. Interfaces and Access Channels

Users can interact with the system via:

- 🌐 **Web Dashboard** - Streamlit frontend
- 💬 **Conversational Agents** — General Campus Information, Feedback Collector, Prognostics, Dashboard, Plotter, Actor

---

## 4. Data Sources and Sensor Integration

The system integrates with various IoT devices and digital infrastructure:

- Smart meters for electricity, HVAC, and lighting
- Occupancy sensors and smart thermostats
- Class timetable system (for future automation)
- Historical energy usage logs
- User feedback and interaction logs

---

## 5. Supported System Features and Automation

- Adaptive control of HVAC based on occupancy and patterns
- Automated alerts for abnormal usage spikes
- Peak demand load shifting and suggestions
- Scheduled reports for departments and facility teams
- Feedback-based tuning of default settings
- Admin-initiated energy-saving protocols

---

## 6. Conversational System Services

1. Personalized chatbot interfaces for:
   - Students
   - Staff
   - Admins
2. Role-based authentication and authorization
3. Access to general campus info: buildings, rooms, HVAC zones
4. Information retrieval about energy policies, initiatives, and protocols
5. Feedback collection from students and staff
6. Prognostics and suggestions tailored to users' roles
7. Role-specific data visualizations and plots
8. Energy monitoring and admin control dashboards
9. Safe execution of system override and change actions (admins only)

---

## 7. Known Limitations

- No integration with electric vehicle (EV) charging stations (yet)
- Manual override requests require admin review and approval
- No support for building-level water or gas monitoring

---

## 8. Feedback and Learning Loops

- Users can submit feedback anytime via chatbot
- Suggestions and complaints are reviewed weekly
- Repeated suggestions may result in new policy or system updates
- The system logs preferences to improve future automation

---

*Last updated: July 2025*