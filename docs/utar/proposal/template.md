\*\* The content of the report structure can be re-organized; the section title and subsection title can be renamed; NOT necessary exactly follow the sequence provided by the template.

PEASE REMOVE THIS SECTION BEFORE SUBMIT THE REPORT

---

# PROJECT TITLE

By

Student Name

A PROPOSAL  
SUBMITTED TO  
Universiti Tunku Abdul Rahman  
in partial fulfillment of the requirements  
for the degree of  
BACHELOR OF COMPUTER SCIENCE (HONOURS)  
Faculty of Information and Communication Technology  
(Kampar Campus)  
OCTOBER 20XX  

---

# ABSTRACT

This project is an IC design project for academic purpose. It will provide students with the methodology, concept and design of digital integrated circuit. This will be illustrated through the construction of a Teaching Chip. Since CMOS technology is well suited for digital circuits, it is therefore implemented in the project. From the design point of view, emphasis is laid on the IC design flow. A flow exists due to the fact that IC design business involves integrating four diverse major areas namely device operation, circuit analysis and design, circuit simulation and lastly, physical layout and re-simulation. Emphasis is also made on the importance of an EDA tool; how it is incorporated into the design flow and aids IC design jobs. The tool used in this project is the Tanner Tools. In the area of device operation and circuit analysis/design, the circuit design job involves hand calculation for DC and transient design. These include designing the logic threshold voltage and propagation delay time of the circuit according to specification. Three common methods, Average-Current, Differential Equation and Digital Model are reviewed for their suitability in delay time hand calculation. Since hand calculation only presents an approximated circuit design, computer simulation is compulsory to verify the design. In the area of circuit simulation, SPICE MOSFET Level 2 model is used due to its suitability for teaching. Thus, at minimum, 2.0-micron CMOS is chosen. Beyond 2.0 micron, more complicated SPICE MOSFET model is required for simulation and is therefore avoided. Suitable CMOS processes are reviewed and consequently, MOSIS/Orbit 2.0-micron process is chosen. In the areas of physical layout and re-simulation, the designed circuit was laid out, design rule check was performed on the layout followed by layout extraction to obtain the equivalent SPICE netlist for re-simulation. Lastly, suitable digital circuits for teaching will be designed and packed onto the Teaching Chip.

Area of Study (Minimum 1 and Maximum 2): Integrated Circuit (IC) Design, CMOS Technology  
Keywords (Minimum 5 and Maximum 10): Digital Circuits, Circuit Analysis and Design, CMOS Processes, Circuit Simulation, Physical Layout  

---

# TABLE OF CONTENTS

| Section / Chapter | Page |
| :--- | :--- |
| **TITLE PAGE** | **i** |
| **ABSTRACT** | **ii** |
| **TABLE OF CONTENTS** | **iii** |
| **LIST OF FIGURES** | **iv** |
| **LIST OF TABLES** | **v** |
| **LIST OF ABBREVIATIONS** | **vi** |
| | |
| **CHAPTER 1 PROJECT BACKGROUND** | **1** |
| 1.1 Introduction | 1 |
| 1.2 Problem Statement | 1 |
| 1.3 Motivation | 1 |
| 1.4 Contributions | 1 |
| | |
| **CHAPTER 2 LITERATURE REVIEW** | **2** |
| 2.1 Previous Works on Deep Learning | 2 |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2.1.1 U-Net: Convolutional Networks for Biomedical Image Segmentation | 2 |
| 2.2 Limitation of Previous Studies | 3 |
| 2.3 Proposed Solutions | 3 |
| | |
| **CHAPTER 3 PROJECT SCOPE AND OBJECTIVES** | **4** |
| 3.1 Project Scope | 4 |
| 3.2 Project Objectives | 4 |
| | |
| **CHAPTER 4 METHODS/TECHNOLOGIES INVOLVED** | **5** |
| 4.1 System Design | 5 |
| | |
| **REFERENCES** | **6** |

---

# LIST OF FIGURES

