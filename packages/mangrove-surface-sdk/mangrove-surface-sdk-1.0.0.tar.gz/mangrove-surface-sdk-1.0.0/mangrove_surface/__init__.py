# coding: utf-8
import time
import warnings
from mangrove_surface.api import MangroveError
from mangrove_surface.api.client_rest import Controller
from mangrove_surface.api.feature_set import FeatureSet
from mangrove_surface.api.license import License
from mangrove_surface.api.project import Project
from mangrove_surface.api.user import User
from mangrove_surface.api.token import Token
from mangrove_surface.api.version import Version
from mangrove_surface.wrapper.classifier import ClassifierWrapper
from mangrove_surface.wrapper.project import ProjectWrapper
from ._version import get_versions
__version__ = get_versions()['version']
del get_versions


class ProjectDoesNotExist(KeyError):
    pass


class SurfaceClient(object):
    """
    Instanciate Mangrove.ai python SDK with instance url and identity access

    :param url: (*optional*) url of the Mangrove.ai instance
        (by default environment variable ``SURFACE_URL`` is used)
    :param token: (*optional*) access token used to secure connection
        (by default, if ``username``/``password`` are given then those are used
        to generate an access token; otherwise environment variable
        ``SURFACE_TOKEN`` is used)
    :param username: (*optional*) username used (with ``password``) to sign in
        (by default, a token is expected)
    :param password: (*optional*) password used to (with ``username``) sign
        in  (by default, a token is expected)

    .. note::

        Surface URL or access token can be explicitly provided as
        parameters or implicitly using environment variables (``SURFACE_URL``
        and ``SURFACE_TOKEN``)

    :raises IOError: if the endpoint doesn't answer correctly
    :raises AttributeError: if url, username-password or token are not
        provided

    Load Surface python SDK::

        >>> from mangrove_surface import SurfaceClient

    Instanciate with url and token are environment variables::

        >>> client = SurfaceClient()

    Or with url as environment variable and an
    explicit token::

        >>> client = SurfaceClient(token='eyJ0eXAiOiJKV1QiLCJhbGciOiJ...')

    Or with explicit url and token::

        >>> client = SurfaceClient(
        ...     url='http://my.surface/api',
        ...     token='eyJ0eXAiOiJKV1QiLCJhbGciOiJ...'
        ... )

    """

    def __init__(
        self, url=None, token=None, username=None, password=None
    ):
        self.admin = self._Admin(self)
        self._controller = Controller(
            self, surface_url=url, token=token,
            username=username, password=password
        )

    class _Admin:
        """
        Administration methods:
        """

        def __init__(self, mang):
            self.mang = mang

        def create_user(self, username, password):
            """
            Create a user

            :param username: new username
            :param password: it password

            """
            return User.create(self.mang._controller, username, password)

        def users(self):
            """
            Retrieve all users

            ::

                >>> mang.admin.users()
                [admin(admin), Toto, Gillou]

            """
            return User.retrieve_all(self.mang._controller)

        def delete_users(self, *usernames):
            """
            Delete users

            :param \*usernames: arbitrary number of usernames

            ::

                >>> mang.admin.delete_users("Alice", "Bob", "Oscar")

            """
            return User.delete(
                self.mang._controller, data={"usernames": list(usernames)}
            )

        def tokens(self):
            """
            List all tokens

            ::

                >>> mang.admin.tokens()
                [{
                    'created_at': '2018-03-29T09:45:06.067Z',
                    'expires_at': 1577833200,
                    'id': '40a6a8b6-65b1-465e-b6c7-6c3021c30952',
                    'name': 'token_jbp',
                    'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiI4MjI0OTg4NC05M2UwLTQwN2MtYmQ3OS02NTllMWE4MzQ2NTUiLCJzY3AiOiJ1c2VyIiwiaWF0IjoxNTAzOTk5OTA2LCJleHAiOjE1Nzc4MzMyMDAsImp0aSI6IjhlN2I5YmM1LTAxODItNGRmYi1hMzM0LTAxYzQ4ODc5OTk1NCIsInR5cGUiOiJhcHBsaWNhdGlvbiJ9.looosUk2TuXOVXREmAvPoVnOx0kLaSLOT4TlOMK_yTA',
                    'updated_at': '2018-03-29T09:45:06.067Z'
                }]

            """
            return Token.retrieve_all(self.mang._controller)

        def create_token(self, token_name, expiration_date):
            """
            Create a new token

            :param token_name:
            :param expiration date: should be a `datetime.datetime` object

            ::

                >>> from datetime import datetime
                >>> expire = datetime(2020, 1, 1)
                >>> mang.admin.create_token('token_jbp', expire)
                {
                    'created_at': '2018-03-29T09:45:06.067Z',
                    'expires_at': 1577833200,
                    'id': '40a6a8b6-65b1-465e-b6c7-6c3021c30952',
                    'name': 'token_jbp',
                    'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiI4MjI0OTg4NC05M2UwLTQwN2MtYmQ3OS02NTllMWE4MzQ2NTUiLCJzY3AiOiJ1c2VyIiwiaWF0IjoxNTAzOTk5OTA2LCJleHAiOjE1Nzc4MzMyMDAsImp0aSI6IjhlN2I5YmM1LTAxODItNGRmYi1hMzM0LTAxYzQ4ODc5OTk1NCIsInR5cGUiOiJhcHBsaWNhdGlvbiJ9.looosUk2TuXOVXREmAvPoVnOx0kLaSLOT4TlOMK_yTA',
                    'updated_at': '2018-03-29T09:45:06.067Z'
                }

            """
            return Token.create(
                self.mang._controller, token_name,
                int(time.mktime(expiration_date.timetuple()))
            )

        def license_information(self, request_code=False):
            """
            Retrieve license information

            :param request_code: (default `False`) if `True` it adds the
                request code to obtain a new license (only for *byol*)

            ::

                >>> mang.admin.license_information()
                [{
                    'expires_at': '2018-08-29 00:00:00 UTC',
                    'service_level': 'full',
                    'system_information': None,
                    'updated_at': '2018-03-29 09:49:34 UTC'
                }]

                >>> mang.admin.license_information(request_code=True)
                [{
                    'expires_at': '2018-08-29 00:00:00 UTC',
                    'service_level': 'full',
                    'system_information': {
                        'request_code': 'kzho-isiA-8dwy-gZyq-gFNb-EC5l-od7s-JBai-RcaF-2hMb-cirj-52rS-P4M3-2sRg-fuZa-/S5W-FkRn-RDSo-srVa-0xlX-q7KO-NkMY-380Y-dmW4-JfHG-Q01x-so3N-NhdO-MoMj-Xw+B-bUdb-Q7VI-K+Hy-gSMF-kVpD-kCkO-v3Ay-a2/f-To9v-Lnxw-3EdE-FEPa-yVMI-x/U4-EsUV-T1eq-LQsM-C88E-yPOS-RtVp-vDtD-zwEn-PAS7-/pSl-MGJ+-jnUq-JllG-uxO+-seDZ-6X+v-rXBI-zHUx-go3p-K2ZO'
                    },
                    'updated_at': '2018-03-29 09:49:34 UTC'
                }]

            :raises MangroveError: if the license has expired

            ::

                {
                    "status": 402,
                    "status_text": "Payment Required",
                    "errors": [
                        {
                            "code": "LICENSE-402-002",
                            "type": "license",
                            "metadata": {
                                "reason": "License not found",
                                "request_code": "P6jC-ns9H-X5ph-KZVg-finF-ttgv-2Jtl-ygPn-Ie/z-VUBc-hYYz-GeLT-yTb4-UrkS-tr/s-w3uf-lzlG-Av34-3fnx-0gl2-8SnL-jaQt-0BJ+-bhKU-zgWl-tu6j-kM4r-i84u-s2Qo-SR4P-JyEH-AIRh-psnw-d0zd-R+Nf-zrl+-8hWy-l3Db-HeD9-6DY7-gwlO-1Zjp-Opvu-pp5I-mxWQ-qDtS-WWTo-xjlK-hE9q-sukL-YEeK-OPWz-aaJl-0ZzB-0sN2-6Gqz-soPd-lEXR-USDl-vDzJ-JltE-RWX+-HfZs-2Njd",
                                "type": "private",
                                "autofetch": False
                            }
                        }
                    ]
                }

            """
            return (
                License.retrieve_with_request_code if request_code else
                License.retrieve
            )(self.mang._controller)

        def new_license(self, license_code):
            """
            Update the licence

            :param license_code: string provided by the Mangrove team

            ::

                >>> mang.admin.new_license('fxbE-D9pK-h0t7-x+5r-B3G7-bY+x-AG6x-dzYW-tccq-HAtl-Bkzb-JPVw-jsFd-zcvN-Nr15-vkIZ-ZK4J-yafW-niK9-RbaV-FGS9-oks5-zsLJ-yweZ-fg3K-SAeT-jDWP-pDnj-bJ8P-ZjKh-Tskp-I/1A-Ymow-fV6s-fvXK-dliu-cHCY-1Orf-pBY0-VDgm-IBaP-3Dz3-CiYS-4MVR-hQsO-KNfu-WK7d-7/6w-CTNW-A0HA-9rnB-im62-evcd-j7HS-KnnL-K/aD-UNlU-5vO5-K9g=')
                {
                    'expires_at': '2018-03-30 00:00:00 UTC',
                    'service_level': 'full',
                    'system_information': None,
                    'updated_at': '2018-03-31 11:47:54 UTC'
                }

            :raise HTTPError: if you provide a wrong license

            (Please use GUI)
            """
            return License.new_license(self.mang._controller, license_code)

        def versions(self):
            """
            Version information

            ::

                >>> mang.admin.versions()
                [
                    {
                        'name': 'atlas',
                        'version': '0.0.1-alpha.1'
                    }, {
                        'name': 'license_authority',
                        'version': u'1.3.2-rc1'
                    }, {
                        'name': 'dmgr',
                        'version': '0.0.1'
                    }, {
                        'name': 'modeler',
                        'version': '0.0.1-alpha.1'
                    }, {
                        'name': 'exporter',
                        'version': '0.0.1'
                    }, {
                        'name': 'mang_sdk',
                        'version': '1.2.1-30-ge792bea-dirty'
                    }
                ]

            """
            return Version.retrieve(self.mang._controller)

    def create_project(
        self, name, schema, description="", schema_test=None, tags=[],
        default_classifier=True, force=False
    ):
        """
        Create a new project

        :param name: project name
        :param description: (*optional*) project description
        :param schema: (*optional*) a data schema which contains train data
            sets and relations, like::

                {
                    "tags": ["dataset", "tag"],
                    "datasets": [
                        {
                            "name": "Dataset Name",
                            "filepath": "/path/to/dataset.csv",
                            "tags": ["optional", "tags"],
                            "central": True | False,
                            "keys: ["index"], # optional if there is only
                                              # one dataset
                            "separator": ",", # could be `|`, `,`, `;` or `\t`
                        }, ...
                    ],
                    "outcome": "FIELD TARGETED",
                    "outcome_modality": "main value targeted"
                }

            `filepath` is an absolute filepath or it could be a S3 uri, like::

                {
                    "type": "s3",
                    "bucket": "mang-model-producer-samples",
                    "key": "CAR_INSURANCE/CHAT_SESSION_CONTENT_TRAIN.csv"
                }

        :param tags: (*optional*) list of project tags
        :param schema_test: (*optional*) a data schema which contains
            test data sets and relations, like **schema**
        :param default_classifier: (*default*: ``True``) indicates if a default
            classifier it provided at the project creation
        :param force: (*default*: ``False``) indicates if a project with the
            same name exists then it is replaced or not

        """
        try:
            pj = ProjectWrapper(
                Project.create(
                    self._controller, name, description, tags
                ),
                self
            )
        except MangroveError as e:
            err0 = e.resource["errors"][0]
            if "metadata" not in err0.keys():
                raise e
            reason = err0["metadata"]["reason"]
            if force and err0["code"] == "ATLAS-422-000" and \
                    reason == "Name has already been taken":
                pj = self.project(name)
                pj.api_resource.delete(
                    self._controller,
                    pj.api_resource.id()
                )
                return self.create_project(
                    name, schema, description=description,
                    schema_test=schema_test, tags=tags,
                    default_classifier=default_classifier, force=False
                )
            else:
                raise

        coll = pj.create_collection()
        fs = coll.create_schema("train", schema)
        fs_test = None
        if schema_test:
            fs_test = coll.create_schema("test", schema_test)

        if default_classifier:
            cl = fs.fit_classifier()
            if fs_test:
                # TODO
                pass
        return pj

    def project(self, name):
        """
        Return project named ``name``

        :param name: the name of the wished project
        """
        pjs = list(filter(lambda pj: pj.name() == name, self.projects()))
        if len(pjs) == 0:
            raise ProjectDoesNotExist(name + ' does not exists')
        elif len(pjs) > 1:
            warnings.warn("There is several projects called `%s`! " % name +
                          "The 1st has been selected.")
        return pjs[0]

    def projects(self):
        """
        List all projects
        """
        return [ProjectWrapper(pjr, self)
                for pjr in Project.retrieve_all(self._controller)]
