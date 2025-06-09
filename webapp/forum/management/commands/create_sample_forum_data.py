from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from forum.models import ForumCategory, ForumPost, Comment
from django.utils import timezone

class Command(BaseCommand):
    help = 'Creates sample forum categories and posts'

    def handle(self, *args, **kwargs):
        # Create categories
        categories = [
            {
                'name': 'General Car Discussion',
                'description': 'A place for general discussions about cars, including maintenance tips, driving experiences, and automotive news.'
            },
            {
                'name': 'Technical & Modifications',
                'description': 'Discuss car modifications, technical specifications, repair guides, and performance upgrades.'
            },
            {
                'name': 'Car Reviews',
                'description': 'Share and read reviews of different car models, both new and used.'
            },
            {
                'name': 'Car Shows & Events',
                'description': 'Discuss upcoming car shows, meetups, and automotive events.'
            },
            {
                'name': 'Buy & Sell',
                'description': 'Marketplace for cars, parts, and automotive accessories.'
            }
        ]

        # Create or get admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'is_staff': True,
                'is_superuser': True,
                'email': 'admin@example.com'
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('Created admin user'))

        # Create categories
        for cat_data in categories:
            category, created = ForumCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created category "{category.name}"'))

                # Create sample posts for each category
                for i in range(1, 4):
                    post = ForumPost.objects.create(
                        title=f'Sample {category.name} Post {i}',
                        content=f'This is a sample post in the {category.name} category. It contains example content that demonstrates how posts appear in the forum.',
                        category=category,
                        author=admin_user
                    )
                    
                    # Create sample comments for each post
                    for j in range(1, 3):
                        Comment.objects.create(
                            post=post,
                            author=admin_user,
                            content=f'Sample comment {j} on this post. This shows how comments appear under posts.'
                        )
                    
                    self.stdout.write(self.style.SUCCESS(f'Created post "{post.title}" with comments'))

        self.stdout.write(self.style.SUCCESS('Successfully created sample forum data'))
