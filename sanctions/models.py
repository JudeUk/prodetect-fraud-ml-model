from django.db import models

# Create your models here.

from django.contrib.postgres.fields import ArrayField
from enum import Enum

class SourceEnum(Enum):
    SDN = "SDN"
    NONSDN = "NONSDN"
    UK = "UK"
    EU = "EU"
    OFAC_SDN = "OFAC SDN"
    OFAC_CONSOLIDATED = "OFAC Consolidated (non-SDN) List"
    BIS_DENIED = "BIS Denied Persons List"
    UN_SECURITY_COUNCIL = "UN Security Council Consolidated Sanctions"
    OFSI = "Office of Financial Sanctions Implementation"
    FSF = "EU Financial Sanctions Files (FSF)"
    PEP = "Politically Exposed Persons (PEP)"
    DFAT = "Australian Department of Foreign Affairs and Trade (DFAT)"
    FHFA = "US FHFA Suspended Counterparty Program"
    SAM = "US SAM Procurement Exclusions"
    HUD = "HUD Excluded Parties Listing"
    DUAL_USE = "Dual Use Items"
    SEMA = "Canadian Special Economic Measures Act Sanctions"
    BFS = "Belgian Financial Sanctions"
    SECO = "Swiss SECO Sanctions and Embargoes"
    MXSAT = "Mexican Tax Code Article 69.B"
    LEIE = "OIG List of Excluded Individuals and Entities"
    LFIU = "Lithuanian FIU Sanctions"
    FINCEN = "FinCEN 311 and 9714 Special Measures"

class EntityTypeEnum(Enum):
    PERSON = "person"
    ORGANIZATION = "organization"
    VESSEL = "vessel"
    AIRCRAFT = "aircraft"

class SanctionsRequest(models.Model):
    api_key = models.CharField(max_length=255)
    sources = ArrayField(models.CharField(max_length=100, choices=[(tag.value, tag.value) for tag in SourceEnum]))
    types = ArrayField(models.CharField(max_length=20, choices=[(tag.value, tag.value) for tag in EntityTypeEnum]))





class Address(models.Model):
    address1 = models.CharField(max_length=255)
    address2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state_or_province = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)

class Identification(models.Model):
    id_number = models.CharField(max_length=255)
    type = models.CharField(max_length=100)
    country = models.CharField(max_length=100, blank=True, null=True)

class Case(models.Model):
    sanctions_request = models.ForeignKey(SanctionsRequest, on_delete=models.CASCADE, related_name='cases')
    case_id = models.CharField(max_length=255)  # Changed from 'id' to 'case_id' to avoid conflict with Django's default 'id'
    name = models.CharField(max_length=255)
    id_number = models.CharField(max_length=255, blank=True, null=True)
    crypto_id = models.CharField(max_length=255, blank=True, null=True)
    address = models.ForeignKey(Address, on_delete=models.CASCADE, null=True)
    identifications = models.ManyToManyField(Identification, related_name='cases')



class ResponseSource(models.Model):
    source = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    publish_date = models.DateField()
    download_date = models.DateTimeField()

    def __str__(self):
        return self.name

# PersonDetails Model
class PersonDetails(models.Model):
    first_name = models.CharField(max_length=255, null=True, blank=True)
    middle_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True)
    birth_dates = models.JSONField(null=True, blank=True)  # Storing multiple birth dates
    citizenships = models.JSONField(null=True, blank=True)
    nationalities = models.JSONField(null=True, blank=True)
    positions = models.JSONField(null=True, blank=True)
    education = models.JSONField(null=True, blank=True)

# VesselDetails Model
class VesselDetails(models.Model):
    vessel_type = models.CharField(max_length=255, null=True, blank=True)
    call_sign = models.CharField(max_length=255, null=True, blank=True)
    flag = models.CharField(max_length=255, null=True, blank=True)
    owner = models.CharField(max_length=255, null=True, blank=True)
    imo_number = models.CharField(max_length=255, null=True, blank=True)
    tonnage = models.CharField(max_length=255, null=True, blank=True)
    gross_tonnage = models.CharField(max_length=255, null=True, blank=True)

# AircraftDetails Model
class AircraftDetails(models.Model):
    icao_code = models.CharField(max_length=255, null=True, blank=True)
    serial_number = models.CharField(max_length=255, null=True, blank=True)

# Result Matches Model
class Match(models.Model):
    match_id = models.CharField(max_length=255)
    match_type = models.CharField(max_length=255)
    categories = models.JSONField(null=True, blank=True)
    name = models.CharField(max_length=255)
    name_formatted = models.CharField(max_length=255, null=True, blank=True)
    entity_link = models.URLField(max_length=255, null=True, blank=True)
    source = models.CharField(max_length=255)
    source_id = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)
    effective_date = models.CharField(max_length=255, null=True, blank=True)
    expiration_date = models.CharField(max_length=255, null=True, blank=True)
    last_update = models.CharField(max_length=255, null=True, blank=True)
    alias = models.JSONField(null=True, blank=True)
    addresses = models.JSONField(null=True, blank=True)
    identifications = models.JSONField(null=True, blank=True)
    email_addresses = models.JSONField(null=True, blank=True)
    phone_numbers = models.JSONField(null=True, blank=True)
    websites = models.JSONField(null=True, blank=True)
    crypto_wallets = models.JSONField(null=True, blank=True)
    source_links = models.JSONField(null=True, blank=True)
    programs = models.JSONField(null=True, blank=True)
    additional_sanctions = models.JSONField(null=True, blank=True)
    additional_information = models.JSONField(null=True, blank=True)
    person_details = models.OneToOneField(PersonDetails, null=True, blank=True, on_delete=models.CASCADE)
    vessel_details = models.OneToOneField(VesselDetails, null=True, blank=True, on_delete=models.CASCADE)
    aircraft_details = models.OneToOneField(AircraftDetails, null=True, blank=True, on_delete=models.CASCADE)

# Results Model
class Result(models.Model):
    result_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    match_count = models.IntegerField()
    matches = models.ManyToManyField(Match)

# Main Response Model
class APIResponse(models.Model):
    error = models.BooleanField(default=False)
    error_message = models.CharField(max_length=255, null=True, blank=True)
    sources = models.ManyToManyField(ResponseSource)
    results = models.ManyToManyField(Result)