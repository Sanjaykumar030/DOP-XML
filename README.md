#  DOP-XML: An Explainable AI Guardian for Digital Dopamine Regulation 🚀

---

## 🎯 Our Mission
To build an **ambient health guardian** that mitigates the risks of **digital dopamine hyper-stimulation in children** through **explainable, real-time AI insights**.

---

## 🌍 The Vision: Answering the Call for an "Ambient Health Guardian"
> *"Health isn’t limited to hospitals or apps; it lives in our everyday choices...  
> What if there were a guardian that quietly walked beside us, nudging us toward better health without demanding our attention? Envision what that guardian could be."*

**DOP-XML is that guardian.**  

In today’s digital age, platforms are engineered for **maximum engagement**, often at the cost of cognitive health.  
DOP-XML acts as a **counterbalance** — transforming passive screen time into an **actively monitored, explainable, and healthier environment** for children’s development.  

---

## ⚡ Core Pillars & Innovations

### 🧠 Explainable AI (XAI) Core
- The **"X" in DOP-XML** represents **explainability**.  
- Goes beyond risk scores — it **explains why** content is flagged.  
- Uses **SHAP** and **LIME** to highlight triggers like:  
  - Bright colors  
  - Repetitive music  
  - Fast visual cuts  
- Provides **transparent, actionable insights** for parents & educators.

---

### 🚀 Real-Time Nudging Engine
- Moves beyond passive analysis → provides **ambient, real-time nudges**.  
- Nudges may include:  
  - Suggesting breaks  
  - Recommending alternative content  
  - Encouraging offline activities  
- Acts as a **digital co-pilot** that reduces overstimulation *before it becomes harmful*.  

---

### 🔒 Privacy-Centric by Design
- Built with a **child-first privacy mindset**.  
- Roadmap emphasizes:  
  - **Minimal data liability**  
  - **On-device processing** (future scope)  
  - **Federated learning** for enhanced security  
- Ensures sensitive user data stays **safe and private**.  

---

## 🛠️ Project Roadmap & Live Status

| Phase | Status | Key Objective | Next Milestone |
|-------|--------|---------------|----------------|
| **1. Data Annotation & Curation** | ✅ Completed | Curated a high-fidelity dataset of 500–600 videos, labeled for dopamine stimulation. | Expand dataset for broader generalization. |
| **2. Data Engineering Pipeline** | ✅ Completed | Automated pipeline for preprocessing video/metadata. | Optimize feature extraction scripts. |
| **3. Iterative Model Training** | ✅ Completed | Trained CatBoost classifier, improving accuracy from 89% → **92%**. | Advanced tuning with Optuna. |
| **4. YouTube API Integration** | ✅ Completed | Built resilient connector to fetch real-time video metadata. | Strengthen error handling & scaling. |
| **5. Backend Service, AI, MLOps & SQL** | ✅ Completed | Containerized model via Flask & deployed microservice. Integrated DeepSeek AI for advanced reasoning. | Expand endpoint validation. Added SQL for tracking history and manipulating data |
| **6. API Definition & Documentation** | 🟡 In Progress | Defined stable `/api/v1` contract with interactive docs. | Finalize `/predict` request/response schema. |
| **7. Frontend UI/UX & Integration** | 🟡 Final Testing | Built responsive React interface for user/advanced modes. | Release fully functional prototype. |

---

## 📊 Model Metrics (CatBoost Classifier)

- **Accuracy:** `0.9200`  
- **ROC AUC:** `0.9664`  

| Class | Precision | Recall | F1-Score | Support |
|-------|-----------|--------|----------|---------|
| **0** | 0.90      | 0.94   | 0.92     | 50      |
| **1** | 0.94      | 0.90   | 0.92     | 50      |

# 📊 Dataset Schema

| Column Name           | Description                                                   | Citation |
|-----------------------|---------------------------------------------------------------|----------|
| `video_id`            | YouTube video identifier                                      | Malik, H. (2017). *A Framework for Collecting YouTube Meta-Data.* Procedia Computer Science. ScienceDirect |
| `channel_name`        | Channel name                                                  | Yang, S. (2022). *The science of YouTube: What factors influence user engagement with online science videos?* PMC |
| `video_title`         | Title of the video                                            | Giankos, E., Giannakopoulos, N. T., & Sakas, D. P. (2025). *Optimizing YouTube Video Visibility and Engagement: The Impact of Keywords on Fisheries’ Product Campaigns in the Supply Chain Sector.* MDPI |
| `freq_cut_per_video`  | Binary flag for frequent cuts (1 if present, 0 if absent)    | Halim, Z. (2022). *Identifying content unaware features influencing popularity of YouTube videos.* Computers in Industry. ScienceDirect |
| `video_duration_sec`  | Duration of the video in seconds                               | Shaikh, A. R. (2022). *YouTube and science: models for research impact.* PLOS ONE. PMC |
| `dominant_color`      | Dominant frame color (categorical)                             | Le, T. (2025). *EnTube: Exploring key video features for advancing video recommendation.* Procedia Computer Science. ScienceDirect |
| `view_count`          | Total number of views                                         | Yang, S. (2022). *The science of YouTube: What factors influence user engagement with online science videos?* PMC |
| `title_word_count`    | Number of words in the video title                             | Giankos, E., Giannakopoulos, N. T., & Sakas, D. P. (2025). *Optimizing YouTube Video Visibility and Engagement: The Impact of Keywords on Fisheries’ Product Campaigns in the Supply Chain Sector.* MDPI |
| `video_category`      | YouTube category label                                        | Halim, Z. (2022). *Identifying content unaware features influencing popularity of YouTube videos.* Computers in Industry. ScienceDirect |
| `is_for_kids`         | Boolean indicating child-targeted content                     | Giankos, E., Giannakopoulos, N. T., & Sakas, D. P. (2025). *Optimizing YouTube Video Visibility and Engagement: The Impact of Keywords on Fisheries’ Product Campaigns in the Supply Chain Sector.* MDPI |
| `date_published`      | Publication date (DD-MM-YYYY)                                 | Halim, Z. (2022). *Identifying content unaware features influencing popularity of YouTube videos.* Computers in Industry. ScienceDirect |
| `key_dopamine_factor` | Dominant dopamine feature (e.g., “jingles”, “flashing”)       | Yang, S. (2022). *The science of YouTube: What factors influence user engagement with online science videos?* PMC |
| `dopamine_label`      | 1 if dopamine-triggering, else 0                               | Shaikh, A. R. (2022). *YouTube and science: models for research impact.* PLOS ONE. PMC |

[Dataset Created & Used For Training](https://github.com/Sanjaykumar030/DOP-XML/blob/main/Dopamine_Data.xlsx)


> ✅ Balanced performance across both classes, ensuring reliability.

---

## 🖥️ Technology Stack

**Machine Learning & Backend:**  
- Python, Scikit-learn, CatBoost  
- Flask (API service), Weights & Biases (tracking)  

**Frontend & UI/UX:**  
- React, Tailwind CSS  
- Figma (visualizations)
-   

**Data & Infrastructure:**  
- SQLite (lightweight DB)  
- Google Cloud Run (YouTube API service)
- OpenRouter (Deepseek API service)  

---

## 🌟 Closing Note
⚡ *DOP-XML is not just a model — it is an **intelligent digital guardian** that quietly ensures healthier interactions with technology, shaping a safer digital future for the next generation.*  

---
