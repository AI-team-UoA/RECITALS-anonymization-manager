"""
REST API for the AnonymizationManager.
"""

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from .adapters.arx.arx import ARXAnonymizer
from .config import AnonymizationConfig
from .core import AnonymizationManager
from .exceptions import (
    AnonymizationError,
    BackendError, 
    ConfigurationError, 
    NoSolutionError,
)

# Starts the JVM, this has to be done in the main thread. Starting the JVM
# from a worker thread where requests run hangs forever.
ARXAnonymizer._load_arx_library()

app = FastAPI()

def _error_response(status_code: int, error: str, detail, backend: str | None = None) -> JSONResponse:
    """Builds an error response with a uniform format for every error."""
    content = {"error": error, "detail": detail}
    if backend:
        content["backend"] = backend
    return JSONResponse(status_code=status_code, content=content)


def _anonymization_error_response(status_code: int, ex: AnonymizationError) -> JSONResponse:
    return _error_response(status_code, type(ex).__name__, ex.message, ex.backend)


@app.exception_handler(RequestValidationError)
async def request_validation_handler(request: Request, ex: RequestValidationError):
    """
    Handles invalid request bodies (wrong types, missing files, invalid privacy requests).

    Returns:
        JSONResponse: A 400 response listing each validation error.
    """
    messages = []
    for err in ex.errors():
        cause = err.get("ctx", {}).get("error")
        if isinstance(cause, ConfigurationError) and isinstance(
            cause.__cause__, ValidationError
        ):
            errors = cause.__cause__.errors()
        else:
            errors = [err]

        for e in errors:
            messages.append(
                {
                    "field": ".".join(str(p) for p in e["loc"] if p != "body"),
                    "message": e["msg"].removeprefix("Value error, "),
                }
            )
    return _error_response(400, "ValidationError", messages)


@app.exception_handler(ConfigurationError)
async def configuration_error_handler(request: Request, ex: ConfigurationError):
    """Handles invalid configurations found by a backend. Returns 400."""
    return _anonymization_error_response(400, ex)


@app.exception_handler(NoSolutionError)
async def no_solution_handler(request: Request, ex: NoSolutionError):
    """Handles runs where no anonymization satisfies the privacy models. Returns 422."""
    return _anonymization_error_response(422, ex)


@app.exception_handler(BackendError)
async def backend_error_handler(request: Request, ex: BackendError):
    """Handles failures of the anonymization engine. Returns 500."""
    return _anonymization_error_response(500, ex)


@app.exception_handler(Exception)
async def unexpected_error_handler(request: Request, ex: Exception):
    """Handles any other error. Returns 500 without internal details."""
    return _error_response(500, "InternalServerError", "An unexpected error occurred.")


@app.post("/anonymize")
def anonymize(config: AnonymizationConfig):
    """
    Anonymizes a dataset according to the provided configuration.

    Args:
        config (AnonymizationConfig): The anonymization configuration.
    
    Returns:
        JSONResponse: A 200 response containing:
            - data: the anonymized dataset as a list of JSON records.
            - metadata: statistics describing the transformation, including the
              anonymization time.
    """
    result = AnonymizationManager.anonymize(config)
    content={
        "data": result.get_anonymized_data_as_dataframe().to_dict(orient="records"),
        "metadata": {
            "anonymization_time_ms" : result.get_anonymization_time(),
            "average_equivalence_class_size" : result.get_average_equivalence_class_size(),
            "transformations" : result.get_transformations(),
        },                      
    }
    return JSONResponse(content=jsonable_encoder(content))
