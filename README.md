# GrameenConnect

GrameenConnect is a web-based platform designed to bridge the digital divide in rural areas. It offers access to local job listings, government scheme awareness, issue reporting, and a micro-marketplace — all in one unified portal to empower villagers and enable smart village growth.

## Features

1. **Local Job Board** - Post and search for work (agriculture, labor, tutoring, etc.)
2. **Government Schemes Info Hub** - Easy-to-read cards listing latest schemes, eligibility, and how to apply
3. **Infrastructure Reporting** - Citizens can report issues (roads, water, electricity) with images & location
4. **Local Marketplace** - Villagers can list handmade goods or produce for sale
5. **Language Toggle** - Support for English and Hindi

## Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, Bootstrap 5
- **Database**: SQLite
- **Template Engine**: Jinja2

## Setup Instructions

### Prerequisites

- Python 3.6 or higher
- pip (Python package manager)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/divyanshu1804/grameenconnect.git
   cd grameenconnect
   ```

2. Create and activate a virtual environment (optional but recommended):
   ```
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the application:
   ```
   python app.py
   ```

5. Access the application at:
   ```
   http://localhost:8080
   ```

## Project Structure

```
GrameenConnect/
├── app/
│   ├── models/
│   │   ├── auth.py
│   │   └── database.py
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   ├── js/
│   │   │   └── main.js
│   │   └── images/
│   │       └── uploads/
│   └── templates/
│       ├── index.html
│       ├── layout.html
│       ├── login.html
│       ├── register.html
│       ├── jobs.html
│       ├── new_job.html
│       ├── schemes.html
│       ├── scheme_details.html
│       ├── issues.html
│       ├── report_issue.html
│       ├── marketplace.html
│       └── new_product.html
├── app.py
├── requirements.txt
└── README.md
```

## Future Enhancements

- Mobile app version for wider accessibility
- Integration with government APIs for real-time scheme updates
- Advanced analytics dashboard for village administrators
- Voice-based interaction for users with limited literacy
- Support for more regional languages

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

For any queries, please contact: info@grameenconnect.org 