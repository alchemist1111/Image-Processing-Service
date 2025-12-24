from faker import Faker
from django.db.utils import IntegrityError
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model



User = get_user_model()

class Command(BaseCommand):
    help = 'Generates fake users'
    
    def handle(self, *args, **kwargs):
        fake = Faker()
        
        # How many users I want to generate
        number_of_users = 1000
        
        # A set to store the already genrated emails to ensure uniqueness
        created_users = set()
        
        for _ in range(number_of_users):
            # Genarate a unique email
            while True:
                email = fake.email()
                if email not in created_users:
                    created_users.add(email)
                    break
                
            # Generate fake user data
            first_name = fake.first_name()
            last_name = fake.last_name()
            password = fake.password()
            created_at = fake.date_time_this_decade()
            updated_at = fake.date_time_this_decade()
            
            # Create and save the user instance
            user = User(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    created_at=created_at,
                    updated_at=updated_at
                )
            user.set_password(password) # Hash the password
            try:
                user.save()
                self.stdout.write(self.style.SUCCESS(f'User {email} created successfully'))
            except IntegrityError:
                self.stdout.write(self.style.ERROR(f'Failed to create user {email}, email already exists'))