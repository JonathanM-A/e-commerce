from django.db import models
from apps.facilities.models import Facility
from rest_framework.serializers import ValidationError
import re
from datetime import date

class Client(models.Model):
    # Gender choices
    # male = "Male"
    # female = "Female"
    # other = "Other"

    GENDER_CHOICES = [("male", "Male"), ("female", "Female"), ("other", "Other")]

    # Member type choices
    # member = "Member"
    # insurance = "Insurance Member"
    # corporate = "Corporate Member"

    MEMBER_TYPE = [
        ("member", "Member"),
        ("insurance", "Insurance Member"),
        ("corporate", "Corporate Member"),
    ]

    # Insurance Company choices
    # acacia = "Acacia Health Insurance"
    # apex = "Apex Health Insurance"
    # glico_health = "Glico Health"
    # glico_tpa = "Glico TPA"
    # allianz = "Allianz"

    INSURANCE_COMPANY = [
        ("acacia", "Acacia Health Insurance"),
        ("apex", "Apex Health Insurance"),
        ("glico_health", "Glico Health Insurane"),
        ("glico_tpa", "Glico TPA")
    ]

    # Corporate choices
    # vivo = "Vivo Energy Limited"
    # mtn = "Scancom PLC"
    # stanbic_bank = "Stanbic Bank Ghana"

    CORPORATE = [
        ("vivo", "Vivo Energy Limited"),
        ("mtn", "MTN Ghana"),
        ("stanbic_bank", "Stanbic Bank Ghana"),
    ]

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    client_id = models.CharField(max_length=6, unique=True)
    gender = models.CharField(choices=GENDER_CHOICES)
    age = models.PositiveIntegerField()
    phone_number = models.CharField(max_length=10)
    member_type = models.CharField(choices=MEMBER_TYPE)
    insurance_id = models.CharField()
    insurance_company = models.CharField(choices=INSURANCE_COMPANY, blank=True)
    corporate_id = models.CharField()
    corporate_company = models.CharField(choices=CORPORATE, blank=True)
    parent_facility = models.ForeignKey(
        Facility, on_delete=models.CASCADE, related_name="clients"
    )
    date_joined = models.DateField(default=date.today)

    # Create a constraint on age(18)
    # Create an account for minors linked to client

    def save(self, *args, **kwargs):
        # regex for first and last name
        names = self.first_name + self.last_name
        if not re.fullmatch(r"[a-z'\.-]+", names, re.I):
            raise ValidationError(
                "Names can only contain alphabets and these special characters(.-')"
            )
        # regex for phone number
        phone_no = re.match(r"^(0)([0-9]{9})$", self.phone_number)
        if not phone_no:
            raise ValidationError("Invalid phone number")
        if phone_no[1] != "0":
            raise ValidationError("Phone number must start with 0")

        # logic for affiliate companies
        if self.member_type == "Member":
            if self.insurance_company or self.corporate_company:
                raise ValidationError(
                    "Member type cannot have an insurance or corporate company"
                )

        if self.member_type == "Insurance":
            if self.corporate_company:
                raise ValidationError(
                    "Insurance member cannot have a corporate company"
                )
            if not self.insurance_company or not self.insurance_id:
                raise ValidationError("Insurance company and ID must be provided")
            
        if self.member_type == "Corporate":
            if self.insurance_company:
                raise ValidationError(
                    "Corporate member cannot have an insurance company"
                )
            if not self.corporate_company or self.corporate_id:
                raise ValidationError("Corporate company and ID must be provided")
            
        # Client ID generation
        if not self.client_id:
            last_client = Client.objects.order_by("-client_id").first()
            if last_client:
                new_id = int(last_client.client_id) + 1
            else:
                new_id = 100000
            self.client_id = f"{new_id:06}"
    
        return super().save(*args, **kwargs)
    
    @property
    def fullname(self):
        return f"{self.first_name} {self.last_name}"
    
    def __str__(self) -> str:
        return self.fullname