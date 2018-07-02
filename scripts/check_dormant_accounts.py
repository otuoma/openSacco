from payments.models import Payment
from members.models import Member
import datetime, calendar
import arrow
from django.core.mail import send_mail


now = datetime.datetime.now()
today = arrow.utcnow().to(tz='Africa/Nairobi')


def last_payment_details(member_id):

    return Payment.objects.filter(member_id=member_id).order_by('-date').last()


def run():

    print('===============Starting script========================\n')

    members = Member.objects.filter(is_active=True)

    for member in members:

        payment_details = last_payment_details(member.pk)

        if payment_details is None:
            continue

        last_date = arrow.get(payment_details.date)

        diff = today - last_date

        if diff.days == 60:

            sixty_day_msg = "Dear " + payment_details.member.get_full_name() + ",<p>"
            sixty_day_msg += "Your SACCO account has been dormant for 60 days now. </p><p>Kindly make a deposit in the next 15 days to avoid being declared inactive.</p>"
            sixty_day_msg += "<p>You last deposited %s on %s. If this is not correct, kindly contact our officials.</p>" % (payment_details.amount, payment_details.date)
            sixty_day_msg += "<p>Thank you.</p>"

            send_mail(
                subject="Dormant Account - First Reminder",
                message="",
                html_message=sixty_day_msg,
                from_email='wecanys2@gmail.com',
                recipient_list=[payment_details.member.email]
            )

        elif diff.days == 75:

            second_msg = "Dear " + payment_details.member.get_full_name() + ",<p>"
            second_msg += "Your SACCO account has been dormant for 75 days now. </p><p> Kindly make a deposit ASAP to avoid being declared inactive.</p>"
            second_msg += "<p>You last deposited %s on %s. If this is not correct, kindly contact our officials.</p>" % (payment_details.amount, payment_details.date)
            second_msg += "<p>Thank you.</p>"

            send_mail(
                subject="Second Reminder - Dormant Account",
                message="",
                html_message=second_msg,
                from_email='wecanys2@gmail.com',
                recipient_list=[payment_details.member.email]
            )

        elif diff.days == 90:

            # Deactivate account

            member_acc = member

            member_acc.is_active = False

            member_acc.save()

            final_msg = "Dear " + payment_details.member.get_full_name() + ",<p>"
            final_msg += "Your SACCO account has been dormant for 90 days now. <br> As a result, the account has been deactivavted.</p>"
            final_msg += "<p>You last deposited %s on %s. If this is not correct, kindly contact our officials.</p>" % (payment_details.amount, payment_details.date)
            final_msg += "<p>Thank you.</p>"

            send_mail(
                subject="Account deactivated",
                message="",
                html_message=final_msg,
                from_email='wecanys2@gmail.com',
                recipient_list=[payment_details.member.email]
            )

        else:
            continue











