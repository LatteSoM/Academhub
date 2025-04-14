from locust import HttpUser, TaskSet, task, between
from locust.exception import StopUser

class ContingentTasks(TaskSet):
    @task(5)
    def discipline_list(self):
        self.client.get("/ContingentApp/discipline/list")
    
    @task(5)
    def specialty_list(self):
        self.client.get("/ContingentApp/specialty/list")
    
    @task(5)
    def qualification_list(self):
        self.client.get("/ContingentApp/qualification/list")
    
    @task(5)
    def group_list(self):
        self.client.get("/ContingentApp/group/list")
    
    @task(5)
    def student_list(self):
        self.client.get("/ContingentApp/student/list")
    
    @task(5)
    def gradebook_list(self):
        self.client.get("/GradeBook/gradebook/list")
    
    @task(5)
    def user_list(self):
        self.client.get("/AccessControl/user/list")
    
    @task(5)
    def group_list_access(self):
        self.client.get("/AccessControl/group/list")

class GradebookTasks(TaskSet):
    @task(5)
    def gradebook_list(self):
        self.client.get("/GradeBook/gradebook/list")
    
    @task(3)
    def teacher_gradebook_list(self):
        self.client.get("/GradeBook/gradebook/teacher/list")

class AccessControlTasks(TaskSet):
    @task(5)
    def user_list(self):
        self.client.get("/AccessControl/user/list")
    
    @task(5)
    def group_list(self):
        self.client.get("/AccessControl/group/list")

class WebsiteUser(HttpUser):
    tasks = {
        ContingentTasks: 5,
        GradebookTasks: 3,
        AccessControlTasks: 2
    }
    wait_time = between(1, 5)
    host = "http://localhost:8000"
    
    def on_start(self):
        self.login()

    def login(self):
        response = self.client.get("/auth/")
        csrftoken = response.cookies['csrftoken']
        
        self.client.post("/auth/",
                        {"username": "admin@admin.admin", "password": "admin"},
                        headers={"X-CSRFToken": csrftoken})
        
        if response.status_code != 200:
            raise StopUser("Failed to login")