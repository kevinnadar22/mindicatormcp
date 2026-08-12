"""Static table category and description catalog."""

TABLE_CATALOG: dict[str, tuple[str, str]] = {
    "stations": ("rail", "Station master list (name, optional lat/lon)"),
    "lines": ("rail", "Suburban corridors (code, direction labels, counts)"),
    "line_stations": ("rail", "Ordered stations on each line"),
    "trains": ("rail", "Train catalog per line"),
    "stop_times": ("rail", "Timetable stops; filter by station_name / time_min"),
    "transfer_paths": ("rail", "From→to path hints (path_desc)"),
    "ticket_fare_routes": ("rail", "Fare route code registry"),
    "ticket_fares": ("rail", "OD ticket fares (fare_1…fare_16 ticket classes)"),
    "bus_agencies": ("bus", "Bus agency summary counts"),
    "bus_stops": ("bus", "Bus stops by agency/area"),
    "bus_routes": ("bus", "Bus routes by agency/code"),
    "bus_route_stops": ("bus", "Ordered stops on each bus route"),
    "auto_fares": ("fares", "Auto rickshaw km tariff (day/night)"),
    "taxi_fares": ("fares", "Black/yellow taxi km tariff"),
    "coolcab_fares": ("fares", "Coolcab km tariff"),
    "auto_complaints": ("fares", "Auto complaint contacts"),
    "ferry_services": ("ferry", "Jetty schedules, frequency, fare"),
    "emergency_contacts": ("emergency", "Emergency numbers by category"),
    "penalties": ("emergency", "Traffic/rail offence fines"),
    "meta": ("config", "Dataset key/value (city, version, tariff notes)"),
    "config_facilities": ("config", "Facility labels"),
    "config_other": ("config", "Misc UI headers"),
    "config_bus_agencies": ("config", "Agency selection flags"),
}


def get_entry(table_name: str) -> tuple[str, str]:
    """Return (category, description) for a table name."""
    return TABLE_CATALOG.get(table_name, ("other", "Mindicator table"))