| Figure Number | Title | Page |
| :--- | :--- | :--- |
| Figure 1.1 | U-net architecture. | 8 |
| Figure 2.1 | Full-custom flow for a microprocessor. | 10 |
| Figure 2.2 | Memory IC design flow. | 13 |
| Figure 2.3 | Full-custom design flow. | 14 |
| Figure 3.1 | Layout design procedure. | 19 |
| Figure 3.2 | Layout floor planning procedure. | 20 |

---

# LIST OF TABLES

| Table Number | Title | Page |
| :--- | :--- | :--- |
| Table 3.1 | Specifications of laptop | 71 |
| Table 4.1 | CMOS 3-Input NAND Timing Comparison. | 73 |
| Table 4.2 | CMOS 3-Input NOR Timing Comparison. | 75 |

---

# LIST OF ABBREVIATIONS

| Abbreviation | Meaning |
| :--- | :--- |
| CMOS | Complementary Metal Oxide Semiconductor |
| MOSFET | Metal Oxide Semiconductor Field Effect Transistor |
| IC | Integrated Circuit |
| DRC | Design Rule Checker |
| SCNA | Scalable CMOS N-Well Analog |
| ASIC | Application Specific Integrated Circuit |
| HDL | Hardware Description Language |

---

# CHAPTER 1  
## Project Background

In this chapter, we present the background and motivation of our research, our contributions to the field, and the outline of the thesis. ………

### 1.1 Introduction
Forensic investigation has been studies….

### 1.2 Problem Statement
Nowadays, criminal and victim identification, including two processes, identification (oneto-many matching), and verification (one-to-one matching), is an integral part of forensic investigation procedures. The identification process means the existing records in a database are compared with the biometric traits found at a crime scene. But the verification process means the biometric traits found at a crime scene are compared with those taken from an arrested suspect. ……

### 1.3 Motivation
The aim of the thesis is to propose new soft biometric traits and efficient algorithms for criminal and victim identification. Although their faces are masked, other body parts can be exposed. In this thesis, the leg geometry is proposed as one of soft biometric traits. ….

### 1.4 Contributions
Our experiment and analysis confirm the feasibility of the proposed biometric features and methods for criminal and victim identification. Firstly, lower leg geometry is shown to be an effective soft biometric trait and it provides a foundation for further research on criminal and victim identification based on body geometry. Secondly, the alignment problem of androgenic hair patterns is handled by using hair follicles and leg geometry for high- and low-resolution images. Thirdly, the ………

---

# CHAPTER 2  
## Literature Review

### 2.1 Previous Works on Deep Learning

#### 2.1.1 U-Net: Convolutional Networks for Biomedical Image Segmentation
(Olaf et al. 2015) proposed a research paper that was inspired by deep convolutional network technique to conduct segmentation on biomedical images. Yet, the development of this kind of technique was restricted by the size of the networks as well as the available training dataset. Convolutional networks were usually used in classification of images as a single class label, but each class label required to be assigned to each pixel of the image, this process was called localisation………

Figure 2.1 U-net architectu

### 2.2 Limitation of Previous Studies
Previous studies did not cover on the …

### 2.3 Proposed Solutions
This project aims to propose…

---

# CHAPTER 3  
## Project Scope and Objectives

### 3.1 Project Scope
The scopes of the project include….

### 3.2 Project Objectives
The aim of the thesis is to propose new soft biometric traits and efficient algorithms for criminal and victim identification. Although their faces are masked, other body parts can be exposed. In this thesis, the leg geometry is proposed as one of soft biometric traits. ….

---

# CHAPTER 4  
## Methods

The processes of the project were categorized into different phases in the development, which were project pre-development, data pre-processing, model training architecture building and data training, and prediction on test dataset.

### 4.1 System Design

#### 4.1.1 Hardware
The hardware involved in this project is computer and android mobile device. A computer issued for the process of 3D visualization and segmentation from MRI and CT datasets to obtain the 3D model objects, then it also used for applying AR technology on the 3D model objects. A mobile device is used for testing and deploying this AR application in learning human anatomy.

