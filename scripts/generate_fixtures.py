import os
import json
import math
from datetime import datetime, timezone, timedelta

os.makedirs('data/fixtures', exist_ok=True)
os.makedirs('data/graphs', exist_ok=True)
os.makedirs('data/models', exist_ok=True)

# 1. Load Gazetteer & Create Segments
with open('data/gazetteer.json', 'r', encoding='utf-8') as f:
    gaz = json.load(f)

nh10_nodes = [g for g in gaz if g['corridor'] == 'NH-10'][:25]
nh6_nodes = [g for g in gaz if g['corridor'] == 'NH-6'][:25]

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000 # meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi/2.0)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(delta_lambda/2.0)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

segments = []

# NH-10 Segments (Siliguri to Gangtok along Teesta River valley)
for i in range(len(nh10_nodes) - 1):
    u = nh10_nodes[i]
    v = nh10_nodes[i+1]
    dist_m = haversine(u['lat'], u['lon'], v['lat'], v['lon'])
    is_deep_hills = i >= 5
    slope = 14.5 + (i % 6) * 3.2 if is_deep_hills else 2.1 + (i % 3) * 1.5
    river_prox = 35.0 + (i % 5) * 40.0 if is_deep_hills else 450.0
    landslide_zone = is_deep_hills and (i in [6, 7, 8, 9, 10, 11, 14, 15, 16, 17, 18, 20])
    speed_kmh = 30.0 if is_deep_hills else 55.0
    base_time_sec = int((dist_m / 1000.0) / speed_kmh * 3600)
    
    seg_id = f"seg_nh10_{i+1:03d}"
    segments.append({
        "id": seg_id,
        "edge_id": f"nh10_e_{i+1:03d}",
        "corridor": "NH-10",
        "road_name": "NH-10",
        "name": f"{u['name']} to {v['name']}",
        "start_node": u['name'],
        "end_node": v['name'],
        "start_lat": u['lat'],
        "start_lon": u['lon'],
        "end_lat": v['lat'],
        "end_lon": v['lon'],
        "geometry": {
            "type": "LineString",
            "coordinates": [
                [u['lon'], u['lat']],
                [(u['lon'] + v['lon'])/2 + 0.001 * math.sin(i), (u['lat'] + v['lat'])/2 + 0.001 * math.cos(i)],
                [v['lon'], v['lat']]
            ]
        },
        "length_m": round(dist_m, 1),
        "base_travel_time_sec": max(base_time_sec, 60),
        "slope_deg": round(slope, 1),
        "river_proximity_m": round(river_prox, 1),
        "landslide_zone": bool(landslide_zone),
        "historical_incident_count": 12 if landslide_zone else 2,
        "road_class": "national_highway"
    })

# NH-6 / NH-27 Segments (Guwahati to Shillong)
for i in range(len(nh6_nodes) - 1):
    u = nh6_nodes[i]
    v = nh6_nodes[i+1]
    dist_m = haversine(u['lat'], u['lon'], v['lat'], v['lon'])
    is_hills = i >= 6
    slope = 9.8 + (i % 5) * 2.5 if is_hills else 1.5
    river_prox = 120.0 + (i % 7) * 80.0
    flood_zone = (i in [3, 4, 5, 8, 9])
    landslide_zone = is_hills and (i in [12, 13, 17, 18, 22])
    speed_kmh = 45.0 if is_hills else 65.0
    base_time_sec = int((dist_m / 1000.0) / speed_kmh * 3600)
    
    seg_id = f"seg_nh6_{i+1:03d}"
    segments.append({
        "id": seg_id,
        "edge_id": f"nh6_e_{i+1:03d}",
        "corridor": "NH-6",
        "road_name": "NH-6",
        "name": f"{u['name']} to {v['name']}",
        "start_node": u['name'],
        "end_node": v['name'],
        "start_lat": u['lat'],
        "start_lon": u['lon'],
        "end_lat": v['lat'],
        "end_lon": v['lon'],
        "geometry": {
            "type": "LineString",
            "coordinates": [
                [u['lon'], u['lat']],
                [(u['lon'] + v['lon'])/2 + 0.0008 * math.sin(i), (u['lat'] + v['lat'])/2 + 0.0008 * math.cos(i)],
                [v['lon'], v['lat']]
            ]
        },
        "length_m": round(dist_m, 1),
        "base_travel_time_sec": max(base_time_sec, 60),
        "slope_deg": round(slope, 1),
        "river_proximity_m": round(river_prox, 1),
        "landslide_zone": bool(landslide_zone or flood_zone),
        "historical_incident_count": 15 if flood_zone else (8 if landslide_zone else 1),
        "road_class": "national_highway"
    })

