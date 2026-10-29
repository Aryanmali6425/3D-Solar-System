"""
planet_facts.py
Static educational data shown in the click-to-inspect info panel.
Numbers are real (rounded); visual sizes/orbits in the scene itself remain
artistically scaled (see README "Scope").
"""

PLANET_FACTS = {
    "Sun": {
        "type": "Star (G-type main-sequence)",
        "moons": 0,
        "day_length": "~27 Earth days (equatorial rotation)",
        "year_length": "N/A",
        "diameter_km": "1,392,700 km",
        "distance_from_sun": "0 (center of the system)",
        "fun_facts": [
            "Contains about 99.8% of the Solar System's total mass.",
            "Core temperature reaches roughly 15 million degrees Celsius.",
            "Light from the Sun takes about 8 minutes 20 seconds to reach Earth.",
            "In about 5 billion years it will swell into a red giant.",
        ],
        "future_note": "In the far future the Sun swells into a red giant; the +100y preview "
                        "here is a stylized foreshadowing (subtle reddening/growth), not a "
                        "physical prediction on a 100-year timescale.",
    },
    "Mercury": {
        "type": "Terrestrial planet",
        "moons": 0,
        "day_length": "58.6 Earth days",
        "year_length": "88 Earth days",
        "diameter_km": "4,879 km",
        "distance_from_sun": "57.9 million km",
        "fun_facts": [
            "Smallest planet in the Solar System.",
            "Surface temperatures swing from -180C at night to 430C in daylight.",
            "Has no atmosphere to retain heat or block impacts.",
        ],
        "future_note": "Airless and geologically quiet — a 100-year window shows "
                        "essentially no visible change beyond micrometeorite dust drift.",
    },
    "Venus": {
        "type": "Terrestrial planet",
        "moons": 0,
        "day_length": "243 Earth days (retrograde)",
        "year_length": "225 Earth days",
        "diameter_km": "12,104 km",
        "distance_from_sun": "108.2 million km",
        "fun_facts": [
            "Hottest planet in the Solar System due to a runaway greenhouse effect.",
            "Rotates backwards compared to most planets.",
            "A day on Venus is longer than its year.",
        ],
        "future_note": "Thick sulfuric-acid cloud cover is stylized to churn slightly "
                        "faster in the +100y view to suggest an intensifying greenhouse state.",
    },
    "Earth": {
        "type": "Terrestrial planet",
        "moons": 1,
        "day_length": "24 hours",
        "year_length": "365.25 days",
        "diameter_km": "12,742 km",
        "distance_from_sun": "149.6 million km",
        "fun_facts": [
            "The only known planet with confirmed life.",
            "71% of the surface is covered by water.",
            "Has a single large natural satellite: the Moon.",
        ],
        "future_note": "The +100y preview is an illustrative climate-stress visualization "
                        "(warmer palette, reduced polar ice tint) — an artistic extrapolation, "
                        "not a scientific climate model.",
    },
    "Mars": {
        "type": "Terrestrial planet",
        "moons": 2,
        "day_length": "24.6 hours",
        "year_length": "687 Earth days",
        "diameter_km": "6,779 km",
        "distance_from_sun": "227.9 million km",
        "fun_facts": [
            "Home to Olympus Mons, the tallest volcano in the Solar System.",
            "Has two small moons: Phobos and Deimos.",
            "Iron oxide (rust) on its surface gives it the red color.",
        ],
        "future_note": "Mostly static; the +100y view slightly deepens surface rust-red "
                        "tones to suggest continued oxidation and dust storm activity.",
    },
    "Jupiter": {
        "type": "Gas giant",
        "moons": 95,
        "day_length": "9.9 hours",
        "year_length": "11.9 Earth years",
        "diameter_km": "139,820 km",
        "distance_from_sun": "778.5 million km",
        "fun_facts": [
            "Largest planet in the Solar System — over 1,300 Earths could fit inside.",
            "The Great Red Spot is a storm larger than Earth that has raged for centuries.",
            "Has the most confirmed moons of any planet.",
        ],
        "future_note": "Banded cloud patterns are stylized to shift and the Great Red Spot "
                        "to shrink slightly in the +100y view, echoing its observed long-term contraction.",
    },
    "Saturn": {
        "type": "Gas giant",
        "moons": 146,
        "day_length": "10.7 hours",
        "year_length": "29.5 Earth years",
        "diameter_km": "116,460 km",
        "distance_from_sun": "1.43 billion km",
        "fun_facts": [
            "Famous for its spectacular ring system made of ice and rock.",
            "Is the least dense planet — it would float in a large enough bathtub of water.",
            "Has 146 confirmed moons, including Titan, larger than Mercury.",
        ],
        "future_note": "Saturn's rings are slowly eroding onto the planet; the +100y view "
                        "shows a very subtle thinning of the ring band as a stylized nod to this.",
    },
    "Uranus": {
        "type": "Ice giant",
        "moons": 28,
        "day_length": "17.2 hours",
        "year_length": "84 Earth years",
        "diameter_km": "50,724 km",
        "distance_from_sun": "2.87 billion km",
        "fun_facts": [
            "Rotates on its side with an axial tilt of about 98 degrees.",
            "Appears pale blue-green due to methane in its atmosphere.",
            "Has faint rings, discovered in 1977.",
        ],
        "future_note": "Essentially unchanged on a 100-year scale; a faint cyan atmospheric "
                        "shimmer is added for the +100y view purely as a visual flourish.",
    },
    "Neptune": {
        "type": "Ice giant",
        "moons": 16,
        "day_length": "16.1 hours",
        "year_length": "165 Earth years",
        "diameter_km": "49,244 km",
        "distance_from_sun": "4.5 billion km",
        "fun_facts": [
            "Has the strongest sustained winds in the Solar System, up to 2,100 km/h.",
            "Was the first planet located through mathematical prediction rather than observation.",
            "One Neptune year equals about 165 Earth years.",
        ],
        "future_note": "Deep-blue storm bands are stylized to intensify slightly for the "
                        "+100y view, echoing Neptune's observed variable storm activity.",
    },
    "Moon": {
        "type": "Natural satellite of Earth",
        "moons": 0,
        "day_length": "27.3 Earth days (tidally locked)",
        "year_length": "27.3 Earth days (orbits Earth)",
        "diameter_km": "3,474 km",
        "distance_from_sun": "N/A (orbits Earth at ~384,400 km)",
        "fun_facts": [
            "Always shows the same face to Earth due to tidal locking.",
            "Responsible for most of Earth's tides.",
            "Slowly drifting away from Earth at about 3.8 cm per year.",
        ],
        "future_note": "The gravity slider on the Moon exaggerates this real drift/spiral "
                        "behavior for a visible, satisfying effect.",
    },
}


def get_facts(name):
    """Return the facts dict for a body name, or a safe default if unknown."""
    return PLANET_FACTS.get(name, {
        "type": "Unknown body",
        "moons": 0,
        "day_length": "Unknown",
        "year_length": "Unknown",
        "diameter_km": "Unknown",
        "distance_from_sun": "Unknown",
        "fun_facts": ["No data available for this body."],
        "future_note": "",
    })
