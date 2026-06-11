# Recommendation Policy

Recommend games by matching the user, group, and play context first; use BGG rank and rating as quality signals, not as the main objective.

## Minimum Inputs

Prefer to know these before giving a confident recommendation:

| Input | Why it matters |
| --- | --- |
| Exact player count | 2-5 player recommendations often change by exact count. Ranges are less useful unless the group size is truly variable. For 6+ players, consider party, social deduction, team, negotiation, and flexible-count games. |
| Country/region and language ability | Infer this from user language and context when reasonable. Confirm only when purchase access, local editions, translations, clubs/stores, or language-dependent games are central and uncertain. |
| Play setting | Home, cafe, board game club/store, convention, family gathering, date night, company event, or fixed heavy-game group each imply different tolerance for length, teaching, table space, and complexity. |
| Experience and complexity tolerance | Distinguish all-new players, mixed groups, one experienced teacher, and dedicated hobbyists. |
| Desired duration | Use as a practical constraint, not just a preference. |

If only one or two details are missing, ask concise follow-up questions. If the user clearly wants immediate recommendations, give a provisional shortlist and state the assumptions.

When there is no usable user profile or play context, ask one short profiling round before making recommendations. Keep it lightweight: 3-5 questions is usually enough. Ask for exact player count, play setting, group experience, and preferred duration/complexity. Infer region/language from the user's wording where possible instead of asking by default. Do not turn the interview into a long form.

## Access, Not Just Purchase

Consider whether the user can realistically play the game:

- Buying: local retail, import, used market, crowdfunding leftovers, price, availability.
- Shared play: board game clubs, cafes, stores, libraries, friends' collections, university clubs.
- Language: localized edition, fan translation, translated rules, text-heavy components, whether one teacher can mediate.
- Community: local popularity, ease of finding players, likelihood a club already owns or teaches it.
- Digital access: Board Game Arena, Tabletop Simulator, Steam/app versions, online tutorials.

When uncertain about current regional availability or popularity, use web search or clearly mark the availability claim as uncertain.

## Fit Signals

Use database fields as follows:

- `min_players`, `max_players`: hard filter for the intended player count.
- `playing_time`, `min_playtime`, `max_playtime`: filter or warn based on session length.
- `average_weight`, `num_weights`: complexity signal; do not treat high weight as bad for dedicated players.
- `average`, `bayes_average`, `rank`, `users_rated`: quality and confidence signals.
- `game_links`: categories, mechanics, designers, publishers, families, honors, and subdomains.
- `game_polls.raw_json`: useful when it contains player-count, language-dependence, age, or weight poll summaries.

## When the Database Is Not Enough

The local database is the default candidate source, not a hard boundary. If the user shows a strong preference that the database does not cover well, broaden the search.

Use external search, current marketplace/community knowledge, or general board game knowledge when:

- The user asks for a niche style, local hit, party game, children's game, print-and-play, indie game, recent release, or region-specific favorite.
- The database query returns too few or obviously narrow candidates.
- Availability, local popularity, translation status, club/store play, or current editions matter.
- The user names a style or comparable game that points outside the current BGG snapshot.

When recommending out-of-database games, clearly mark them as "outside the local database" or "not found in the current snapshot" and explain the confidence level. Do not discard a good fit only because it is absent from the local SQLite cache.

## Recommendation Shape

Prefer a compact shortlist:

1. 3-5 primary picks.
2. Optional alternatives when different styles fit the same request.
3. For each game: name, player count fit, duration, complexity, why it fits, and one caveat or access note.

Use the game name that users in the target country/region are most likely to search for or recognize. If the localized/common name is known, write it first and include the BGG/English name in parentheses when useful, such as `Localized Title (BGG/English Title)`. If the local name is uncertain, keep the official/BGG name and mention that the local title should be verified.

Use "fit condition" instead of calling heavy/long games bad. For example: "Best if someone can teach and the group has 3 hours" is more useful than "too heavy."

Avoid recommending only the highest-ranked games. Include variety when the user's preference is broad.

## Common Cautions

- Mixed-experience groups need games where new players stay engaged and are not easily crushed by experts.
- Party and family requests may need lower teaching time more than high BGG rank.
- Dedicated club/store players may prefer deeper, longer, more specialized games.
- Cooperative game requests should include coverage across weight bands when broad: classic easy-to-table co-ops, medium co-ops, heavy strategy co-ops, campaign/legacy co-ops, and semi-coops if appropriate. Do not omit classic gateway co-ops such as Pandemic just because heavier or higher-ranked coops also fit.
- Some themes or mechanics can be socially sensitive: bluffing, betrayal, direct conflict, horror, war, colonial themes, or heavy negotiation.
- If data is missing or the database seems thin for a niche, say so and supplement with general knowledge or current web checks.
