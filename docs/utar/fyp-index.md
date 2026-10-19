> **🤖 AI SYSTEM INSTRUCTION (ROUTING & FLEXIBILITY RULES)**:
> 
> 1. **Project Nature & Context**:
>    - This is a **Development-Based Data Engineering Project** focusing on a modern Lakehouse architecture (ingesting GTFS transit data using Apache Kafka, Apache Spark, Apache Iceberg, ClickHouse, Apache Airflow, and dbt).
>    - Main chapters (Chapter 1 to Chapter n) are strictly mandatory per UTAR guidelines, but sub-sections (H2, H3) MUST be dynamically organized for this Data Engineering context. NEVER generate generic IoT/hardware content.
> 
> 2. **Phase Routing & Strict Scope Isolation (CRITICAL)**:
>    - You must first determine which phase the current task belongs to:
>      * **Phase 1 (Proposal)**: Strictly reference `docs/utar/proposal/guidelines.md` & `template.md`.
>      * **Phase 2 (FYP 1)**: Strictly reference `docs/utar/fyp1/guidelines.md` & `template.md`.
>      * **Phase 3 (FYP 2)**: Strictly reference `docs/utar/fyp2/guidelines.md` & `template.md`.
>    - **DO NOT CROSS-CONTAMINATE**: When generating content for one phase, NEVER mix chapter numbering, templates, or marking rubrics from another phase (e.g., do not pull FYP2 evaluation requirements into FYP1).
> 
> 3. **Execution Workflow**:
>    - Step 1: Read Section 1 of this file for global formatting (margins, font, IEEE citations).
>    - Step 2: Read ONLY the target phase's directory (`docs/utar/<target-phase>/`).


---

## 1. Global Formatting & Typesetting Specifications

All generated documents must strictly adhere to the following baseline rules:
* **Language & Tone**: British English; formal, objective third-person past/present tense (No "I", "we", "you").
* **Font**: Times New Roman, 12 pt for body text (10-11 pt for headers, footers, figures, tables). Variable symbols in *Italics*.
* **Line Spacing**: 1.5 lines.
* **Margins**: Left 1.0" (Front cover 1.2"); Right, Top, Bottom 1.0"; Header 0.5"; Footer 0.4".
* **Referencing**: IEEE Style.
* **Visuals**: Captions for Tables go ABOVE; Captions for Figures go BELOW. Sequentially numbered by chapter (e.g., Figure 4.1).

---

## 2. Phase 1: IIPSPW (Preliminary Proposal)
**Docs**: `docs/utar/proposal/guidelines.md`, `docs/utar/proposal/template.md`
**Goal**: Define the problem, literature, scope, and initial methodology.

### 2.1 Structure
* **Front Matter**: Title Page, Abstract (with Area of Study & Keywords), TOC, List of Figures/Tables.
* **Chapter 1: Project Background** 
* **Chapter 2: Literature Review** 
* **Chapter 3: Project Scope and Objectives** 
* **Chapter 4: Methods/Technologies Involved** 
* **References & Appendices**.

---

## 3. Phase 2: FYP 1 (System Design & Preliminary Work)
**Docs**: `docs/utar/fyp1/guidelines.md`, `docs/utar/fyp1/template.md`
**Goal**: Solidify the system design, complete preliminary data ingestion/setup, and prepare for full implementation.

### 3.1 Marking Scheme
* **Proposal Report (50%)**: Research Methods/Tools (10%), Literature Review (7%), Problem & Objectives (7%), Conclusion (7%), Plan (6%), Format (5%), Language (5%), Title (3%).
* **Presentation (40%)**: Preliminary Work/Result (10%), Innovation (10%), Slide Design (7%), Content (7%), Q&A (3%), Preparation (3%).
* **General Effort (10%)**: Punctuality, independence, ethics.

### 3.2 Structure
* **Front Matter**: Title Page, Copyright, Acknowledgements, Abstract, TOC.
* **Chapter 1: Introduction**
* **Chapter 2: Literature Review** 
* **Chapter 3: Proposed Method/Approach** 
* **Chapter 4: Preliminary Work** 
* **Chapter 5: Conclusion**.

---

## 4. Phase 3: FYP 2 (Implementation, Testing & Evaluation)
**Docs**: `docs/utar/fyp2/guidelines.md`, `docs/utar/fyp2/template.md`
**Goal**: Fully realize the architecture, perform data transformations, optimize queries, and evaluate pipeline performance.

### 4.1 Marking Scheme
* **Technical Achievement (50%)**: Evaluation and Analysis (15%), Prototyping (10%), General (15%), Contribution/Innovation (10%).
* **Report Format and Writing (30%)**: Implementation (5%), Experimental Results (5%), Conclusion (5%), Presentation of Report (3%), Abstract/Scope (3%), Literature Review (3%), Problem Analysis (3%), Modelling (3%).
* **Presentation (10%)**.
* **General Effort (10%)**.

### 4.2 Structure
* **Front Matter**: Front Cover, Title Page, Copyright, Acknowledgements, Abstract, TOC.
* **Chapter 1: Introduction**.
* **Chapter 2: Literature Review**.
* **Chapter 3: System Methodology/Approach** 
* **Chapter 4: System Design** 
* **Chapter 5: System Implementation** 
* **Chapter 6: System Evaluation and Discussion** 
* **Chapter 7: Conclusion and Recommendation** 