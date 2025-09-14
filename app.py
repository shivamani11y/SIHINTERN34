from flask import Flask, request, render_template_string
import requests
import pandas as pd
from bs4 import BeautifulSoup

app = Flask(__name__)

# Load job listings from CSV
def load_job_listings():
    """Load job listings from a CSV file."""
    df = pd.read_csv('./job_listings.csv')
    return df

# Internship scraping function with error handling
def fetch_internships(skills, location=None):
    """Fetch internships based on skills and location from Internshala with error handling."""
    # Use the first skill as primary search term
    primary_skill = skills[0] if skills else "internship"
    query = primary_skill.replace(' ', '-').lower()
    
    url = f"https://internshala.com/internships/keywords-{query}"
    if location and location.lower() != "any":
        url += f"/location-{location.replace(' ', '-').lower()}"
    
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        internships = []
        listings = soup.find_all('div', class_='internship_meta')

        for listing in listings[:10]:  # Limit to top 10 internships
            try:
                title = listing.find('h3').get_text(strip=True)
                company_tag = listing.find('a', class_='link_display_like_text')
                company = company_tag.get_text(strip=True) if company_tag else "N/A"
                link = "https://internshala.com" + listing.find('a')['href']
                internships.append({'title': title, 'company': company, 'link': link})
            except AttributeError as e:
                print(f"Error parsing internship listing: {e}")
                continue

        return internships

    except Exception as e:
        print(f"Error fetching internships: {e}")
        return []

def get_job_suggestions(skills, education_level=None, sector_interests=None):
    """Get job suggestions based on skills, education, and sector interests."""
    job_listings = load_job_listings()
    suggestions = []
    
    for _, row in job_listings.iterrows():
        required_skills = [skill.strip().lower() for skill in row['Required_Skills'].split(', ')]
        user_skills = [skill.strip().lower() for skill in skills]
        
        # Check if any user skills match required skills
        skill_match = any(user_skill in required_skills for user_skill in user_skills)
        
        if skill_match:
            suggestions.append({
                'title': row['Job_Title'],
                'company': row.get('Company', 'N/A'),
                'location': row.get('Location', 'N/A'),
                'skills': row['Required_Skills']
            })

    return suggestions[:10]  # Limit to top 10 job suggestions

