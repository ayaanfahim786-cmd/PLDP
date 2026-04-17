import streamlit as st
import pandas as pd
import numpy as np
import json

st.set_page_config(page_title="Course Feedback Analyzer", layout="wide", page_icon="🎓")

def load_data():
    with open("course_data.json", "r") as f:
        data = json.load(f)
    return data

def process_data(data):
    # data is a list of dicts: {"CourseID", "InstructorID", "Rating", "Enrollment", "Semester", "Comments"}
    
    # Calculate per-course metrics iteratively using Python dictionaries mapped by CourseID
    course_stats = {}
    for row in data:
        cid = row["CourseID"]
        if cid not in course_stats:
            course_stats[cid] = {
                "InstructorID": row["InstructorID"],
                "Enrollment": row["Enrollment"],
                "Ratings": [],
                "Semesters": set()
            }
        course_stats[cid]["Ratings"].append(row["Rating"])
        course_stats[cid]["Semesters"].add(row["Semester"])
        
    course_list = []
    
    for cid, stats in course_stats.items():
        # Use NumPy to process arrays of ratings
        ratings = np.array(stats["Ratings"])
        avg_rating = np.mean(ratings)
        
        course_list.append({
            "Course ID": cid,
            "Instructor ID": stats["InstructorID"],
            "Enrollment": stats["Enrollment"],
            "Average Rating": round(avg_rating, 2),
            "Total Reviews": len(ratings),
            "Semesters": ", ".join(list(stats["Semesters"]))
        })
        
    return course_list, data

def inject_custom_css():
    st.markdown("""
<style>
    /* Metric cards: Matte black with gold on hover */
    div[data-testid="stMetric"] {
        background-color: #1a1a1a;
        border: 1px solid #2a2a2a;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        transition: transform 0.2s, border-color 0.2s;
        border-left: 4px solid #333333;
    }
    
    /* Make metric labels slightly muted */
    label[data-testid="stMetricLabel"] {
        color: #aaaaaa;
    }
    
    /* Metric values in crisp white */
    div[data-testid="stMetricValue"] {
        color: #ffffff;
    }
    
    /* Hover effects adding gold accents */
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        border-color: #555555;
        border-left: 4px solid #d4af37; /* Gold accent line */
        box-shadow: 0 6px 15px rgba(212, 175, 55, 0.08);
    }
    
    /* Main H1 Title in Gold */
    h1 {
        font-weight: 800 !important;
        letter-spacing: -1px;
        color: #d4af37 !important;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

def main():
    inject_custom_css()
    st.title("University Course Feedback Analyzer")
    st.markdown("Analyzing student ratings and comments.")
    
    try:
        raw_data = load_data()
    except FileNotFoundError:
        st.error("Data file not found. Please ensure you have run `python generate_data.py` to create `course_data.json`.")
        return
        
    course_data, raw_data_list = process_data(raw_data)
    
    # Sort courses by average rating
    sorted_courses = sorted(course_data, key=lambda x: x["Average Rating"], reverse=True)
    df_courses = pd.DataFrame(sorted_courses)
    
    # Calculate weighted average rating considering enrollment size
    # Using NumPy
    enrollments = np.array([c["Enrollment"] for c in sorted_courses])
    avg_ratings = np.array([c["Average Rating"] for c in sorted_courses])
    weighted_university_rating = np.average(avg_ratings, weights=enrollments)
    
    # Top-level Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Reviews Processed", len(raw_data_list))
    with col2:
        st.metric("Total Courses Analyzed", len(sorted_courses))
    with col3:
        st.metric("Global Avg Rating", f"{np.mean(avg_ratings):.2f}")
    with col4:
        st.metric("Weighted Avg Rating", f"{weighted_university_rating:.2f}",
                  help="Average rating weighted by course enrollment size")
                
    st.divider()
    
    tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "🏆 Teaching Awards", "💬 Student Comments"])
    
    with tab1:
        colA, colB = st.columns(2)
        
        with colA:
            st.subheader("📈 Leaderboard: Top Rated Courses")
            st.dataframe(
                df_courses.head(15), 
                use_container_width=True,
                column_config={
                    "Average Rating": st.column_config.NumberColumn("Average Rating", format="%.2f ⭐"),
                    "Enrollment": st.column_config.ProgressColumn("Enrollment", min_value=0, max_value=int(df_courses["Enrollment"].max()), format="%d")
                },
                hide_index=True
            )
            
        with colB:
            st.subheader("⚠️ Improvement Plans Needed (Rating < 3.0)")
            # Find courses with rating <3.0 for improvement plans
            needs_improvement = [c for c in sorted_courses if c["Average Rating"] < 3.0]
            
            if needs_improvement:
                df_improvement = pd.DataFrame(needs_improvement)
                st.dataframe(
                    df_improvement, 
                    use_container_width=True,
                    column_config={"Average Rating": st.column_config.NumberColumn("Average Rating", format="%.2f ⚠️")},
                    hide_index=True
                )
            else:
                st.success("Great news! No courses have an average rating below 3.0.")

    with tab2:
        # Identify instructors in top 15% for teaching awards
        st.subheader("🏆 Prestigious Teaching Awards (Top 15% Instructors)")
        
        instructor_stats = {}
        for row in raw_data_list:
            iid = row["InstructorID"]
            if iid not in instructor_stats:
                instructor_stats[iid] = []
            instructor_stats[iid].append(row["Rating"])
            
        instructor_list = []
        for iid, ratings in instructor_stats.items():
            instructor_list.append({
                "Instructor ID": iid,
                "Average Rating": np.mean(ratings),
                "Total Reviews": len(ratings)
            })
            
        # Sort instructors
        instructor_list.sort(key=lambda x: x["Average Rating"], reverse=True)
        
        # Get top 15%
        top_15_percent_count = max(1, int(len(instructor_list) * 0.15))
        top_instructors = instructor_list[:top_15_percent_count]
        
        df_instructors = pd.DataFrame(top_instructors)
        df_instructors["Average Rating"] = df_instructors["Average Rating"].round(2)
        
        st.dataframe(
            df_instructors, 
            use_container_width=True,
            column_config={
                "Average Rating": st.column_config.NumberColumn("Average Rating", format="%.2f ⭐"),
                "Total Reviews": st.column_config.ProgressColumn("Total Reviews", min_value=0, max_value=int(df_instructors["Total Reviews"].max()), format="%d")
            },
            hide_index=True
        )
        
    with tab3:
        # Let users explore comments
        st.subheader("💬 Dive into Student Comments")
        selected_course = st.selectbox("Select a Course ID", df_courses["Course ID"].tolist())
        
        course_comments = [row for row in raw_data_list if row["CourseID"] == selected_course]
        for c in list(course_comments)[:5]: # Display up to 5 comments
            # Convert rating to stars for better visual
            rating_stars = "⭐" * int(c["Rating"])
            with st.chat_message("user", avatar="👤"):
                st.write(f"**Semester:** {c['Semester']} &nbsp; • &nbsp; **Score:** {rating_stars}")
                st.write(f"*{c['Comments']}*")

if __name__ == "__main__":
    main()
