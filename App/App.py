
###### Packages Used ######
import streamlit as st # core package used in this project
import pandas as pd
import base64, random
import time,datetime
import pymysql
import os
import socket
import platform
import geocoder
import secrets
import io,random
import re
import validate_email
import plotly.express as px
import plotly.graph_objects as go
from geopy.geocoders import Nominatim
# from streamlit.components.v1 import IFrame
# libraries used to parse the pdf files
from pyresparser import ResumeParser
from pdfminer3.layout import LAParams, LTTextBox
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.converter import TextConverter
from streamlit_tags import st_tags
from PIL import Image
import streamlit.components.v1 as components
# pre stored data for prediction purposes
from Courses import ds_course,web_course,android_course,ios_course,uiux_course,resume_videos,interview_videos, jobs_webDev_freshers, jobs_ds_freshers, jobs_android_freshers, jobs_webDev_experienced
import nltk
nltk.download('stopwords')


###### Preprocessing functions ######

# Generates a link allowing the data in a given panda dataframe to be downloaded in csv format 
def get_csv_download_link(df,filename,text):
    csv = df.to_csv(index=False)
    ## bytes conversions
    b64 = base64.b64encode(csv.encode()).decode()      
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href




# Reads Pdf file and check_extractable
def pdf_reader(file):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    with open(file, 'rb') as fh:
        for page in PDFPage.get_pages(fh,
                                      caching=True,
                                      check_extractable=True):
            page_interpreter.process_page(page)
            # print(page)
        text = fake_file_handle.getvalue()

    ## close open handles
    converter.close()
    fake_file_handle.close()
    return text


# show uploaded file path to view pdf_display
def show_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)


# // Checking with css

def course_recommender(course_list):
    st.markdown('''<hr>''',unsafe_allow_html=True)
    st.markdown('''<h2 style = 'text-align:center; font-weight:bolder;'>Course Suggestions</h2>''',unsafe_allow_html=True)
    # st.subheader("**Course Suggestions**")
    c = 0
    rec_course = []
    
    random.shuffle(course_list)
    for c_name, c_link in course_list:
        c += 1
        video_id = c_link.split("/")[-1]
        video_url = f"https://www.youtube.com/embed/{video_id}"
        iframe = f'<iframe style="display:block;margin:auto;" width="560" height="315" src="{video_url}" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>'
        st.markdown('''<hr>''',unsafe_allow_html=True)
        st.markdown(f"<div style='text-align:center; font-weight:bolder; font-size:1.5rem; margin-bottom:5%;'>({c}) {c_name}</div>", unsafe_allow_html=True)
        # st.write(f"**({c}) {c_name}**")


        st.markdown(iframe, unsafe_allow_html=True)
        rec_course.append(c_name)

    return rec_course


def jobs_recommender(jobs_list):
    # with st.spinner('Looking for job openings...'):
    #     time.sleep(4)
    st.markdown('''<hr>''',unsafe_allow_html=True)
    st.markdown('''<h2 style='text-align:center; font-weight:bolder;'>Checkout some jobs available according to your resume</h2>''',unsafe_allow_html=True)
    
    rec_jobs = []
    random.shuffle(jobs_list)
    
    for i, (job_title, job_link) in enumerate(jobs_list):
        st.markdown(f"<div class='job-container'><div class='job-count'>{i+1}</div><div class='job-details'><a href='{job_link}'>{job_title}</a></div></div>", unsafe_allow_html=True)
        rec_jobs.append(job_title)
    
    st.markdown("""
        <style>
            .job-container {
                display: flex;
                flex-direction: row;
                justify-content: flex-start;
                align-items: center;
                margin: 20px 0px;
                border-bottom: 1px solid #ccc;
            }
            .job-count {
                font-size: 20px;
                font-weight: bold;
                margin-right: 10px;
            }
            .job-details {
                flex: 1;
            }
            .job-details a {
                text-decoration: none;
                color: #039be5;
                font-size: 18px;
                font-weight: bold;
            }
            .job-details a:hover {
                text-decoration: underline;
                transform: scale(1.05);
            }
        </style>
    """, unsafe_allow_html=True)
    
    return rec_jobs

###### Database Stuffs ######


# sql connector
connection = pymysql.connect(host='localhost',user='root',password='ghrceproject@54536',db='cv')
cursor = connection.cursor()



# inserting miscellaneous data, fetched results, prediction and recommendation into user_data table
# def insert_data(sec_token,ip_add,host_name,dev_user,os_name_ver,latlong,city,state,country,act_name,act_mail,act_mob,name,email,res_score,timestamp,no_of_pages,reco_field,cand_level,skills,recommended_skills,courses,pdf_name):
   
