class ConfigurationRouter:
    """
    A router to control all database operations on models in the
    auth and contenttypes applications.
    """
    route_app_labels = {'auth', 'contenttypes','admin','sessions','administrator','configuration','lms'}

    def db_for_read(self, model, **hints):
        """
        Attempts to read auth and contenttypes models go to auth_db.
        """
        if model._meta.app_label in self.route_app_labels:
            return 'configuration_db'
        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write auth and contenttypes models go to auth_db.
        """
        if model._meta.app_label in self.route_app_labels:
            return 'configuration_db'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the auth or contenttypes apps is
        involved.
        """
        if (
            obj1._meta.app_label in self.route_app_labels or
            obj2._meta.app_label in self.route_app_labels
        ):
           return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure the auth and contenttypes apps only appear in the
        'auth_db' database.
        """
        if app_label in self.route_app_labels:
            return db == 'configuration_db'
        return None

class ApplicantRouter:
    route_app_labels = {'applicant'}

    def db_for_read(self, model, **hints):
        
        if model._meta.app_label in self.route_app_labels:
            return 'applicant_db'
        return None

    def db_for_write(self, model, **hints):
        
        if model._meta.app_label in self.route_app_labels:
            return 'applicant_db'
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        
        if app_label in self.route_app_labels:
            return db == 'applicant_db'
        return None

class StudentRouter:
    route_app_labels = {'academic','attendance','result','student','studentpage','card'}

    def db_for_read(self, model, **hints):
        
        if model._meta.app_label in self.route_app_labels:
            return 'student_db'
        return None

    def db_for_write(self, model, **hints):
        
        if model._meta.app_label in self.route_app_labels:
            return 'student_db'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        
        if (
            obj1._meta.app_label in self.route_app_labels or
            obj2._meta.app_label in self.route_app_labels
        ):
           return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        
        if app_label in self.route_app_labels:
            return db == 'student_db'
        return None

class HostelRouter:
    route_app_labels = {'hostel'}

    def db_for_read(self, model, **hints):
        
        if model._meta.app_label in self.route_app_labels:
            return 'hostel_db'
        return None

    def db_for_write(self, model, **hints):
        
        if model._meta.app_label in self.route_app_labels:
            return 'hostel_db'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        
        if (
            obj1._meta.app_label in self.route_app_labels or
            obj2._meta.app_label in self.route_app_labels
        ):
           return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        
        if app_label in self.route_app_labels:
            return db == 'hostel_db'
        return None

class StaffRouter:
    route_app_labels = {'staff'}

    def db_for_read(self, model, **hints):
        
        if model._meta.app_label in self.route_app_labels:
            return 'staff_db'
        return None

    def db_for_write(self, model, **hints):
        
        if model._meta.app_label in self.route_app_labels:
            return 'staff_db'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        
        if (
            obj1._meta.app_label in self.route_app_labels or
            obj2._meta.app_label in self.route_app_labels
        ):
           return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        
        if app_label in self.route_app_labels:
            return db == 'staff_db'
        return None

class MiscellaneousRouter:
    route_app_labels = {'payment','news','activity'}

    def db_for_read(self, model, **hints):
        
        if model._meta.app_label in self.route_app_labels:
            return 'miscellaneous_db'
        return None

    def db_for_write(self, model, **hints):
        
        if model._meta.app_label in self.route_app_labels:
            return 'miscellaneous_db'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        
        if (
            obj1._meta.app_label in self.route_app_labels or
            obj2._meta.app_label in self.route_app_labels
        ):
           return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        
        if app_label in self.route_app_labels:
            return db == 'miscellaneous_db'
        return None