##### Table 4.1 Specifications of laptop

| Description | Specifications |
| :--- | :--- |
| Model | Asus A456U series |
| Processor | Intel Core i5-7200U |
| Operating System | Windows 10 |
| Graphic | NVIDIA GeForce GT 930MX 2GB DDR3 |
| Memory | 4GB DDR4 RAM |
| Storage | 1TB SATA HDD |

---

# REFERENCES

Note: For the latest version of the Guide & Examples, please refer to UTAR library IEEE Referencing Style:  
https://opac.utar.edu.my/gw_2013_2_8/html/default/en/Guides/IEEE-Reference-Guide-Online-v.04-20-2021.pdf  
Or refer to the PDF attachment “IEEE Referencing Style” on the FYP portal.

### Format: Books
**Basic Format:**  
J. K. Author, “Title of chapter in the book,” in *Title of His Published Book*, xth ed. City of Publisher, (only U.S. State), Country: Abbrev. of Publisher, year, ch. x, sec. x, pp. xxx–xxx.

**Examples:**  
1. B. Klaus and P. Horn, *Robot Vision*. Cambridge, MA, USA: MIT Press, 1986.  
L. Stein, “Random patterns,” in *Computers and You*, J. S. Brake, Ed. New York, NY, USA: Wiley, 1994, pp. 55–70.

### Format: E-Books
**Basic Format:**  
J. K. Author, “Title of chapter in the book,” in *Title of Published Book*, xth ed. City of Publisher, State, Country: Abbrev. of Publisher, year, ch. x, sec. x, pp. xxx–xxx. [Online]. Available: http://www.web.com

**Examples:**  
2. G. O. Young, “Synthetic structure of industrial plastics,” in *Plastics*, vol. 3, *Polymers of Hexadromicon*, J. Peters, Ed., 2nd ed. New York, NY, USA: McGraw-Hill, 1964, pp. 15–64. [Online]. Available: http://www.bookref.com.  
3. P. B. Kurland and R. Lerner, Eds., *The Founders’ Constitution*. Chicago, IL, USA: Univ. of Chicago Press, 1987. Accessed: Feb. 28, 2010. [Online]. Available: http://press-pubs.uchicago.edu/founders/

### Format: Book with Series Title, Volume Title, and Edition
**Basic Format:**  
J. K. Author, “Title of chapter in the book,” in *Title of His Published Book*, X. Editor, Ed., xth ed. City of Publisher, State (only U.S.), Country: Abbrev. of Publisher, year, ch. x, sec. x, pp. xxx–xxx.

**Examples:**  
4. A. Taflove, *Computational Electrodynamics: The Finite-Difference Time-Domain Method in Computational Electrodynamics II*, vol. 3, 2nd ed. Norwood, MA, USA: Artech House, 1996.  
5. M. Abramowitz and I. A. Stegun, Eds., *Handbook of Mathematical Functions* (Applied Mathematics Series 55). Washington, DC, USA: NBS, 1964, pp. 32–33.

### Format: Conference Paper (Paper Presented at a Conference)
**Basic Format:**  
J. K. Author, “Title of paper,” presented at the Abbreviated Name of Conf., City of Conf., Abbrev. State, Country, Month and day(s), year, Paper number.

**Examples:**  
6. D. Caratelli, M. C. Viganó, G. Toso, and P. Angeletti, “Analytical placement technique for sparse arrays,” presented at the 32nd ESA Antenna Workshop, Noordwijk, The Netherlands, Oct. 5–8, 2010.  
7. J. G. Kreifeldt, “An analysis of surface-detected EMG as an amplitude-modulated noise,” presented at the 1989 Int. Conf. Med. Biol. Eng., Chicago, IL, USA, Nov. 9–12, 1989.

