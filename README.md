# qNMR Analysis Automation

Automated pipeline for extracting, processing, and visualizing quantitative NMR (qNMR) data directly from Mestrelab Mnova.

## Overview
This tool bridges the gap between Mnova's internal C++ API and modern Python data science libraries (Pandas, Matplotlib). It allows users to extract peak and integral data from an active Mnova spectrum with a single click, calculates stable integration areas using a threshold-based growth algorithm, and automatically generates a PDF report.

## Prerequisites
- **OS:** macOS, Windows, or Linux
- **Software:** Mestrelab Mnova (v17+)
- **Python:** Python 3.10 or higher

## Installation

To ensure the pipeline runs smoothly without interfering with Mnova's internal Python interpreter (especially on macOS where external C-libraries are blocked), you must set up a local Virtual Environment.

Clone this repository to your local machine:

git clone [https://github.com/lukas32123/qNMR_analysis_automation.git](https://github.com/lukas32123/qNMR_analysis_automation.git)

cd qNMR_analysis_automation

## Set up venv

### On macOS/Linux

python3 -m venv venv
source venv/bin/activate
### On Windows
python -m venv venv
venv\Scripts\activate
