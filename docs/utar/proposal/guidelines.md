# UTAR FICT IIPSPW Preliminary Proposal Report Guidelines (Development-Based)

> **Context**: Reference specification for writing the Preliminary Proposal Report for Development-based Final Year Projects in FICT (UTAR). Used by AI agents to guide document structure, chapter contents, and formatting compliance.

---

## 1. General Project Constraints & Writing Rules

* **Project Category**: **Development-based Project**.
  * Focuses on the non-trivial design and construction of an application/system (software, hardware, or mixed).
  * Must follow an established software/hardware engineering methodology.
  * Deliverables must provide sufficient architectural and implementation details for third-party continuation.
* **Core Deliverables to address in Proposal**:
  1. The purpose of the hardware/software.
  2. Novelty of the project.
  3. Underlying theories/concepts underpinning the work.
  4. Applicable software/data engineering methods to be used.
  5. Tools, frameworks, and technologies involved.
  6. Methods used to test, validate, and evaluate the system.
  7. Justification of project complexity appropriate for a Final Year Project.
* **Writing Style**:
  * **Tone**: Formal, objective third-person narrative style (strictly avoid *I, we, us, you*).
  * **Tense**: Past tense for completed background/prior literature; formal present/future for proposed work.
  * **Language**: British English.
  * **Originality**: Similarity index must be **less than 20%**. Strict adherence to anti-plagiarism policies. All facts, claims, and external data must be properly cited using IEEE style.

---

## 2. Proposal Structure & Content Requirements

The proposal must follow the exact order and chapter arrangements below:

### 2.1 Preliminary Sections

1. **Title Page**:
   * Title of project proposal (UPPERCASE)
   * Student's full name (Title Case)
   * Universiti Tunku Abdul Rahman (Title Case)
   * Statement of degree (UPPERCASE)
   * Faculty name: Faculty of Information and Communication Technology (Title Case)
   * Trimester and Year
2. **Abstract**:
   * Length: Max 1 page (typically 150 – 300 words).
   * Content: Field of study, problem definition, methodology/architecture adopted, development process, expected results, and novelties.
   * Metadata (placed below abstract):
     * **Areas of Study**: Minimum 1, Maximum 2.
     * **Keywords**: Minimum 5, Maximum 10.
3. **Table of Contents**: Complete listing of preliminary sections, chapters, subsections (up to 3 levels: e.g., 2.1.1), and page numbers.
4. **List of Figures** *(if applicable)*: Ordered by chapter (e.g., Figure 2.1).
5. **List of Tables** *(if applicable)*: Ordered by chapter (e.g., Table 2.1).
6. **List of Symbols** *(if applicable)*: Alphabetical order with meanings and SI units.
7. **List of Abbreviations** *(if applicable)*: Alphabetical order with full expansions.

---

### 2.2 Body Chapters

#### Chapter 1: Project Background (2 to 10 pages)
* General introduction to the domain, field, and relevant background.
* **Key questions to resolve**:
  * What is the core problem/issue to be addressed?
  * Who is affected by this problem and requires the solution?
  * Why is the problem important and critical to solve?
  * What does this study aim to establish or demonstrate?

#### Chapter 2: Literature Review (5 to 20 pages)
* Critical analysis and synthesis of literature, related systems, or existing engineering solutions.
* **Key questions to resolve**:
  * What approaches/systems have prior developers or researchers used to address this problem?
  * What are the strengths of existing solutions?
  * What are the weaknesses, gaps, or architectural limitations of existing solutions?
  * How will the proposed project address or overcome these limitations?

#### Chapter 3: Project Scope and Objectives (1 to 5 pages)
* **Project Scope**:
  * Clear overview of the proposed solution.
  * Precise deliverables produced by the end of the project (e.g., software prototype, data pipeline, system architecture).
  * Explicit definition of boundaries (what is included vs. excluded).
* **Project Objectives**:
  * Main objective broken down into clear, measurable sub-objectives.
  * Specific innovation or engineering contribution of the project.

#### Chapter 4: Methods / Technologies Involved (2 to 20 pages)
* Detailed, coherent description of adopted methodologies and tech stack.
* Explains how the outputs will be designed, implemented, and verified.
* Includes architectural diagrams, pipeline flows, root cause analysis, or system components.
* **Key questions to resolve**:
  * What engineering methods, frameworks, and technologies are used?
  * Why are these choices justified to achieve each stated sub-objective?

---

### 2.3 Post-Body Sections

1. **References**:
   * Target: 10 to 50 reputable references.
   * Format: Strictly **IEEE Referencing Style** (numbered in citation order `[1]`, `[2]`, etc.).
2. **Appendices**:
   * Labeled alphabetically (Appendix A, Appendix B, etc.).
   * Supplementary technical data, hardware/software specifications, lengthy schemas, code listings, or survey instruments.

---

## 3. Formatting & Typesetting Specifications

| Component | Standard Specification |
| :--- | :--- |
| **Language** | British English |
| **Page Margins** | Left: 1.5" (3.81 cm) <br> Right, Top, Bottom: 1.0" (2.54 cm) <br> Header: 0.5" (1.27 cm) <br> Footer: 0.4" (1.02 cm) |
| **Font Family** | Times New Roman |
| **Font Sizes** | Body text: **12 pt** <br> Headers, Footers, Footnotes, Table/Figure text: **10 – 11 pt** |
| **Font Colors & Styles**| Black only. Variable symbols must be in *Italics*. |
| **Headings** | Chapter Title: **UPPERCASE, BOLD, LEFT-ALIGNED** <br> Subsections: **Title Case, Bold, Left-Aligned** (max 3 levels) |
| **Line Spacing** | 1.5 lines spacing |
| **Page Numbering** | Right-aligned in footer: <br>• Preliminaries: lowercase Roman numerals (*ii, iii, iv...* ; title page is *i* but unprinted). <br>• Main Body (Ch 1 through References): Arabic numerals (*1, 2, 3...*). <br>• Appendices: Alpha-numeric (*A-1, A-2...*). |
| **Header** | Left-aligned: Chapter number and title |
| **Footer** | Left-aligned: Degree title and faculty (as specified in template) <br> Right-aligned: Page number |

---

## 4. Visuals, Data, and Mathematics Rules

* **Tables**:
  * Numbered sequentially per chapter (e.g., Table 3.1).
  * Centered on the page.
  * **Caption placement: ABOVE the table, centered.**
  * Must be explicitly referenced and explained in text prior to appearance.
* **Figures** (diagrams, flowcharts, screenshots, charts):
  * Numbered sequentially per chapter (e.g., Figure 1.2).
  * Centered on the page.
  * **Caption placement: BELOW the figure, centered.**
  * Must be explicitly cited and analyzed in the body text.
* **Equations**:
  * Centered horizontally with Arabic equation numbers right-aligned in parentheses: `(2.1)`.
  * Define all symbols and SI units immediately following first use.
  * Avoid ambiguous inline representations (e.g., use `(y/x) = ax + b` instead of `y/x = ax + b`).