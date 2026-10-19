# UTAR FICT FYP2 Report Guidelines (Development-Based)

> **Context**: Reference specification for writing the Final Year Project II (FYP2) Report for Development-based projects. Used by AI agents to guide document structure, chapter contents, and formatting compliance.

---

## 1. General Project Constraints

* **Project Category**: **Development-based Project**.
  * Involves the design and construction of a non-trivial prototype for an application (hardware, software, or mixed).
  * Development must follow an established hardware/software engineering method.
* **Core Deliverables**: The report must explicitly state the purpose of the application, its novelty, underlying theories, engineering methods, tools, testing/evaluation methods, and project complexity.
* **Word Count**: The report should comprise between **8,000 – 20,000 words**.
* **Originality**: Similarity index must be within approved limits; all sources must be properly cited.

---

## 2. Report Structure & Chapter Arrangement

The report must follow this exact top-down arrangement. Each chapter must begin on a new page, and subsections are limited to a maximum of 3 levels (e.g., 2.1.1).

### 2.1 Preliminary Sections
1. **Front Cover & Title Page**: Strict adherence to formatting templates.
2. **Copyright Statement**: 1 page.
3. **Acknowledgements**: 1 page.
4. **Abstract**: Maximum 1 page (150 – 300 words). Includes field of study, problem definition, methodology, research process, results, conclusion, and novelties. Must list Area of Study (1-2) and Keywords (5-10).
5. **Table of Contents, List of Figures, List of Tables, List of Symbols, List of Abbreviations**.

### 2.2 Core Chapters (Development-Based)

> **🤖 AI SYSTEM INSTRUCTION (FLEXIBILITY RULE)**:
> While the main chapters (Chapter 1 to Chapter 7) are strictly mandatory, the sub-sections (H2, H3 levels) provided below are merely examples. 
> You MUST dynamically rename, reorganize, add, or remove sub-sections to perfectly fit the user's specific project domain while maintaining logical flow and academic rigor.

#### Chapter 1: Introduction (5 to 10 pages)
* 1.1 Problem Statement and Motivation
* 1.2 Objectives
* 1.3 Project Scope
* 1.4 Contributions
* 1.5 Report Organization

#### Chapter 2: Literature Review (5 to 30 pages)
* 2.1 Review of the Technologies
  * 2.1.1 Hardware Platform / 2.1.2 Firmware/OS / 2.1.3 Database / 2.1.4 Programming Language / 2.1.5 Algorithm
  * 2.1.6 Summary of the Technologies Review
* 2.2 Review of the Existing Systems/Applications
  * 2.2.1 Existing System A / 2.2.2 Existing System B (etc.)
  * 2.2.5 Summary of the Existing Systems

#### Chapter 3: System Methodology/Approach
* 3.1 System Design Diagram/Equation
  * 3.1.1 System Architecture Diagram
  * 3.1.2 Use Case Diagram and Description
  * 3.1.3 Activity Diagram

#### Chapter 4: System Design (5 to 30 pages)
*(Provides necessary information for a third party to rebuild the system)*
* 4.1 System Block Diagram
* 4.2 System Components Specifications
* 4.3 Circuits and Components Design
* 4.4 System Components Interaction Operations

#### Chapter 5: System Implementation
* 5.1 Hardware Setup
* 5.2 Software Setup
* 5.3 Setting and Configuration
* 5.4 System Operation (with Screenshot)
* 5.5 Implementation Issues and Challenges
* 5.6 Concluding Remark

#### Chapter 6: System Evaluation And Discussion
* 6.1 System Testing and Performance Metrics
* 6.2 Testing Setup and Result
* 6.3 Project Challenges
* 6.4 Objectives Evaluation
* 6.5 Concluding Remark

#### Chapter 7: Conclusion and Recommendation (2 to 5 pages)
* 7.1 Conclusion
* 7.2 Recommendation

### 2.3 Post-Body Sections
* **References**: 10 to 60 references.
* **Appendices**: Supplementary materials (specifications, data sheets, lengthy derivations, etc.).
* **Poster**: A4 size.

## 3. Formatting & Typesetting Specifications

### 3.1 Report Format Requirements
* **Writing Style**: Third person and past tense (Strictly avoid "I" or "you").
* **Language**: British English.
* **Line Spacing**: 1.5 lines spacing.
* **Font Family**: Times New Roman.
* **Font Sizes**:
  * Body Text, Chapter Headings, Subheadings, Citations, Table/Figure Captions: **12 pt**.
  * Header, Footer, Footnotes, Words inside Figures/Tables: **10 to 11 pt**.
* **Font Color**: Black.

### 3.2 Page Margins
* Left: 1.0 inch (Exception: Front Cover is 1.2 inches).
* Right: 1.0 inch.
* Top & Bottom: 1.0 inch.
* Header: 0.5 inch / Footer: 0.4 inch.

### 3.3 Headers, Footers & Page Numbering
* **Header**: Align left with chapter number and title.
* **Footer**: 
  * Align left: `[Statement of Degree]` (e.g., Bachelor of Computer Science (Honours)) <br> Faculty of Information and Communication Technology (Kampar Campus), UTAR.
  * Align right: Page number.
* **Page Numbering Rules**:
  * Preliminaries (Title, Copyright, Acknowledgements, Abstract, TOC, Listings): Small Roman numerals (*i, ii, iii...*). Note: Title page is *i* but the number is not printed.
  * Main Body (Chapters & References): Arabic numerals (*1, 2, 3...*).
  * Appendices: Alpha-numeric (*A-1, A-2, B-1...*).

### 3.4 Visuals & Equations
* **Figures and Tables**: Numbered sequentially per chapter (e.g., Table 2-2 means 2nd table in Chapter 2). Captions must be placed *immediately below* the table or figure. Ensure clear legends and coordinate units (abscissa).
* **Equations**: Typed in *Italic*. Avoid ambiguous inline equations (use `(y/x) = ax + b` instead of `y/x = ax + b`).
* **Units**: Use International System Units (S.I.).

### 3.5 Front Cover & Title Page Fields
Must strictly adhere to the following sequence (all centered, 12pt TNR, no UTAR logo on cover):
1. PROJECT TITLE (UPPERCASE)
2. BY (UPPERCASE)
3. STUDENT NAME (UPPERCASE)
4. A REPORT
5. SUBMITTED TO
6. Universiti Tunku Abdul Rahman
7. in partial fulfillment of the requirements for the degree of
8. BACHELOR OF COMPUTER SCIENCE (HONOURS) (UPPERCASE)
9. Faculty of Information and Communication Technology (Kampar Campus)
10. MONTH YEAR (e.g., OCTOBER 2025)

---

## 4. Marking Scheme for FYP2

The marking scheme dictates the weightage of the project and report, which should guide the effort and detail invested into each chapter:

**1. Technical Achievement (50%)**
* Evaluation and Analysis (15%)
* Prototyping (10%)
* General (15%)
* Contribution/Innovation (10%)

**2. Report Format and Writing (30%)**
* Presentation of Report (3%)
* Abstract, Problem Statement, Objectives and Project Scope (3%)
* Literature Review (3%)
* Problem Analysis and Hypothesis (3%)
* Modelling (3%)
* Implementation/Prototyping of System (5%)
* Experimental/Survey Results (5%)
* Conclusion (5%)

**3. Presentation (10%)**

**4. General Effort (10%)**

**Total: 100%**