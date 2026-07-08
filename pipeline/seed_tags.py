from supabase_client import supabase
from embedding_generator import generate_tag_embedding

official_tags = [
    {
        "name": "Gaming",
        "keywords": ["Gaming news covering video game releases, updates, patch notes, reviews, and gaming culture across PC, console, and mobile platforms."]
    },
    {
        "name": "World News",
        "keywords": ["World news covering international politics, global events, conflicts, diplomacy, and major happenings from around the globe."]
    },
    {
        "name": "Technology",
        "keywords": ["Technology news covering startups, product launches, software, AI, gadgets, and the tech industry."]
    },
    {
        "name": "Business & Finance",
        "keywords": ["Business and finance news covering markets, the economy, corporate moves, investing, and financial trends."]
    },
    {
        "name": "Sports",
        "keywords": ["Sports news covering match results, scores, transfers, tournaments, and analysis across football, basketball, and other major sports."]
    },
    {
        "name": "Entertainment",
        "keywords": ["Entertainment news covering movies, TV shows, celebrities, box office results, and pop culture."]
    },
    {
        "name": "Science",
        "keywords": ["Science news covering research breakthroughs, discoveries, the environment, and scientific studies."]
    },
]

for tag in official_tags:
    embedding = generate_tag_embedding(tag)
    supabase.table("topics").insert({
        "name": tag["name"],
        "keywords": tag["keywords"],
        "is_official": True,
        "created_by": None,
        "embedding": embedding
    }).execute()
    print(f"Inserted tag: {tag['name']}")