#     DB_table_name = 'user_data'
#     insert_sql = "insert into " + DB_table_name + """
#     values (0,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
#     rec_values = (str(sec_token),str(ip_add),host_name,dev_user,os_name_ver,str(latlong),city,state,country,act_name,act_mail,act_mob,name,email,str(res_score),timestamp,str(no_of_pages),reco_field,cand_level,skills,recommended_skills,courses,pdf_name)
#     cursor.execute(insert_sql, rec_values)
#     connection.commit()


def insert_data(sec_token, ip_add, host_name, dev_user, os_name_ver, latlong, city, state, country, act_name, act_mail, act_mob, name, email, res_score, timestamp, no_of_pages, reco_field, cand_level, skills, recommended_skills, courses, pdf_name):
    DB_table_name = 'user_data'
    select_sql = "SELECT * FROM " + DB_table_name + " WHERE act_mail = %s"
    insert_sql = "INSERT INTO " + DB_table_name + " VALUES (0,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    rec_values = (str(sec_token), str(ip_add), host_name, dev_user, os_name_ver, str(latlong), city, state, country, act_name, act_mail, act_mob, name, email, str(res_score), timestamp, str(no_of_pages), reco_field, cand_level, skills, recommended_skills, courses, pdf_name)
    cursor.execute(select_sql, (act_mail,))
    result = cursor.fetchone()
    if result is None:
        cursor.execute(insert_sql, rec_values)
        connection.commit()
        return True
    else:
        return False


###### Setting Page Configuration (favicon, Logo, Title) ######


st.set_page_config(
   page_title="Smart Resume Reviewer",
   page_icon='./Logo/recommend.png',
)


###### Main function run() ######


