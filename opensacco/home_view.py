from django.views.generic import (TemplateView, FormView, ListView)
from members.forms import (SignUpForm, LoginForm)
from .forms import ContactForm
from django.core.mail import mail_managers, send_mail
from django.contrib import messages
from django.shortcuts import render, redirect
from website.models import FooterLeft, FooterCenter, FooterRight, LoanProduct, Loans, Projects, FunActivity, SupervisoryCommittee, Home, About, ManagementTeam, SectionImage
from website.models import Faq, Download


class ViewDownloads(ListView):
    template_name = 'downloads.html'

    def get(self, request, *args, **kwargs):

        context = {
            'download_list': Download.objects.all(),
            'footer_left': FooterLeft.objects.first(),
            'footer_center': FooterCenter.objects.first(),
            'footer_right': FooterRight.objects.first(),
        }

        return render(request, self.template_name, context=context)


class ViewFAQS(ListView):
    model = Faq
    template_name = 'faqs.html'

    def get(self, request, *args, **kwargs):

        faq_list = Faq.objects.filter(is_active=True)

        context = {
            'faq_list': faq_list
        }

        return render(request, self.template_name, context=context)


class SendContactMessage(FormView):

    def post(self, request, *args, **kwargs):

        form = ContactForm(data=request.POST)

        if form.is_valid():

            recipients = ['muchemis@gmail.com',]
            from_email = form.cleaned_data['email']
            subject = 'Contact Message from %s : %s ' % (form.cleaned_data['name'], form.cleaned_data['phone'])
            message = form.cleaned_data['message']
            message += '<hr> Reply to %s ' % (form.cleaned_data['email'])

            # Send notification to managers and new member
            try:
                send_mail(
                    subject=subject,
                    message='',
                    html_message=message,
                    recipient_list=recipients,
                    from_email=from_email,
                )
            except Exception:
                pass

            messages.success(request, 'Success, your message has been sent.', extra_tags='alert alert-success')

        else:

            messages.error(request, 'Fail, errors occured in the form', extra_tags='alert alert-danger')

        return redirect(to='home')


class LoadHome(TemplateView):
    template_name = 'home.html'

    def get(self, request, *args, **kwargs):

        form = LoginForm

        context = {
            'form': form,
            'home_items': Home.objects.first(),
            'about_section': About.objects.first(),
            'management_section': ManagementTeam.objects.first(),
            'management_images': SectionImage.objects.filter(section='management'),
            'supervisory_section': SupervisoryCommittee.objects.first(),
            'supervisory_images': SectionImage.objects.filter(section='supervisory'),
            'activity_section': FunActivity.objects.first(),
            'activity_images': SectionImage.objects.filter(section='activities'),
            'projects_section': Projects.objects.first(),
            'projects_images': SectionImage.objects.filter(section='projects'),
            'loans_section': Loans.objects.first(),
            'loan_products': LoanProduct.objects.all(),
            'footer_left': FooterLeft.objects.first(),
            'footer_center': FooterCenter.objects.first(),
            'footer_right': FooterRight.objects.first(),
        }

        return render(request, self.template_name, context=context)