### Format: Conference Proceedings in Print (Paper Presented at a Conference)
**Basic Format:**  
J. K. Author, “Title of paper,” in *Abbreviated Name of Conf.*, (location of conference is optional), (Month and day(s) if provided) year, pp. xxx-xxx.

**Examples:**  
8. A. Amador-Perez and R. A. Rodriguez-Solis, “Analysis of a CPW-fed annular slot ring antenna using DOE,” in *Proc. IEEE Antennas Propag. Soc. Int. Symp.*, Jul. 2006, pp. 4301–4304.  
9. G. R. Faulhaber, “Design of service systems with priority reservation,” in *Conf. Rec. 1995 IEEE Int. Conf. Commun.*, pp. 3–8. \*\*\* If the year is given in the conference title, it may be omitted from the end of the reference as shown here. \*\*\*

### Format: Conference Proceedings With DOI
**Basic Format:**  
J. K. Author, “Title of paper,” in *Abbreviated Name of Conf.*, (location of conference is optional), year, pp. xxx–xxx, doi: xxx.

**Examples:**  
10. G. Veruggio, “The EURON roboethics roadmap,” in *Proc. Humanoids ’06: 6th IEEE-RAS Int. Conf. Humanoid Robots*, 2006, pp. 612–617, doi: 10.1109/ICHR.2006.321337.  
11. J. Zhao, G. Sun, G. H. Loh, and Y. Xie, “Energy-efficient GPU design with reconfigurable in-package graphics memory,” in *Proc. ACM/IEEE Int. Symp. Low Power Electron. Design (ISLPED)*, Jul. 2012, pp. 403–408, doi: 10.1145/2333660.2333752.

### Format: Conference Paper Online
**Basic Format:**  
J. K. Author. (Date). Title. Presented at Abbreviated Conf. title. [Type of Medium]. Available: site/path/file

**Examples:**  
12. Process Software Corp., Framingham, MA, USA. Intranets: Internet technologies deployed behind the firewall for corporate productivity. Presented at INET’96 Annu. Meeting. [Online]. Available: http://www.process.com/Intranets/wp2.htp  
13. J. A. Taylor. (Nov. 2006). Assessment: A tool for development and engagement in the first year of university study. Presented at Engaging Students: 9th Pacific Rim in Higher Education (FYHE) Conf., Griffith, Australia. [Online]. Available: http://www.fyhe.com.au/past_papers/2006/Papers/Taylor.pdf.

### Format: Conference Proceedings Online
**Basic Format:**  
J. K. Author, “Title of paper,” in *Abbreviated Name of Conf.*, (location of conference is optional), year, pp. xxxxxx. [Online]. Available: http://www.url.com

**Examples:**  
14. T. Schubert, “Real challenges and solutions for validating system-on-chip high level formal verification of nextgeneration microprocessors,” in *Proc. 40th Design Automat. Conf. (DAC’03)*, Jun. 2–6, 2003. [Online]. Available: http://www.computer.org/csdl/proceedings/dac/2003/2394/00/2394001-abs.html  
15. J. Yanamadala et al., “Segmentation of the visible human project (VHP) female cryosection images within MATLAB environment,” in *Proc. 23rd Int. Meshing Roundtable*, London, U.K., Oct. 2014. [Online]. Available: http://www.imr.sandia.gov/papers/imr23.htm

### Format: Published mixed data/software package
**Basic Format:**  
Author, Date, Year. “Title of Dataset,” distributed by Publisher/Distributor, http://url.com (or if DOI is used, end with a period)

**Example:**  
16. S. Ansolabehere, M. Palmer, and A. Lee, January 20, 2014, “Precinct-Level Election Data. V1,” distributed by Harvard Election Data Archive, http://hdl.handle.net/1902.1/21919UNF:5:5C9UfGjdLy2ONVPtgr45qA==

### Format: Lectures Notes
**Basic Format:**  
J. K. Author. (Year). Title of lecture [Type of Medium]. Available: URL