with open('data/corridors.json', 'w', encoding='utf-8') as f:
    json.dump(segments, f, indent=2)

print(f"Generated {len(segments)} segments in data/corridors.json")

# 2. Generate 12 Realistic Advisories for Offline Fixture Mode
now = datetime.now(timezone.utc)
advisories = [
    {
        "id": "adv_001",
        "url": "https://sikkimexpress.com/news/nh10-massive-landslide-at-29th-mile-traffic-halted",
        "title": "Massive landslide halts traffic on NH-10 near 29th Mile",
        "corridor": "NH-10",
        "published_at": (now - timedelta(hours=2)).isoformat(),
        "text": "Vehicular movement between Siliguri and Gangtok on National Highway 10 has been completely suspended following a massive landslide at 29th Mile early Tuesday morning. Heavy boulders and mud debris have covered a 120-meter stretch of the highway near Teesta Bazar. District authorities and PWD machines are on site clearing debris, but continuous rockfall is hampering restoration operations.",
        "expected_event": {
            "event_type": "landslide",
            "status": "blocked",
            "road": "NH-10",
            "location_text": "29th Mile near Teesta Bazar",
            "severity": 5,
            "evidence_quote": "completely suspended following a massive landslide at 29th Mile early Tuesday morning"
        }
    },
    {
        "id": "adv_002",
        "url": "https://eastmojo.com/sikkim/kalijhora-settlement-subsidence-single-lane-advisory",
        "title": "Subsidence near Kalijhora restricts NH-10 to single-lane movement",
        "corridor": "NH-10",
        "published_at": (now - timedelta(hours=5)).isoformat(),
        "text": "The Kalimpong District Administration has issued a travel advisory restricting traffic to single-lane movement near Kalijhora Dam due to road subsidence caused by rising water levels in the Teesta River. Light motor vehicles are permitted with caution, while heavy trucks are being diverted via Coronation Bridge and Gorubathan route.",
        "expected_event": {
            "event_type": "road_closed",
            "status": "partially_open",
            "road": "NH-10",
            "location_text": "Kalijhora Dam",
            "severity": 3,
            "evidence_quote": "restricting traffic to single-lane movement near Kalijhora Dam due to road subsidence"
        }
    },
    {
        "id": "adv_003",
        "url": "https://morungexpress.com/assam-meghalaya-jorabat-flooded-traffic-crawls",
        "title": "Incessant downpour triggers severe waterlogging at Jorabat on NH-6",
        "corridor": "NH-6",
        "published_at": (now - timedelta(hours=3)).isoformat(),
        "text": "Incessant monsoon rains across the Khasi Hills foothills caused severe waterlogging on the Guwahati-Shillong corridor at Jorabat junction on NH-6. Water levels exceeded two feet along the tri-junction, leaving hundreds of trucks and passenger vehicles stranded in knee-deep water. Traffic police are advising drivers to exercise extreme caution.",
        "expected_event": {
            "event_type": "waterlogging",
            "status": "partially_open",
            "road": "NH-6",
            "location_text": "Jorabat Traffic Junction",
            "severity": 4,
            "evidence_quote": "severe waterlogging on the Guwahati-Shillong corridor at Jorabat junction on NH-6"
        }
    },
    {
        "id": "adv_004",
        "url": "https://themeghalayan.com/shillong-umiam-bridge-repair-traffic-diversion",
        "title": "Umiam Bridge structural inspection causes slow-moving traffic on NH-6",
        "corridor": "NH-6",
        "published_at": (now - timedelta(hours=7)).isoformat(),
        "text": "Commuters traveling between Guwahati and Shillong experienced significant delays near Barapani Bridge on NH-6 today as MeECL engineers conducted non-destructive structural vibration testing on the Umiam Dam spillway bridge. One-way traffic regulation is in effect until evening.",
        "expected_event": {
            "event_type": "bridge_damage",
            "status": "partially_open",
            "road": "NH-6",
            "location_text": "Barapani Bridge Causeway",
            "severity": 2,
            "evidence_quote": "One-way traffic regulation is in effect until evening near Barapani Bridge on NH-6"
        }
    },
    {
        "id": "adv_005",
        "url": "https://sikkimchronicle.com/burdang-restoration-nh10-reopened",
        "title": "Road cleared at Burdang: Normal traffic resumes on Singtam-Rangpo stretch",
        "corridor": "NH-10",
        "published_at": (now - timedelta(hours=1)).isoformat(),
        "text": "Border Roads Organisation (BRO) Project Swastik has successfully cleared debris at Burdang near Singtam following yesterday's mudslide. NH-10 is now restored for regular two-way movement between Rangpo and Singtam. Drivers are advised to observe speed limits.",
        "expected_event": {
            "event_type": "restored",
            "status": "open",
            "road": "NH-10",
            "location_text": "Burdang Landslide Stretch",
            "severity": 1,
            "evidence_quote": "NH-10 is now restored for regular two-way movement between Rangpo and Singtam"
        }
    },
    {
        "id": "adv_006",
        "url": "https://hubnetwork.in/umsning-bypass-accident-cleared",
        "title": "Overturned freight trailer cleared on Umsning Expressway Bypass",
        "corridor": "NH-6",
        "published_at": (now - timedelta(hours=4)).isoformat(),
        "text": "A container truck that overturned near Umsning Expressway Bypass on NH-6 early morning has been removed using heavy cranes. Traffic flow toward Shillong is now moving normally.",
        "expected_event": {
            "event_type": "accident",
            "status": "open",
            "road": "NH-6",
            "location_text": "Umsning Expressway Bypass Entry",
            "severity": 1,
            "evidence_quote": "container truck that overturned near Umsning Expressway Bypass on NH-6 has been removed"
        }
    },
    {
        "id": "adv_007",
        "url": "https://telegraphindia.com/north-east/seti-jhora-flash-mudflow-alert-nh10",
        "title": "Flash mudflow at Seti Jhora prompts safety advisory on NH-10",
        "corridor": "NH-10",
        "published_at": (now - timedelta(hours=6)).isoformat(),
        "text": "High intensity rainfall in the Kalimpong hills led to an unexpected flash mudflow over Seti Jhora bridge on NH-10. Boulders and slush on the carriageway caused minor vehicle damage. Police have halted heavy commercial vehicles at Sevoke.",
        "expected_event": {
            "event_type": "landslide",
            "status": "partially_open",
            "road": "NH-10",
            "location_text": "Seti Jhora Fall",
            "severity": 4,
            "evidence_quote": "flash mudflow over Seti Jhora bridge on NH-10 caused heavy vehicles halt"
        }
    },
    {
        "id": "adv_008",
        "url": "https://sentinelassam.com/byrnihat-flash-flood-road-inundated",
        "title": "Byrnihat tax gate flooded as Umtru river overflows its banks",
        "corridor": "NH-6",
        "published_at": (now - timedelta(hours=8)).isoformat(),
        "text": "Water from the swelling Umtru River has inundated a 300-meter section of NH-6 near Byrnihat Commercial Checkpost. Passenger cabs and two-wheelers are advised not to cross the flooded section until water recedes.",
        "expected_event": {
            "event_type": "flood",
            "status": "blocked",
            "road": "NH-6",
            "location_text": "Byrnihat Commercial Checkpost",
            "severity": 4,
            "evidence_quote": "swelling Umtru River has inundated a 300-meter section of NH-6 near Byrnihat"
        }
    },
    {
        "id": "adv_009",
        "url": "https://voiceofsikkim.com/melli-dara-rockfall-single-lane",
        "title": "Intermittent shooting stones at Melli Dara: Travelers urged to remain alert",
        "corridor": "NH-10",
        "published_at": (now - timedelta(hours=10)).isoformat(),
        "text": "Sikkim Police have issued an urgent travel warning for motorists traveling past Melli Dara Bridge along NH-10. Active shooting stones and loose rocks continue to fall from overhead hill cuttings.",
        "expected_event": {
            "event_type": "landslide",
            "status": "partially_open",
            "road": "NH-10",
            "location_text": "Melli Dara Hill",
            "severity": 3,
            "evidence_quote": "Active shooting stones and loose rocks continue to fall from overhead hill cuttings at Melli Dara"
        }
    },
    {
        "id": "adv_010",
        "url": "https://shillongtimes.com/mawlai-bypass-landslip-clearing-underway",
        "title": "Minor landslip near Mawlai Phudmuri on Shillong entry corridor",
        "corridor": "NH-6",
        "published_at": (now - timedelta(hours=11)).isoformat(),
        "text": "Heavy morning showers triggered a minor landslip near Mawlai Phudmuri Chowk on NH-6. Mud debris partially blocked the inbound lane towards Shillong city. District authorities cleared the road within 90 minutes.",
        "expected_event": {
            "event_type": "landslide",
            "status": "open",
            "road": "NH-6",
            "location_text": "Mawlai Phudmuri Chowk",
            "severity": 2,
            "evidence_quote": "District authorities cleared the road within 90 minutes after minor landslip at Mawlai"
        }
    },
    {
        "id": "adv_011",
        "url": "https://sikkimexpress.com/teesta-bazar-submerged-nh10-cut-off",
        "title": "Teesta River crosses danger mark: NH-10 at Teesta Bazar submerged",
        "corridor": "NH-10",
        "published_at": (now - timedelta(hours=14)).isoformat(),
        "text": "Following torrential rainfall in North Sikkim, the Teesta River has breached embankments at Teesta Bazar. Low-lying sections of NH-10 near the suspension bridge are under water. All traffic between Siliguri and Gangtok is diverted via Lava, Algarah and Reshi.",
        "expected_event": {
            "event_type": "flood",
            "status": "blocked",
            "road": "NH-10",
            "location_text": "Teesta Bazar",
            "severity": 5,
            "evidence_quote": "Teesta River has breached embankments at Teesta Bazar, low-lying sections of NH-10 under water"
        }
    },
    {
        "id": "adv_012",
        "url": "https://guwahatitimes.com/nongpoh-culvert-subsidence-caution-nh6",
        "title": "Culvert subsidence near Nongpoh: Heavy vehicles speed restricted on NH-6",
        "corridor": "NH-6",
        "published_at": (now - timedelta(hours=18)).isoformat(),
        "text": "NHAI engineers have detected foundation subsidence at a major culvert near Nongpoh Main Town on NH-6. Speed limits of 20 km/h have been posted for heavy transport vehicles while repair work proceeds.",
        "expected_event": {
            "event_type": "road_closed",
            "status": "partially_open",
            "road": "NH-6",
            "location_text": "Nongpoh Main Town",
            "severity": 2,
            "evidence_quote": "foundation subsidence at a major culvert near Nongpoh Main Town on NH-6"
        }
    }
]

