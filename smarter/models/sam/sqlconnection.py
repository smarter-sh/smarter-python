"""
SAM model of the ``SqlConnection`` kind, generated from the Smarter platform's JSON Schema.

Do not edit: run ``scripts/generate_sam_models.py``. See :mod:`smarter.models.sam`.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Optional, Union
from uuid import UUID

from pydantic import Field

from smarter.models.sam.base import SAMModel


class Connection(SAMModel):
    """Smarter API - generic SQL Connection class."""

    authenticationMethod: str | None = Field("none", title="Authenticationmethod")
    """
    The authentication method to use for the connection.

    Example: 'Standard TCP/IP', 'Standard TCP/IP over SSH', 'LDAP User/Password'.
    """
    database: str = Field(..., title="Database")
    """
    The name of the database to connect to.

    Examples: 'sales' or 'mydb'.
    """
    dbEngine: str = Field(..., title="Dbengine")
    """A valid SQL database engine. Common db_engines: ['django.db.backends.postgresql', 'django.db.backends.mysql', 'django.db.backends.oracle', 'django.db.backends.sqlite3', 'django.db.backends.mssql', 'django.db.backends.sybase']."""
    hostname: str = Field(..., title="Hostname")
    """
    The remote host of the SQL connection.

    Should be a valid internet domain name. Example: 'localhost' or 'mysql.mycompany.com'.
    """
    maxOverflow: int | None = Field(10, title="Maxoverflow")
    """The maximum number of connections to allow beyond the pool size."""
    password: str | None = Field(None, title="Password")
    """The password."""
    poolSize: int | None = Field(5, title="Poolsize")
    """The size of the connection pool."""
    port: int | None = Field(None, title="Port")
    """
    The port of the SQL connection.

    Default values are assigned based on the dbEngine.
    """
    proxyHost: str | None = Field(None, title="Proxyhost")
    """
    The remote host of the SQL proxy connection.

    Should be a valid internet domain name.
    """
    proxyPassword: str | None = Field(None, title="Proxypassword")
    """The password for the proxy connection."""
    proxyPort: int | None = Field(None, title="Proxyport")
    """The port of the SQL proxy connection."""
    proxyUsername: str | None = Field(None, title="Proxyusername")
    """The username for the proxy connection."""
    sshKnownHosts: str | None = Field(None, title="Sshknownhosts")
    """The known_hosts file content for verifying SSH connections."""
    sslCa: str | None = Field(None, title="Sslca")
    """The Certificate Authority (CA) certificate for verifying the server."""
    sslCert: str | None = Field(None, title="Sslcert")
    """The SSL certificate for the connection, if required."""
    sslKey: str | None = Field(None, title="Sslkey")
    """The SSL key for the connection, if required."""
    timeout: int | None = Field(30, title="Timeout")
    """
    The timeout for the database connection in seconds.

    Default is 30 seconds.
    """
    useSsl: bool | None = Field(False, title="Usessl")
    """Whether to use SSL/TLS for the connection."""
    username: str | None = Field(None, title="Username")
    """The database username."""


class SAMConnectionCommonMetadata(SAMModel):
    """Smarter API Connection Manifest - common Metadata class."""

    annotations: None | (
        list[dict[str, str | int | float | bool | date | datetime | UUID | bytes | list | dict[str, Any]]]
    ) = Field(None, title="Annotations")
    """
    The manifest annotations.

    Used for storing arbitrary metadata as
                key-value pairs. Example: [{'smarter.sh/test-manifest/project-name': 'Scooby dooby do'}]. The
                key should be a valid url-friendly string. The value accepts
                multi-line string values (YAML block scalars) and various scalar types including
                str, int, float, bool, datetime.date, datetime.datetime, decimal.Decimal, uuid.UUID, bytes, list, dict.
    """
    description: str | None = Field(..., title="Description")
    """
    The description for this resource.

    Be brief. Keep it under 255 characters.
    """
    name: str = Field(..., title="Name")
    """The camelCase name of the manifest resource."""
    tags: list[str] | None = Field(None, title="Tags")
    """
    The tags of the manifest.

    Used for generic resource categorization and search. Example: ['tag1', 'tag2']
    """
    version: str | None = Field(..., title="Version")
    """
    The semantic version of the manifest.

    Example: 0.1.0
    """


class SAMDependency(SAMModel):
    """A resource that depends on the resource that a manifest describes."""

    kind: str = Field(..., title="Kind")
    """
    Kind[String]: The SAM kind of the resource that depends on this resource, e.g. LLMClient.

    Read only.
    """
    name: str = Field(..., title="Name")
    """
    Name[String]: The name of the resource that depends on this resource.

    Read only.
    """


class SAMSqlConnectionSpec(SAMModel):
    """Smarter API Sql Connection Manifest Connection.spec."""

    connection: Connection
    """SqlConnection.spec.selector[obj]: the selector logic to use for the SqlConnection."""


class SAMConnectionCommonStatus(SAMModel):
    """Smarter API Connection Manifest - Status class."""

    account_number: str = Field(..., title="Account Number")
    """
    Connection.status.account_number: The account owner of this Connection.

    Read only.
    """
    created: datetime = Field(..., title="Created")
    """
    The date in which this resource was created.

    Read only.
    """
    dependencies: list[SAMDependency] | None = Field(None, title="Dependencies")
    """
    Dependencies[List]: The resources that depend on this resource, and that must be deleted, or stop referring to it, before it can be deleted.

    Lists only the resources that you can read. Read only.
    """
    modified: datetime = Field(..., title="Modified")
    """
    The date in which this resource was most recently changed.

    Read only.
    """
    recordLocator: str = Field(..., title="Recordlocator")
    """
    RecordLocator[String]: An optional identifier used to locate the resource record associated with this manifest.

    Read only.
    """
    username: str = Field(..., title="Username")
    """
    Connection.status.username: The Smarter user who created this Connection.

    Read only.
    """


class SAMSqlConnection(SAMModel):
    """Smarter API Manifest - SqlConnection Model."""

    apiVersion: str = Field(..., title="Apiversion")
    """
    ApiVersion[String]: Required.

    The API version of the AbstractSAMBase.
    """
    kind: str = Field(..., title="Kind")
    """
    Kind[String]: Required.

    The kind of resource described by the manifest.
    """
    metadata: SAMConnectionCommonMetadata
    """SqlConnection.metadata[obj]: Required, the SqlConnection metadata."""
    spec: SAMSqlConnectionSpec
    """SqlConnection.spec[obj]: Required, the SqlConnection specification."""
    status: SAMConnectionCommonStatus | None = None
    """
    SqlConnection.status[obj]: Optional, Read-only.

    Stateful status information about the SqlConnection.
    """
