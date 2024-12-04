"""TODO: DOCS"""

from typing import Literal, overload
from os import environ
from datetime import datetime
from requests import api, RequestException
from ..data.dynamics_service import (
    DataApiAuthentication, DataApiCredentials, DataApiPayload, DataApiResService,
    DataApiServiceBills, DataApiServiceProducts, DataApiServicePrices
)
from ..config import Configuration, KeySitesDynamics
from ..utils import ENVIRONMENT

def login_service(dynamics_env: KeySitesDynamics | None = None, /) -> DataApiAuthentication:
    """Realiza la peticion para hacer login en microsoft."""
    dynamics_env = dynamics_env or ("prod" if ENVIRONMENT == "prod" else "uat")

    ### Implementación de la caché, memoizacion de la autenticación.
    if not hasattr(login_service, "__cache__"):
        setattr(login_service, "__cache__", {})
    __cache__: dict[KeySitesDynamics, DataApiAuthentication] = getattr(login_service, "__cache__")

    if dynamics_env in __cache__:
        authentication: DataApiAuthentication = __cache__[dynamics_env]
        auth_is_expired = datetime.now() > authentication.expires_on
        if not auth_is_expired:
            return authentication

    resource = Configuration.get_site("dynamics:" + dynamics_env)
    credentials = DataApiCredentials(resource=resource.geturl())

    credentials.grant_type = environ.get("DYNAMICS_SERVICE_AUTH_GRANTYPE")
    credentials.aad_tenant = environ.get("DYNAMICS_SERVICE_AAD_TENANT")
    credentials.client_id = environ.get("DYNAMICS_SERVICE_CLIENT_ID")
    credentials.client_secret = environ.get("DYNAMICS_SERVICE_CLIENT_SECRET")

    if not credentials.exists():
        raise EnvironmentError("No se han establecido las credenciales del servicio Dynamics 365.")

    credentials_dict = credentials.to_dict()
    aad_tenant = credentials_dict.pop("aad_tenant")
    url = Configuration.get_site("dynamics_login", "login", aad_tenant=aad_tenant)
    timeout = Configuration.api_service.dynamics_timeout
    response = api.post(url.geturl(), data=credentials_dict, timeout=timeout)
    if response.status_code != 200:
        raise RequestException("No se pudo hacer login en el servicio Dynamics 365.")

    authentication = DataApiAuthentication.from_dict(response.json())
    __cache__[dynamics_env] = authentication
    setattr(login_service, "__cache__", __cache__)
    return authentication

DynamicsService = Literal["bills", "products", "prices"]

def request_service(service: DynamicsService,
                    payload: DataApiPayload,
                    dynamics_env: KeySitesDynamics | None = None,
                    /) -> DataApiResService:
    """Lanzar el servicio de dynamics 365."""
    dynamics_env = dynamics_env or ("prod" if ENVIRONMENT == "prod" else "uat")
    url = Configuration.get_site("dynamics:" + dynamics_env, "service_" + service)

    auth = login_service(dynamics_env)

    headers = {"Authorization": f"Bearer {auth.access_token}"}
    body = {"_request": payload.to_dict()}
    timeout = Configuration.api_service.dynamics_timeout

    response = api.post(url.geturl(), headers=headers, json=body, timeout=timeout)
    status_code = response.status_code
    if status_code != 200:
        msg = f"No se pudo obtener la data en el servicio Dynamics 365: Status code, {status_code}"
        raise RequestException(msg)
    return DataApiResService.from_dict(response.json())


@overload
def get_service(service: Literal["bills"],
                 payload: DataApiPayload,
                 dynamics_env: KeySitesDynamics | None = None,
                 /) -> list[DataApiServiceBills]: pass
@overload
def get_service(service: Literal["products"],
                 payload: DataApiPayload,
                 dynamics_env: KeySitesDynamics | None = None,
                 /) -> list[DataApiServiceProducts]: pass
@overload
def get_service(service: Literal["prices"],
                 payload: DataApiPayload,
                 dynamics_env: KeySitesDynamics | None = None,
                 /) -> list[DataApiServicePrices]: pass
def get_service(service: DynamicsService,
                payload: DataApiPayload,
                dynamics_env: KeySitesDynamics | None = None,
                /):
    """Lanza el servicio de dynamics y devuelve como resultado la data del servicio."""
    data_response = request_service(service, payload, dynamics_env)
    data_class = None
    if service == "bills":
        data_class = DataApiServiceBills
    elif service == "products":
        data_class = DataApiServiceProducts
    elif service == "prices":
        data_class = DataApiServicePrices
    else:
        raise TypeError("No se ha seleccionado el servicio correcto en API Dynamics 365.")

    return [data_class.from_dict(data) for data in data_response.DebugMessage]
