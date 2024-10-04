# from django.shortcuts import render

# Create your views here.

# sanctions/views.py

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import requests
from .models import APIResponse, AircraftDetails, PersonDetails, ResponseSource, SanctionsRequest, Case, Identification, Address, Result, Match, SourceEnum, EntityTypeEnum, VesselDetails

# @method_decorator(csrf_exempt, name='dispatch')
@csrf_exempt
# class SanctionsSearchView(View):
def sanctions_search_view(request):
        try:
            # Parse the incoming JSON request
            data = json.loads(request.body)
            
            # Validate sources
            valid_sources = set(item.value for item in SourceEnum)
            if not set(data.get('sources', [])).issubset(valid_sources):
                return JsonResponse({'error': True, 'errorMessage': 'Invalid source provided'}, status=400)

            # Validate types
            valid_types = set(item.value for item in EntityTypeEnum)
            if not set(data.get('types', [])).issubset(valid_types):
                return JsonResponse({'error': True, 'errorMessage': 'Invalid entity type provided'}, status=400)
            
            # Create a SanctionsRequest instance
            sanctions_request = SanctionsRequest.objects.create(
                api_key=data['apiKey'],
                sources=data['sources'],
                types=data['types']
            )
            
            # Process cases
            for case_data in data.get('cases', []):
                address_data = case_data.get('address')
                address = None
                if address_data:
                    address = Address.objects.create(**address_data)
                
                case = Case.objects.create(
                    sanctions_request=sanctions_request,
                    case_id=case_data['id'],
                    name=case_data['name'],
                    id_number=case_data.get('idNumber'),
                    crypto_id=case_data.get('cryptoId'),
                    address=address
                )
                
                for id_data in case_data.get('identification', []):
                    identification = Identification.objects.create(
                        id_number=id_data['idNumber'],
                        type=id_data['type'],
                        country=id_data.get('country')
                    )
                    case.identifications.add(identification)
            
            # Prepare the request to the OFAC API
            url = "https://api.ofac-api.com/v4/search"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {data['apiKey']}"
            }
            
            # Make the request to the OFAC API
            response = requests.post(url, json=data, headers=headers)
            json_data = response.json()

            response_obj = {
            "error": json_data.get('error', False),
            "error_message": json_data.get('errorMessage', ''),
            "sources": [],
            "results": []
        }

            # Process sources
            for source in json_data.get('sources', []):
                source_obj = {
                    "source": source.get('source'),
                    "name": source.get('name'),
                    "country": source.get('country'),
                    "publish_date": source.get('publishDate'),
                    "download_date": source.get('downloadDate'),
                }
                response_obj["sources"].append(source_obj)

            # Process results
            for result in json_data.get('results', []):
                result_obj = {
                    "id": result.get('id'),
                    "name": result.get('name'),
                    "match_count": result.get('matchCount'),
                    "matches": []
                }

                for match in result.get('matches', []):
                    # Handle PersonDetails if present
                    person_details_obj = None
                    if match.get('personDetails'):
                        person_details_data = match['personDetails']
                        person_details_obj = {
                            "first_name": person_details_data.get('firstName', ''),
                            "middle_name": person_details_data.get('middleName', ''),
                            "last_name": person_details_data.get('lastName', ''),
                            "title": person_details_data.get('title', ''),
                            "gender": person_details_data.get('gender', ''),
                            "birth_dates": person_details_data.get('birthDates', []),
                            "citizenships": person_details_data.get('citizenships', []),
                            "nationalities": person_details_data.get('nationalities', []),
                            "positions": person_details_data.get('positions', []),
                            "education": person_details_data.get('education', [])
                        }

                    # Handle VesselDetails if present
                    vessel_details_obj = None
                    if match.get('vesselDetails'):
                        vessel_details_data = match['vesselDetails']
                        vessel_details_obj = {
                            "vessel_type": vessel_details_data.get('vesselType', ''),
                            "call_sign": vessel_details_data.get('callSign', ''),
                            "flag": vessel_details_data.get('flag', ''),
                            "owner": vessel_details_data.get('owner', ''),
                            "imo_number": vessel_details_data.get('imoNumber', ''),
                            "tonnage": vessel_details_data.get('tonnage', ''),
                            "gross_tonnage": vessel_details_data.get('grossTonnage', '')
                        }

                    # Handle AircraftDetails if present
                    aircraft_details_obj = None
                    if match.get('aircraftDetails'):
                        aircraft_details_data = match['aircraftDetails']
                        aircraft_details_obj = {
                            "icao_code": aircraft_details_data.get('icaoCode', ''),
                            "serial_number": aircraft_details_data.get('serialNumber', '')
                        }

                    match_obj = {
                        "id": match.get('id'),
                        "type": match.get('type'),
                        "categories": match.get('categories', []),
                        "name": match.get('name'),
                        "name_formatted": match.get('nameFormatted', ''),
                        "entity_link": match.get('entityLink', ''),
                        "source": match.get('source', ''),
                        "source_id": match.get('sourceId', ''),
                        "description": match.get('description', ''),
                        "remarks": match.get('remarks', ''),
                        "effective_date": match.get('effectiveDate', ''),
                        "expiration_date": match.get('expirationDate', ''),
                        "last_update": match.get('lastUpdate', ''),
                        "alias": match.get('alias', []),
                        "addresses": match.get('addresses', []),
                        "identifications": match.get('identifications', []),
                        "email_addresses": match.get('emailAddresses', []),
                        "phone_numbers": match.get('phoneNumbers', []),
                        "websites": match.get('websites', []),
                        "crypto_wallets": match.get('cryptoWallets', []),
                        "source_links": match.get('sourceLinks', []),
                        "programs": match.get('programs', []),
                        "additional_sanctions": match.get('additionalSanctions', []),
                        "additional_information": match.get('additionalInformation', []),
                        "person_details": person_details_obj,
                        "vessel_details": vessel_details_obj,
                        "aircraft_details": aircraft_details_obj
                    }

                    result_obj["matches"].append(match_obj)

                response_obj["results"].append(result_obj)

            return JsonResponse(response_obj, json_dumps_params={'indent': 2})
        
        except Exception as e:
            return JsonResponse({'error': True, 'errorMessage': str(e)}, status=500)
        




        # response_obj.save()

        # return JsonResponse({'message': 'Response processed successfully!'})
            
        #     # Create a SanctionsResponse instance
        #     sanctions_response = SanctionsResponse.objects.create(
        #         error=response_data.get('error', False),
        #         error_message=response_data.get('errorMessage')
        #     )
            
        #     # Process and save the results
        #     for result_data in response_data.get('results', []):
        #         result = Result.objects.create(
        #             response=sanctions_response,
        #             result_id=result_data['id'],
        #             name=result_data['name'],
        #             match_count=result_data['matchCount']
        #         )
                
        #         for match_data in result_data.get('matches', []):
        #             Match.objects.create(
        #                 result=result,
        #                 match_id=match_data['id'],
        #                 type=match_data['type'],
        #                 categories=match_data['categories'],
        #                 name=match_data['name'],
        #                 name_formatted=match_data['nameFormatted'],
        #                 entity_link=match_data['entityLink'],
        #                 source=match_data['source'],
        #                 source_id=match_data['sourceId'],
        #                 description=match_data.get('description'),
        #                 remarks=match_data.get('remarks'),
        #                 identifications=match_data.get('identifications', []),
        #                 # Add other fields as necessary
        #             )
            
        #     # Return the response from the OFAC API
        #     return JsonResponse(response_data)
        
        # except Exception as e:
        #     return JsonResponse({'error': True, 'errorMessage': str(e)}, status=500)