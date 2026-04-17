import json
import random

def generate_data():
    num_courses = 100
    num_students = 3000
    
    departments = ["CS", "MATH", "PHY", "ENG", "HIST", "BIO", "CHEM", "ECON", "PSY", "ART"]
    semesters = ["Fall 2023", "Spring 2024", "Fall 2024"]
    
    courses = []
    instructors = [f"Prof. {chr(65+i)}{chr(65+(i*2)%26)}" for i in range(50)] # 50 instructors
    
    # Generate 100 courses
    course_base = {}
    for i in range(num_courses):
        dept = random.choice(departments)
        course_id = f"{dept}{random.randint(100, 499)}"
        # Ensure unique course IDs
        while course_id in course_base:
             course_id = f"{dept}{random.randint(100, 499)}"
             
        enrollment = random.randint(20, 200)
        instructor = random.choice(instructors)
        
        course_base[course_id] = {
            "InstructorID": instructor,
            "Enrollment": enrollment
        }
        courses.append(course_id)

    feedback_data = []

    comments_good = ["Great course!", "Loved the lectures.", "Very informative.", "Instructor was helpful.", "Clear explanations.", "Engaging material."]
    comments_bad = ["Too much homework.", "Lectures were confusing.", "Exams were too hard.", "Not enough practice material.", "Didn't enjoy it.", "Needs better organization."]
    comments_avg = ["It was okay.", "Standard course.", "Nothing special.", "Just fine.", "Met expectations."]

    # Give each course a "true quality" to make ratings somewhat clustered around course mean
    course_qualities = {cid: random.uniform(2.0, 5.0) for cid in courses}

    for _ in range(num_students):
        cid = random.choice(courses)
        course_info = course_base[cid]
        
        # Base rating around the "true quality"
        true_q = course_qualities[cid]
        rating = round(random.gauss(true_q, 0.8))
        rating = max(1, min(5, rating)) # clamp between 1 and 5
        
        # Decide comment based on rating
        if rating >= 4:
            comment = random.choice(comments_good)
        elif rating <= 2:
            comment = random.choice(comments_bad)
        else:
            comment = random.choice(comments_avg)
            
        feedback = {
            "CourseID": cid,
            "InstructorID": course_info["InstructorID"],
            "Rating": rating,
            "Enrollment": course_info["Enrollment"],
            "Semester": random.choice(semesters),
            "Comments": comment
        }
        feedback_data.append(feedback)

    with open("course_data.json", "w") as f:
        json.dump(feedback_data, f, indent=4)
        
    print(f"Successfully generated {len(feedback_data)} feedback entries across {len(courses)} courses.")

if __name__ == "__main__":
    generate_data()
