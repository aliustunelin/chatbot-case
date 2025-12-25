# 🥗 AI-Powered Role-Playing Chatbot – Healthy Eating Evaluation

## 📌 Task Overview

In this assignment, you are required to design and implement a **text-based AI chatbot** using **Python** that leverages a **Large Language Model (LLM)** to conduct **role-playing conversations** with a human user.

The chatbot’s primary goal is to **engage the user in a natural conversation**, continuously analyze the dialogue, and **evaluate how well the user addresses specific aspects of healthy eating**.

---

## 🎯 Chosen Topic: **Healthy Eating**

The chatbot must focus on a single topic and monitor the conversation for the following **key concepts**:

### 🔑 Target Keywords & Concepts

1. **Fruits & Vegetables**

   * Daily intake
   * Variety in consumption
   * Nutritional benefits

2. **Hydration**

   * Importance of drinking enough water
   * Maintaining hydration throughout the day

3. **Balanced Meals**

   * Proper balance of proteins, carbohydrates, and fats
   * Awareness of portion control

4. **Processed Foods**

   * Awareness of additives, sugar, salt, and unhealthy fats
   * Preference for whole or minimally processed foods

5. **Meal Timing**

   * Regular eating patterns
   * Avoiding long gaps between meals

---

## 🧠 Chatbot Responsibilities

The chatbot should:

* Conduct a **role-playing conversation** related to healthy eating.
* Maintain **conversational context** across multiple turns.
* **Detect keywords and related concepts** even if they are phrased indirectly.
* Evaluate:

  * Presence of keywords
  * Contextual relevance
  * Depth and quality of the user’s response

---

## 📊 Scoring Mechanism

* At the end of the conversation (or after a defined interaction window), the chatbot must assign a **score between 0 and 100**.
* The score should reflect **how well the user addressed the healthy eating concepts** listed above.
* Scoring should be based on:

  * Coverage of topics
  * Accuracy of information
  * Relevance and clarity

---

## 🧾 Output Requirements

* The final output should be **structured** (e.g., JSON or clearly formatted text).
* It must include:

  * The final score (0–100)
  * A brief explanation or breakdown of the evaluation

---

## 💬 Example Conversation Flow

```text
Chatbot: Hey! I’ve heard that you have some thoughts about healthy eating.
Chatbot: Could you tell me more? What do you think has the biggest influence on maintaining good nutrition?

User: I think eating balanced meals with enough vegetables and drinking enough water every day really makes a difference...
```

---

## 🛠️ Technical Expectations

Your implementation should demonstrate:

* Integration with an **LLM API**
* Clean and readable **Python code structure**
* Effective **keyword detection and scoring logic**
* Proper handling of **conversation state**
* Clear separation of:

  * Conversation logic
  * Evaluation logic
  * Scoring logic

---

## ✨ Evaluation Criteria

* Correctness and completeness of functionality
* Code clarity and structure
* Effective use of the LLM
* Logical and fair scoring approach
* **Creativity in role-playing and conversational design**