with open('data/fixtures/advisories.json', 'w', encoding='utf-8') as f:
    json.dump(advisories, f, indent=2)

print(f"Generated {len(advisories)} advisories in data/fixtures/advisories.json")

# 3. Weather Fixtures (Open-Meteo format)
weather_fixture = {
    "NH-10": {
        "location": "Siliguri - Gangtok Corridor",
        "latitude": 27.05,
        "longitude": 88.45,
        "current": {
            "temperature_2m": 19.4,
            "relative_humidity_2m": 92,
            "precipitation": 14.8,
            "rain": 14.8,
            "weather_code": 65
        },
        "hourly": {
            "precipitation_past_24h_mm": 68.5,
            "precipitation_forecast_24h_mm": 84.2,
            "max_rain_intensity_mmh": 18.0
        }
    },
    "NH-6": {
        "location": "Guwahati - Shillong Corridor",
        "latitude": 25.85,
        "longitude": 91.88,
        "current": {
            "temperature_2m": 22.1,
            "relative_humidity_2m": 88,
            "precipitation": 8.2,
            "rain": 8.2,
            "weather_code": 63
        },
        "hourly": {
            "precipitation_past_24h_mm": 42.0,
            "precipitation_forecast_24h_mm": 51.5,
            "max_rain_intensity_mmh": 12.5
        }
    }
}

with open('data/fixtures/weather.json', 'w', encoding='utf-8') as f:
    json.dump(weather_fixture, f, indent=2)

# 4. TinyFish Search and Fetch fixtures
tinyfish_fixture = {
    "search": {
        "NH-10 landslide road blocked Sikkim": [
            {
                "title": adv["title"],
                "url": adv["url"],
                "snippet": adv["text"][:220] + "..."
            }
            for adv in advisories if adv["corridor"] == "NH-10"
        ],
        "Guwahati Shillong NH6 waterlogging": [
            {
                "title": adv["title"],
                "url": adv["url"],
                "snippet": adv["text"][:220] + "..."
            }
            for adv in advisories if adv["corridor"] == "NH-6"
        ]
    },
    "fetch": {
        adv["url"]: {
            "url": adv["url"],
            "status": 200,
            "content": f"# {adv['title']}\n\n**Published**: {adv['published_at']}\n\n{adv['text']}"
        }
        for adv in advisories
    }
}

with open('data/fixtures/tinyfish_responses.json', 'w', encoding='utf-8') as f:
    json.dump(tinyfish_fixture, f, indent=2)

print("Generated weather and TinyFish fixtures successfully.")
