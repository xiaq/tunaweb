from flatland import String
from flatland.validation import Present, IsEmail


OptionalText = String.using(optional=True)
RequiredText = String.validated_by(Present())
RequiredEmail = String.validated_by(Present(), IsEmail())
