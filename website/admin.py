from django.contrib import admin
from website.models import Download, Faq, FooterRight, FooterCenter, FooterLeft, Home, About, FunActivity, Loans, ManagementTeam, SupervisoryCommittee, Projects, LoanProduct, SectionImage


#  DownloadAdmin section
class DownloadAdmin(admin.ModelAdmin):
    pass


admin.site.register(Download, DownloadAdmin)


#  FAQAdmin section
class FaqAdmin(admin.ModelAdmin):
    pass


admin.site.register(Faq, FaqAdmin)


#  FooterRight section
class FooterRightAdmin(admin.ModelAdmin):
    pass


admin.site.register(FooterRight, FooterRightAdmin)


#  FooterCenter section
class FooterCenterAdmin(admin.ModelAdmin):
    pass


admin.site.register(FooterCenter, FooterCenterAdmin)


#  FooterLeft section
class FooterLeftAdmin(admin.ModelAdmin):
    pass


admin.site.register(FooterLeft, FooterLeftAdmin)


#  SectionImage section
class SectionImageAdmin(admin.ModelAdmin):
    fields = ['caption', 'description', 'section', 'image', 'image_tag']
    readonly_fields = ['image_tag', ]


admin.site.register(SectionImage, SectionImageAdmin)


#  LoanProduct section
class LoanProductAdmin(admin.ModelAdmin):
    pass


admin.site.register(LoanProduct, LoanProductAdmin)


#  Projects section
class ProjectsAdmin(admin.ModelAdmin):
    pass


admin.site.register(Projects, ProjectsAdmin)


#  SupervisoryCommittee section
class SupervisoryCommitteeAdmin(admin.ModelAdmin):
    pass


admin.site.register(SupervisoryCommittee, SupervisoryCommitteeAdmin)


#  ManagementTeam section
class ManagementTeamAdmin(admin.ModelAdmin):
    pass


admin.site.register(ManagementTeam, ManagementTeamAdmin)


#  Loans section
class LoansAdmin(admin.ModelAdmin):
    pass


admin.site.register(Loans, LoansAdmin)


#  FunActivity section
class FunActivityAdmin(admin.ModelAdmin):
    pass


admin.site.register(FunActivity, FunActivityAdmin)


#  About section
class AboutAdmin(admin.ModelAdmin):
    pass


admin.site.register(About, AboutAdmin)


# Home/Header section
class HomeAdmin(admin.ModelAdmin):
    pass


admin.site.register(Home, HomeAdmin)


