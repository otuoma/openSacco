from django.db import models
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _


class Download(models.Model):
    title = models.CharField(max_length=100)
    document = models.FileField(upload_to='downloads')

    def __str__(self):
        return self.title


class Faq(models.Model):
    question = models.CharField(max_length=100)
    answer = models.TextField(max_length=5000,)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.question


class FooterRight(models.Model):
    title = models.CharField(max_length=100)
    text = models.TextField(max_length=100)
    signup_link_text = models.CharField(max_length=100)

    def __str__(self):
        return "Footer Right"


class FooterCenter(models.Model):
    title = models.CharField(max_length=100)
    facebook_url = models.URLField(max_length=500)
    googleplus_url = models.URLField(max_length=500)
    twitter_url = models.URLField(max_length=500)
    linked_in_url = models.URLField(max_length=500)
    dribble_url = models.URLField(max_length=500)

    def __str__(self):

        return "Footer Center"


class FooterLeft(models.Model):
    title = models.CharField(max_length=100)
    text = models.TextField(max_length=500)

    def __str__(self):
        return "Footer Left"


class ManagementTeam(models.Model):

    page_title = models.CharField(max_length=150)

    def __str__(self):
        return 'Management Page'


class SupervisoryCommittee(models.Model):
    page_title = models.CharField(max_length=150)

    def __str__(self):
        return 'Supervisory Committee Page'


class FunActivity(models.Model):
    page_title = models.CharField(max_length=150)

    def __str__(self):
        return 'Activities Page'


class Projects(models.Model):
    page_title = models.CharField(max_length=150)
    description = models.CharField(max_length=250)

    def __str__(self):
        return 'Projects Page'


class Loans(models.Model):
    page_title = models.CharField(max_length=150)

    def __str__(self):
        return 'Loans Page'


class LoanProduct(models.Model):
    product_name = models.CharField(max_length=150)
    description = models.TextField(max_length=2000)

    def __str__(self):

        return self.product_name


class SectionImage(models.Model):
    image = models.ImageField(upload_to='management_team')
    caption = models.CharField(max_length=150)
    description = models.CharField(max_length=1000, blank=True)
    section = models.CharField(
        max_length=150,
        choices=(
            ('management', 'Management'),
            ('supervisory', 'Supervisory committee'),
            ('activities', 'Activities'),
            ('projects', 'Projects'),
        ),
    )

    def image_tag(self):

        return mark_safe("<img src='/media/" + str(self.image) + "' width=150 />")

    image_tag.short_description = "Thumbnail"
    image_tag.allow_tags = True

    def __str__(self):

        return self.caption


class About(models.Model):
    page_title = models.CharField(max_length=150)
    tagline_left = models.CharField(max_length=150)

    section1_title = models.CharField(max_length=150)
    section1_text = models.TextField(verbose_name='Section1 text')

    section2_title = models.CharField(max_length=150)
    section2_text = models.TextField(verbose_name='Section2 text')

    section3_title = models.CharField(max_length=150)
    section3_text = models.TextField(verbose_name='Section3 text')

    section4_title = models.CharField(max_length=150)
    section4_text = models.TextField(verbose_name='Section4 text')

    section5_title = models.CharField(max_length=150)
    section5_text = models.TextField(verbose_name='Section5 text')

    def __str__(self):
        return "About Section"


class Home(models.Model):
    title_top = models.CharField(max_length=150)
    title_bottom = models.CharField(max_length=150)
    keyword1 = models.CharField(max_length=150)
    keyword2 = models.CharField(max_length=150)
    keyword3 = models.CharField(max_length=150)
    form_title = models.CharField(max_length=150)
    background_image = models.ImageField(upload_to='background_images')

    def __str__(self):
        return "Home page items"

    class Meta:
        permissions = (
            ('can_update_website', _('Can update website')),
        )
