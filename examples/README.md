# Reddit Answers Scraper, website (https://www.reddit.com/answers/)

## Input Schema

### Example

```json
{
  "question":"tips to improve water pressure"
}

```

### Input Parameters
  - question (required): An string of question you want answers for. Each question will be submitted to Reddit Answers.

## Output Schema

### Example

```json
{
  "url": "https://www.reddit.com/answers/91ede21d-7f09-437e-91a6-4d5ae1f6d936/?q=how+many+planet+are+in+our+solar+system%3F&source=ANSWERS",
  "question": "how many planet are in our solar system?",
  "sources": [
    "https://www.reddit.com/r/threebodyproblem",
    "https://www.reddit.com/r/technology",
    "https://www.reddit.com/r/Astronomy"
  ],
  "sections": [
    {
      "heading": "Current Consensus",
      "content": [
        "8 Planets: The current official count of planets in our solar system is eight. This includes Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, and Neptune."
      ]
    },
    {
      "heading": "Pluto and Dwarf Planets",
      "content": [
        "Pluto's Reclassification: Pluto was reclassified as a dwarf planet in 2006..."
      ]
    },
    {
      "heading": "Potential Additional Planets",
      "content": [
        "Planet Nine: There is ongoing discussion and research about the potential existence of a ninth planet..."
      ]
    },
    {
      "heading": "Fun Facts",
      "content": [
        "Orbital Periods: The orbital periods of planets vary dramatically..."
      ]
    },
    {
      "heading": "Subreddits for Further Exploration",
      "content": [
        "r/Astronomy    r/space    r/askscience",
        "Feel free to dive deeper into these subreddits to learn more!"
      ]
    }
  ],
  "relatedPosts": [
    {
      "rank": "1",
      "title": "8 planets in the solar system.",
      "subreddit": "threebodyproblem",
      "url": "https://www.reddit.com/r/threebodyproblem/comments/1mmdaq8/8_planets_in_the_solar_system/",
      "upvotes": 59,
      "comments": 24,
      "domain": "self.threebodyproblem",
      "promoted": false,
      "score": 59
    },
    {
      "rank": "2",
      "title": "Our solar system may indeed have 9 planets, paper finds",
      "subreddit": "technology",
      "url": "https://www.reddit.com/r/technology/comments/1kqmmfg/our_solar_system_may_indeed_have_9_planets_paper/",
      "upvotes": 16,
      "comments": 75,
      "domain": "nicenews.com",
      "promoted": false,
      "score": 16
    }
  ],
  "relatedTopics": [
    "how many moons does each planet have?",
    "what are the characteristics of dwarf planets?",
    "is there a ninth planet in our solar system?"
  ]
}
```

### Output Fields
  - url: The Reddit Answers page URL for the question
  - question: The question that was asked
  - sources: Array of subreddit URLs that contributed to the answer
  - sections: Organized answer sections with headings and content
  - relatedPosts: Array of relevant Reddit posts with metadata (rank, title, subreddit, upvotes, comments, etc.)
  - relatedTopics: Suggested related questions for further exploration

