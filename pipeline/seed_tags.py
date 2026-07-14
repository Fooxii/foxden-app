from supabase_client import supabase
from embedding_generator import generate_tag_embedding

official_tags = [
    {
        "name": "Gaming",
        "keywords": ["Video game news, reviews, previews, and industry developments. Covers PC, console, and mobile game releases, esports tournaments, game engine technology, modding communities, and platform updates from Steam, Epic, Xbox, PlayStation, and Nintendo. Includes game design, narrative, monetization, and player community discussions. Related terms: video game, RPG, FPS, MMO, battle royale, esports, speedrun, mod, DLC, patch, update, Steam, Xbox, PlayStation, Nintendo, indie game, AAA, open world, multiplayer, co-op, battle pass, loot box, game engine, Unity, Unreal Engine."]
    },
    {
        "name": "Finance",
        "keywords": ["Financial markets, investing, and economic policy. Covers stock markets, bonds, central bank decisions, corporate earnings, IPOs, mergers, private equity, venture capital, and macroeconomic indicators. Includes cryptocurrency, blockchain, DeFi, and fintech developments. Related terms: stock, S&P 500, Dow Jones, Nasdaq, ETF, bond, treasury, yield, interest rate, Federal Reserve, inflation, recession, GDP, earnings, IPO, M&A, crypto, Bitcoin, Ethereum, blockchain, DeFi, forex, trading, portfolio, dividend, commodity, oil, gold."]
    },
    {
        "name": "Car Industry",
        "keywords": ["Automotive industry news, electric vehicle developments, and autonomous driving technology. Covers Tesla, Rivian, Lucid, BYD, Ford, GM, Volkswagen, Toyota, and other manufacturers. Includes battery technology, charging infrastructure, EPA ratings, safety testing, recalls, and motorsports. Related terms: EV, electric vehicle, battery, lithium, charging station, supercharger, self-driving, FSD, ADAS, LIDAR, horsepower, torque, range, auto show, concept car, recall, NHTSA, IIHS, Formula E, NASCAR, Le Mans, dealership, lease."]
    },
    {
        "name": "PC Hardware",
        "keywords": ["Desktop and laptop computer components, peripherals, and build guides. Covers CPU and GPU launches from Intel, AMD, NVIDIA, motherboard chipsets, DDR5 and PCIe 5.0 memory and storage, cooling solutions, power supplies, PC cases, monitors, and peripherals. Includes benchmarking, overclocking, thermal testing, and component comparisons. Related terms: processor, graphics card, RAM, SSD, HDD, motherboard, PSU, cooler, case, benchmark, frame rate, thermal, overclock, gaming PC, workstation, mini-ITX, ATX, DDR5, PCIe, NVIDIA, AMD, Intel, Radeon, GeForce, Ryzen, Core i9, Threadripper, AIO cooler, BIOS, UEFI, VRM, M.2, NVMe, refresh rate, 4K, 1440p, DLSS, FSR, ray tracing."]
    },
    {
        "name": "Cinema",
        "keywords": ["Film industry news, movie reviews, box office analysis, and filmmaking craft. Covers Hollywood blockbusters, independent cinema, international film, and major franchises. Includes film festivals, cinematography, visual effects, casting, production, distribution, and the business of filmmaking. Related terms: movie, film, director, actor, screenplay, box office, premiere, trailer, Oscar, Academy Awards, Cannes, Sundance, IMAX, documentary, animation, sequel, reboot, franchise, studio, streaming, Netflix, HBO."]
    },
    {
        "name": "Music",
        "keywords": ["Music industry news, album and single releases, artist interviews, and live performances. Covers all genres from pop, hip-hop, rock, and electronic to classical, jazz, country, and K-pop. Includes streaming platforms, record labels, royalties, copyright, concerts, tours, and festivals. Related terms: album, single, EP, artist, band, concert, tour, festival, Spotify, Apple Music, record label, royalty, hip-hop, rap, rock, pop, electronic, EDM, jazz, classical, producer, DJ, remix, Grammy, Billboard, chart, vinyl."]
    },
    {
        "name": "Science Research",
        "keywords": ["Peer-reviewed scientific research, study summaries, and laboratory breakthroughs across physics, biology, chemistry, and medicine. Covers genetics, neuroscience, climate science, materials science, biotechnology, and emerging fields. Includes research funding, academic publishing, and university science. Related terms: research, study, experiment, hypothesis, breakthrough, discovery, biotechnology, genetics, genomics, CRISPR, vaccine, clinical trial, neuroscience, brain, cognition, climate change, renewable energy, nanotechnology, quantum computing, laboratory, university, peer review, Nature, Science, Cell, NIH, NSF."]
    },
    {
        "name": "Politics",
        "keywords": ["Political news, elections, policy developments, and international relations. Covers legislative battles, executive actions, diplomacy, treaties, geopolitical conflicts, sanctions, and trade disputes. Includes international organizations and human rights issues. Related terms: election, vote, campaign, candidate, president, parliament, congress, senate, legislation, bill, law, policy, regulation, treaty, summit, NATO, EU, UN, G7, G20, Brexit, geopolitics, conflict, war, sanctions, protest, lobbying, polling, coalition."]
    },
    {
        "name": "AI",
        "keywords": ["Artificial intelligence, machine learning, and large language model research and product news. Covers model releases from OpenAI, Anthropic, Google DeepMind, Meta, Mistral, and open-source projects. Includes AI safety, alignment, regulation, enterprise adoption, generative AI tools, computer vision, robotics, and AI policy debates. Related terms: LLM, transformer, neural network, deep learning, NLP, GPT, Claude, Gemini, inference, training, fine-tuning, prompt engineering, AGI, multimodal AI, AI agent, foundation model."]
    },
    {
        "name": "Space",
        "keywords": ["Space exploration missions, astronomical discoveries, and planetary science. Covers NASA, ESA, SpaceX, Blue Origin, and commercial launches including Artemis, Starship, and satellites. Includes telescope observations, exoplanets, black holes, cosmology, and solar system exploration. Related terms: rocket, launch, satellite, ISS, Mars, Moon, Artemis, James Webb, JWST, Hubble, telescope, exoplanet, galaxy, black hole, supernova, nebula, asteroid, comet, orbit, astronaut, rover, lander, probe, astrophysics, SETI, eclipse."]
    },
    {
        "name": "Sports",
        "keywords": ["Professional and amateur sports coverage across all major disciplines. Includes football, basketball, baseball, tennis, golf, cricket, rugby, Formula 1, motorsports, athletics, swimming, boxing, MMA, and the Olympic Games. Covers match results, player transfers, injury reports, tournaments, records, coaching changes, and sports business. Related terms: Premier League, Champions League, World Cup, NFL, NBA, MLB, NHL, UFC, tournament, match, transfer, injury, coach, team, stadium, draft, playoff, championship, medal, score, fixture."]
    },
]

for tag in official_tags:
    embedding = generate_tag_embedding(tag)
    supabase.table("tags").insert({
        "name": tag["name"],
        "keywords": tag["keywords"],
        "is_official": True,
        "created_by": None,
        "embedding": embedding
    }).execute()
    print(f"Inserted tag: {tag['name']}")
