SAFETY_GUIDELINES = {
    "earthquake": {
        "before": [
            "Secure heavy items and furniture to walls.",
            "Prepare an emergency kit with food, water, and first aid supplies.",
            "Identify safe spots in each room, such as under sturdy tables.",
            "Practice earthquake drills with your family."
        ],
        "during": [
            "Drop, cover, and hold on until the shaking stops.",
            "Stay away from windows and heavy objects that could fall.",
            "If outdoors, move to an open area away from buildings and power lines.",
            "If driving, stop in a safe place and stay inside the vehicle."
        ],
        "after": [
            "Check yourself and others for injuries.",
            "Be prepared for aftershocks.",
            "Inspect your home for damage and hazards.",
            "Listen to emergency broadcasts and follow official instructions."
        ],
        "general": [
            "Be prepared, stay calm, and follow safety protocols during an earthquake."
        ]
    },
    "flood": {
        "before": [
            "Know your area's flood risk and evacuation routes.",
            "Prepare an emergency kit with food, water, flashlight, and first aid supplies.",
            "Keep important documents in a waterproof container.",
            "Move valuables and electrical items to higher floors.",
            "Install check valves in plumbing to prevent floodwater backup."
        ],
        "during": [
            "Move to higher ground immediately if there is a flood warning.",
            "Avoid walking or driving through floodwaters.",
            "Stay away from bridges over fast-moving water.",
            "Listen to emergency broadcasts and follow evacuation orders.",
            "Disconnect electrical appliances if safe to do so."
        ],
        "after": [
            "Return home only when authorities say it is safe.",
            "Avoid floodwater as it may be contaminated.",
            "Clean and disinfect everything that got wet.",
            "Watch out for snakes and other animals displaced by floods.",
            "Document property damage with photos for insurance claims."
        ],
        "general": [
            "Stay informed, avoid floodwaters, and follow official instructions during a flood."
        ]
    },
    "weather": {
        "general": [
            "Stay informed about weather conditions through reliable sources",
            "Have an emergency kit ready with essential supplies",
            "Know your evacuation routes",
            "Keep important documents in a waterproof container",
            "Have a communication plan with family members"
        ],
        "heavy_rain": [
            "Avoid driving through flooded areas",
            "Stay away from streams, rivers, and drainage channels",
            "Move to higher ground if flooding is possible",
            "Keep emergency supplies ready",
            "Monitor local weather alerts and warnings",
            "Clear gutters and drains to prevent water buildup",
            "Have sandbags ready if you're in a flood-prone area",
            "Keep important documents and valuables in waterproof containers"
        ],
        "tsunami": [
            "Move to higher ground immediately if you're near the coast",
            "Follow evacuation routes marked by local authorities",
            "Stay away from the beach and coastal areas",
            "Listen to emergency alerts and warnings",
            "Do not return to coastal areas until authorities say it's safe",
            "If you're in a boat, move to deep water",
            "Stay away from rivers and streams that lead to the ocean",
            "Have an emergency kit ready with essential supplies"
        ],
        "tornado": [
            "Go to a basement or an interior room on the lowest floor",
            "Stay away from windows and exterior walls",
            "Cover yourself with blankets or mattresses",
            "If in a vehicle, drive to the nearest shelter",
            "If no shelter is available, lie flat in a ditch or low-lying area",
            "Protect your head and neck with your arms",
            "Stay away from mobile homes and vehicles",
            "Have a battery-powered weather radio for updates"
        ],
        "hurricane": [
            "Board up windows and secure outdoor objects",
            "Evacuate if ordered by local authorities",
            "Stay in an interior room away from windows",
            "Keep emergency supplies ready",
            "Monitor local news and weather updates",
            "Fill bathtubs and containers with water",
            "Turn refrigerator to coldest setting",
            "Have important documents in waterproof containers"
        ],
        "wildfire": [
            "Evacuate immediately if ordered",
            "Close all windows and doors",
            "Turn off gas, propane, or fuel oil supplies",
            "Wear protective clothing if you must stay",
            "Have an emergency supply kit ready",
            "Create a defensible space around your home",
            "Keep gutters and roofs clear of debris",
            "Have a plan for pets and livestock",
            "Know multiple evacuation routes",
            "Keep important documents ready to take"
        ],
        "heat_wave": [
            "Stay hydrated by drinking plenty of water",
            "Stay in air-conditioned buildings as much as possible",
            "Avoid strenuous activities during the hottest part of the day",
            "Wear lightweight, light-colored clothing",
            "Check on elderly neighbors and relatives",
            "Never leave children or pets in vehicles",
            "Take cool showers or baths",
            "Use fans and keep curtains closed during the day",
            "Know the signs of heat-related illnesses",
            "Have a plan for power outages"
        ],
        "blizzard": [
            "Stay indoors and avoid unnecessary travel",
            "Keep emergency supplies including food, water, and medications",
            "Dress in layers if you must go outside",
            "Keep your home's heating system in good working order",
            "Have a backup heating source available",
            "Keep a battery-powered radio for updates",
            "Have extra blankets and warm clothing ready",
            "Keep your car's gas tank full",
            "Have a winter emergency kit in your vehicle",
            "Know the signs of frostbite and hypothermia"
        ],
        "drought": [
            "Conserve water by fixing leaks and using water-efficient appliances",
            "Follow local water restrictions",
            "Collect rainwater for non-potable uses",
            "Use drought-resistant plants in landscaping",
            "Have an emergency water supply",
            "Take shorter showers and turn off water while brushing teeth",
            "Only run full loads in dishwashers and washing machines",
            "Use a broom instead of a hose to clean outdoor areas",
            "Install water-saving devices in your home",
            "Have a plan for water shortages"
        ]
    }
}

def get_safety_guidelines(disaster_type, phase=None):
    """
    Get safety guidelines for a specific disaster type and phase.
    
    Args:
        disaster_type (str): Type of disaster (e.g., 'earthquake', 'flood')
        phase (str, optional): Phase of the disaster (e.g., 'before', 'during', 'after')
                             For weather, can be 'general', 'heavy_rain', etc.
    Returns:
        list: List of safety guidelines
    """
    if disaster_type not in SAFETY_GUIDELINES:
        return ["No safety guidelines available for this disaster type."]
    
    if phase:
        if phase in SAFETY_GUIDELINES[disaster_type]:
            return SAFETY_GUIDELINES[disaster_type][phase]
        elif "general" in SAFETY_GUIDELINES[disaster_type]:
            return SAFETY_GUIDELINES[disaster_type]["general"]
        else:
            return ["No specific guidelines available for this phase."]
    
    # If no phase specified, return all guidelines (before, during, after, general, etc.)
    all_guidelines = []
    for key in SAFETY_GUIDELINES[disaster_type]:
        all_guidelines.extend(SAFETY_GUIDELINES[disaster_type][key])
    if all_guidelines:
        return all_guidelines
    return ["No safety guidelines available for this disaster type."] 