import json
from flask import Flask, session, render_template_string, request, redirect, url_for

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with a secure random key in production

# Load questions from a JSON file
def load_questions():
    with open('questions.json', 'r') as f:
        data = json.load(f)
    return data.get('questions', [])

# Load questions once at startup
questions = load_questions()

# Function to classify the total score
def classify_score(score):
    if 0 <= score <= 7:
        return "Normal"
    elif 8 <= score <= 13:
        return "Mild depression"
    elif 14 <= score <= 18:
        return "Moderate depression"
    elif 19 <= score <= 22:
        return "Severe depression"
    elif score >= 23:
        return "Very severe depression"
    return "Unknown"

# HTML template for the question page with enhanced animations and a two-decimal progress percentage
QUESTION_TEMPLATE = '''
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>HAM-D Questionnaire</title>
  <!-- Bootstrap CSS -->
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  <!-- Google Fonts -->
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&family=Playfair+Display:wght@500;600;700&display=swap" rel="stylesheet">
  <!-- Animate.css for enhanced animations -->
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css"/>
  <!-- Bootstrap Icons -->
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">

  <style>
    :root {
      --primary: #4361ee;
      --primary-light: #4895ef;
      --primary-dark: #3f37c9;
      --accent: #f72585;
      --accent-light: #ff85a1;
      --background: #f8f9fa;
      --text-dark: #212529;
      --text-light: #6c757d;
      --white: #ffffff;
      --card-shadow: 0 10px 40px rgba(0, 0, 0, 0.08);
      --hover-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
      --transition-main: all 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
      --transition-fast: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
    }
    
    body { 
      font-family: 'Poppins', sans-serif;
      background: radial-gradient(circle at 50% 0%, rgba(227, 242, 253, 1) 0%, rgba(241, 245, 249, 1) 100%);
      min-height: 100vh;
      transition: var(--transition-main);
      overflow-x: hidden;
    }
    
    /* Animated Background */
    .bg-animation {
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      z-index: -1;
      opacity: 0.15;
    }
    
    .bg-circle {
      position: absolute;
      border-radius: 50%;
      background: linear-gradient(135deg, var(--primary-light), var(--primary));
      opacity: 0.2;
      animation: float 15s linear infinite;
    }
    
    .bg-circle:nth-child(1) {
      top: 10%;
      left: 10%;
      width: 200px;
      height: 200px;
      animation-delay: 0s;
    }
    
    .bg-circle:nth-child(2) {
      top: 40%;
      right: 15%;
      width: 300px;
      height: 300px;
      animation-delay: 2s;
      background: linear-gradient(135deg, var(--accent-light), var(--accent));
    }
    
    .bg-circle:nth-child(3) {
      bottom: 5%;
      left: 20%;
      width: 250px;
      height: 250px;
      animation-delay: 4s;
    }
    
    @keyframes float {
      0% { transform: translateY(0) translateX(0) rotate(0); filter: blur(20px); }
      25% { transform: translateY(-20px) translateX(10px) rotate(10deg); filter: blur(15px); }
      50% { transform: translateY(0) translateX(20px) rotate(20deg); filter: blur(20px); }
      75% { transform: translateY(20px) translateX(10px) rotate(10deg); filter: blur(15px); }
      100% { transform: translateY(0) translateX(0) rotate(0); filter: blur(20px); }
    }
    
    .hospital-header {
      background: linear-gradient(135deg, var(--primary), var(--primary-dark));
      color: var(--white);
      border-radius: 0 0 60px 60px;
      box-shadow: 0 15px 35px rgba(67, 97, 238, 0.3);
      overflow: hidden;
      position: relative;
      transform-origin: top;
      transition: var(--transition-main);
      margin-bottom: 3rem;
      padding: 2.5rem 2rem;
      text-align: center;
    }
    
    .hospital-header:hover {
      transform: translateY(-5px);
      box-shadow: 0 20px 45px rgba(67, 97, 238, 0.4);
    }
    
    .header-title {
      font-family: 'Playfair Display', serif;
      font-weight: 700;
      position: relative;
      display: inline-block;
      margin-bottom: 1.5rem;
    }
    
    .header-title::after {
      content: '';
      position: absolute;
      width: 40%;
      height: 4px;
      background: var(--accent);
      bottom: -6px;
      left: 30%;
      border-radius: 2px;
    }
    
    /* Enhanced animated progress bar */
    .progress-container {
      max-width: 80%;
      margin: 1rem auto;
      position: relative;
    }
    
    .progress {
      height: 14px;
      border-radius: 50px;
      overflow: hidden;
      background-color: rgba(255, 255, 255, 0.2);
      box-shadow: inset 0 1px 5px rgba(0, 0, 0, 0.1);
      backdrop-filter: blur(5px);
    }
    
    @keyframes progressGlow {
      0% { box-shadow: 0 0 8px rgba(255, 255, 255, 0.5); }
      50% { box-shadow: 0 0 20px rgba(255, 255, 255, 0.8); }
      100% { box-shadow: 0 0 8px rgba(255, 255, 255, 0.5); }
    }
    
    @keyframes progressShine {
      0% { background-position: 0% 50%; }
      50% { background-position: 100% 50%; }
      100% { background-position: 0% 50%; }
    }
    
    .progress-bar {
      background: linear-gradient(-45deg, var(--accent-light), var(--accent), var(--primary-light), var(--primary));
      background-size: 400% 400%;
      animation: progressShine 3s ease infinite, progressGlow 2s infinite;
      box-shadow: 0 0 15px rgba(247, 37, 133, 0.7);
      transition: width 0.8s cubic-bezier(0.22, 1, 0.36, 1);
      border-radius: 50px;
      height: 100%;
      position: relative;
    }
    
    .progress-bar::after {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: linear-gradient(90deg, 
                rgba(255,255,255,0) 0%, 
                rgba(255,255,255,0.4) 50%, 
                rgba(255,255,255,0) 100%);
      animation: shine 1.5s infinite;
      background-size: 200% 100%;
    }
    
    @keyframes shine {
      0% { background-position: -200% 0; }
      100% { background-position: 200% 0; }
    }
    
    .progress-percentage {
      animation: countUp 0.5s forwards;
      font-weight: 600;
      color: var(--white);
      font-size: 1.2rem;
      text-shadow: 0 2px 4px rgba(0,0,0,0.1);
      display: block;
      margin-top: 0.5rem;
    }
    
    .question-card {
      background: var(--white);
      border-radius: 30px;
      box-shadow: var(--card-shadow);
      border: none;
      padding: 2.5rem;
      transition: var(--transition-main);
      overflow: hidden;
      position: relative;
      margin-bottom: 3rem;
    }
    
    .question-card::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      width: 6px;
      height: 100%;
      background: linear-gradient(to bottom, var(--primary), var(--accent));
    }
    
    .question-card:hover {
      transform: translateY(-10px);
      box-shadow: var(--hover-shadow);
    }
    
    .question-title {
      font-family: 'Playfair Display', serif;
      font-weight: 600;
      color: var(--primary-dark);
      position: relative;
      display: inline-block;
      margin-bottom: 2rem;
      font-size: 1.8rem;
    }
    
    .option-card {
      border-left: 5px solid var(--primary-light);
      background: linear-gradient(to right, rgba(248, 249, 250, 0.7), var(--white));
      border-radius: 15px;
      box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
      margin-bottom: 15px;
      overflow: hidden;
      transition: var(--transition-fast);
      position: relative;
    }
    
    .option-card:hover {
      transform: translateX(8px);
      border-left-color: var(--accent);
      box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
    }
    
    .option-card:hover .form-check-label {
      color: var(--primary-dark);
    }
    
    .form-check-input {
      width: 22px;
      height: 22px;
      margin-top: 0.2rem;
      border: 2px solid rgba(67, 97, 238, 0.3);
      transition: var(--transition-fast);
    }
    
    .form-check-input:checked {
      background-color: var(--primary);
      border-color: var(--primary);
      box-shadow: 0 0 0 0.25rem rgba(67, 97, 238, 0.25);
    }
    
    .form-check-label {
      padding-left: 0.5rem;
      font-weight: 500;
      transition: var(--transition-fast);
    }
    
    /* Improved entrance animations */
    @keyframes floatUp {
      from { transform: translateY(50px); opacity: 0; }
      to { transform: translateY(0); opacity: 1; }
    }
    
    @keyframes fadeInScale {
      from { transform: scale(0.9); opacity: 0; }
      to { transform: scale(1); opacity: 1; }
    }
    
    .float-up {
      opacity: 0;
      animation: floatUp 0.8s forwards;
    }
    
    .fade-scale {
      opacity: 0;
      animation: fadeInScale 0.8s forwards;
    }
    
    /* Staggered animation for options */
    .option-1 { animation-delay: 0.1s; }
    .option-2 { animation-delay: 0.2s; }
    .option-3 { animation-delay: 0.3s; }
    .option-4 { animation-delay: 0.4s; }
    .option-5 { animation-delay: 0.5s; }
    
    /* Next button styling */
    .btn-next {
      background: linear-gradient(135deg, var(--primary), var(--primary-dark));
      border: none;
      border-radius: 50px;
      padding: 14px 35px;
      font-weight: 600;
      letter-spacing: 0.5px;
      box-shadow: 0 5px 15px rgba(67, 97, 238, 0.3);
      transition: var(--transition-fast);
      color: var(--white);
      position: relative;
      overflow: hidden;
      z-index: 1;
    }
    
    .btn-next::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: linear-gradient(135deg, var(--primary-dark), var(--primary));
      opacity: 0;
      z-index: -1;
      transition: var(--transition-fast);
    }
    
    .btn-next:hover::before {
      opacity: 1;
    }
    
    .btn-next:hover {
      transform: translateY(-3px);
      box-shadow: 0 8px 25px rgba(67, 97, 238, 0.4);
      color: var(--white);
    }
    
    /* Progress percentage animation */
    @keyframes countUp {
      from { opacity: 0; transform: translateY(10px); }
      to { opacity: 1; transform: translateY(0); }
    }
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
      .hospital-header {
        border-radius: 0 0 40px 40px;
        padding: 1.5rem 1rem;
      }
      
      .question-card {
        padding: 1.5rem;
      }
      
      .header-title {
        font-size: 1.8rem;
      }
      
      .question-title {
        font-size: 1.5rem;
      }
    }
  </style>
</head>
<body>
<!-- Background Animation -->
<div class="bg-animation">
  <div class="bg-circle"></div>
  <div class="bg-circle"></div>
  <div class="bg-circle"></div>
</div>

<div class="container py-5">
  <div class="hospital-header animate__animated animate__fadeIn">
    <h1 class="header-title display-4">
      Clinical Depression Assessment
    </h1>
    <div class="progress-container">
      <div class="progress">
        <div class="progress-bar" role="progressbar" 
             style="width: {{ ((current_index + 1) / total_questions)*100 }}%;" 
             aria-valuenow="{{ ((current_index + 1) / total_questions)*100 | round(2) }}" 
             aria-valuemin="0" 
             aria-valuemax="100"></div>
      </div>
    </div>
    <span class="progress-percentage">{{ "%.2f" % (((current_index + 1) / total_questions)*100) }}% complete</span>
  </div>

  <div class="question-card fade-scale">
    <h3 class="question-title">{{ question.question }}</h3>
    
    <form method="post">
      <div class="row g-3 mt-4">
        {% for opt in question.options %}
        <div class="col-12">
          <div class="option-card p-3 float-up option-{{ loop.index }}">
            <div class="form-check">
              <input class="form-check-input" type="radio" name="answer" 
                     id="option{{ loop.index }}" value="{{ opt.score }}" required>
              <label class="form-check-label fs-5" for="option{{ loop.index }}">
                {{ opt.text }}
              </label>
            </div>
          </div>
        </div>
        {% endfor %}
      </div>

      <div class="d-grid gap-2 mt-5">
        <button type="submit" class="btn-next btn-lg py-3 float-up" style="animation-delay: 0.6s;">
          {% if current_index + 1 == total_questions %}
            <i class="bi bi-check-circle me-2"></i> Complete Assessment
          {% else %}
            Next Question <i class="bi bi-arrow-right ms-2"></i>
          {% endif %}
        </button>
      </div>
    </form>
  </div>
</div>

<footer class="text-center mt-5 mb-3">
  <p>Project by AVS</p>
</footer>

<!-- Bootstrap JS -->
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

# HTML template for the result page with enhanced animations
RESULT_TEMPLATE = '''
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Assessment Result</title>
  <!-- Bootstrap CSS -->
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  <!-- Google Fonts -->
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&family=Playfair+Display:wght@500;600;700&display=swap" rel="stylesheet">
  <!-- Animate.css -->
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css"/>
  <!-- Bootstrap Icons -->
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
  
  <style>
    :root {
      --primary: #4361ee;
      --primary-light: #4895ef;
      --primary-dark: #3f37c9;
      --accent: #f72585;
      --accent-light: #ff85a1;
      --success: #4cc9f0;
      --success-dark: #4361ee;
      --warning: #f8961e;
      --warning-dark: #f3722c;
      --danger: #f72585;
      --danger-dark: #b5179e;
      --background: #f8f9fa;
      --text-dark: #212529;
      --text-light: #6c757d;
      --white: #ffffff;
      --card-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
      --hover-shadow: 0 30px 70px rgba(0, 0, 0, 0.15);
      --transition-main: all 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
      --transition-fast: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
    }
    
    body { 
      font-family: 'Poppins', sans-serif;
      background: radial-gradient(circle at 50% 0%, rgba(227, 242, 253, 1) 0%, rgba(241, 245, 249, 1) 100%);
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      position: relative;
      overflow-x: hidden;
    }
    
    /* Background Animation */
    .bg-animation {
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      z-index: -1;
      opacity: 0.15;
    }
    
    .bg-circle {
      position: absolute;
      border-radius: 50%;
      background: linear-gradient(135deg, var(--primary-light), var(--primary));
      opacity: 0.2;
      animation: float 15s linear infinite;
    }
    
    .bg-circle:nth-child(1) {
      top: 10%;
      left: 10%;
      width: 200px;
      height: 200px;
      animation-delay: 0s;
    }
    
    .bg-circle:nth-child(2) {
      top: 40%;
      right: 15%;
      width: 300px;
      height: 300px;
      animation-delay: 2s;
      background: linear-gradient(135deg, var(--accent-light), var(--accent));
    }
    
    .bg-circle:nth-child(3) {
      bottom: 5%;
      left: 20%;
      width: 250px;
      height: 250px;
      animation-delay: 4s;
    }
    
    @keyframes float {
      0% { transform: translateY(0) translateX(0) rotate(0); filter: blur(20px); }
      25% { transform: translateY(-20px) translateX(10px) rotate(10deg); filter: blur(15px); }
      50% { transform: translateY(0) translateX(20px) rotate(20deg); filter: blur(20px); }
      75% { transform: translateY(20px) translateX(10px) rotate(10deg); filter: blur(15px); }
      100% { transform: translateY(0) translateX(0) rotate(0); filter: blur(20px); }
    }
    
    .result-card {
      background: var(--white);
      border-radius: 30px;
      box-shadow: var(--card-shadow);
      padding: 3.5rem;
      max-width: 650px;
      width: 100%;
      text-align: center;
      position: relative;
      overflow: hidden;
      transition: var(--transition-main);
      z-index: 1;
    }
    
    .result-card::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 10px;
      background: var(--primary);
      z-index: 2;
    }
    
    /* Result card background gradients */
    .result-card.normal-result {
      background: linear-gradient(135deg, rgba(76, 201, 240, 0.05), rgba(67, 97, 238, 0.05));
    }
    
    .result-card.mild-result {
      background: linear-gradient(135deg, rgba(248, 150, 30, 0.05), rgba(243, 114, 44, 0.05));
    }
    
    .result-card.severe-result {
      background: linear-gradient(135deg, rgba(247, 37, 133, 0.05), rgba(181, 23, 158, 0.05));
    }
    
    .result-card:hover {
      transform: translateY(-10px);
      box-shadow: var(--hover-shadow);
    }
    
    .result-header {
      margin-bottom: 2.5rem;
    }
    
    .result-title {
      font-family: 'Playfair Display', serif;
      font-weight: 700;
      color: var(--text-dark);
      margin-bottom: 0.5rem;
    }
    
    .severity-container {
      position: relative;
      margin-bottom: 2.5rem;
    }
    
    .severity-indicator {
      width: 140px;
      height: 140px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      margin: 0 auto;
      position: relative;
      transform-origin: center;
      transition: var(--transition-main);
      box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
    }
    
    .severity-normal {
      background: linear-gradient(135deg, var(--success), var(--success-dark));
    }
    
    .severity-mild {
      background: linear-gradient(135deg, var(--warning), var(--warning-dark));
    }
    
    .severity-severe {
      background: linear-gradient(135deg, var(--danger), var(--danger-dark));
    }
    
    .severity-indicator::before {
      content: '';
      position: absolute;
      top: -10px;
      left: -10px;
      right: -10px;
      bottom: -10px;
      border-radius: 50%;
      background: inherit;
      opacity: 0.4;
      filter: blur(10px);
      animation: pulse-ring 2s ease infinite;
    }
    
    .severity-indicator::after {
      content: '';
      position: absolute;
      top: -5px;
      left: -5px;
      right: -5px;
      bottom: -5px;
      border-radius: 50%;
      background: inherit;
      opacity: 0.6;
      filter: blur(5px);
      animation: pulse-ring 2s ease 0.5s infinite;
    }
    
    @keyframes pulse-ring {
      0% { transform: scale(0.95); opacity: 0.7; }
      50% { transform: scale(1.05); opacity: 0.3; }
      100% { transform: scale(0.95); opacity: 0.7; }
    }
    
    .severity-indicator:hover {
      transform: scale(1.1);
    }
    
    .score-display {
      font-size: 2.8rem;
      font-weight: 700;
      color: var(--white);
      text-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
      position: relative;
      z-index: 2;
    }
    
    .classification-container {
      margin-bottom: 2.5rem;
    }
    
    .classification-text {
      font-size: 2rem;
      font-weight: 600;
      margin-bottom: 1rem;
      background: linear-gradient(135deg, var(--primary-dark), var(--primary));
      -webkit-background-clip: text;
      background-clip: text;
      -webkit-text-fill-color: transparent;
      display: inline-block;
    }
    
    .classification-description {
      color: var(--text-light);
      font-size: 1.1rem;
      max-width: 80%;
      margin: 0 auto;
    }
    
    /* Button styling */
    .btn-action {
      display: inline-block;
      background: linear-gradient(135deg, var(--primary), var(--primary-dark));
      color: var(--white);
      border: none;
      border-radius: 50px;
      padding: 14px 35px;
      font-weight: 600;
      letter-spacing: 0.5px;
      box-shadow: 0 5px 15px rgba(67, 97, 238, 0.3);
      transition: var(--transition-fast);
      text-decoration: none;
      position: relative;
      overflow: hidden;
      z-index: 1;
    }
    
    .btn-action::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: linear-gradient(135deg, var(--primary-dark), var(--primary));
      opacity: 0;
      z-index: -1;
      transition: var(--transition-fast);
    }
    
    .btn-action:hover::before {
      opacity: 1;
    }
    
    .btn-action:hover {
      transform: translateY(-3px);
      box-shadow: 0 8px 25px rgba(67, 97, 238, 0.4);
      color: var(--white);
    }
    
    @keyframes fadeInUp {
      from { transform: translateY(30px); opacity: 0; }
      to { transform: translateY(0); opacity: 1; }
    }
    
    .fade-in-up {
      opacity: 0;
      animation: fadeInUp 0.8s forwards;
    }
    
    .delay-1 { animation-delay: 0.2s; }
    .delay-2 { animation-delay: 0.4s; }
    .delay-3 { animation-delay: 0.6s; }
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
      .result-card {
        padding: 2rem;
      }
      
      .result-title {
        font-size: 1.8rem;
      }
      
      .score-display {
        font-size: 2rem;
      }
      
      .classification-text {
        font-size: 1.5rem;
      }
      
      .classification-description {
        font-size: 1rem;
      }
    }
  </style>
