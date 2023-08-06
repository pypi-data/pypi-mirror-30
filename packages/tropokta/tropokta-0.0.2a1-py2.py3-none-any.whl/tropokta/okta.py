from troposphere import AWSObject


class OktaUser(AWSObject):
    resource_type = "Custom::OktaUser"

    props = {
        'ServiceToken': (str, True),
        'firstName': (baseString, True),
        'lastName': (baseString, True),
        'email': (baseString, True),
        'login': (baseString, True)
    }


class OktaGroup(AWSObject):
    resource_type = "Custom::OktaGroup"

    props = {
        'ServiceToken': (str, True),
        'name': (str, True),
        'description': (str, True)
    }


class OktaUserGroupAttachment(AWSObject):
    resource_type = "Custom::OktaUserGroupAttachment"

    props = {
        'ServiceToken': (str, True),
        'groupId': (str, True),
        'userId': (str, True)
    }
