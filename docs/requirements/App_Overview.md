# AI Phonics Tutor – Application Specification

## 1. Purpose & Objectives

### 1.1 Goal

Build a **child‑safe, AI‑assisted phonics learning web application** for children aged **5–7**, using **Python + Django**, deployed on **Azure**, demonstrating:

- Structured phonics education
- AI‑enhanced speech interaction
- Adaptive, encouraging feedback
- Safe, governed use of LLMs
- Scalable architecture suitable beyond a demo

---

### 1.2 Non‑Goals (Explicit)

- Not a free‑form conversational chatbot
- Not storing personally identifiable child data
- Not replacing speech recognition with LLMs

---

## 2. Target Users

### Primary Users

- Children aged **5–7**
  - Pre‑readers or early readers
  - Native and non‑native English speakers

### Secondary Users

- Parents / teachers (read‑only view)
- Demo audience / stakeholders

---

## 3. Functional Requirements

---

## 3.1 Phonics Coverage (Complete Scope)

The app must support **all standard English phonics**, not a demo subset.

### 3.1.1 Phonics Categories

#### ✅ Single Letter Sounds

- Consonants: `b c d f g h j k l m n p r s t v w y z`
- Short vowels: `a e i o u`

#### ✅ Digraphs

- Consonant digraphs: `ch sh th wh ph ng`
- Silent digraphs: `kn wr`

#### ✅ Blends

- Initial blends: `bl cl fl gr st tr`
- Final blends: `mp nd st nk`

#### ✅ Long Vowel Patterns

- Magic E: `a_e i_e o_e u_e`
- Vowel teams: `ai ee oa oo ie`

#### ✅ R‑Controlled Vowels

- `ar er ir or ur`

#### ✅ Diphthongs

- `oi oy ou ow`

✅ **Requirement**: Phonics must be **data‑driven**, not hard‑coded.

---

## 3.2 Learning Flow

Each phonics unit follows the same structured pedagogy.

### Standard Learning Loop

1.  **Listen** – AI plays sound
2.  **Observe** – letter + animation
3.  **Repeat** – child speaks
4.  **Practice** – interactive game
5.  **Reinforce** – encouragement + reward

✅ Each loop < **3 minutes**

---

## 3.3 Game‑Based Interactions

### Required Game Types

- Sound → Picture matching
- Beginning sound selection
- Blend builder (drag & drop)
- Balloon pop (correct sound only)

✅ One learning objective per game

---

## 3.4 Speech Interaction

### 3.4.1 Speech Recognition

- Child speaks:
  - Phoneme (e.g. `/sh/`)
  - Simple word (e.g. “ship”)
- System captures:
  - Confidence score
  - Common substitution error
  - Attempt count

### 3.4.2 Feedback Rules

- **Never say “wrong”**
- Always:
  - Acknowledge effort
  - Provide guidance
  - Offer retry gently

---

## 3.5 AI (LLM) Responsibilities (Strictly Bounded)

### The LLM MUST:

- Interpret speech metadata
- Choose feedback strategy
- Generate age‑appropriate encouragement
- Adjust approach if repeated failure occurs

### The LLM MUST NOT:

- Judge pronunciation correctness from raw audio
- Ask open‑ended questions
- Generate unsupervised text

✅ Use **prompt templates and output constraints only**

---

## 4. Safety, Trust & Compliance

### 4.1 Child Safety Constraints

- No free‑text input
- No personal data requests
- No external web access
- No unscripted AI responses

### 4.2 Data Protection

- Anonymous user IDs only
- No voice recordings stored permanently
- Session data retained < 24 hours (configurable)

✅ This is critical for education demos.

---

## 5. Non‑Functional Requirements

### 5.1 Performance

- Speech feedback < 1.5 seconds
- UI interaction < 100ms response

### 5.2 Availability

- 99% uptime (demo acceptable)
- Stateless web frontend

### 5.3 Accessibility

- WCAG‑aware color contrast
- Audio‑first interactions
- Large clickable elements

---

## 6. System Architecture (Azure)

### 6.1 High‑Level Architecture

    Browser (Child)
       │
       ▼
    Azure App Service (Django)
       │
       ├─ Phonics Engine
       ├─ Progress Engine
       ├─ Game Engine
       │
       ├─ Azure Speech Services
       │     ├─ Speech-to-Text
       │     └─ Text-to-Speech
       │
       ├─ Azure OpenAI (via AI Foundry)
       │     └─ Pedagogical Reasoning
       │
       └─ Azure SQL / PostgreSQL

---

## 7. Backend Design (Django)

---

### 7.1 Core Django Apps

#### ✅ `phonics`

- Phoneme definitions
- Categories
- Associated words & images

#### ✅ `sessions`

- Anonymous child sessions
- Learning progress
- Attempt history

#### ✅ `speech`

- Speech input handling
- Confidence metrics
- Error types

#### ✅ `ai_tutor`

- Prompt templates
- LLM response validation
- Feedback strategies

#### ✅ `games`

- Game definitions
- Game‑phonics mappings

---

## 7.2 Data Model (Simplified)

```python
class Phoneme(models.Model):
    symbol = models.CharField()
    category = models.CharField()
    example_words = models.JSONField()

class LearningSession(models.Model):
    session_id = models.UUIDField()
    current_phoneme = models.ForeignKey(Phoneme)

class SpeechAttempt(models.Model):
    phoneme = models.ForeignKey(Phoneme)
    confidence = models.FloatField()
    detected_error = models.CharField()
```

✅ Phonics data must be extensible without code changes.

---

## 8. AI Prompt Design (Controlled)

### Example System Prompt (Simplified)

```text
You are a friendly phonics tutor for children aged 5–7.
You must:
- Use simple words
- Be encouraging
- Avoid saying "wrong"
- Never ask personal questions
- Respond in 1–2 short sentences only
```

### User Context Input

```json
{
  "phoneme": "/sh/",
  "confidence": 0.61,
  "error": "/s/",
  "attempts": 3
}
```

---

## 9. Frontend Requirements

### 9.1 Technology

- HTML5 + CSS
- Minimal JS
- Touch‑first design

### 9.2 UI Rules

- No text instructions > 5 words
- Icons + audio cues preferred
- Consistent mascot presence

---

## 10. Observability & Demo Diagnostics

- Log:
  - Phoneme attempts
  - AI feedback types
- Dashboard:
  - Success per phoneme
  - Time spent
  - Retry rates

✅ Useful for stakeholder demos.

---

## 11. Demo‑Readiness Checklist

✅ All phonics data‑driven  
✅ AI safety constraints enforced  
✅ No child data risk  
✅ Clear AI vs non‑AI boundaries  
✅ Extendable beyond demo

---

## 12. Optional Enhancements (Future)

- Multi‑accent speech tuning
- Offline phonics packs
- Parent dashboard with insights
- Multilingual phonics base

---

## Final Summary (One Line for Stakeholders)

> _This application combines structured phonics education with AI‑driven pedagogical reasoning, enabling adaptive, child‑safe learning experiences that are impossible to scale using traditional rule‑based approaches._
