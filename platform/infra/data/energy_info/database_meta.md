# Metadata of the Smart Campus Database

This metadata describes the schema and semantics of the Smart Campus database with a focus on energy management, used for simulation of user-agent interactions, system testing, and query generation.

---

## User Roles (`roles`)
Defines role-based access and functionality in the system.
- `Student`: Access to personal room data, bookings, comfort preferences, and feedback submission.
- `Staff`: Can manage events, submit maintenance requests, monitor departmental zones.
- `Admin`: Full access to dashboards, override controls, HVAC actions, and energy analytics.

---

## Spatial Hierarchy and Infrastructure

### `Building`
Describes individual buildings on campus.
- Includes `building_type`: `Academic`, `Residential`, `Administrative`

### `HVACZone`
HVAC zones within buildings for heating, ventilation, and air-conditioning control

### `Room`
Represents rooms inside buildings with:
- `room_type`: `Lecture`, `Lab`, `Office`, `Common`
- `equipment`: Assets (e.g., HVAC, lights, projectors)
- `zone_id`: Reference to the HVAC zone

---

## Assets and Maintenance

### `Asset`
Physical equipment in rooms, such as:
- `asset_type`: `Heating`, `Ventilation`, `AirConditioning`, `Lights`, `Projector`
- Lifecycle metadata: model, status, last maintenance

### `MaintenanceSchedule`
Pre-planned maintenance tasks per asset:
- `task_type`: `Inspect`, `Repair`, `Replace`
- Tracks `due_date`, `status`, and whether auto-generated

### `WorkOrder`
Reactive or urgent maintenance requests.
- `priority`: `Low`, `Med`, `High`
- `status`: `Open`, `Assigned`, `InProgress`, `Done`
- Tracks `raised_by`, assigned staff, timestamps

---

## Events and Bookings

### `Event`
Campus activities scheduled in rooms:
- Includes organizer, participant list, type, budget, and room assignment

### `Booking`
User-initiated reservations:
- May reference an `event_id`
- Tracks `schedule`, `purpose`, and creation time

### `Timetable`
Institution-wide schedule map of room usage.

---

## Sensor and Environment Data

### `SensorReading`
Time-series data by room and sensor:
- `sensor_type`: `Temperature`, `Humidity`, `Co2`, `Light`, `Occupancy`, `Power`, `Noise`
- Supports trend analysis and live monitoring

### `RoomStatus`
Derived summary for comfort & environment control:
- Combines latest sensor values and preferences
- Fields: `current_temperature`, `desired_temperature`, `occupants`, `last_entry`

---

## System Agent Actions

### `HVAC_Action`
Logged actions taken on HVAC systems:
- `zone_id`, `setpoint_temperature`, `ventilation_mode`, `co2_control_enabled`
- Captures `reason` and `agent_id` who issued the change

### `Light_Action`
Control log of lighting in rooms:
- `status`: on/off
- `brightness`: dimming level
- Includes `reason` and responsible `agent_id`

---

## Energy Usage and Reporting

### `EnergyUsage`
Zone-level aggregate of energy usage over time:
- Metrics: `total_energy_kwh`, `hvac_energy_kwh`, `lighting_energy_kwh`
- Linked to `HVACZone`

---

*Last updated: July 2025*