**Examples:**  
17. J. Barney. (2011). Documenting literature [PowerPoint slides]. Available: http://moodle.cotr/english/gill  
18. Z. Yardish. Tumbling past data [Online]. Available: http://www.statistics.cotr.ca/classes/statistics/Yardish/index.html

### Format: Lecture Online
**Basic Format:**  
University name. (year). Title of lecture. [Type of Medium]. Available: URL

**Example:**  
19. Argosy University Online. (2012). Information literacy and communication: Module 2 filing and organization. [Online]. Available: http://www.myeclassonline.com

### Format: Online Video (e.g., YouTube)
**Basic Format:**  
Video Owner/Creator, Location (if available). Title of Video: In Initial Caps. (Release date). Accessed: Month Day, Year. [Online Video]. Available: http://URL.onlinevideo.org

**Examples:**  
20. mtaOnline1, Fazi Mosque, U.K. An Occasionally Accurate History of Australia: Part I. (Oct. 23, 2006). Accessed: Oct. 6, 2010. [Online Video]. Available: http://www.youtube.com/watch?v=IJjNsCVHc34  
21. Doane Academy, Burlington, NJ, USA. Second Grade Bossy R. (Feb. 28, 2013). Accessed: Jun. 3, 2018.

### Format: Periodicals
**Basic Format:**  
J. K. Author, “Name of paper,” *Abbrev. Title of Periodical*, vol. x, no. x, pp. xxx-xxx, Abbrev. Month, year.  
J. K. Author, “Name of paper,” *Abbrev. Title of Periodical*, vol. x, no. x, pp. xxx-xxx, Abbrev. Month, year, doi: xxx.

**Examples:**  
22. M. M. Chiampi and L. L. Zilberti, “Induction of electric field in human bodies moving near MRI: An efficient BEM computational procedure,” *IEEE Trans. Biomed. Eng.*, vol. 58, pp. 2787–2793, Oct. 2011, doi: 10.1109/TBME.2011.2158315.  
23. M. Ito et al., “Application of amorphous oxide TFT to electrophoretic display,” *J. Non-Cryst. Solids*, vol. 354, no. 19, pp. 2777–2782, Feb. 2008.  
24. R. Fardel, M. Nagel, F. Nuesch, T. Lippert, and A. Wokaun, “Fabrication of organic light emitting diode pixels by laser-assisted forward transfer,” *Appl. Phys. Lett.*, vol. 91, no. 6, Aug. 2007, Art. no. 061103.  
25. J. Zhang and N. Tansu, “Optical gain and laser characteristics of InGaN quantum wells on ternary InGaN substrates,” *IEEE Photon. J.*, vol. 5, no. 2, Apr. 2013, Art no. 2600111.

### Format: Virtual Journal
**Basic Format:**  
Name(s) of Ed(s)., “Title of Issue,” in *Title of Journal*, Abbrev. month year. [Online]. Available: URL

**Examples:**  
26. J. Smith, T. Jones, and B. Simpson, Eds., “IEEE Biometrics Compendium Issue 30 December 2017,” in *IEEE Biometrics Compendium*, Dec. 2017. [Online]. Available: http://ieeexplore.ieee.org/virtual-journals/biocomp/issue/30/  
27. T. Robertson, Ed., “RFIC Virtual Journal–Issue 6,” in *IEEE RFIC Virtual Journal*, Oct. 2014. [Online]. Available: http://ieeexplore.ieee.org/virtual-journals/rfic/issue/6/

### Format: Websites
**Basic Format:**  
First Name Initial(s) Last Name. “Page Title.” Website Title. Web Address (retrieved Date Accessed).

**Examples:**  
28. J. Smith. “Obama inaugurated as President.” CNN.com. http://www.cnn.com/POLITICS/01/21/obama_inaugurated/index.html (accessed Feb. 1, 2009).  
29. P. Costanzo, “Clemson Orange Uniforms Are Messing With the Color on My TV. And Apparently Messing With the ND Offense, Too.” Twitter. https://twitter.com/PaulCostanzo/status/817826295707041793 (accessed Apr. 19, 2021).