import datetime
from main_app.models import PayProduct
from celery import task


@task
def check_reservation_bot():
    timenow = datetime.datetime.now(datetime.timezone.utc)
    queryset = PayProduct.objects.all()
    for item in queryset:
        time_passed = abs(int((item.datetime - timenow).total_seconds() / 60))
        if time_passed >= 1:
            item.cancel_reservation()
