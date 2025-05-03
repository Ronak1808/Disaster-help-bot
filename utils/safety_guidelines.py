SAFETY_GUIDELINES = {
    "earthquake": {
        "before": [
            "Identify safe spots in each room (under sturdy furniture, against inside walls)",
            "Practice 'Drop, Cover, and Hold On' with family members",
            "Secure heavy furniture and appliances to walls",
            "Keep emergency supplies ready (water, food, flashlight, first aid kit)",
            "Know how to turn off gas, water, and electricity"
        ],
        "during": [
            "DROP to the ground",
            "Take COVER under a sturdy table or desk",
            "HOLD ON until the shaking stops",
            "Stay indoors until the shaking stops and you're sure it's safe to exit",
            "If you're in bed, stay there and protect your head with a pillow",
            "Stay away from windows, glass, and exterior doors"
        ],
        "after": [
            "Check yourself and others for injuries",
            "Check for gas leaks and turn off gas if you smell it",
            "Check for electrical system damage",
            "Be prepared for aftershocks",
            "Listen to the radio for emergency information",
            "Use the telephone only for emergency calls"
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
        "flood": [
            "Move to higher ground immediately",
            "Do not walk or drive through flood waters",
            "Stay away from bridges over fast-moving water",
            "Evacuate if told to do so",
            "Turn off utilities at the main switches if instructed",
            "Keep emergency supplies including food, water, and medications",
            "Have a battery-powered radio for updates",
            "Stay away from electrical equipment if you're wet"
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
        disaster_type (str): Type of disaster (e.g., 'earthquake', 'weather')
        phase (str, optional): Phase of the disaster (e.g., 'before', 'during', 'after')
                             For weather, can be 'general', 'heavy_rain', 'flood', etc.
    
    Returns:
        list: List of safety guidelines
    """
    if disaster_type not in SAFETY_GUIDELINES:
        return ["No specific guidelines available for this type of disaster."]
    
    if phase:
        if phase in SAFETY_GUIDELINES[disaster_type]:
            return SAFETY_GUIDELINES[disaster_type][phase]
        else:
            return ["No specific guidelines available for this phase."]
    
    # If no phase specified, return all guidelines
    all_guidelines = []
    for phase_guidelines in SAFETY_GUIDELINES[disaster_type].values():
        all_guidelines.extend(phase_guidelines)
    return all_guidelines 