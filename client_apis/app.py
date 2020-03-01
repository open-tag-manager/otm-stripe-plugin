from chalice import Blueprint, Response
from botocore.errorfactory import ClientError
from chalicelib import authorizer, s3, has_role
import stripe
import json
import os

plugin_app = Blueprint(__name__)

stripe.api_key = os.environ.get('STRIPE_SK')


def get_payment_data(org):
    bucket = os.environ.get('OTM_BUCKET')
    file = org + '_payment.json'
    object = s3.Object(bucket, file)
    try:
        response = object.get()
        data = json.loads(response['Body'].read())
        return data
    except ClientError:
        return None


@plugin_app.route('/', methods=['GET'], cors=True, authorizer=authorizer)
def get_payment_customer(org):
    app = plugin_app._current_app
    if not has_role(app, org, 'write'):
        return Response(body={'error': 'permission error'}, status_code=401)

    data = get_payment_data(org)

    if data:
        customer = stripe.Customer.retrieve(data['id'])
        pm_id = customer['invoice_settings']['default_payment_method']
        pm = stripe.PaymentMethod.retrieve(pm_id)

        return {'id': data['id'], 'name': customer['name'], 'email': customer['email'], 'payment_method': pm}

    return None


@plugin_app.route('/', methods=['PUT'], cors=True, authorizer=authorizer)
def put_payment_customer(org):
    app = plugin_app._current_app
    if not has_role(app, org, 'write'):
        return Response(body={'error': 'permission error'}, status_code=401)

    request = app.current_request
    body = request.json_body

    if body.keys() < {'email', 'name', 'payment_method'}:
        return Response(body={'error': 'email, name and payment_method is required'}, status_code=400)

    data = get_payment_data(org)

    if data:
        stripe.PaymentMethod.attach(body['payment_method'], customer=data['id'])
        customer = stripe.Customer.modify(
            data['id'],
            email=body['email'],
            name=body['name'],
            invoice_settings={'default_payment_method': body['payment_method']}
        )
    else:
        customer = stripe.Customer.create(
            email=body['email'],
            name=body['name'],
            metadata={'org': org},
            payment_method=body['payment_method'],
            invoice_settings={'default_payment_method': body['payment_method']}
        )

    bucket = os.environ.get('OTM_BUCKET')
    file = org + '_payment.json'
    object = s3.Object(bucket, file)
    object.put(Body=json.dumps(customer), ContentType='application/json')

    pm_id = customer['invoice_settings']['default_payment_method']
    pm = stripe.PaymentMethod.retrieve(pm_id)

    return {'id': customer['id'], 'name': body['name'], 'email': body['email'], 'payment_method': pm}
