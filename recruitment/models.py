from django.db import models

from core.models import Company,Employee
from django.contrib.auth.models import User 
from django.utils import timezone
from django.core.exceptions import ValidationError


from django.db import models



class Project(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name=models.CharField(max_length=20,null=True,blank=True)
    company = models.ForeignKey(Company,on_delete=models.CASCADE,null=True,blank=True)
    description = models.TextField(null=True,blank=True)
    deadline=models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  
    def __str__(self):
        return self.name


class ScoreCard(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  
    def __str__(self):
        return self.name
    

class JobCategory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    description= models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  
    def __str__(self):
        return self.name
    


from core.models import SalaryStructure,Department,Position,Location

class Job(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    job_code = models.CharField(max_length=30,blank=True, null=True)
    project=models.ForeignKey(Project,on_delete=models.CASCADE,null=True,blank=True,related_query_name='project_job')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    company=models.ForeignKey(Company,on_delete=models.CASCADE)
    department=models.ForeignKey(Department,on_delete=models.CASCADE,null=True,blank=True,related_name='job_department')
    score_card=models.ForeignKey(ScoreCard,on_delete=models.CASCADE,null=True,blank=True)
    job_category = models.ForeignKey(JobCategory,on_delete=models.CASCADE,null=True,blank=True)
    title = models.CharField(max_length=200,null=True,blank=True)
    position=models.ForeignKey(Position,on_delete=models.CASCADE,null=True,blank=True,related_name='job_position')
    reporting_manager = models.ForeignKey(Employee,on_delete=models.CASCADE,null=True,blank=True,help_text='Please write reporting manager or hiring manager name')
    location=models.ForeignKey(Location,on_delete=models.CASCADE,null=True,blank=True,related_name='job_location')
    no_of_vacancies = models.IntegerField(null=True,blank=True)
    salary_structure = models.ForeignKey(SalaryStructure,on_delete=models.CASCADE,null=True,blank=True,related_name='job_salary_structure')
   
    deadline = models.DateField()   
    is_active = models.BooleanField(default=False,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  

    def __str__(self):
        return self.title
    


class Experience(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    score_card = models.ForeignKey(ScoreCard, on_delete=models.CASCADE,related_name='score_experience')
    year_of_experience = models.PositiveIntegerField()  
    area_of_experience = models.CharField(max_length=100,null=True,blank=True)  
    score = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  

    def __str__(self):
        return f"{self.year_of_experience} years experience in {self.area_of_experience}"



class Education(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    score_card = models.ForeignKey(ScoreCard, on_delete=models.CASCADE,related_name='score_education')
    degree_awarded = models.CharField(max_length=50,null=True,blank=True)
    score = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  

    def __str__(self):
        return f"{self.degree_awarded}"


class EducationalInstitution(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    score_card = models.ForeignKey(ScoreCard, on_delete=models.CASCADE,related_name='score_institution')
    institution_name = models.CharField(max_length=100)
    score = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  

    def __str__(self):
        return self.institution_name


class EducationalSubject(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    score_card = models.ForeignKey(ScoreCard, on_delete=models.CASCADE,related_name='score_esubject')
    subject = models.CharField(max_length=100)
    score = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  

    def __str__(self):
        return self.subject


class Age(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    score_card = models.ForeignKey(ScoreCard, on_delete=models.CASCADE,related_name='score_age')
    age = models.PositiveIntegerField()
    score = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  

    def __str__(self):
        return f"{self.age} years"


class Certification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    score_card = models.ForeignKey(ScoreCard, on_delete=models.CASCADE,related_name='score_certification')
    certificate_name = models.CharField(max_length=100)
    score = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  

    def __str__(self):
        return self.certificate_name


class Skills(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    score_card = models.ForeignKey(ScoreCard, on_delete=models.CASCADE,related_name='score_skills')
    skill_name = models.CharField(max_length=100)
    score = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  

    def __str__(self):
        return self.skill_name
    
    
class Language(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    score_card = models.ForeignKey(ScoreCard, on_delete=models.CASCADE,related_name='score_language')
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  
    def __str__(self):
        return self.name


class LanguageSkillLevel(models.Model):  
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name="skill_levels")
    level = models.CharField(
        max_length=40,
        choices=[('average', 'Average'), ('good', 'Good'), ('excellent', 'Excellent')]
    )
    score = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  

    def __str__(self):
        return f"{self.language.name} - {self.level}"



class Candidate(models.Model):   
    candidate = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,related_name='candidate')
    applied_job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="candidates",null=True, blank=True)    
    full_name = models.CharField(max_length=255,null=True, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=15,null=True, blank=True)  
    pp_photo = models.FileField(upload_to='Candidate_photo/',null=True, blank=True)
    resume = models.FileField(upload_to='resumes/')
    applied_at = models.DateTimeField(auto_now_add=True)
   

    status = models.CharField(
        max_length=50,
        choices=
        [
            ('APPLIED', 'Applied'), 
            ('SHORT-LISTED', 'Shortlisted'), 
            ('REJECTED', 'Rejected'),           
            ('SELECTED','Selected'),
            ('ONBOARD','Onboard'),
          
            ],
        default='Applied',null=True,blank=True
    )   
 
    cv_screening_score = models.DecimalField(max_digits=20,decimal_places=2,default=0.0,null=True, blank=True)
    exam_score = models.DecimalField(max_digits=20,decimal_places=2,default=0.0,null=True, blank=True)
    interview_score = models.DecimalField(max_digits=20,decimal_places=2,default=0.0,null=True, blank=True)
    total_score = models.DecimalField(max_digits=20,decimal_places=2,default=0.0,null=True, blank=True)
    
    cv_screening_status=models.CharField(max_length=30,choices=[('SHORT-LISTED','Short Listed'),('REJECTED','Rejected')],null=True, blank=True)
    exam_status=models.CharField(max_length=30,choices=[('EXAM-PASS','Exam Pass'),('EXAM-FAIL','Exam Fail')],null=True, blank=True)
    interview_status=models.CharField(max_length=30,choices=[('INTERVIEW-PASS','Interview Pass'),('INTERVIEW-FAIL','Interview Fail')],null=True, blank=True)
   

    offer_status = models.CharField(max_length=20, choices=[('offered', 'Offered'), ('waitlist', 'Waitlist')],null=True,blank=True)
    confirmation_status = models.CharField(max_length=20, choices=[('accepted', 'Accepted'), ('declined', 'Declined'),],null=True,blank=True)
    onboard_status = models.CharField(max_length=20, choices=[('onboard', 'Onboard'),('declined', 'Declined')],null=True,blank=True)
    
    confirmation_deadline=models.DateField(null=True,blank=True)
    joining_deadline = models.DateField(null=True,blank=True)
    expected_joining_date = models.DateField(null=True,blank=True)
    manager_confirmation_of_joining= models.BooleanField(default=False)
    
    hiring_status = models.BooleanField(default=False)
   
    gender = models.CharField(max_length=20,choices=[('male','Male'),('female','Female'),('other','other')],null=True, blank=True)
    age = models.ForeignKey(Age, on_delete=models.CASCADE,null=True, blank=True)
    education = models.ManyToManyField(Education,blank=True)
    subject_of_education = models.ManyToManyField(EducationalSubject,blank=True)
    institution_of_education = models.ManyToManyField(EducationalInstitution,blank=True)
    experience = models.ManyToManyField(Experience,blank=True)
    certification = models.ManyToManyField(Certification,blank=True)
    skills = models.ManyToManyField(Skills,blank=True)     
    language_skill_level = models.ManyToManyField(LanguageSkillLevel,blank=True)
    
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)    

    def calculate_cv_screening_score(self):  
        if not self.pk: 
            return 0       

        language_scores = self.language_skill_level.all()
        language_score = sum(
            lang_skill.score
            for lang_skill in language_scores
            if lang_skill.language.score_card == self.applied_job.score_card
        )
 
        experience_score = sum(
            exp.score
            for exp in self.experience.all()
            if exp.score_card == self.applied_job.score_card
        )

        age_score = sum(
            age.score
            for age in self.age.all()
            if age.score_card == self.applied_job.score_card
        )

        edu_score = sum(
            edu.score
            for edu in self.education.all()
            if edu.score_card == self.applied_job.score_card
        )

        edu_inst_score = sum(
            edu_inst.score
            for edu_inst in self.institution_of_education.all()
            if edu_inst.score_card == self.applied_job.score_card
        )

        edu_sub_score = sum(
            edu_sub.score
            for edu_sub in self.subject_of_education.all()
            if edu_sub.score_card == self.applied_job.score_card
        )

        certification_score = sum(
            cert.score
            for cert in self.certification.all()
            if cert.score_card == self.applied_job.score_card
        )

        skills_score = sum(
            skill.score
            for skill in self.skills.all()
            if skill.score_card == self.applied_job.score_card
        )
  
        cv_screening_score = language_score + experience_score + age_score + edu_score \
              + edu_inst_score + edu_sub_score + certification_score + skills_score
        return cv_screening_score
  
    def __str__(self):
        return f"{self.full_name}"
    
    

class Exam(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)   
    job = models.ForeignKey(Job,on_delete=models.CASCADE,related_name='job_exam')
    title = models.CharField(max_length=255) 
    total_marks = models.IntegerField() 
    pass_marks = models.IntegerField(blank=True, null=True) 
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(default=timezone.now)
    duration = models.DurationField() 
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=False,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  

    def save(self,*args,**kwargs):
        if self.start_time and self.end_time:
            self.duration = self.end_time - self.start_time            
        super().save(*args,*kwargs)

    def is_expired(self):   
        return timezone.now() > self.end_time
    

    def __str__(self):
        return self.title
    

class Question(models.Model):
    name=models.CharField(max_length=30,null=True,blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()
    marks = models.IntegerField(default=1,blank=True, null=True)
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    correct_answer = models.CharField(
        max_length=1,
        choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')]
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  
  

    def __str__(self):
        return f"{self.name} (Exam: {self.exam.title})"



class TakeExam(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name="answers")
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="exam_attempts",null=True,blank=True)
    obtained_marks = models.IntegerField(blank=True, null=True) 
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="candidate_answers")
    selected_option = models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')])
   
    status = models.CharField(
        max_length=50,
        choices=
        [
        ('APPEARED', 'Appeared'), 
        ('PASS', 'Pass'), 
        ('FAIL', 'Fail'),            
        ],
        default='Appeared'
    )   
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  

    def is_correct(self):
        return self.selected_option == self.question.correct_answer

    def __str__(self):
        return f"{self.candidate.full_name} - {self.exam.title} - {self.question.text}"
    


class Panel(models.Model):
     user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
     name=models.CharField(max_length=20,null=True,blank=True) 
     job = models.ManyToManyField(Job,blank=True,related_name='job_panel')
     exam= models.ManyToManyField(Exam, blank=True,related_name='exam_panel')
     description=models.CharField(max_length=255,null=True,blank=True)   
     is_active=models.BooleanField(default=True)
     created_at = models.DateTimeField(auto_now_add=True)
     updated_at = models.DateTimeField(auto_now=True)  

     def __str__(self):
        return f"{self.name}"



class PanelMember(models.Model): 
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    panel=models.ManyToManyField(Panel,blank=True,related_name='panel_member_panel')    
    panel_member=models.ForeignKey(Employee,on_delete=models.CASCADE)    
    is_active=models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  

    def __str__(self):
        return f"{self.panel_member}"
    
from django.core.validators import MinValueValidator, MaxValueValidator

class Interview(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='interviews')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='interviews')
    exam= models.ForeignKey(Exam,on_delete=models.CASCADE,related_name='interview_exam')
    panel_members = models.ManyToManyField(PanelMember, through='InterviewScore')  # Custom relationship
    interview_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  

    def __str__(self):
        return f" candidate:{self.candidate}; job:{self.job}; exam:{self.exam}"
    


class InterviewScore(models.Model):
    interview = models.ForeignKey(Interview, on_delete=models.CASCADE, related_name='scores')
    panel_member = models.ForeignKey(PanelMember, on_delete=models.CASCADE, related_name='panel_scores')
    communication_skill_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,)
    managerial_skill_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    interpersonal_skill_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    technical_skill_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    problem_solving_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    total_score = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    avg_score = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)   
   
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        for field_name in [
            'communication_skill_score',
            'managerial_skill_score',
            'interpersonal_skill_score',
            'technical_skill_score',
            'problem_solving_score',
        ]:
            value = getattr(self, field_name)
            if value is not None and (value < 0 or value > 10):
                raise ValidationError({field_name: 'Score must be between 0 and 10.'})       
        super().clean() 

    def save(self, *args, **kwargs): 
        scores = [
            self.communication_skill_score or 0,
            self.managerial_skill_score or 0,
            self.interpersonal_skill_score or 0,
            self.technical_skill_score or 0,
            self.problem_solving_score or 0,
        ]
        self.total_score = sum(scores)
        self.avg_score = self.total_score / len(scores) if len(scores) > 0 else 0

        super().save(*args, **kwargs)





class CandidateScreeningHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    status = models.CharField(max_length=50)
    threshold_score = models.DecimalField(max_digits=5, decimal_places=2)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    screening_round = models.IntegerField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)  

    def __str__(self):
        return f'{self.candidate.full_name} - {self.status}'
    

class ExamScreeningHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    status = models.CharField(max_length=50)
    threshold_score = models.DecimalField(max_digits=5, decimal_places=2)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    screening_round = models.IntegerField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)  

    def __str__(self):
        return f'{self.candidate.full_name} - {self.status}'
    

class InterviewScreeningHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    status = models.CharField(max_length=50)
    threshold_score = models.DecimalField(max_digits=5, decimal_places=2)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    screening_round = models.IntegerField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)  

    def __str__(self):
        return f'{self.candidate.full_name} - {self.status}'



class CommonDocument(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='common_documents/') 
    document_type = models.CharField(max_length=100, choices=[('policy', 'Policy'), ('handbook', 'Handbook'), ('contract', 'Contract')])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  
    def __str__(self):
        return self.name



class CandidateDocument(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='candidate_documents/')
    candidate = models.ForeignKey(Candidate, related_name='documents', on_delete=models.CASCADE)
    document_type = models.CharField(max_length=100, choices=[('contract', 'Contract'), ('id_proof', 'ID Proof'),('others', 'Others')])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  
    
    def __str__(self):
        return f"{self.document_type}: {self.name} for {self.candidate.full_name}"

