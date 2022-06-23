from rest_framework.serializers import ValidationError


def validate_latitude(value):
    if value < -90 or value > 90:
        raise ValidationError(
            {"latitude": "Latitude is supposed to be between -90 and 90."}
        )


def validate_longitude(value):
    if value < -180 or value > 180:
        raise ValidationError(
            {"longitude": "Longitude is supposed to be between -180 and 180."}
        )


def validate_rating(value):
    if value < 0 or value > 5:
        raise ValidationError({"rating": "Rating is supposed to be from 0 to 5."})


def validate_distance(value):
    if value <= 0 or value >= 40076:
        raise ValidationError(
            {"distance": "Distance must be between 0 and 40076 kilometers."}
        )
