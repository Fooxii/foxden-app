export const mockArticles = [
  {
    id: 1,
    title: 'RTX 5090 benchmarks leak ahead of launch',
    source: "Tom's Hardware",
    time: '2h ago',
    contentType: 'news',
    tags: ['RTX 5090', 'PC Hardware']
  },
  {
    id: 2,
    title: 'BG3 Patch 7.1 — full changelog released',
    source: 'Larian Studios',
    time: '5h ago',
    contentType: 'patch_notes',
    tags: ['BG3 Patch Notes', 'Gaming']
  }
]

export const mockTrending = [
  {
    id: 1,
    source: 'X (Twitter)',
    items: [
      { rank: 1, topic: 'PC Hardware', title: '#RTX5090 trending as benchmarks surface', meta: '142K posts' },
      { rank: 2, topic: 'Esports', title: '#Worlds2024 — T1 sweeps into semifinals', meta: '98K posts' },
      { rank: 3, topic: 'Gaming', title: '#BG3 Patch 7.1 drops', meta: '61K posts' }
    ]
  },
  {
    id: 2,
    source: 'Reddit',
    items: [
      { rank: 1, topic: 'PC Hardware', title: 'AMD RX 9070 XT vs RTX 5080 — which to buy?', meta: 'r/hardware · 34K upvotes' },
      { rank: 2, topic: 'Gaming', title: 'Larian confirms no paid DLC ever for BG3', meta: 'r/BaldursGate3 · 28K upvotes' },
      { rank: 3, topic: 'Mobile Gaming', title: 'Genshin 4.5 leaks confirmed', meta: 'r/Genshin_Impact · 19K upvotes' }
    ]
  }
]

export const mockUser = {
  name: 'Name LastName',
  email: 'email@email.com',
  memberSince: 'January 2025',
  topics: ['PC Hardware', 'BG3 Patch Notes', 'Esports', 'Mobile Gaming', 'RTX 5090']
}