# Modern HTML template with attractive UI
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Career Opportunity Finder</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .gradient-bg {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .card-hover {
            transition: all 0.3s ease;
        }
        .card-hover:hover {
            transform: translateY(-5px);
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        }
        .skill-tag {
            background: linear-gradient(45deg, #4f46e5, #7c3aed);
        }
        .animate-fade-in {
            animation: fadeIn 0.6s ease-in;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
    </style>
</head>
<body class="gradient-bg min-h-screen">
    <div class="container mx-auto px-4 py-8">
        <!-- Header -->
        <div class="text-center mb-12 animate-fade-in">
            <h1 class="text-5xl font-bold text-white mb-4">
                <i class="fas fa-rocket mr-3"></i>Career Opportunity Finder
            </h1>
            <p class="text-xl text-white opacity-90">Discover your perfect internship and job matches</p>
        </div>

        <!-- Main Form Card -->
        <div class="max-w-4xl mx-auto bg-white rounded-2xl shadow-2xl overflow-hidden animate-fade-in">
            <div class="bg-gradient-to-r from-indigo-500 to-purple-600 p-6">
                <h2 class="text-3xl font-bold text-white text-center">
                    <i class="fas fa-user-graduate mr-2"></i>Tell Us About Yourself
                </h2>
            </div>
            
            <form action="/" method="POST" class="p-8 space-y-8">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <!-- Education Level -->
                    <div class="space-y-2">
                        <label for="education" class="flex items-center text-lg font-semibold text-gray-700">
                            <i class="fas fa-graduation-cap mr-2 text-indigo-500"></i>Education Level
                        </label>
                        <select name="education" id="education" class="w-full p-4 border-2 border-gray-200 rounded-xl focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 transition-all duration-300" required>
                            <option value="">Select your education level</option>
                            <option value="High School">High School</option>
                            <option value="Diploma">Diploma</option>
                            <option value="Bachelor's Degree">Bachelor's Degree</option>
                            <option value="Master's Degree">Master's Degree</option>
                            <option value="PhD">PhD</option>
                        </select>
                    </div>

                    <!-- Location -->
                    <div class="space-y-2">
                        <label for="location" class="flex items-center text-lg font-semibold text-gray-700">
                            <i class="fas fa-map-marker-alt mr-2 text-red-500"></i>Preferred Location
                        </label>
                        <input type="text" name="location" id="location" placeholder="e.g., Mumbai, Delhi, Bangalore, Remote" 
                               class="w-full p-4 border-2 border-gray-200 rounded-xl focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 transition-all duration-300" required>
                    </div>
                </div>

                <!-- Skills -->
                <div class="space-y-2">
                    <label for="skills" class="flex items-center text-lg font-semibold text-gray-700">
                        <i class="fas fa-code mr-2 text-green-500"></i>Your Skills
                    </label>
                    <textarea name="skills" id="skills" rows="3" placeholder="e.g., Python, JavaScript, Machine Learning, Data Analysis, Marketing, Design..." 
                              class="w-full p-4 border-2 border-gray-200 rounded-xl focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 transition-all duration-300 resize-none" required></textarea>
                    <p class="text-sm text-gray-500">Separate multiple skills with commas</p>
                </div>

                <!-- Sector Interests -->
                <div class="space-y-2">
                    <label for="sectors" class="flex items-center text-lg font-semibold text-gray-700">
                        <i class="fas fa-industry mr-2 text-blue-500"></i>Sector Interests
                    </label>
                    <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
                        <label class="flex items-center space-x-2 p-3 border-2 border-gray-200 rounded-lg hover:border-indigo-300 cursor-pointer transition-all duration-300">
                            <input type="checkbox" name="sectors" value="Technology" class="text-indigo-500 focus:ring-indigo-500">
                            <span class="text-sm font-medium">Technology</span>
                        </label>
                        <label class="flex items-center space-x-2 p-3 border-2 border-gray-200 rounded-lg hover:border-indigo-300 cursor-pointer transition-all duration-300">
                            <input type="checkbox" name="sectors" value="Finance" class="text-indigo-500 focus:ring-indigo-500">
                            <span class="text-sm font-medium">Finance</span>
                        </label>
                        <label class="flex items-center space-x-2 p-3 border-2 border-gray-200 rounded-lg hover:border-indigo-300 cursor-pointer transition-all duration-300">
                            <input type="checkbox" name="sectors" value="Healthcare" class="text-indigo-500 focus:ring-indigo-500">
                            <span class="text-sm font-medium">Healthcare</span>
                        </label>
                        <label class="flex items-center space-x-2 p-3 border-2 border-gray-200 rounded-lg hover:border-indigo-300 cursor-pointer transition-all duration-300">
                            <input type="checkbox" name="sectors" value="Marketing" class="text-indigo-500 focus:ring-indigo-500">
                            <span class="text-sm font-medium">Marketing</span>
                        </label>
                        <label class="flex items-center space-x-2 p-3 border-2 border-gray-200 rounded-lg hover:border-indigo-300 cursor-pointer transition-all duration-300">
                            <input type="checkbox" name="sectors" value="Education" class="text-indigo-500 focus:ring-indigo-500">
                            <span class="text-sm font-medium">Education</span>
                        </label>
                        <label class="flex items-center space-x-2 p-3 border-2 border-gray-200 rounded-lg hover:border-indigo-300 cursor-pointer transition-all duration-300">
                            <input type="checkbox" name="sectors" value="Design" class="text-indigo-500 focus:ring-indigo-500">
                            <span class="text-sm font-medium">Design</span>
                        </label>
                        <label class="flex items-center space-x-2 p-3 border-2 border-gray-200 rounded-lg hover:border-indigo-300 cursor-pointer transition-all duration-300">
                            <input type="checkbox" name="sectors" value="Consulting" class="text-indigo-500 focus:ring-indigo-500">
                            <span class="text-sm font-medium">Consulting</span>
                        </label>
                        <label class="flex items-center space-x-2 p-3 border-2 border-gray-200 rounded-lg hover:border-indigo-300 cursor-pointer transition-all duration-300">
                            <input type="checkbox" name="sectors" value="Media" class="text-indigo-500 focus:ring-indigo-500">
                            <span class="text-sm font-medium">Media</span>
                        </label>
                    </div>
                </div>

                <!-- Submit Button -->
                <div class="text-center pt-6">
                    <button type="submit" class="bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white font-bold py-4 px-12 rounded-xl shadow-lg transition-all duration-300 transform hover:scale-105 hover:shadow-xl">
                        <i class="fas fa-search mr-2"></i>Find My Opportunities
                    </button>
                </div>
            </form>
        </div>

        <!-- Results Section -->
        {% if internships or job_suggestions %}
        <div class="max-w-6xl mx-auto mt-12 animate-fade-in">
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <!-- Internships -->
                <div class="bg-white rounded-2xl shadow-2xl overflow-hidden">
                    <div class="bg-gradient-to-r from-blue-500 to-cyan-500 p-6">
                        <h2 class="text-2xl font-bold text-white text-center">
                            <i class="fas fa-briefcase mr-2"></i>Internship Opportunities
                        </h2>
                    </div>
                    <div class="p-6 space-y-4 max-h-96 overflow-y-auto">
                        {% if internships %}
                            {% for internship in internships %}
                            <div class="card-hover bg-gradient-to-r from-blue-50 to-cyan-50 p-4 rounded-xl border border-blue-100">
                                <h3 class="font-bold text-lg text-gray-800">{{ internship.title }}</h3>
                                {% if internship.company != "N/A" %}
                                    <p class="text-gray-600 mb-2">
                                        <i class="fas fa-building mr-1"></i>{{ internship.company }}
                                    </p>
                                {% endif %}
                                <a href="{{ internship.link }}" target="_blank" 
                                   class="inline-flex items-center text-blue-600 hover:text-blue-800 font-medium">
                                    <i class="fas fa-external-link-alt mr-1"></i>View Details
                                </a>
                            </div>
                            {% endfor %}
                        {% else %}
                            <p class="text-gray-500 text-center py-8">No internships found. Try different skills or location.</p>
                        {% endif %}
                    </div>
                </div>

                <!-- Job Suggestions -->
                <div class="bg-white rounded-2xl shadow-2xl overflow-hidden">
                    <div class="bg-gradient-to-r from-green-500 to-emerald-500 p-6">
                        <h2 class="text-2xl font-bold text-white text-center">
                            <i class="fas fa-star mr-2"></i>Job Suggestions
                        </h2>
                    </div>
                    <div class="p-6 space-y-4 max-h-96 overflow-y-auto">
                        {% if job_suggestions %}
                            {% for job in job_suggestions %}
                            <div class="card-hover bg-gradient-to-r from-green-50 to-emerald-50 p-4 rounded-xl border border-green-100">
                                <h3 class="font-bold text-lg text-gray-800">{{ job.title }}</h3>
                                {% if job.company != "N/A" %}
                                    <p class="text-gray-600">
                                        <i class="fas fa-building mr-1"></i>{{ job.company }}
                                    </p>
                                {% endif %}
                                {% if job.location != "N/A" %}
                                    <p class="text-gray-600">
                                        <i class="fas fa-map-marker-alt mr-1"></i>{{ job.location }}
                                    </p>
                                {% endif %}
                                <div class="mt-2">
                                    <span class="text-xs text-gray-500">Required Skills:</span>
                                    <p class="text-sm text-gray-700">{{ job.skills }}</p>
                                </div>
                            </div>
                            {% endfor %}
                        {% else %}
                            <p class="text-gray-500 text-center py-8">No job suggestions found. Try different skills or sectors.</p>
                        {% endif %}
                    </div>
                </div>
            </div>

            <!-- Try Again Button -->
            <div class="text-center mt-8">
                <a href="/" class="inline-flex items-center bg-gray-600 hover:bg-gray-700 text-white font-bold py-3 px-8 rounded-xl transition-all duration-300 transform hover:scale-105">
                    <i class="fas fa-redo mr-2"></i>Search Again
                </a>
            </div>
        </div>
        {% endif %}
    </div>

    <script>
        // Add some interactive effects
        document.addEventListener('DOMContentLoaded', function() {
            // Animate form elements on focus
            const inputs = document.querySelectorAll('input, select, textarea');
            inputs.forEach(input => {
                input.addEventListener('focus', function() {
                    this.parentElement.classList.add('transform', 'scale-105');
                });
                input.addEventListener('blur', function() {
                    this.parentElement.classList.remove('transform', 'scale-105');
                });
            });
        });
    </script>
</body>
</html>'''

@app.route('/', methods=['GET', 'POST'])
def index():
    internships = []
    job_suggestions = []

    if request.method == 'POST':
        # Get form data
        education = request.form.get('education')
        location = request.form.get('location')
        skills_input = request.form.get('skills')
        sectors = request.form.getlist('sectors')
        
        # Process skills (split by comma and clean)
        skills = [skill.strip() for skill in skills_input.split(',') if skill.strip()]
        
        # Fetch internships based on skills and location
        if skills:
            internships = fetch_internships(skills, location)
        
        # Get job suggestions based on skills, education, and sectors
        job_suggestions = get_job_suggestions(skills, education, sectors)

    return render_template_string(HTML_TEMPLATE, internships=internships, job_suggestions=job_suggestions)

if __name__ == '__main__':
    app.run(debug=True)