</head>
<body>
<!-- Background Animation -->
<div class="bg-animation">
  <div class="bg-circle"></div>
  <div class="bg-circle"></div>
  <div class="bg-circle"></div>
</div>

<div class="result-card animate__animated animate__fadeIn">
  <div class="result-header">
    <h1 class="result-title">Assessment Complete</h1>
  </div>
  <div class="severity-container">
    <div class="severity-indicator {% if 'Normal' in classification %}severity-normal{% elif 'Mild' in classification %}severity-mild{% else %}severity-severe{% endif %}">
      <div class="score-display">{{ total_score }}</div>
    </div>
  </div>
  <div class="classification-container">
    <div class="classification-text">{{ classification }}</div>
    <p class="classification-description">
      Your total score suggests that your depression level is categorized as <strong>{{ classification }}</strong>.
    </p>
  </div>
  <a href="{{ url_for('restart') }}" class="btn-action">
    ↻ Restart Assessment
  </a>
</div>

<footer class="text-center mt-5 mb-3">
  <p>Project by AVS</p>
</footer>

<!-- Bootstrap JS -->
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

# Route to restart the questionnaire
@app.route("/restart")
def restart():
    session.clear()
    return redirect(url_for('question'))

# Main route to display one question at a time
@app.route("/", methods=["GET", "POST"])
@app.route("/question", methods=["GET", "POST"])
def question():
    # Initialize session variables if not already set
    if 'current_index' not in session:
        session['current_index'] = 0
        session['answers'] = []
    
    current_index = session.get('current_index', 0)
    total_questions = len(questions)
    
    # Process the answer when the form is submitted
    if request.method == "POST":
        answer = request.form.get("answer")
        if answer is not None:
            answers = session.get('answers', [])
            answers.append(int(answer))
            session['answers'] = answers
            current_index += 1
            session['current_index'] = current_index
            # If all questions answered, calculate and display the result
            if current_index >= total_questions:
                total_score = sum(session.get('answers', []))
                classification = classify_score(total_score)
                session.clear()
                return render_template_string(RESULT_TEMPLATE, total_score=total_score, classification=classification)
    
    # If not finished, display the current question
    if current_index < total_questions:
        question_data = questions[current_index]
        # Check if the question JSON includes an external image URL; if not, fallback to a local static image.
        image_url = question_data.get("image_url")
        if not image_url:
            image_url = url_for('static', filename=f'images/q{question_data["id"]}.jpg')
        return render_template_string(QUESTION_TEMPLATE,
                                      question=question_data,
                                      current_index=current_index,
                                      total_questions=total_questions,
                                      image_url=image_url)
    else:
        return redirect(url_for('restart'))

if __name__ == "__main__":
    app.run(debug=True)