def run():
    
    # (Logo, Heading, Sidebar etc)
    # img = Image.open('./Logo/RESUM.png')
    # st.image(img)
    st.markdown('''<h1>Smart resume Reviewer</h1> ''', unsafe_allow_html=True)
    st.sidebar.markdown("# Panel ")
    activities = ["User", "About", "Admin"]
    choice = st.sidebar.selectbox("Choose among the given options:", activities)
    link = '<b>Built with 🤍 by Group B_01</b>' 
    st.sidebar.markdown(link, unsafe_allow_html=True)

    ###### Creating Database and Table ######


    # Create the DB
    db_sql = """CREATE DATABASE IF NOT EXISTS CV;"""
    cursor.execute(db_sql)


    # Create table user_data and user_feedback
    DB_table_name = 'user_data'
    table_sql = "CREATE TABLE IF NOT EXISTS " + DB_table_name + """
                    (ID INT NOT NULL AUTO_INCREMENT,
                    sec_token varchar(20) NOT NULL,
                    ip_add varchar(50) NULL,
                    host_name varchar(50) NULL,
                    dev_user varchar(50) NULL,
                    os_name_ver varchar(50) NULL,
                    latlong varchar(50) NULL,
                    city varchar(50) NULL,
                    state varchar(50) NULL,
                    country varchar(50) NULL,
                    act_name varchar(50) NOT NULL,
                    act_mail varchar(50) NOT NULL,
                    act_mob varchar(20) NOT NULL,
                    Name varchar(500) NOT NULL,
                    Email_ID VARCHAR(500) NOT NULL,
                    resume_score VARCHAR(8) NOT NULL,
                    Timestamp VARCHAR(50) NOT NULL,
                    Page_no VARCHAR(5) NOT NULL,
                    Predicted_Field BLOB NOT NULL,
                    User_level BLOB NOT NULL,
                    Actual_skills BLOB NOT NULL,
                    Recommended_skills BLOB NOT NULL,
                    Recommended_courses BLOB NOT NULL,
                    pdf_name varchar(50) NOT NULL,
                    PRIMARY KEY (ID)
                    );
                """
    cursor.execute(table_sql)


    DBf_table_name = 'user_feedback'
    tablef_sql = "CREATE TABLE IF NOT EXISTS " + DBf_table_name + """
                    (ID INT NOT NULL AUTO_INCREMENT,
                        feed_name varchar(50) NOT NULL,
                        feed_email VARCHAR(50) NOT NULL,
                        feed_score VARCHAR(5) NOT NULL,
                        comments VARCHAR(100) NULL,
                        Timestamp VARCHAR(50) NOT NULL,
                        PRIMARY KEY (ID)
                    );
                """
    cursor.execute(tablef_sql)


    ###### CODE FOR CLIENT SIDE (USER) ######

    if choice == 'User':
        
        # Collecting Miscellaneous Information
        
        act_name = st.text_input('Enter your Name')
        act_mail = st.text_input('Enter your E-mail', placeholder='example@exmaple.com')
        # # pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        # is_valid_email = re.match(pattern, act_mail)

        # if not is_valid_email:
        #     st.error('Please enter a valid email address.')
        is_valid_email = validate_email.validate_email(act_mail)

        if not is_valid_email and act_mail.strip()!='':
            st.warning('Invalid E-mail format')
        else:

            act_mob  = st.text_input('Enter your Mobile Number')

            sec_token = secrets.token_urlsafe(12)
            host_name = socket.gethostname()
            ip_add = socket.gethostbyname(host_name)
            dev_user = os.getlogin()
            # os_name_ver = platform.system() + " " + platform.release()
            os_name_ver = st.text_input('Enter your college')
            g = geocoder.ip('me')
            latlong = g.latlng
            geolocator = Nominatim(user_agent="geoapiExercises")
            location = geolocator.reverse(latlong, language='en')
            address = location.raw['address']
            cityy = address.get('city', '')
            statee = address.get('state', '')
            countryy = address.get('country', '')  
            city = cityy
            state = statee
            country = countryy


            # Upload Resume
            st.markdown('''<h5 style='text-align: left; color: #021659;'> Upload Your Resume</h5>''',unsafe_allow_html=True)
            
            ## file upload in pdf format
            pdf_file = st.file_uploader("Choose your Resume", type=["pdf"])
            if pdf_file is not None:
                with st.spinner('Processing your resume...'):
                    time.sleep(4)
            
                ### saving the uploaded resume to folder
                save_image_path = './Uploaded_Resumes/'+pdf_file.name
                pdf_name = pdf_file.name
                with open(save_image_path, "wb") as f:
                    f.write(pdf_file.getbuffer())
                show_pdf(save_image_path)

                ### parsing and extracting whole resume 
                resume_data = ResumeParser(save_image_path).get_extracted_data()
                if resume_data:
                    
                    ## Get the whole resume data into resume_text
                    resume_text = pdf_reader(save_image_path)

                    ## Showing Analyzed data from (resume_data)
                    st.markdown('''<hr>''',unsafe_allow_html=True)
                    st.success("Hello "+ resume_data['name'])
                    st.markdown('''<h1 style= 'text-align:center; font-weight:bolder' >Processed Data</h1>''',unsafe_allow_html=True)
                    # st.header("**Processed Data**")
                    # st.success("Hello "+ resume_data['name'])
                    st.subheader("**Your Basic info**")
                    try:
                        st.text('Name: '+resume_data['name'])
                        st.text('Email: ' + resume_data['email'])
                        st.text('Contact: ' + resume_data['mobile_number'])
                        st.text('Degree: '+str(resume_data['degree']))                    
                        st.text('Resume pages: '+str(resume_data['no_of_pages']))

                    except:
                        pass


                    ## Predicting Candidate Experience Level 

                    ### Trying with different possibilities
                    cand_level = ''
                    if resume_data['no_of_pages'] < 1:
                        cand_level = "NA"
                        st.markdown('''<h4 style='text-align: left; color: #990099;'>Candidate level : Fresher</h4>''', unsafe_allow_html=True)
                    elif any(x in resume_text.upper() for x in ['EXPERIENCE', 'WORK EXPERIENCE']):
                        cand_level = "Experienced"
                        st.markdown('''<h4 style='text-align: left; color: #990099;'>Candidate level : Experienced</h4>''', unsafe_allow_html=True)
                    elif any(x in resume_text.upper() for x in ['INTERNSHIP', 'INTERNSHIPS']):
                        cand_level = "Intermediate"
                        st.markdown('''<h4 style='text-align: left; color: #990099;'>Candidate level : Intermediate</h4>''', unsafe_allow_html=True)
                    else:
                        cand_level = "Fresher"
                        st.markdown('''<h4 style='text-align: left; color: #990099;'>Candidate level : Fresher</h4>''', unsafe_allow_html=True)





                    ## Skills Analyzing and Recommendation
                    # st.subheader("**Skills Recommendation 💡**")
                    st.markdown('''<hr>''',unsafe_allow_html=True)
                    ### Current Analyzed Skills
                    st.markdown('''<h1 style='text-align: center; font-weight:bolder margin-bottom:20px'>Analysis</h1>''',unsafe_allow_html=True)
                    keywords = st_tags(label='### Your Current Skills',
                    text='See suggestions below!',value=resume_data['skills'],key = '1  ')

                    ### Keywords for Recommendations
                    ds_keyword = ['tensorflow','keras','pytorch','machine learning','deep Learning','flask','streamlit']
                    web_keyword = ['react', 'django', 'node jS', 'react js', 'php', 'laravel', 'magento', 'wordpress','javascript', 'angular js', 'C#', 'Asp.net', 'flask', 'html', 'css']
                    android_keyword = ['android','android development','flutter','kotlin','xml','kivy']
                    ios_keyword = ['ios','ios development','swift','cocoa','cocoa touch','xcode']
                    uiux_keyword = ['ux','adobe xd','figma','zeplin','balsamiq','ui','prototyping','wireframes','storyframes','adobe photoshop','photoshop','editing','adobe illustrator','illustrator','adobe after effects','after effects','adobe premier pro','premier pro','adobe indesign','indesign','wireframe','solid','grasp','user research','user experience']
                    n_any = ['english','communication','writing', 'microsoft office', 'leadership','customer management', 'social media']
                    ### Skill Recommendations Starts                
                    recommended_skills = []
                    reco_field = ''
                    rec_course = ''

                    ### condition starts to check skills from keywords and predict field
                    for i in resume_data['skills']:
                        # st.text('Resume skills: '+i.lower())
                        #### Data science recommendation
                        if i.lower() in ds_keyword:
                            print(i.lower())
                            reco_field = 'Data Science'
                            st.success("** Our analysis says you are looking for Data Science Jobs.**")
                            recommended_skills = ['Data Visualization','Predictive Analysis','Statistical Modeling','Data Mining','Clustering & Classification','Data Analytics','Quantitative Analysis','Web Scraping','ML Algorithms','Keras','Pytorch','Probability','Scikit-learn','Tensorflow',"Flask",'Streamlit']
                            recommended_keywords = st_tags(label='### Suggested skills for you..',
                            text='Recommended skills generated from System',value=recommended_skills,key = '2')
                            st.markdown('''<h5 style='text-align: left; color: #990099;'>Consider learning some skills among these which can increase your chances of resume shortlisting!!</h5>''',unsafe_allow_html=True)
                            # course recommendation
                            rec_course = course_recommender(ds_course)
                            rec_jobs = jobs_recommender(jobs_ds_freshers)
                            break

                        #### Web development recommendation
                        elif i.lower() in web_keyword:
                            print(i.lower())
                            reco_field = 'Web Development'
                            st.success("** Our analysis says you are looking for Web Development Jobs **")
                            recommended_skills = ['React','Django','Node JS','React JS','php','wordpress','Javascript','Angular JS']
                            recommended_keywords = st_tags(label='### Suggested skills for you..',
                            text='Recommended skills generated from System',value=recommended_skills,key = '3')
                            st.markdown('''<h5 style='text-align: left; color: #990099;'>Consider learning some skills among these which can increase your chances of resume shortlisting!!</h5>''',unsafe_allow_html=True)
                            # course recommendation
                            rec_course = course_recommender(web_course)
                            if cand_level=="Fresher" or cand_level=="Intermediate":
                                rec_jobs = jobs_recommender(jobs_webDev_freshers)

                            elif cand_level=="Experienced":
                                rec_jobs = jobs_recommender(jobs_webDev_experienced)
                            break

                        #### Android App Development
                        elif i.lower() in android_keyword:
                            print(i.lower())
                            reco_field = 'Android Development'
                            st.success("** Our analysis says you are looking for Android App Development Jobs **")
                            recommended_skills = ['Android','Android development','Flutter','Kotlin','XML','Java','Kivy','GIT','SDK','SQLite']
                            recommended_keywords = st_tags(label='### Suggested skills for you..',
                            text='Recommended skills generated from System',value=recommended_skills,key = '4')
                            st.markdown('''<h5 style='text-align: left; color: #990099;'>Consider learning some skills among these which can increase your chances of resume shortlisting!!</h5>''',unsafe_allow_html=True)
                            # course recommendation
                            rec_course = course_recommender(android_course)
                            rec_jobs = jobs_recommender(jobs_android_freshers)
                            break

                        #### IOS App Development
                        elif i.lower() in ios_keyword:
                            print(i.lower())
                            reco_field = 'IOS Development'
                            st.success("** Our analysis says you are looking for IOS App Development Jobs **")
                            recommended_skills = ['IOS','IOS Development','Swift','Cocoa','Cocoa Touch','Xcode','Objective-C','SQLite','Plist','StoreKit',"UI-Kit",'AV Foundation','Auto-Layout']
                            recommended_keywords = st_tags(label='### Suggested skills for you..',
                            text='Recommended skills generated from System',value=recommended_skills,key = '5')
                            st.markdown('''<h5 style='text-align: left; color: #990099;'>Consider learning some skills among these which can increase your chances of resume shortlisting!!</h5>''',unsafe_allow_html=True)
                            # course recommendation
                            rec_course = course_recommender(ios_course)
                            break

                        #### Ui-UX Recommendation
                        elif i.lower() in uiux_keyword:
                            print(i.lower())
                            reco_field = 'UI-UX Development'
                            st.success("** Our analysis says you are looking for UI-UX Development Jobs **")
                            recommended_skills = ['UI','User Experience','Adobe XD','Figma','Zeplin','Balsamiq','Prototyping','Wireframes','Storyframes','Adobe Photoshop','Editing','Illustrator','After Effects','Premier Pro','Indesign','Wireframe','Solid','Grasp','User Research']
                            recommended_keywords = st_tags(label='### Suggested skills for you..',
                            text='Recommended skills generated from System',value=recommended_skills,key = '6')
                            st.markdown('''<h5 style='text-align: left; color: #990099;'>Consider learning some skills among these which can increase your chances of resume shortlisting!!</h5>''',unsafe_allow_html=True)
                            # course recommendation
                            rec_course = course_recommender(uiux_course)
                            break

                    st.markdown('''<hr>''',unsafe_allow_html=True)

                    ## Resume Scorer & Resume Writing Tips
                    st.markdown('''<h3 style='text-align: center; font-weight:bolder margin-bottom:20px'>Resume suggestions</h3>''',unsafe_allow_html=True)
                    # st.subheader("**Resume suggestions**")
                    resume_score = 0
                    
                    ### Predicting Whether these key points are added to the resume
                    if 'Objective' or 'Summary' in resume_text:
                        resume_score = resume_score+6
                        st.markdown('''<h5 style='text-align: left; color: #008000; margin-top:15px;'>> Awesome! You have added Objective/Summary</h4>''',unsafe_allow_html=True)                
                    else:
                        st.markdown('''<h5 style='text-align: left; color: #ff4d4d; margin-top:10px;'>! Please add your career objective as it states your career goals.</h4>''',unsafe_allow_html=True)

                    if 'Education' or 'School' or 'College'  in resume_text:
                        resume_score = resume_score + 12
                        st.markdown('''<h5 style='text-align: left; color: #008000;'>> Awesome! You have added Education Details</h4>''',unsafe_allow_html=True)
                    else:
                        st.markdown('''<h5 style='text-align: left; color: #ff4d4d;'>! Please add Education. It will give Your Qualification level to the recruiter</h4>''',unsafe_allow_html=True)

                    if 'INTERNSHIPS'  in resume_text:
                        resume_score = resume_score + 6
                        st.markdown('''<h5 style='text-align: left; color: #008000;'>> Awesome! You have added Internships</h4>''',unsafe_allow_html=True)
                    elif 'INTERNSHIP'  in resume_text:
                        resume_score = resume_score + 6
                        st.markdown('''<h5 style='text-align: left; color: #008000;'>> Awesome! You have added Internships</h4>''',unsafe_allow_html=True)
                    elif 'Internships'  in resume_text:
                        resume_score = resume_score + 6
                        st.markdown('''<h5 style='text-align: left; color: #008000;'>> Awesome! You have added Internships</h4>''',unsafe_allow_html=True)
                    elif 'Internship'  in resume_text:
                        resume_score = resume_score + 6
                        st.markdown('''<h5 style='text-align: left; color: #008000;'>> Awesome! You have added Internships</h4>''',unsafe_allow_html=True)
                    else:
                        st.markdown('''<h5 style='text-align: left; color: #ff4d4d;'>! Please add Internships if any. It will help you to stand out from the crowd</h4>''',unsafe_allow_html=True)

                    # List of skills keywords

                    st.markdown('''<h5 style='text-align: left; color: #008000;'>> Awesome! You have added Skills</h4>''',unsafe_allow_html=True)
                    # skills_keywords = ['SKILLS', 'SKILL', 'Skills', 'Skill']

                    # # Check if any of the skills keywords are present in the resume_text variable
                    # if any(keyword in resume_text for keyword in skills_keywords):
                    #     resume_score += 7
                    #     st.markdown('''<h5 style='text-align: left; color: #008000;'>> Awesome! You have added Skills</h4>''',unsafe_allow_html=True)
                    # else:
                    #     st.markdown('''<h5 style='text-align: left; color: #ff4d4d;'>! Please add Skills as it's a must for any job</h4>''',unsafe_allow_html=True)


                    if 'HOBBIES' in resume_text:
                        resume_score = resume_score + 4
                        st.markdown('''<h5 style='text-align: left; color: #008000;'>> Awesome! You have added your Hobbies</h4>''',unsafe_allow_html=True)
                    elif 'Hobbies' in resume_text:
                        resume_score = resume_score + 4
                        st.markdown('''<h5 style='text-align: left; color: #008000;'>> Awesome! You have added your Hobbies</h4>''',unsafe_allow_html=True)
                    else:
                        st.markdown('''<h5 style='text-align: left; color: #ff4d4d;'>! Please add Hobbies as it plays an important role in demonstrating how you'll relate to the company's culture.</h4>''',unsafe_allow_html=True)


                    if 'ACHIEVEMENTS' in resume_text:
                        resume_score = resume_score + 13
                        st.markdown('''<h5 style='text-align: left; color: #008000;'>> Awesome! You have added your Achievements </h4>''',unsafe_allow_html=True)
                    elif 'Achievements' in resume_text:
                        resume_score = resume_score + 13
                        st.markdown('''<h5 style='text-align: left; color: #008000;'>> Awesome! You have added your Achievements </h4>''',unsafe_allow_html=True)
                    else:
                        st.markdown('''<h5 style='text-align: left; color: #ff4d4d;'>! Please add Extra-Curricular activities if any as it can give recruiters an idea of skills and personal qualities that can be an asset to their companies.</h4>''',unsafe_allow_html=True)

                    if 'CERTIFICATIONS' in resume_text:
                        resume_score = resume_score + 12
                        st.markdown('''<h5 style='text-align: left; color: #008000;'>> Awesome! You have added your Certifications </h4>''',unsafe_allow_html=True)
                    elif 'Certifications' in resume_text:
                        resume_score = resume_score + 12
                        st.markdown('''<h5 style='text-align: left; color: #008000;'>> Awesome! You have added your Certifications </h4>''',unsafe_allow_html=True)
                    elif 'Certification' in resume_text:
                        resume_score = resume_score + 12
                        st.markdown('''<h5 style='text-align: left; color: #008000;'>> Awesome! You have added your Certifications </h4>''',unsafe_allow_html=True)
                    else:
                        st.markdown('''<h5 style='text-align: left; color: #ff4d4d;'>! Please add Certifications. It will show that you have done some specialization for the required position.</h4>''',unsafe_allow_html=True)

                    if 'PROJECTS' in resume_text:
                        resume_score = resume_score + 19
                        st.markdown('''<h5 style='text-align: left; color: #008000;'>> Awesome! You have added your Projects</h4>''',unsafe_allow_html=True)
                    elif 'PROJECT' in resume_text:
                        resume_score = resume_score + 19
                        st.markdown('''<h5 style='text-align: left; color: #008000;'>> Awesome! You have added your Projects</h4>''',unsafe_allow_html=True)
                    elif 'Projects' in resume_text:
                        resume_score = resume_score + 19
                        st.markdown('''<h5 style='text-align: left; color: #008000;'>> Awesome! You have added your Projects</h4>''',unsafe_allow_html=True)
                    elif 'Project' in resume_text:
                        resume_score = resume_score + 19
                        st.markdown('''<h5 style='text-align: left; color: #008000;'>> Awesome! You have added your Projects</h4>''',unsafe_allow_html=True)
                    else:
                        st.markdown('''<h5 style='text-align: left; color: #ff4d4d;'>! Please add Projects as it shows how well you can implement the skills you have practically.</h4>''',unsafe_allow_html=True)

                    
                    st.markdown('''<hr>''',unsafe_allow_html=True)

                    # st.subheader("**Resume Score 📝**")
                    
                    # st.markdown(
                    #     """
                    #     <style>
                    #         .stProgress > div > div > div > div {
                    #             background-color: #d73b5c;
                    #         }
                    #     </style>""",
                    #     unsafe_allow_html=True,
                    # )

                    # ### Score Bar
                    # my_bar = st.progress(0)
                    # score = 0
                    # for percent_complete in range(resume_score):
                    #     score +=1
                    #     time.sleep(0.1)
                    #     my_bar.progress(percent_complete + 1)

                    # ### Score
                    # st.success('** Your Resume Writing Score: ' + str(score)+'**')
                    # st.warning("** Note: This score is calculated based on the content that you have in your Resume. **")

                    # print(str(sec_token), str(ip_add), (host_name), (dev_user), (os_name_ver), (latlong), (city), (state), (country), (act_name), (act_mail), (act_mob), resume_data['name'], resume_data['email'], str(resume_score), timestamp, str(resume_data['no_of_pages']), reco_field, cand_level, str(resume_data['skills']), str(recommended_skills), str(rec_course), pdf_name)


                    ### Getting Current Date and Time
                    ts = time.time()
                    cur_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                    cur_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                    timestamp = str(cur_date+'_'+cur_time)


                else:
                    st.error('Something went wrong..')  



    ## Insert into the database (On hold!!!). Insert here on 4th progress seminar
                # st.markdown('''<p>Checking occ next should print in insert</p>''',unsafe_allow_html=True)
                insert_data(str(sec_token), str(ip_add), (host_name), (dev_user), (os_name_ver), (latlong), (city), (state), (country), (act_name), (act_mail), (act_mob), resume_data['name'], resume_data['email'], str(resume_score), timestamp, str(resume_data['no_of_pages']), reco_field, cand_level, str(resume_data['skills']), str(recommended_skills), str(rec_course), pdf_name)


                # st.markdown('''<p>Checking occ in user</p>''',unsafe_allow_html=True)
                checkName = act_mail

                        ### Fetch user data from user_data(table) and convert it into dataframe
                        # Define the SQL query with a parameter placeholder
                query = '''
                SELECT ID, sec_token, act_name, act_mail, act_mob, convert(Predicted_Field using utf8), Timestamp, Name, Email_ID, Page_no, pdf_name, convert(User_level using utf8), convert(Actual_skills using utf8), convert(Recommended_skills using utf8), convert(Recommended_courses using utf8), state, country 
                FROM user_data 
                WHERE act_mail = %s
                '''

                        # Execute the query with the parameter
                cursor.execute(query, (checkName,))
                data = cursor.fetchall()                

                st.header("**User's Data**")
                df = pd.DataFrame(data, columns=['ID', 'Token', 'Name', 'E-mail', 'Mobile Number', 'Predicted_Field', 'Timestamp','Extracted Name', 'Extracted Mail', 'Total Pages',  'File Name','User Level', 'Actual_skills', 'Recommended Skills', 'Recommended Course', 'State', 'Country'])
                        
                        ### Viewing the dataframe
                st.dataframe(df)
                        
                        ### Downloading Report of user_data in csv file
                st.markdown(get_csv_download_link(df,'User_Data.csv','Download Report'), unsafe_allow_html=True)
                # st.markdown('''<p>Done</p>''',unsafe_allow_html=True)
                st.markdown('''<hr>''',unsafe_allow_html=True)






             
                              
    
    ###### CODE FOR ABOUT PAGE ######
    elif choice == 'About':   

        # st.subheader("**About The Tool - AI RESUME ANALYZER**")

        st.markdown('''

        <p align='justify'>
            A tool which parses information from a resume using natural language processing and finds the keywords, cluster them onto sectors based on their keywords. And lastly show tips, analytics to the applicant based on keyword matching.
        </p>

        <p align="justify">
            <b>How to use it: -</b> <br/><br/>
            <b>User -</b> <br/>
            In the Side Bar choose yourself as user and fill the required fields and upload your resume in pdf format.<br/>
            Our tool will then analyze your resume and will show you the results.<br/><br/>
            <b>Admin -</b> <br/>
            This is only for the admin use. Admin can login using the username and password<br/>
            It will load all the required stuffs and perform analysis.
        </p><br/><br/>

        <p align="justify">
            Built with 🤍 by Group B_01
            <!-- <a href="https://dnoobnerd.netlify.app/" style="text-decoration: none; color: grey;">Deepak Padhi</a> through 
            <a href="https://www.linkedin.com/in/mrbriit/" style="text-decoration: none; color: grey;">Dr Bright --(Data Scientist)</a> -->
        </p>

        ''',unsafe_allow_html=True)  


    ###### CODE FOR ADMIN SIDE (ADMIN) ######
    else:
        st.success('Welcome to Admin Side')

        #  Admin Login
        ad_user = st.text_input("Username")
        ad_password = st.text_input("Password", type='password')
        if st.button('Login'):
            
            ## Credentials 
            if ad_user == 'admin' and ad_password == 'admin@resume-analyzer':
                
                ### Fetch miscellaneous data from user_data(table) and convert it into dataframe
                clg_name = 'GHRCE'
                query1 = '''SELECT ID, ip_add, resume_score, convert(Predicted_Field using utf8), convert(User_level using utf8), city, state, country from user_data WHERE os_name_ver=%s'''
                cursor.execute(query1, (clg_name,))
                # cursor.execute('''SELECT ID, ip_add, resume_score, convert(Predicted_Field using utf8), convert(User_level using utf8), city, state, country from user_data''')
                datanalys = cursor.fetchall()
                plot_data = pd.DataFrame(datanalys, columns=['Idt', 'IP_add', 'resume_score', 'Predicted_Field', 'User_Level', 'City', 'State', 'Country'])
                
                ### Total Users Count with a Welcome Message
                values = plot_data.Idt.count()
                st.success("Welcome!! Total users %d " % values)                
                
                ### Fetch user data from user_data(table) and convert it into dataframe
                
                query = '''SELECT ID, sec_token, act_name, act_mail, act_mob, os_name_ver,convert(Predicted_Field using utf8), Timestamp, Name, Email_ID, Page_no, pdf_name, convert(User_level using utf8), convert(Actual_skills using utf8), convert(Recommended_skills using utf8), convert(Recommended_courses using utf8), state, country from user_data WHERE os_name_ver = %s'''

                cursor.execute(query, (clg_name,))

                # cursor.execute('''SELECT ID, sec_token, act_name, act_mail, act_mob, os_name_ver,convert(Predicted_Field using utf8), Timestamp, Name, Email_ID, Page_no, pdf_name, convert(User_level using utf8), convert(Actual_skills using utf8), convert(Recommended_skills using utf8), convert(Recommended_courses using utf8), state, country from user_data''')
                data = cursor.fetchall()                

                st.header("**User's Data**")
                df = pd.DataFrame(data, columns=['ID', 'Token', 'Name', 'E-mail', 'Mobile Number', 'College','Predicted_Field', 'Timestamp','Extracted Name', 'Extracted Mail', 'Total Pages',  'File Name','User Level', 'Actual_skills', 'Recommended Skills', 'Recommended Course', 'State', 'Country'])
                
                ### Viewing the dataframe
                st.dataframe(df)
                
                ### Downloading Report of user_data in csv file
                st.markdown(get_csv_download_link(df,'User_Data.csv','Download Report'), unsafe_allow_html=True)

                st.markdown('''<hr>''',unsafe_allow_html=True)
                

                # fetching Predicted_Field from the query and getting the unique values and total value count                 
                # labels = plot_data.Predicted_Field.unique()
                # values = plot_data.Predicted_Field.value_counts()

                # Pie chart for predicted field recommendations
                # st.subheader("**Pie-Chart for Predicted Field Recommendation**")
                # st.markdown('''<h2 style = 'text-align:center; font-weight:bolder;'>Pie Chart for Domains</h2>''',unsafe_allow_html=True)
                # fig = px.pie(df, values=values, names=labels, color_discrete_sequence=px.colors.sequential.Aggrnyl_r)
                # st.plotly_chart(fig)


                # labels = df.Predicted_Field.unique()
                # values = df.Predicted_Field.value_counts()

                # Pie chart for predicted field recommendations
                # st.markdown('''<h2 style='text-align:center; font-weight:bolder;'>Pie Chart for Domains</h2>''', unsafe_allow_html=True)
                # fig = px.pie(df, values=values, names=labels, color_discrete_sequence=px.colors.sequential.Aggrnyl_r)
                # st.plotly_chart(fig)


                labels = plot_data.Predicted_Field.value_counts().index.tolist()
                values = plot_data.Predicted_Field.value_counts().tolist()

                # Pie chart for predicted field recommendations
                st.markdown('''<h2 style = 'text-align:center; font-weight:bolder;'>Pie Chart for Domains</h2>''',unsafe_allow_html=True)
                fig = px.pie(df, values=values, names=labels, color_discrete_sequence=px.colors.qualitative.Alphabet)
                st.plotly_chart(fig)








                st.markdown('''<hr>''',unsafe_allow_html=True)
                # fetching User_Level from the query and getting the unique values and total value count                 
                labels = plot_data.User_Level.unique()
                values = plot_data.User_Level.value_counts()

                # Pie chart for User's👨‍💻 Experienced Level
                # st.subheader("**Pie-Chart for User's Experienced Level**")
                st.markdown('''<h2 style = 'text-align:center; font-weight:bolder;'>Pie Chart based on experience</h2>''',unsafe_allow_html=True)
                fig = px.pie(df, values=values, names=labels, color_discrete_sequence=px.colors.qualitative.Set2)
                st.plotly_chart(fig)


                # fetching IP_add from the query and getting the unique values and total value count 
                # labels = plot_data.IP_add.unique()
                # values = plot_data.IP_add.value_counts()

                # Pie chart for Users
                # st.subheader("**Pie-Chart for Users App Used Count**")
                # fig = px.pie(df, values=values, names=labels, title='Usage Based On IP Address 👥', color_discrete_sequence=px.colors.sequential.matter_r)
                # st.plotly_chart(fig)

                # fetching City from the query and getting the unique values and total value count 
                # labels = plot_data.City.unique()
                # values = plot_data.City.value_counts()

                # Pie chart for City
                # st.subheader("**Pie-Chart for City**")
                # fig = px.pie(df, values=values, names=labels, title='Usage Based On City 🌆', color_discrete_sequence=px.colors.sequential.Jet)
                # st.plotly_chart(fig)

                # fetching State from the query and getting the unique values and total value count 
                # labels = plot_data.State.unique()
                # values = plot_data.State.value_counts()

                # Pie chart for State
                # st.subheader("**Pie-Chart for State**")
                # fig = px.pie(df, values=values, names=labels, title='Usage Based on State 🚉', color_discrete_sequence=px.colors.sequential.PuBu_r)
                # st.plotly_chart(fig)

                # fetching Country from the query and getting the unique values and total value count 
                # labels = plot_data.Country.unique()
                # values = plot_data.Country.value_counts()

                # Pie chart for Country
                # st.subheader("**Pie-Chart for Country**")
                # fig = px.pie(df, values=values, names=labels, title='Usage Based on Country 🌏', color_discrete_sequence=px.colors.sequential.Purpor_r)
                # st.plotly_chart(fig)

            ## For Wrong Credentials
            else:
                st.error("Wrong ID & Password Provided")

# Calling the main (run()) function to make the whole process run
run()
