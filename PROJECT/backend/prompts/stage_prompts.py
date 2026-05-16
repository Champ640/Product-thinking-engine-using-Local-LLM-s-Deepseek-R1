"""
Stage-specific prompt templates for each pipeline stage.
Each template receives context from previous stages and
instructs the LLM on exactly what to produce.
"""

BRAINSTORM_PROMPT = """## Stage 1: Brainstorming & Idea Generation

The user's occupation: {occupation}
Their rough idea: {idea}

Generate exactly 10 refined product ideas based on their rough concept.
For each idea, provide:

1. **Product Name** — catchy, memorable
2. **One-Liner** — what it does in one sentence
3. **Target Audience** — who would use this
4. **Key Differentiator** — why this stands out from existing solutions
5. **Feasibility Score** (1-10) — based on the user's occupation and skills

Format each idea as a numbered list. Be creative but realistic.
Consider the user's occupation-specific strengths when scoring feasibility.
Think deeply about market gaps and unmet needs.
"""


SENTIMENT_PROMPT = """## Stage 2: Market Sentiment Analysis

The user's occupation: {occupation}
Their original idea: {idea}

Here are the brainstormed ideas from Stage 1:
{brainstorm_results}

Here is real-time web data about the market:
{web_data}

For the top 5 most promising ideas, analyze:

1. **Market Demand** — evidence of people wanting this (High/Medium/Low)
2. **Existing Solutions** — what already exists and their weaknesses
3. **Pain Points** — specific problems users face with current solutions
4. **Sentiment Score** — positive/negative/neutral ratio from web signals
5. **Gap Analysis** — what's missing in the current market

Rank the ideas by market opportunity. Be data-driven — reference the
web research provided above. Be honest about saturated markets.
"""


NICHE_PROMPT = """## Stage 3: Niche Discovery & Market Opportunities

The user's occupation: {occupation}
Their original idea: {idea}

Brainstorm results:
{brainstorm_results}

Sentiment analysis:
{sentiment_results}

Competitor and market data from the web:
{web_data}

Now identify the single best niche opportunity:

1. **Niche Definition** — the specific underserved market segment
2. **Market Size Estimate** — TAM/SAM/SOM if possible
3. **Competitor Landscape** — who's here, who's missing, market gaps
4. **Timing Signal** — why NOW is the right time for this
5. **User Persona** — detailed description of the ideal first customer
6. **Entry Strategy** — how to enter this niche with minimal resources
7. **Moat Potential** — what defensible advantage can be built

Select the ONE idea with the highest potential and explain why.
Be specific about the niche — "AI tools" is too broad, "AI code review
for Python Django teams" is the right level of specificity.
"""


MVP_PROMPT = """## Stage 4: MVP Plan Generation

The user's occupation: {occupation}
Their original idea: {idea}

Selected winning idea from analysis:
{niche_results}

All previous analysis context:
- Brainstorm: {brainstorm_summary}
- Sentiment: {sentiment_summary}
- Market data: {web_data}

Create a comprehensive MVP plan with these sections:

### 📋 Product Vision
- Product name
- Tagline (max 10 words)
- Elevator pitch (2-3 sentences)
- Problem statement
- Solution summary

### 👥 Target Users
- Primary persona (name, age, role, pain points)
- Secondary persona
- User journey map (awareness → consideration → purchase → retention)

### 🚀 Core Features (MVP)
- List exactly 5 must-have features for launch
- For each: name, description, priority (P0/P1/P2), estimated effort

### 💻 Tech Stack Recommendation
- Frontend, backend, database, hosting
- Tailored to the user's occupation and skills
- Include estimated monthly costs

### 📈 Go-to-Market Strategy
- Launch channels (top 3)
- Pre-launch activities
- Launch day plan
- First 30 days post-launch

### 💰 Revenue Model
- Pricing strategy (freemium/subscription/one-time)
- Price points with justification
- Revenue projection (Month 1, 3, 6, 12)

### 📅 30/60/90 Day Roadmap
- Month 1: Build & launch MVP
- Month 2: Iterate & grow
- Month 3: Scale & optimize
- Key milestones and metrics for each phase

### ⚠️ Risk Analysis
- Top 5 risks
- Mitigation strategy for each
- Kill criteria (when to pivot or stop)

Make this plan actionable — the user should be able to start
building tomorrow based on this document.
"""
